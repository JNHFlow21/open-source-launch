from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_open_source.py"
SPEC = importlib.util.spec_from_file_location("audit_open_source", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)


class OpenSourceAuditTests(unittest.TestCase):
    def test_flags_privacy_portability_and_package_blockers_without_leaking_value(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            init_repo(root)
            secret = "ghp_" + "abcdefghijklmnopqrstuvwxyz123456"
            machine_path = "/Users/" + "alice/private/demo"
            (root / "README.md").write_text(
                f"# Demo\n\nRuns only from {machine_path}.\n",
                encoding="utf-8",
            )
            (root / ".env").write_text(f"GITHUB_TOKEN={secret}\n", encoding="utf-8")

            report = MODULE.audit(root)
            codes = {finding["code"] for finding in report["findings"]}
            serialized = json.dumps(report)

            self.assertEqual(report["status"], "blocked")
            self.assertIn("missing-license", codes)
            self.assertIn("tracked-env-file", codes)
            self.assertIn("secret-pattern", codes)
            self.assertIn("machine-specific-path", codes)
            self.assertNotIn(secret, serialized)

    def test_minimal_clean_fixture_has_no_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            init_repo(root)
            (root / "README.md").write_text(
                "# Demo\n\nDemo turns text into a deterministic local result for developers.\n\n"
                "## Quick start\n\nRun `python3 demo.py`; expected output is `ok`.\n",
                encoding="utf-8",
            )
            (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (root / ".gitignore").write_text(".env\n", encoding="utf-8")
            (root / "SECURITY.md").write_text("Report privately through GitHub.\n", encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text("Run tests before a PR.\n", encoding="utf-8")
            workflow = root / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "test.yml").write_text("name: test\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "fixture"],
                cwd=root,
                check=True,
            )

            report = MODULE.audit(root)

            self.assertEqual(report["status"], "static-audit-clean")
            self.assertEqual(report["summary"]["errors"], 0)
            self.assertEqual(report["summary"]["warnings"], 0)

    def test_external_symlink_is_a_portability_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            outside = Path(temporary) / "outside.txt"
            root.mkdir()
            init_repo(root)
            outside.write_text("private", encoding="utf-8")
            (root / "README.md").write_text("# Demo\n\n## Quick start\n", encoding="utf-8")
            (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (root / "linked.txt").symlink_to(outside)

            report = MODULE.audit(root)

            self.assertIn(
                "external-symlink",
                {finding["code"] for finding in report["findings"]},
            )
            self.assertIn(
                "absolute-symlink",
                {finding["code"] for finding in report["findings"]},
            )

    def test_env_example_is_allowed_and_secret_value_is_still_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            init_repo(root)
            (root / "README.md").write_text("# Demo\n\n## Quick start\n", encoding="utf-8")
            (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (root / ".env.example").write_text("API_TOKEN=replace-me\n", encoding="utf-8")

            report = MODULE.audit(root)
            codes = {finding["code"] for finding in report["findings"]}

            self.assertNotIn("tracked-env-file", codes)
            self.assertNotIn("secret-pattern", codes)


if __name__ == "__main__":
    unittest.main()
