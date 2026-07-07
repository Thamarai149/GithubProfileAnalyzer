from .analyzer import ProfileAnalyzer
from .api import GitHubAPI, GitHubAPIError
from .exporter import ReportExporter
from .models import UserProfile
from .ui import RichInterface


class GitHubProfileAnalyzerApp:
    def __init__(self) -> None:
        self.api = GitHubAPI()
        self.ui = RichInterface()
        self.exporter = ReportExporter()

    def run(self) -> None:
        self.ui.show_banner()
        while True:
            self.ui.show_menu()
            choice = self.ui.prompt("\nChoose an option: ").strip()

            if choice == "1":
                self.analyze_profile()
            elif choice == "2":
                self.compare_users()
            elif choice == "3":
                self.export_current_report()
            elif choice == "4":
                self.search_another_user()
            elif choice == "5":
                self.show_recent_repositories()
            elif choice == "6":
                self.ui.show_message("Goodbye!", style="bold green")
                break
            else:
                self.ui.show_message("Please select a valid option.", style="bold red")

    def analyze_profile(self) -> None:
        username = self.ui.prompt("Enter a GitHub username: ").strip()
        if not username:
            self.ui.show_message("Username cannot be empty.", style="bold red")
            return
        self._display_user_report(username)

    def compare_users(self) -> None:
        first = self.ui.prompt("Enter first GitHub username: ").strip()
        second = self.ui.prompt("Enter second GitHub username: ").strip()
        if not first or not second:
            self.ui.show_message("Both usernames are required.", style="bold red")
            return
        try:
            first_profile = self._load_profile(first)
            second_profile = self._load_profile(second)
            first_summary = self._summarize(first_profile)
            second_summary = self._summarize(second_profile)
        except GitHubAPIError as exc:
            self.ui.show_message(str(exc), style="bold red")
            return

        self.ui.show_comparison(first_profile, second_profile, first_summary, second_summary)

    def export_current_report(self) -> None:
        username = self.ui.prompt("Enter a GitHub username to export: ").strip()
        if not username:
            self.ui.show_message("Username cannot be empty.", style="bold red")
            return
        custom_name = self.ui.prompt("Optional base filename (press Enter to use default): ").strip()
        try:
            profile = self._load_profile(username)
            summary = self._summarize(profile)
            txt_path = self.exporter.export_txt(profile, summary, f"{custom_name}_report.txt" if custom_name else None)
            json_path = self.exporter.export_json(profile, summary, f"{custom_name}_report.json" if custom_name else None)
            self.ui.show_message(f"Exported TXT report to {txt_path}", style="green")
            self.ui.show_message(f"Exported JSON report to {json_path}", style="green")
        except GitHubAPIError as exc:
            self.ui.show_message(str(exc), style="bold red")

    def search_another_user(self) -> None:
        self.analyze_profile()

    def show_recent_repositories(self) -> None:
        username = self.ui.prompt("Enter a GitHub username: ").strip()
        if not username:
            self.ui.show_message("Username cannot be empty.", style="bold red")
            return
        try:
            profile = self._load_profile(username)
            analyzer = ProfileAnalyzer(profile)
            self.ui.show_recent_repositories(analyzer.recent_repositories())
        except GitHubAPIError as exc:
            self.ui.show_message(str(exc), style="bold red")

    def _display_user_report(self, username: str) -> None:
        try:
            profile = self._load_profile(username)
            summary = self._summarize(profile)
        except GitHubAPIError as exc:
            self.ui.show_message(str(exc), style="bold red")
            return
        except Exception as exc:  # pragma: no cover - defensive fallback
            self.ui.show_message(f"Network error: {exc}", style="bold red")
            return

        self.ui.show_profile(profile)
        self.ui.show_repository_summary(profile, summary)
        self.ui.show_top_repositories(summary["top_repos"])
        analyzer = ProfileAnalyzer(profile)
        self.ui.show_language_bars(analyzer.build_language_bars())

    def _load_profile(self, username: str) -> UserProfile:
        profile = self.api.get_user_profile(username)
        profile.repositories = self.api.get_user_repositories(username)
        return profile

    def _summarize(self, profile: UserProfile):
        analyzer = ProfileAnalyzer(profile)
        return analyzer.summarize_repositories()
