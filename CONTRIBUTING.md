# Contributing

Thanks for improving Open Source Launch.

## Before opening an issue

- Use a private security advisory for vulnerabilities or sensitive findings.
- Search existing issues.
- Remove credentials, private repository content, personal paths, and user data
  from examples.
- State whether the behavior came from `audit`, `prepare`, `launch`, or
  `refresh` mode.

## Development setup

Requirements: Git and Python 3.10 or newer. The runtime scripts use only the
Python standard library.

```bash
git clone https://github.com/JNHFlow21/open-source-launch.git
cd open-source-launch
python3 -m unittest discover -s skills/open-source-launch/tests -v
python3 -m compileall -q skills/open-source-launch
```

Run the public-surface audit before submitting:

```bash
python3 skills/open-source-launch/scripts/audit_open_source.py . --strict
```

If Gitleaks is installed locally, also run:

```bash
python3 skills/open-source-launch/scripts/audit_open_source.py . \
  --run-gitleaks --strict
```

## Pull requests

- Keep the core `SKILL.md` concise and move conditional detail into a directly
  linked reference.
- Add or update deterministic tests for script changes.
- Preserve redaction: tests and reports must never print matched secret values.
- Keep English and Simplified Chinese README claims synchronized.
- Describe the evidence behind any new platform, installer, security, or
  distribution claim.
- Do not weaken publication gates merely to make a fixture pass.

By contributing, you agree that your contribution is licensed under the MIT
License.
