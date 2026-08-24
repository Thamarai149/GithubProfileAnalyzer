/* ─── Language color map ────────────────────────────────── */
const LANG_COLORS = {
  JavaScript: '#f7df1e', TypeScript: '#3178c6', Python:  '#3572a5',
  Rust:       '#dea584', Go:         '#00add8', Java:    '#b07219',
  CSS:        '#563d7c', HTML:       '#e34c26', C:       '#555555',
  'C++':      '#f34b7d', Ruby:       '#701516', Swift:   '#f05138',
  Kotlin:     '#7f52ff', Shell:      '#89e051', Vue:     '#41b883',
  PHP:        '#4f5d95',
};
function langColor(lang) {
  return LANG_COLORS[lang] || '#4a5675';
}

/* ─── DOM refs ──────────────────────────────────────────── */
const form         = document.getElementById('analyze-form');
const statusEl     = document.getElementById('status');
const resultsEl    = document.getElementById('results');
const analyzeBtn   = document.getElementById('analyze-btn');
const btnText      = analyzeBtn.querySelector('.btn-text');
const btnSpinner   = analyzeBtn.querySelector('.btn-spinner');
const usernameInput = document.getElementById('username');

/* ─── Mobile sidebar toggle ─────────────────────────────── */
const sidebar        = document.getElementById('sidebar');
const sidebarToggle  = document.getElementById('sidebarToggle');
const sidebarOverlay = document.getElementById('sidebarOverlay');

sidebarToggle.addEventListener('click', () => {
  sidebar.classList.toggle('open');
  sidebarOverlay.classList.toggle('open');
});
sidebarOverlay.addEventListener('click', () => {
  sidebar.classList.remove('open');
  sidebarOverlay.classList.remove('open');
});

/* ─── Nav items — scroll to section ────────────────────── */
const toolSections = ['compare', 'saved', 'settings'];

document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', e => {
    e.preventDefault();

    const section = item.dataset.section;

    // Tool items (no real section) — don't change active state
    if (toolSections.includes(section)) {
      document.getElementById('search-section')
        .scrollIntoView({ behavior: 'smooth', block: 'start' });
      sidebar.classList.remove('open');
      sidebarOverlay.classList.remove('open');
      return;
    }

    // Update active state only for real sections
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    item.classList.add('active');

    // Close mobile sidebar
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('open');

    const targetId = item.dataset.target;
    if (!targetId) return;

    const target = document.getElementById(targetId);
    if (!target) return;

    // If results are hidden, scroll to search instead
    const resultsHidden = document.getElementById('results').classList.contains('hidden');
    const scrollTarget = (targetId !== 'search-section' && resultsHidden)
      ? document.getElementById('search-section')
      : target;

    scrollTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Flash highlight on the card
    if (!resultsHidden && targetId !== 'results' && targetId !== 'search-section') {
      target.classList.add('nav-highlight');
      setTimeout(() => target.classList.remove('nav-highlight'), 900);
    }
  });
});

/* ─── Form submit ───────────────────────────────────────── */
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = usernameInput.value.trim();
  if (!username) return;

  setLoading(true);
  setStatus('Analyzing profile…', false);

  try {
    const res  = await fetch('/api/analyze', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ username }),
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || 'Unable to analyze profile.');

    renderResults(data);
    setStatus(`Showing results for @${data.profile.login}`, false);
  } catch (err) {
    setStatus(err.message, true);
    resultsEl.classList.add('hidden');
  } finally {
    setLoading(false);
  }
});

/* ─── Loading state ─────────────────────────────────────── */
function setLoading(on) {
  analyzeBtn.classList.toggle('loading', on);
  btnText.classList.toggle('hidden', on);
  btnSpinner.classList.toggle('hidden', !on);
}

function setStatus(msg, isError) {
  statusEl.textContent = msg;
  statusEl.classList.toggle('error', isError);
}

