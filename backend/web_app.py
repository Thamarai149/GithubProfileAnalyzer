from typing import Any, Dict, cast

from flask import Flask, jsonify, render_template, request
import requests

from .analyzer import ProfileAnalyzer
from .api import GitHubAPI, GitHubAPIError


class GitHubAnalysisService:
    def __init__(self) -> None:
        self.api = GitHubAPI()

    def analyze_user(self, username: str) -> Dict[str, Any]:
        profile = self.api.get_user_profile(username)
        profile.repositories = self.api.get_user_repositories(username)
        analyzer = ProfileAnalyzer(profile)
        summary = cast(Dict[str, Any], analyzer.summarize_repositories())
        insights = cast(Dict[str, Any], analyzer.build_insights())

        return {
            "profile": profile.to_dict(),
            "summary": {
                "total_stars": summary["total_stars"],
                "total_forks": summary["total_forks"],
                "most_starred_repo": summary["most_starred_repo"].__dict__ if summary["most_starred_repo"] else None,
                "most_used_language": summary["most_used_language"],
                "avg_stars": summary["avg_stars"],
                "top_repos": [repo.__dict__ for repo in summary["top_repos"]],
                "language_counter": dict(summary["language_counter"]),
            },
            "language_usage": [
                {"language": language, "width": width}
                for language, width in analyzer.build_language_bars()
            ],
            "recent_repositories": [repo.__dict__ for repo in analyzer.recent_repositories()],
            "insights": {
                "repo_count": insights["repo_count"],
                "language_diversity": insights["language_diversity"],
                "activity_score": insights["activity_score"],
                "top_forked_repos": [repo.__dict__ for repo in insights["top_forked_repos"]],
            },
        }


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../frontend", static_folder="../frontend", static_url_path="")
    service = GitHubAnalysisService()

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/health")
    def health() -> Any:
        return jsonify({"status": "ok"})

    @app.post("/api/analyze")
    def analyze() -> Any:
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        if not username:
            return jsonify({"error": "Username is required."}), 400

        try:
            result = service.analyze_user(username)
            return jsonify(result)
        except GitHubAPIError as exc:
            return jsonify({"error": str(exc)}), 404
        except requests.RequestException as exc:
            return jsonify({"error": f"Network error: {exc}"}), 502

    return app


app = create_app()
