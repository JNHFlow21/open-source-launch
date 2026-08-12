from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).parents[1]
INSTALLER = ROOT / "scripts" / "install_repository_pulse.py"
RENDERER = ROOT / "assets" / "repository-pulse" / "render_repository_metrics.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


INSTALL = load_module("install_repository_pulse", INSTALLER)
RENDER = load_module("render_repository_metrics", RENDERER)


def traffic_fixture() -> dict[str, object]:
    return {
        "unique_visitors_14d": 4,
        "views_14d": 8,
        "unique_cloners_14d": 2,
        "clones_14d": 3,
        "traffic_as_of": "2026-08-11T00:00:00Z",
        "clone_series_14d": [
            {"timestamp": "2026-08-10T00:00:00Z", "count": 1, "username": "private-user"},
            {"timestamp": "2026-08-11T00:00:00Z", "count": 2},
        ],
        "top_referrers": [{"referrer": "private.example"}],
        "token": "must-not-survive",
    }


class RepositoryPulseTests(unittest.TestCase):
    def test_installer_writes_only_sanitized_component_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)

            paths = INSTALL.install(root, "owner/demo", traffic_fixture())
            snapshot_path = root / ".github" / "repository-metrics-traffic.json"
            serialized = snapshot_path.read_text(encoding="utf-8")

            self.assertEqual(len(paths), 3)
            self.assertTrue((root / ".github" / "workflows" / "repository-metrics.yml").is_file())
            self.assertTrue((root / "scripts" / "render_repository_metrics.py").is_file())
            self.assertNotIn("private-user", serialized)
            self.assertNotIn("private.example", serialized)
            self.assertNotIn("must-not-survive", serialized)
            self.assertEqual(
                set(json.loads(serialized)),
                INSTALL.TRAFFIC_FIELDS,
            )

    def test_installer_refuses_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            INSTALL.install(root, "owner/demo", traffic_fixture())

            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                INSTALL.install(root, "owner/demo", traffic_fixture())

    def test_installer_refuses_destination_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            outside = Path(temporary) / "outside.yml"
            root.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            outside.write_text("do not overwrite\n", encoding="utf-8")
            workflow = root / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "repository-metrics.yml").symlink_to(outside)

            with self.assertRaisesRegex(ValueError, "symlink"):
                INSTALL.install(root, "owner/demo", traffic_fixture(), force=True)

            self.assertEqual(outside.read_text(encoding="utf-8"), "do not overwrite\n")

    def test_renderer_outputs_clone_curve_and_aggregate_cards(self) -> None:
        traffic = INSTALL.sanitize_traffic_snapshot(traffic_fixture())
        snapshot = {
            "repository": "owner/demo",
            "created_at": "2026-08-01T00:00:00Z",
            "generated_at": "2026-08-11T01:00:00Z",
            "stars": 5,
            "forks": 1,
            "commits": 7,
            "traffic_live": False,
            **traffic,
        }

        svg = RENDER.render_svg(snapshot)

        ET.fromstring(svg)
        self.assertIn("Total clones over time", svg)
        self.assertIn("Total clones", svg)
        self.assertIn("GitHub Traffic owner snapshot: 2026-08-11", svg)
        self.assertNotIn("GITHUB_TOKEN", svg)

    def test_workflow_uses_ephemeral_token_and_no_pull_request_trigger(self) -> None:
        workflow = (ROOT / "assets" / "repository-pulse" / "repository-metrics.yml").read_text(encoding="utf-8")

        self.assertIn("github.token", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("pull_request:", workflow)

    def test_readme_snippet_contains_only_heading_and_linked_chart(self) -> None:
        snippet = INSTALL.readme_snippet("owner/demo")

        self.assertEqual(
            snippet,
            "## Repository activity\n\n"
            "[![Repository Pulse for owner/demo](https://raw.githubusercontent.com/owner/demo/metrics/repository-metrics.svg)]"
            "(https://github.com/owner/demo)",
        )
        self.assertNotIn("GitHub Traffic values", snippet)
        self.assertNotIn("proof", snippet.lower())


if __name__ == "__main__":
    unittest.main()
