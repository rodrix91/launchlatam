"""Safety checks for the read-only LaunchLatam quality workflow."""

from pathlib import Path
import re
import unittest

WORKFLOW = (
    Path(__file__).resolve().parents[1] / ".github" / "workflows" / "quality.yml"
).read_text(encoding="utf-8")


class QualityWorkflowContract(unittest.TestCase):
    def test_official_actions_are_pinned_to_commit_hashes(self) -> None:
        refs = re.findall(r"(?m)^\s*(?:-\s*)?uses:\s*(actions/[\w-]+)@([^\s#]+)", WORKFLOW)
        self.assertEqual({name for name, _ in refs}, {
            "actions/checkout",
            "actions/setup-python",
            "actions/setup-node",
        })
        self.assertEqual(len(refs), 3)
        for name, ref in refs:
            with self.subTest(action=name):
                self.assertRegex(ref, r"^[0-9a-f]{40}$")

    def test_unprivileged_events_and_no_repository_write(self) -> None:
        self.assertIn("  pull_request:", WORKFLOW)
        self.assertIn("  push:", WORKFLOW)
        self.assertNotIn("pull_request_target", WORKFLOW)
        self.assertRegex(WORKFLOW, r"(?m)^permissions:\s*\n  contents: read\s*$")
        self.assertNotIn("contents: write", WORKFLOW)
        self.assertNotIn("secrets.", WORKFLOW)
        self.assertIn("persist-credentials: false", WORKFLOW)

    def test_checks_do_not_invoke_production_operations(self) -> None:
        self.assertIn("python tools/check_site.py", WORKFLOW)
        self.assertIn("python -m unittest discover -s tests -p 'test_*.py' -v", WORKFLOW)
        self.assertIn("npm test", WORKFLOW)
        for command in ("wrangler deploy", "npm publish", "deploy.sh", "git push"):
            self.assertNotIn(command, WORKFLOW)


if __name__ == "__main__":
    unittest.main()
