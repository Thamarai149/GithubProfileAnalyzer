from typing import Any, Dict, List, Optional, cast

import requests

from .models import Repository, UserProfile


class GitHubAPIError(Exception):
    """Raised when the GitHub API request fails."""


class GitHubAPI:
    BASE_URL = "https://api.github.com"
    USER_AGENT = "GitHub-Profile-Analyzer/1.0"

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": self.USER_AGENT,
        }
        response = requests.get(
            f"{self.BASE_URL}{endpoint}",
            params=params or {},
            headers=headers,
            timeout=self.timeout,
        )
        if response.status_code == 404:
            raise GitHubAPIError("User not found.")
        if response.status_code >= 400:
            raise GitHubAPIError(f"API request failed with status {response.status_code}.")
        return response.json()

    def get_user_profile(self, username: str) -> UserProfile:
        data = cast(Dict[str, Any], self._get(f"/users/{username}"))
        return UserProfile(
            login=str(data.get("login", username)),
            name=self._as_optional_str(data.get("name")),
            bio=self._as_optional_str(data.get("bio")),
            company=self._as_optional_str(data.get("company")),
            location=self._as_optional_str(data.get("location")),
            blog=self._as_optional_str(data.get("blog")),
            email=self._as_optional_str(data.get("email")),
            avatar_url=self._as_optional_str(data.get("avatar_url")),
            followers=int(data.get("followers", 0) or 0),
            following=int(data.get("following", 0) or 0),
            public_repos=int(data.get("public_repos", 0) or 0),
            public_gists=int(data.get("public_gists", 0) or 0),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def get_user_repositories(self, username: str) -> List[Repository]:
        repos_data = cast(List[Dict[str, Any]], self._get(f"/users/{username}/repos", params={"per_page": 100, "sort": "updated"}))
        repositories = []
        for item in repos_data:
            repositories.append(
                Repository(
                    name=str(item.get("name", "Unnamed")),
                    full_name=str(item.get("full_name", "")),
                    stars=int(item.get("stargazers_count", 0) or 0),
                    forks=int(item.get("forks_count", 0) or 0),
                    language=self._as_optional_str(item.get("language")),
                    updated_at=str(item.get("updated_at", "")),
                    html_url=str(item.get("html_url", "")),
                )
            )
        return repositories

    @staticmethod
    def _as_optional_str(value: Any) -> Optional[str]:
        if value is None:
            return None
        return str(value)
