# Open-source readiness contract

## Claim envelope

Every material public claim must be one of:

- `verified` — observed in the intended public artifact or live repository;
- `planned` — explicitly labeled roadmap work;
- `missing_evidence` — not safe to advertise yet.

Evidence should name the revision, platform, runtime, command, output, and
limitations needed to reproduce the result. “Implemented” is not equivalent to
“packaged,” “published,” “installable,” or “accepted by a new user.”

## Gate order

1. **Public intent** — product, audience, license, support commitment.
2. **Privacy and IP** — current tree, history, release assets, screenshots.
3. **Portability** — dependency and platform contract plus isolated install.
4. **Distribution** — package/release channel and update path.
5. **First success** — one complete user job from the public artifact.
6. **Trust** — limitations, security reporting, data and permission behavior.
7. **Documentation** — conversion README and deeper routes.
8. **Discovery** — metadata, topics, social preview, linked evidence.
9. **Publication** — PR, CI, visibility, release, and live readback.
10. **Adoption** — distribution and measured feedback loop.

Do not reorder the workflow to make the repository look polished before it is
safe and usable.

## Product acceptance record

Capture at least:

| Field | Example |
| --- | --- |
| Revision | commit SHA or release tag |
| Artifact | package/version, release asset, app bundle, container digest |
| Environment | OS, architecture, runtime, clean HOME/container/VM |
| Install | exact command and exit state |
| First job | exact command/workflow |
| Result | output, file, UI state, URL, or typed response |
| Boundaries | network, permissions, secrets, persistence, known gaps |
| Evidence | CI URL, log path, screenshot, checksum, test report |

## Publication stop conditions

Stop before changing visibility or publishing when any of these is true:

- a secret, private key, customer/user data, personal media, or internal host is
  present in current files, history, screenshots, or artifacts;
- license or third-party asset provenance is unresolved;
- the canonical install depends on a maintainer checkout or undeclared machine
  state;
- the first-success path has not run from the intended public artifact;
- README claims exceed verified product behavior;
- required CI/privacy checks are red or missing;
- the public support/security route would expose a private address or secret.

## Repository settings evidence

After launch, read back rather than assume:

- `visibility`, `defaultBranchRef`, archived/fork status;
- description, homepage, topics, social preview;
- Actions permissions and required checks;
- private vulnerability reporting or `SECURITY.md` route;
- release/tag and package availability;
- rendered README and linked assets.
