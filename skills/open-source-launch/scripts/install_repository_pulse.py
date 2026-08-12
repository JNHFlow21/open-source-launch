#!/usr/bin/env python3
"""Install the token-safe Repository Pulse component into a Git repository."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Iterable


REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
TRAFFIC_FIELDS = {
    "unique_visitors_14d",
    "views_14d",
    "unique_cloners_14d",
    "clones_14d",
    "traffic_as_of",
    "clone_series_14d",
}


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def validate_repository_root(value: str | Path) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"target directory does not exist: {root}")
    result = _run(["git", "rev-parse", "--show-toplevel"], cwd=root)
    if result.returncode != 0:
        raise ValueError("target must be a Git repository root")
    git_root = Path(os.fsdecode(result.stdout).strip()).resolve()
    if git_root != root:
        raise ValueError(f"target must be the Git root: {git_root}")
    return root


def _nonnegative_int(value: object, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a non-negative integer")
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} must be a non-negative integer") from error
    if number < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return number


def _timestamp(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO-8601 timestamp")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from error
    return value


def sanitize_traffic_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(TRAFFIC_FIELDS - payload.keys())
    if missing:
        raise ValueError(f"traffic snapshot is missing: {', '.join(missing)}")
    raw_series = payload["clone_series_14d"]
    if not isinstance(raw_series, list):
        raise ValueError("clone_series_14d must be a list")
    series: list[dict[str, object]] = []
    for index, item in enumerate(raw_series):
        if not isinstance(item, dict):
            raise ValueError(f"clone_series_14d[{index}] must be an object")
        series.append(
            {
                "timestamp": _timestamp(item.get("timestamp"), f"clone_series_14d[{index}].timestamp"),
                "count": _nonnegative_int(item.get("count"), f"clone_series_14d[{index}].count"),
            }
        )
    series.sort(key=lambda item: str(item["timestamp"]))
    if len(series) > 14:
        raise ValueError("clone_series_14d must contain at most 14 daily points")
    return {
        "unique_visitors_14d": _nonnegative_int(payload["unique_visitors_14d"], "unique_visitors_14d"),
        "views_14d": _nonnegative_int(payload["views_14d"], "views_14d"),
        "unique_cloners_14d": _nonnegative_int(payload["unique_cloners_14d"], "unique_cloners_14d"),
        "clones_14d": _nonnegative_int(payload["clones_14d"], "clones_14d"),
        "traffic_as_of": _timestamp(payload["traffic_as_of"], "traffic_as_of"),
        "clone_series_14d": series,
    }


def _gh_api(repository: str, endpoint: str, root: Path) -> dict[str, Any]:
    if not shutil.which("gh"):
        raise ValueError("gh is required for --collect-traffic")
    result = _run(["gh", "api", f"repos/{repository}/traffic/{endpoint}"], cwd=root)
    if result.returncode != 0:
        raise ValueError(
            f"GitHub Traffic {endpoint} request failed; authenticate gh as a repository owner. Raw output was suppressed."
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(f"GitHub Traffic {endpoint} returned invalid JSON") from error
    if not isinstance(payload, dict):
        raise ValueError(f"GitHub Traffic {endpoint} returned an unexpected shape")
    return payload


def collect_traffic_snapshot(repository: str, root: Path) -> dict[str, Any]:
    views = _gh_api(repository, "views", root)
    clones = _gh_api(repository, "clones", root)
    clone_items = clones.get("clones", [])
    if not isinstance(clone_items, list):
        raise ValueError("GitHub Traffic clones returned an unexpected daily-series shape")
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    raw = {
        "unique_visitors_14d": views.get("uniques"),
        "views_14d": views.get("count"),
        "unique_cloners_14d": clones.get("uniques"),
        "clones_14d": clones.get("count"),
        "traffic_as_of": generated_at,
        "clone_series_14d": [
            {"timestamp": item.get("timestamp"), "count": item.get("count")}
            for item in clone_items
            if isinstance(item, dict)
        ],
    }
    return sanitize_traffic_snapshot(raw)


def load_traffic_snapshot(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"could not read traffic snapshot: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"traffic snapshot is not valid JSON: {path}") from error
    if not isinstance(payload, dict):
        raise ValueError("traffic snapshot must be a JSON object")
    return sanitize_traffic_snapshot(payload)


def readme_snippet(repository: str) -> str:
    owner, name = repository.split("/", 1)
    raw_url = f"https://raw.githubusercontent.com/{owner}/{name}/metrics/repository-metrics.svg"
    repository_url = f"https://github.com/{owner}/{name}"
    return (
        "## Repository activity\n\n"
        f"[![Repository Pulse for {repository}]({raw_url})]({repository_url})"
    )


def install(
    target: str | Path,
    repository: str,
    traffic: dict[str, Any],
    *,
    force: bool = False,
) -> list[Path]:
    if not REPOSITORY_RE.fullmatch(repository):
        raise ValueError("repository must use owner/name format")
    root = validate_repository_root(target)
    sanitized = sanitize_traffic_snapshot(traffic)
    asset_root = Path(__file__).parents[1] / "assets" / "repository-pulse"
    sources = {
        root / ".github" / "workflows" / "repository-metrics.yml": asset_root / "repository-metrics.yml",
        root / "scripts" / "render_repository_metrics.py": asset_root / "render_repository_metrics.py",
    }
    traffic_path = root / ".github" / "repository-metrics-traffic.json"
    destinations = [*sources.keys(), traffic_path]
    for destination in destinations:
        if destination.is_symlink():
            raise ValueError(
                f"refusing to write through a symlink: {destination.relative_to(root)}"
            )
        try:
            destination.resolve(strict=False).relative_to(root)
        except (OSError, RuntimeError, ValueError) as error:
            raise ValueError(
                f"component path resolves outside the repository: {destination}"
            ) from error
    existing = [path for path in destinations if path.exists()]
    if existing and not force:
        paths = ", ".join(path.relative_to(root).as_posix() for path in existing)
        raise ValueError(f"refusing to overwrite existing files without --force: {paths}")

    for destination, source in sources.items():
        if not source.is_file():
            raise ValueError(f"Skill asset is missing: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        if destination.name.endswith(".py"):
            destination.chmod(destination.stat().st_mode | 0o111)
    traffic_path.parent.mkdir(parents=True, exist_ok=True)
    traffic_path.write_text(
        json.dumps(sanitized, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destinations


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Target Git repository root")
    parser.add_argument("--repository", required=True, help="GitHub owner/name")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--collect-traffic", action="store_true", help="Collect the owner-only rolling 14-day snapshot with gh")
    source.add_argument("--traffic-json", type=Path, help="Use an existing aggregate traffic snapshot")
    parser.add_argument("--force", action="store_true", help="Overwrite only the three component files")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not REPOSITORY_RE.fullmatch(args.repository):
        parser.error("--repository must use owner/name format")
    try:
        root = validate_repository_root(args.target)
        traffic = (
            collect_traffic_snapshot(args.repository, root)
            if args.collect_traffic
            else load_traffic_snapshot(args.traffic_json)
        )
        paths = install(root, args.repository, traffic, force=args.force)
    except ValueError as error:
        parser.error(str(error))

    print("Installed Repository Pulse files:")
    for path in paths:
        print(f"- {path.relative_to(root).as_posix()}")
    print("\nAdd this section near the end of README.md:\n")
    print(readme_snippet(args.repository))
    print("\nNo README, commit, branch, remote, or repository visibility was changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
