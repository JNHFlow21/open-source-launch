#!/usr/bin/env python3
"""Run a deterministic, privacy-safe static audit before open-source launch.

The audit deliberately reports locations and finding classes, never matched
secret values. A clean result means only that this static gate is clean; it is
not proof of clean Git history, portable packaging, or stranger-first success.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Iterable


MAX_TEXT_BYTES = 2 * 1024 * 1024
README_NAMES = ("README.md", "README.rst", "README.txt", "README")
LICENSE_NAMES = (
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "LICENCE",
    "LICENCE.md",
    "LICENCE.txt",
    "COPYING",
)
ENV_EXAMPLE_SUFFIXES = (".example", ".sample", ".template", ".dist")
IGNORED_FALLBACK_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "coverage",
}

QUICKSTART_RE = re.compile(
    r"(?:quick\s*start|get(?:ting)? started|installation|install|usage|"
    r"快速开始|快速上手|开始使用|安装|使用)",
    re.IGNORECASE,
)
MACHINE_PATH_RE = re.compile(
    r"(?:/Users/[A-Za-z0-9._-]+(?:/|\b)|/home/[A-Za-z0-9._-]+(?:/|\b)|"
    r"[A-Za-z]:\\Users\\[A-Za-z0-9._-]+(?:\\|\b)|file:///(?:Users|home)/)",
    re.IGNORECASE,
)
PRIVATE_HOST_RE = re.compile(
    r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
    r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}|"
    r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?:internal|local|lan))\b",
    re.IGNORECASE,
)
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("openai-key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{12,}\b")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    (
        "literal-bearer-token",
        re.compile(r"(?i)\bAuthorization\s*[:=]\s*[\"']?Bearer\s+[A-Za-z0-9._~+/-]{20,}"),
    ),
)


@dataclass(frozen=True)
class Finding:
    gate: str
    severity: str
    code: str
    message: str
    path: str | None = None
    line: int | None = None


def _run(
    command: list[str], *, cwd: Path, check: bool = False
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _git_root(root: Path) -> Path | None:
    try:
        result = _run(["git", "rev-parse", "--show-toplevel"], cwd=root, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return Path(os.fsdecode(result.stdout).strip()).resolve()


def _tracked_paths(root: Path) -> tuple[list[Path], bool]:
    git_root = _git_root(root)
    if git_root == root:
        try:
            result = _run(
                ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                cwd=root,
                check=True,
            )
            paths = [
                root / os.fsdecode(raw)
                for raw in result.stdout.split(b"\0")
                if raw
            ]
            return sorted(paths, key=lambda item: item.as_posix()), True
        except (OSError, subprocess.CalledProcessError):
            pass

    paths: list[Path] = []
    for candidate in root.rglob("*"):
        try:
            relative_parts = candidate.relative_to(root).parts
        except ValueError:
            continue
        if any(part in IGNORED_FALLBACK_DIRS for part in relative_parts):
            continue
        if candidate.is_file() or candidate.is_symlink():
            paths.append(candidate)
    return sorted(paths, key=lambda item: item.as_posix()), False


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _add(
    findings: list[Finding],
    gate: str,
    severity: str,
    code: str,
    message: str,
    path: str | None = None,
    line: int | None = None,
) -> None:
    findings.append(Finding(gate, severity, code, message, path, line))


def _is_env_example(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in ENV_EXAMPLE_SUFFIXES)


def _read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None, "large"
        data = path.read_bytes()
    except OSError:
        return None, "unreadable"
    if b"\0" in data[:8192]:
        return None, "binary"
    return data.decode("utf-8", errors="replace"), None


def _scan_file(root: Path, path: Path, findings: list[Finding]) -> None:
    relative = _relative(root, path)
    lower_name = path.name.lower()

    if path.is_symlink():
        try:
            raw_target = os.readlink(path)
        except OSError:
            raw_target = ""
        if os.path.isabs(raw_target):
            _add(
                findings,
                "portability",
                "error",
                "absolute-symlink",
                "Symlink uses an absolute target and will not survive a clone to another location.",
                relative,
            )
        try:
            target = path.resolve(strict=False)
            target.relative_to(root)
        except (OSError, RuntimeError, ValueError):
            _add(
                findings,
                "portability",
                "error",
                "external-symlink",
                "Symlink resolves outside the repository; package the dependency or use a repository-relative target.",
                relative,
            )
        return

    if lower_name == ".env" or (lower_name.startswith(".env.") and not _is_env_example(path)):
        _add(
            findings,
            "privacy",
            "error",
            "tracked-env-file",
            "A non-example environment file is public-surface material; replace it with a synthetic template and keep values in the secret manager.",
            relative,
        )

    if lower_name.endswith((".pem", ".p12", ".pfx", ".mobileprovision")) or (
        lower_name.endswith(".key") and "public" not in lower_name
    ):
        _add(
            findings,
            "privacy",
            "error",
            "credential-artifact",
            "A certificate, signing profile, or private-key-shaped artifact is included in the public surface.",
            relative,
        )

    if lower_name.endswith((".sqlite", ".sqlite3", ".db", ".log")):
        _add(
            findings,
            "privacy",
            "warning",
            "runtime-data-artifact",
            "Database/log-shaped runtime data needs explicit synthetic-fixture and privacy review.",
            relative,
        )

    text, skip_reason = _read_text(path)
    if text is None:
        if skip_reason in {"large", "unreadable"}:
            _add(
                findings,
                "privacy",
                "warning",
                f"{skip_reason}-file-not-scanned",
                "Static text scanning did not inspect this file; review it separately before publication.",
                relative,
            )
        return

    for number, line in enumerate(text.splitlines(), 1):
        for secret_kind, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                _add(
                    findings,
                    "privacy",
                    "error",
                    "secret-pattern",
                    f"Detected a {secret_kind} pattern; value intentionally redacted from the report.",
                    relative,
                    number,
                )
                break
        if MACHINE_PATH_RE.search(line):
            _add(
                findings,
                "portability",
                "error",
                "machine-specific-path",
                "Found a maintainer-machine path; replace it with a portable placeholder, config directory, or runtime discovery.",
                relative,
                number,
            )
        if PRIVATE_HOST_RE.search(line):
            _add(
                findings,
                "privacy",
                "warning",
                "private-host-reference",
                "Found a private-network/internal host reference; verify it is a synthetic example and not infrastructure disclosure.",
                relative,
                number,
            )


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _readme_checks(root: Path, findings: list[Finding]) -> None:
    readme = next((root / name for name in README_NAMES if (root / name).is_file()), None)
    if readme is None:
        _add(findings, "documentation", "error", "missing-readme", "Add a root README that states the user outcome and verified first-success route.")
        return

    text = readme.read_text(encoding="utf-8", errors="replace")
    relative = _relative(root, readme)
    if not re.search(r"(?m)^#\s+\S", text) and readme.suffix.lower() == ".md":
        _add(findings, "documentation", "warning", "missing-readme-title", "Add one H1 product title.", relative)
    if not QUICKSTART_RE.search(text):
        _add(findings, "documentation", "warning", "missing-quickstart", "Document one canonical install/first-use route and the expected result.", relative)
    prose = [
        line.strip()
        for line in text.splitlines()[:40]
        if line.strip() and not line.lstrip().startswith(("#", "![", "[![", "<", "---"))
    ]
    if not any(len(line) >= 32 for line in prose):
        _add(findings, "documentation", "warning", "missing-value-proposition", "Add a plain-language outcome sentence near the title.", relative)


def _repository_package_checks(root: Path, findings: list[Finding]) -> None:
    if not any((root / name).is_file() for name in LICENSE_NAMES):
        _add(
            findings,
            "trust",
            "error",
            "missing-license",
            "No root license file was found; source-visible is not open source without granted reuse rights.",
        )
    if not (root / ".gitignore").is_file():
        _add(findings, "privacy", "warning", "missing-gitignore", "Add a project-specific .gitignore before generating local state.")
    if not any((root / name).is_file() for name in ("SECURITY.md", ".github/SECURITY.md")):
        _add(findings, "trust", "warning", "missing-security-policy", "Document supported versions and a private vulnerability reporting route.")
    if not any((root / name).is_file() for name in ("CONTRIBUTING.md", ".github/CONTRIBUTING.md")):
        _add(findings, "community", "warning", "missing-contributing", "Document contributor setup, tests, and review expectations if contributions are accepted.")
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir() or not any(workflows.glob("*.y*ml")):
        _add(findings, "quality", "warning", "missing-ci", "No GitHub Actions workflow was found; verify supported environments another auditable way or add CI.")


def _runtime_checks(root: Path, findings: list[Finding]) -> None:
    pyproject = root / "pyproject.toml"
    python_markers = any((root / name).exists() for name in ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"))
    if python_markers:
        version_declared = any((root / name).is_file() for name in (".python-version", "runtime.txt"))
        if pyproject.is_file():
            text = pyproject.read_text(encoding="utf-8", errors="replace")
            version_declared = version_declared or bool(re.search(r"(?m)^\s*requires-python\s*=", text))
        if not version_declared:
            _add(findings, "portability", "warning", "missing-python-version", "Declare the supported Python range in package metadata or a runtime version file.")

    package_json = root / "package.json"
    if package_json.is_file():
        package = _read_json(package_json)
        engines = package.get("engines")
        if not isinstance(engines, dict) or not engines.get("node"):
            if not any((root / name).is_file() for name in (".nvmrc", ".node-version", ".tool-versions")):
                _add(findings, "portability", "warning", "missing-node-version", "Declare the supported Node.js range in package.json engines or a runtime version file.")
        if not any((root / name).is_file() for name in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb")):
            _add(findings, "portability", "warning", "missing-node-lockfile", "No Node dependency lockfile was found; verify reproducible dependency resolution.")

    if (root / "Cargo.toml").is_file() and not (root / "Cargo.lock").is_file():
        _add(findings, "portability", "warning", "missing-cargo-lock", "No Cargo.lock was found; expected for applications, optional for published libraries—document the choice.")


def _git_state_checks(root: Path, findings: list[Finding], used_git: bool) -> None:
    if not used_git:
        _add(findings, "source", "warning", "not-git-root", "Target is not a Git repository root; tracked-file and history guarantees are unavailable.")
        return
    try:
        result = _run(["git", "status", "--porcelain"], cwd=root, check=True)
    except (OSError, subprocess.CalledProcessError):
        _add(findings, "source", "warning", "git-status-unavailable", "Could not read Git working-tree status.")
        return
    if result.stdout.strip():
        _add(findings, "source", "warning", "dirty-worktree", "Working tree has uncommitted or untracked changes; pin the audited revision before a release gate.")


def _run_gitleaks(root: Path, findings: list[Finding]) -> None:
    binary = shutil.which("gitleaks")
    if not binary:
        _add(findings, "privacy", "error", "gitleaks-unavailable", "--run-gitleaks was requested but gitleaks is not installed; full-history secret evidence is missing.")
        return

    with tempfile.TemporaryDirectory(prefix="open-source-audit-") as temporary:
        report = Path(temporary) / "gitleaks.json"
        result = _run(
            [
                binary,
                "git",
                "--no-banner",
                "--redact",
                "--report-format",
                "json",
                "--report-path",
                str(report),
                ".",
            ],
            cwd=root,
        )
        if result.returncode == 0:
            return
        if result.returncode == 1:
            count = 0
            try:
                payload = json.loads(report.read_text(encoding="utf-8"))
                count = len(payload) if isinstance(payload, list) else 0
            except (OSError, json.JSONDecodeError):
                pass
            detail = f" ({count} redacted finding{'s' if count != 1 else ''})" if count else ""
            _add(findings, "privacy", "error", "gitleaks-findings", f"Gitleaks found potential secrets in Git history{detail}; perform an authorized local review and rewrite affected history before publication.")
            return
        _add(findings, "privacy", "error", "gitleaks-failed", "Gitleaks could not complete; secret-history evidence is missing. Its raw output was intentionally suppressed.")


def audit(root_value: str | Path, *, run_gitleaks: bool = False) -> dict[str, object]:
    root = Path(root_value).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"repository directory does not exist: {root}")

    paths, used_git = _tracked_paths(root)
    findings: list[Finding] = []
    _git_state_checks(root, findings, used_git)
    _repository_package_checks(root, findings)
    _readme_checks(root, findings)
    _runtime_checks(root, findings)
    for path in paths:
        _scan_file(root, path, findings)
    if run_gitleaks:
        _run_gitleaks(root, findings)

    findings.sort(key=lambda item: (0 if item.severity == "error" else 1, item.gate, item.path or "", item.line or 0, item.code))
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    status = "blocked" if errors else "needs-work" if warnings else "static-audit-clean"
    return {
        "repository": str(root),
        "status": status,
        "summary": {"errors": errors, "warnings": warnings, "files_considered": len(paths)},
        "limitations": [
            "Static-audit-clean is not launch-ready.",
            "Review Git history, media/IP, release artifacts, clean-room install, first success, CI, and live repository settings separately.",
        ],
        "findings": [asdict(item) for item in findings],
    }


def _print_text(report: dict[str, object]) -> None:
    summary = report["summary"]
    assert isinstance(summary, dict)
    print(f"Open-source static audit: {report['status']}")
    print(f"Repository: {report['repository']}")
    print(f"Errors: {summary['errors']}  Warnings: {summary['warnings']}  Files: {summary['files_considered']}")
    findings = report["findings"]
    assert isinstance(findings, list)
    for finding in findings:
        assert isinstance(finding, dict)
        location = str(finding.get("path") or "repository")
        if finding.get("line"):
            location += f":{finding['line']}"
        print(f"[{str(finding['severity']).upper()}] {finding['gate']}/{finding['code']} {location} — {finding['message']}")
    print("Boundary: static-audit-clean is not launch-ready; complete the non-static gates.")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", help="Repository root to audit")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors")
    parser.add_argument("--run-gitleaks", action="store_true", help="Run a redacted full-history gitleaks scan")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        report = audit(args.repository, run_gitleaks=args.run_gitleaks)
    except ValueError as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_text(report)

    summary = report["summary"]
    assert isinstance(summary, dict)
    if int(summary["errors"]) > 0:
        return 2
    if args.strict and int(summary["warnings"]) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
