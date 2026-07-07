import unittest

from backend.analyzer import ProfileAnalyzer
from backend.models import Repository, UserProfile


class ProfileAnalyzerTests(unittest.TestCase):
    def test_build_insights_reports_repository_metrics(self) -> None:
        profile = UserProfile(
            login="octocat",
            name="The Octocat",
            bio=None,
            company=None,
            location=None,
            blog=None,
            email=None,
            avatar_url=None,
            followers=120,
            following=45,
            public_repos=3,
            public_gists=2,
            created_at="",
            updated_at="",
            repositories=[
                Repository("alpha", "octocat/alpha", 50, 20, "Python", "2024-01-01T00:00:00Z", "https://example.com/alpha"),
                Repository("beta", "octocat/beta", 35, 15, "JavaScript", "2024-02-01T00:00:00Z", "https://example.com/beta"),
                Repository("gamma", "octocat/gamma", 10, 40, "Python", "2024-03-01T00:00:00Z", "https://example.com/gamma"),
            ],
        )

        analyzer = ProfileAnalyzer(profile)
        insights = analyzer.build_insights()

        self.assertEqual(insights["repo_count"], 3)
        self.assertEqual(insights["language_diversity"], 2)
        self.assertEqual(insights["top_forked_repos"][0].name, "gamma")
        self.assertGreaterEqual(insights["activity_score"], 0)


if __name__ == "__main__":
    unittest.main()
