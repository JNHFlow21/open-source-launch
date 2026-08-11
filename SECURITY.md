# Security Policy

## Supported versions

Security fixes are provided for the latest tagged release and the current
`main` branch. Older tags may not receive backports.

## Report a vulnerability privately

Use [GitHub private vulnerability reporting](https://github.com/JNHFlow21/open-source-launch/security/advisories/new).
Do not include credentials, private repository content, personal data, or an
unpatched exploit in a public issue.

Include:

- affected release or commit;
- the smallest safe reproduction;
- expected impact and required access;
- suggested remediation, if known.

You should receive an acknowledgement within seven days. No bounty or fixed
resolution deadline is promised.

## Security boundary

The Skill can instruct an agent to inspect files, run local tools, use GitHub
APIs, and prepare repository changes. Remote writes remain subject to the
requested mode and explicit authorization. The bundled scripts do not include
telemetry and intentionally suppress matched credential values in reports.
