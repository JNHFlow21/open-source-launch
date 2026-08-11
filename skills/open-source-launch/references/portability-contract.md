# Stranger-first portability contract

## Principle

Test the distribution unit a stranger receives. A source checkout that works
because the maintainer already has dependencies, config, databases, models,
credentials, or symlinked files is not portable.

## Hidden-state inventory

Check for:

- absolute `/Users/...`, `/home/...`, drive-letter, `file://`, and private host
  references;
- symlinks that resolve outside the repository;
- untracked files imported by build/package scripts;
- global npm/Python/Ruby packages, Homebrew formulae, shell functions, aliases,
  PATH additions, launch agents, daemons, and open ports;
- existing dotfiles, keychain entries, browser profiles, databases, caches,
  model files, and app support directories;
- private registries, Git dependencies, submodules, binary downloads, or APIs;
- undeclared environment variables, credentials, permissions, and network
  requirements;
- architecture-specific binaries or platform APIs;
- developer fixtures presented as user data or defaults.

## Verification ladder

Use the cheapest faithful environment, then increase isolation when risk
requires it:

1. clean temporary directory outside the source checkout;
2. `git archive` extraction or fresh clone at the release revision;
3. temporary HOME/config/cache/data directories;
4. clean language environment or container/VM;
5. a second supported OS/architecture or CI runner;
6. signed/notarized/released artifact installed through the advertised channel.

Do not claim cross-platform support from static code inspection.

## Product-type evidence

### CLI

- package installs from the public registry or release;
- executable is on PATH without source-relative imports;
- `--help`, one real command, representative output, update/uninstall;
- shell and OS matrix matches CI.

### Library or SDK

- clean dependency resolution from the public registry;
- minimal complete import/example and returned value;
- supported runtime versions and optional extras;
- API docs and compatibility policy.

### Desktop or mobile

- versioned artifact, architecture/OS support, checksums;
- signing/notarization or honest unsigned/ad-hoc state;
- install, launch, permissions, local data, update, uninstall;
- real privacy-reviewed screenshot from the shipped revision.

### Self-hosted service

- durable container/package route and default URL;
- required database, volumes, migrations, auth, ports, backup, upgrade;
- no private image registry or maintainer-only infrastructure.

### Skill or plugin

- platform-native installation and explicit project/global activation scope;
- trigger examples, tool/network/secret requirements, expected output;
- update/remove flow and no credentials inside Skill files.

## First-success acceptance

A passing record contains all five:

1. public/release artifact installed;
2. no maintainer HOME/config reused;
3. one intended user task completed;
4. result observed and captured;
5. cleanup/update/recovery behavior understood.

If a platform cannot be tested, say `missing_evidence`; document a support
boundary rather than guessing.