/* ─── Render ────────────────────────────────────────────── */
function renderResults(data) {
  const { profile, summary, insights, language_usage, recent_repositories } = data;

  renderProfile(profile);
  renderKPIs(profile, summary, insights);
  renderRepoTable(summary.top_repos);
  renderLanguageBars(language_usage);
  renderInsights(summary, insights);
  renderRecentRepos(recent_repositories);

  resultsEl.classList.remove('hidden');

  // Update topbar avatar
  const avatarWrap = document.getElementById('topbar-avatar');
  avatarWrap.innerHTML = `<img src="${profile.avatar_url}" alt="avatar" />`;

  // Smooth scroll to results
  setTimeout(() => {
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 80);
}

/* ── Profile card ─── */
function renderProfile(p) {
  document.getElementById('avatar').src        = p.avatar_url || 'https://github.com/github.png';
  document.getElementById('profile-name').textContent  = p.name || p.login;
  document.getElementById('profile-login').textContent = `@${p.login}`;
  document.getElementById('profile-bio').textContent   = p.bio || 'No bio available.';
  document.getElementById('profile-link').href         = `https://github.com/${p.login}`;

  // Meta items
  const meta = document.getElementById('profile-meta');
  meta.innerHTML = '';
  const metaItems = [
    p.company  ? { icon: buildingIcon(), text: p.company } : null,
    p.location ? { icon: pinIcon(),      text: p.location } : null,
    p.blog     ? { icon: linkIcon(),     text: p.blog, href: p.blog.startsWith('http') ? p.blog : `https://${p.blog}` } : null,
    p.created_at ? { icon: calIcon(),   text: `Joined ${p.created_at.slice(0,4)}` } : null,
  ].filter(Boolean);
  metaItems.forEach(({ icon, text, href }) => {
    const el = document.createElement('div');
    el.className = 'meta-item';
    el.innerHTML = href
      ? `${icon}<a href="${href}" target="_blank" rel="noopener">${escHtml(text)}</a>`
      : `${icon}<span>${escHtml(text)}</span>`;
    meta.appendChild(el);
  });

  // Tags
  const tags = document.getElementById('profile-tags');
  tags.innerHTML = '';
  [
    p.public_repos ? `${p.public_repos} repos` : null,
    p.public_gists ? `${p.public_gists} gists` : null,
  ].filter(Boolean).forEach(t => {
    const s = document.createElement('span');
    s.className = 'profile-tag';
    s.textContent = t;
    tags.appendChild(s);
  });
}

/* ── KPI cards ─── */
function renderKPIs(profile, summary, insights) {
  setText('followers',      fmtNum(profile.followers));
  setText('following',      fmtNum(profile.following));
  setText('repos',          fmtNum(profile.public_repos));
  setText('insight-activity', fmtNum(insights.activity_score));
  setText('total-stars',    fmtNum(summary.total_stars));
}

/* ── Repo table ─── */
function renderRepoTable(repos) {
  const tbody = document.getElementById('repo-table-body');
  const badge = document.getElementById('repo-count-badge');
  tbody.innerHTML = '';
  badge.textContent = `${repos.length} repos`;

  repos.slice(0, 10).forEach(repo => {
    const tr = document.createElement('tr');
    const color = langColor(repo.language);
    tr.innerHTML = `
      <td>
        <div class="repo-name-cell">
          <a class="repo-name-link" href="https://github.com/${repo.full_name}" target="_blank" rel="noopener">${escHtml(repo.name)}</a>
        </div>
      </td>
      <td>
        ${repo.language
          ? `<span style="display:flex;align-items:center;gap:6px">
               <span class="lang-dot" style="background:${color}"></span>${escHtml(repo.language)}
             </span>`
          : '<span style="color:var(--text-3)">—</span>'
        }
      </td>
      <td><span class="star-count">★ ${fmtNum(repo.stars)}</span></td>
      <td><span class="fork-count">${fmtNum(repo.forks)}</span></td>
      <td style="color:var(--text-3)">${repo.updated_at.slice(0, 10)}</td>
    `;
    tbody.appendChild(tr);
  });
}

/* ── Language bars ─── */
function renderLanguageBars(langUsage) {
  const container = document.getElementById('language-bars');
  const diversity = document.getElementById('lang-diversity');
  container.innerHTML = '';
  diversity.textContent = `${langUsage.length} languages`;

  const total = langUsage.reduce((s, i) => s + i.width, 0);
  langUsage.forEach(item => {
    const pct = total > 0 ? ((item.width / total) * 100).toFixed(1) : 0;
    const color = langColor(item.language);
    const row = document.createElement('div');
    row.className = 'lang-bar-row';
    row.innerHTML = `
      <div class="lang-bar-header">
        <span class="lang-name">
          <span class="lang-dot" style="background:${color}"></span>
          ${escHtml(item.language)}
        </span>
        <span class="lang-pct">${pct}%</span>
      </div>
      <div class="lang-track">
        <div class="lang-fill" style="background:${color}; width:0%" data-width="${pct}"></div>
      </div>
    `;
    container.appendChild(row);
  });

  // Animate bars after paint
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      container.querySelectorAll('.lang-fill').forEach(el => {
        el.style.width = el.dataset.width + '%';
      });
    });
  });
}

/* ── Profile insights ─── */
function renderInsights(summary, insights) {
  setText('insight-repos',     fmtNum(insights.repo_count));
  setText('insight-languages', fmtNum(insights.language_diversity));
  setText('insight-avg-stars', fmtNum(summary.avg_stars));
  setText('insight-forks',     fmtNum(summary.total_forks));
  setText('insight-top-repo',  summary.most_starred_repo?.name || '—');
  setText('insight-top-fork',  insights.top_forked_repos?.[0]?.name || '—');
}

/* ── Recent repos ─── */
function renderRecentRepos(repos) {
  const grid = document.getElementById('recent-repos-grid');
  grid.innerHTML = '';

  repos.slice(0, 8).forEach(repo => {
    const card = document.createElement('div');
    card.className = 'recent-repo-card';
    card.onclick = () => window.open(`https://github.com/${repo.full_name}`, '_blank');
    const color = langColor(repo.language);
    card.innerHTML = `
      <div class="recent-repo-name">${escHtml(repo.name)}</div>
      <div class="recent-repo-meta">
        ${repo.language ? `<span class="recent-meta-item"><span class="lang-dot" style="background:${color}"></span>${escHtml(repo.language)}</span>` : ''}
        <span class="recent-meta-item">★ ${fmtNum(repo.stars)}</span>
        <span class="recent-meta-item">${repo.updated_at.slice(0, 10)}</span>
      </div>
    `;
    grid.appendChild(card);
  });
}

/* ─── Helpers ───────────────────────────────────────────── */
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function fmtNum(n) {
  if (n == null) return '—';
  const num = Number(n);
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M';
  if (num >= 1_000)     return (num / 1_000).toFixed(1) + 'k';
  return num.toLocaleString();
}

function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ─── SVG icon helpers ──────────────────────────────────── */
function buildingIcon() {
  return `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>`;
}
function pinIcon() {
  return `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>`;
}
function linkIcon() {
  return `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>`;
}
function calIcon() {
  return `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`;
}
