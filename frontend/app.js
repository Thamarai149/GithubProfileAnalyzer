const form = document.getElementById('analyze-form');
const results = document.getElementById('results');
const status = document.getElementById('status');
const repoTableBody = document.getElementById('repo-table-body');
const languageBars = document.getElementById('language-bars');

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const username = document.getElementById('username').value.trim();
    status.textContent = 'Analyzing profile...';

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Unable to analyze profile');
        }

        renderResults(data);
        status.textContent = `Loaded profile for ${data.profile.login}`;
    } catch (error) {
        status.textContent = error.message;
    }
});

function renderResults(data) {
    const profile = data.profile;
    document.getElementById('profile-name').textContent = profile.name || profile.login;
    document.getElementById('profile-login').textContent = `@${profile.login}`;
    document.getElementById('profile-bio').textContent = profile.bio || 'No bio available.';
    document.getElementById('followers').textContent = profile.followers.toLocaleString();
    document.getElementById('following').textContent = profile.following.toLocaleString();
    document.getElementById('repos').textContent = profile.public_repos.toLocaleString();
    document.getElementById('language').textContent = data.summary.most_used_language || 'N/A';
    document.getElementById('avatar').src = profile.avatar_url || 'https://github.com/github.png';

    const tags = document.getElementById('profile-tags');
    tags.innerHTML = '';
    const tagList = [
        profile.company ? `Works at ${profile.company}` : null,
        profile.location ? `From ${profile.location}` : null,
        profile.blog ? 'Has a website' : null,
        profile.public_repos ? `${profile.public_repos} repos` : null,
    ].filter(Boolean);
    tagList.forEach((tag) => {
        const chip = document.createElement('span');
        chip.className = 'tag';
        chip.textContent = tag;
        tags.appendChild(chip);
    });
    document.getElementById('insight-repos').textContent = data.insights.repo_count;
    document.getElementById('insight-languages').textContent = data.insights.language_diversity;
    document.getElementById('insight-activity').textContent = data.insights.activity_score;
    document.getElementById('insight-top-fork').textContent = data.insights.top_forked_repos?.[0]?.name || 'N/A';

    repoTableBody.innerHTML = '';
    data.summary.top_repos.slice(0, 8).forEach((repo) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${repo.name}</td>
            <td>${repo.stars}</td>
            <td>${repo.language || 'N/A'}</td>
            <td>${repo.updated_at.slice(0, 10)}</td>
        `;
        repoTableBody.appendChild(row);
    });

    languageBars.innerHTML = '';
    const total = data.language_usage.reduce((sum, item) => sum + item.width, 0);
    data.language_usage.forEach((item) => {
        const percentage = total > 0 ? ((item.width / total) * 100).toFixed(1) : 0;
        const row = document.createElement('div');
        row.className = 'bar-row';
        row.innerHTML = `
            <div class="bar-label-row">
                <strong>${item.language}</strong>
                <span>${percentage}%</span>
            </div>
            <div class="bar-track">
                <span class="bar" style="width:${Math.max(8, item.width * 2)}px"></span>
            </div>
        `;
        languageBars.appendChild(row);
    });

    results.classList.remove('hidden');
}
