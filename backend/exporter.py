import json
from pathlib import Path
from typing import Dict, Optional

from .models import UserProfile


class ReportExporter:
    def __init__(self, output_dir: Optional[str] = None) -> None:
        self.output_dir = Path(output_dir or "exports")
        self.output_dir.mkdir(exist_ok=True)

    def export_txt(self, profile: UserProfile, summary: Dict[str, object], filename: Optional[str] = None) -> str:
        file_path = self.output_dir / (filename or f"{profile.login}_report.txt")
        lines = [
            f"GitHub Profile Report for {profile.login}",
            "=" * 40,
            f"Name: {profile.name or 'N/A'}",
            f"Username: {profile.login}",
            f"Bio: {profile.bio or 'N/A'}",
            f"Company: {profile.company or 'N/A'}",
            f"Location: {profile.location or 'N/A'}",
            f"Website: {profile.blog or 'N/A'}",
            f"Followers: {profile.followers}",
            f"Following: {profile.following}",
            f"Public Repositories: {profile.public_repos}",
            f"Public Gists: {profile.public_gists}",
            f"Total Stars: {summary['total_stars']}",
            f"Total Forks: {summary['total_forks']}",
            f"Most Starred Repo: {summary['most_starred_repo'].name if summary['most_starred_repo'] else 'N/A'}",
        ]
        file_path.write_text("\n".join(lines), encoding="utf-8")
        return str(file_path)

    def export_json(self, profile: UserProfile, summary: Dict[str, object], filename: Optional[str] = None) -> str:
        file_path = self.output_dir / (filename or f"{profile.login}_report.json")
        data = profile.to_dict()
        
        # Make the summary dictionary fully JSON-serializable
        serializable_summary = {
            "total_stars": summary["total_stars"],
            "total_forks": summary["total_forks"],
            "most_starred_repo": summary["most_starred_repo"].__dict__ if summary["most_starred_repo"] else None,
            "most_used_language": summary["most_used_language"],
            "avg_stars": summary["avg_stars"],
            "top_repos": [repo.__dict__ for repo in summary["top_repos"]] if isinstance(summary["top_repos"], list) else [],
            "language_counter": dict(summary["language_counter"]) if summary["language_counter"] else {}
        }
        
        data["summary"] = serializable_summary
        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return str(file_path)
