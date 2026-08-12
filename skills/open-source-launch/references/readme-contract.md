# Conversion README contract

The README is the shortest verified route from repository landing page to
first value. It is not the full manual and not a substitute for packaging.

## Default information order

1. Product name and one sentence stating user, job, and outcome.
2. Only evidence-bearing badges.
3. Real screenshot/demo/result for the primary job.
4. One canonical quick start, prerequisites, and expected result.
5. Outcome-oriented capabilities and representative examples.
6. Supported environments, maturity, permissions, data/network behavior, and
   material limitations.
7. Architecture/configuration only when needed for adoption.
8. Docs, support, security, activity, contribution, and license.

Repository activity belongs near the end. Low stars or clone counts do not
belong above product proof or the quick start.

## Evidence rules

- Verify the exact install and first-use commands outside the source checkout.
- Use released package names, artifact URLs, versions, checksums, signing, and
  platform claims only after reading them back from their public source.
- Label alpha/beta state near the top.
- Do not present planned features as current.
- Never show a real secret or machine-specific path.
- Visual products require a real, privacy-reviewed product screenshot.
- CLI/library projects should show a concrete input and observable result.
- Keep `README.md` canonical English when targeting a broad public developer
  audience; place a language switch first and synchronize critical claims in
  stable siblings such as `README.zh-CN.md`.

## Multilingual quality gate

A translated README must work as an independent product page for a native
reader. Do not accept a literal, sentence-by-sentence translation merely
because every English paragraph has a counterpart.

For each maintained language:

1. preserve the canonical section order, capability matrix, commands, example
   outputs, links, maturity, costs, and trust boundaries;
2. rewrite headings and prose in natural target-language syntax and established
   technical terminology;
3. keep the shortest useful explanation and move exhaustive implementation
   detail to shared reference docs;
4. remove maintainer-only machine context, duplicated setup guidance, and stale
   hard-coded versions;
5. render the document, validate code fences/tables/links, and compare it with
   the canonical README for semantic—not necessarily line-for-line—parity.

For Simplified Chinese, prefer direct Chinese developer prose over translated
English noun stacks or mixed-language headings. Keep product and protocol names
in English only when that is the familiar ecosystem term.

Repository Pulse is self-describing. By default, place only the linked SVG in
the activity section; do not generate a generic English or Chinese paragraph
about Traffic windows, automatic refresh, or whether clones prove adoption.

## Avoid

- badge walls, decorative traffic counters, or Star History as product proof;
- several equal-priority installation methods;
- architecture before the user outcome;
- `curl | sh` when a trustworthy native distribution exists;
- source-build instructions presented as the end-user installer;
- empty templates, exhaustive configuration tables, and stale screenshots;
- adjectives such as secure, private, fast, production-ready, or one-click
  without direct evidence.

For a deeper README-only workflow, activate the sibling
`write-github-readme` Skill and run its deterministic audit.
