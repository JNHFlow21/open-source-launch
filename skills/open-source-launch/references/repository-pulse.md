# Repository Pulse component

## Purpose

Use only when the maintainer wants a compact white-background activity graphic
near the end of the README. It is supporting evidence, not the product hero.

The component shows:

- cumulative total clones inside GitHub's rolling 14-day Traffic window;
- stars, forks, and commit count;
- unique visitors, unique cloners, and total clones for the same owner snapshot.

## Security model

- GitHub Actions uses the ephemeral repository-scoped `github.token` for public
  metadata and publishing the generated SVG to an orphan `metrics` branch.
- GitHub does not grant that Actions token access to the owner-only Traffic API.
  The installer therefore stores only a dated aggregate snapshot and daily
  clone counts—never usernames, referrers, paths, or credentials.
- Never embed a long-lived or encrypted personal token in a public README URL.
- The public chart must state that Traffic is a dated rolling-window snapshot.

## Install

From a repository owner checkout with `gh` already authenticated:

```bash
python3 <skill-directory>/scripts/install_repository_pulse.py \
  /path/to/repository --repository OWNER/REPO --collect-traffic
```

The command writes:

- `.github/workflows/repository-metrics.yml`
- `.github/repository-metrics-traffic.json`
- `scripts/render_repository_metrics.py`

It does not edit README, commit, push, create a branch, or change visibility.
Add the printed README snippet near the end, commit through the normal PR path,
then manually dispatch `repository-metrics.yml` after merge.

## Verification

1. Workflow succeeds on the default branch.
2. `metrics/repository-metrics.svg` returns HTTP 200 and `image/svg+xml`.
3. SVG contains `Total clones over time` and no credential markers.
4. README uses the raw `metrics` branch URL.
5. Chart position follows product docs/development and precedes
   contribution/license material.
6. Traffic date and rolling-window language are visible.

Refresh the owner snapshot explicitly when fresh clone/visitor data is needed;
the weekly Action refreshes public cards but cannot refresh private Traffic.
