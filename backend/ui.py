from datetime import datetime
from typing import Optional, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import Repository, UserProfile


class RichInterface:
    def __init__(self) -> None:
        self.console = Console()

    def show_banner(self) -> None:
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]GitHub Profile Analyzer[/bold cyan]\n[white]Explore public GitHub profiles and repository activity[/white]",
                border_style="cyan",
            )
        )

    def show_menu(self) -> None:
        table = Table(title="Main Menu", box=None)
        table.add_column("Option", style="bold cyan")
        table.add_column("Action")
        table.add_row("1", "Analyze Profile")
        table.add_row("2", "Compare Two Users")
        table.add_row("3", "Export Report")
        table.add_row("4", "Search Another User")
        table.add_row("5", "View Recent Repositories")
        table.add_row("6", "Exit")
        self.console.print(table)

    def show_profile(self, profile: UserProfile) -> None:
        self.console.print(Panel.fit(f"[bold green]{profile.name or profile.login}[/bold green]", border_style="green"))
        table = Table(title="Profile Overview")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        table.add_row("Photo URL", profile.avatar_url or "N/A")
        table.add_row("Name", profile.name or "N/A")
        table.add_row("Username", profile.login)
        table.add_row("Bio", profile.bio or "N/A")
        table.add_row("Company", profile.company or "N/A")
        table.add_row("Location", profile.location or "N/A")
        table.add_row("Website", profile.blog or "N/A")
        table.add_row("Email", profile.email or "N/A")
        table.add_row("Followers", str(profile.followers))
        table.add_row("Following", str(profile.following))
        table.add_row("Public Repositories", str(profile.public_repos))
        table.add_row("Public Gists", str(profile.public_gists))
        table.add_row("Created", self._format_date(profile.created_at))
        table.add_row("Updated", self._format_date(profile.updated_at))
        self.console.print(table)

    def show_repository_summary(self, profile: UserProfile, summary: dict) -> None:
        table = Table(title="Repository Summary")
        table.add_column("Metric", style="bold")
        table.add_column("Value")
        table.add_row("Total Stars", str(summary["total_stars"]))
        table.add_row("Total Forks", str(summary["total_forks"]))
        table.add_row("Most Starred Repo", summary["most_starred_repo"].name if summary["most_starred_repo"] else "N/A")
        table.add_row("Most Used Language", str(summary["most_used_language"]))
        table.add_row("Average Stars / Repo", str(summary["avg_stars"]))
        self.console.print(table)

    def show_top_repositories(self, repositories: List[Repository]) -> None:
        table = Table(title="Top 10 Repositories by Stars")
        table.add_column("Repository", style="bold cyan")
        table.add_column("Stars")
        table.add_column("Forks")
        table.add_column("Language")
        table.add_column("Updated")
        for repo in repositories:
            table.add_row(repo.name, str(repo.stars), str(repo.forks), repo.language or "N/A", self._format_date(repo.updated_at))
        self.console.print(table)

    def show_recent_repositories(self, repositories: List[Repository]) -> None:
        table = Table(title="Recently Updated Repositories")
        table.add_column("Repository", style="bold cyan")
        table.add_column("Language")
        table.add_column("Updated")
        table.add_column("Stars")
        for repo in repositories:
            table.add_row(repo.name, repo.language or "N/A", self._format_date(repo.updated_at), str(repo.stars))
        self.console.print(table)

    def show_language_bars(self, bars: List[Tuple[str, int]]) -> None:
        self.console.print(Panel("[bold yellow]Language Usage[/bold yellow]", border_style="yellow"))
        for language, width in bars:
            bar = "#" * width
            self.console.print(f"[cyan]{language:<15}[/cyan] [{bar:<30}] {width}")

    def show_insights(self, insights: dict) -> None:
        self.console.print(Panel("[bold magenta]Repository Insights[/bold magenta]", border_style="magenta"))
        table = Table(show_header=False)
        table.add_column("Metric", style="bold")
        table.add_column("Value")
        table.add_row("Repositories Analyzed", str(insights["repo_count"]))
        table.add_row("Language Diversity", str(insights["language_diversity"]))
        table.add_row("Activity Score", str(insights["activity_score"]))
        table.add_row("Top Forked Repo", insights["top_forked_repos"][0].name if insights["top_forked_repos"] else "N/A")
        self.console.print(table)

    def show_comparison(self, first_profile: UserProfile, second_profile: UserProfile, first_summary: dict, second_summary: dict) -> None:
        table = Table(title="User Comparison")
        table.add_column("Metric", style="bold")
        table.add_column(first_profile.login)
        table.add_column(second_profile.login)
        table.add_row("Followers", str(first_profile.followers), str(second_profile.followers))
        table.add_row("Following", str(first_profile.following), str(second_profile.following))
        table.add_row("Public Repos", str(first_profile.public_repos), str(second_profile.public_repos))
        table.add_row("Public Gists", str(first_profile.public_gists), str(second_profile.public_gists))
        table.add_row("Total Stars", str(first_summary["total_stars"]), str(second_summary["total_stars"]))
        table.add_row("Most Used Language", str(first_summary["most_used_language"]), str(second_summary["most_used_language"]))
        self.console.print(table)

    def show_message(self, message: str, style: str = "white") -> None:
        self.console.print(Text(message, style=style))

    def prompt(self, message: str) -> str:
        return input(message)

    def _format_date(self, value: str) -> str:
        if not value:
            return "N/A"
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except ValueError:
            return value
