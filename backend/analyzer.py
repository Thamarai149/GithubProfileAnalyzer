from collections import Counter
from typing import Any, Dict, List, Tuple, cast

from .models import Repository, UserProfile


class ProfileAnalyzer:
    def __init__(self, profile: UserProfile) -> None:
        self.profile = profile

    def build_insights(self) -> Dict[str, Any]:
        repositories = self.profile.repositories
        language_counter: Counter[str] = Counter(repo.language for repo in repositories if repo.language)
        top_forked_repos: List[Repository] = sorted(repositories, key=lambda repo: repo.forks, reverse=True)[:3]
        activity_score = sum(repo.stars + repo.forks for repo in repositories)
        return {
            "repo_count": len(repositories),
            "language_diversity": len(language_counter),
            "top_forked_repos": top_forked_repos,
            "activity_score": activity_score,
        }

    def summarize_repositories(self) -> Dict[str, Any]:
        repositories = self.profile.repositories
        total_stars = sum(repo.stars for repo in repositories)
        total_forks = sum(repo.forks for repo in repositories)
        most_starred_repo = max(repositories, key=lambda repo: repo.stars, default=None)
        languages = [repo.language for repo in repositories if repo.language]
        language_counter: Counter[str] = Counter(languages)
        most_used_language = language_counter.most_common(1)[0][0] if language_counter else "N/A"
        avg_stars = round(total_stars / len(repositories), 2) if repositories else 0.0

        top_repos = sorted(repositories, key=lambda repo: repo.stars, reverse=True)[:10]

        return {
            "total_stars": total_stars,
            "total_forks": total_forks,
            "most_starred_repo": most_starred_repo,
            "most_used_language": most_used_language,
            "avg_stars": avg_stars,
            "top_repos": top_repos,
            "language_counter": language_counter,
        }

    def build_language_bars(self, max_width: int = 30) -> List[Tuple[str, int]]:
        summary = cast(Dict[str, Any], self.summarize_repositories())
        language_counter = cast(Counter[str], summary["language_counter"])
        total = sum(language_counter.values())
        bars: List[Tuple[str, int]] = []
        for language, count in language_counter.most_common(8):
            width = int((count / total) * max_width) if total else 0
            bars.append((language, width))
        return bars

    def recent_repositories(self, limit: int = 10) -> List[Repository]:
        return sorted(
            self.profile.repositories,
            key=lambda repo: repo.updated_at,
            reverse=True,
        )[:limit]
