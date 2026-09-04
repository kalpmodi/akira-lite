<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/wordmark-dark.png">
  <img alt="akira-lite" src="assets/wordmark-light.png" width="440">
</picture>

A single Claude Code skill that reviews your own code for security bugs before you push.

[![License: MIT](https://img.shields.io/github/license/kalpmodi/akira-lite)](LICENSE)
[![Release](https://img.shields.io/github/v/release/kalpmodi/akira-lite?sort=semver)](https://github.com/kalpmodi/akira-lite/releases)
[![Validate](https://img.shields.io/github/actions/workflow/status/kalpmodi/akira-lite/validate.yml?label=validate)](https://github.com/kalpmodi/akira-lite/actions/workflows/validate.yml)

</div>

> Purpose-built for fast, shift-left review inside your own workflow. It complements
> a professional VAPT, audit, or compliance engagement rather than replacing one,
> its findings are actionable guidance you confirm before shipping.
>
> When you need industry-grade assurance, step up to
> [akira](https://github.com/kalpmodi/akira): the professional, top-tier offensive
> security platform built for real VAPT engagements, autonomous recon, exploit
> chaining, and audit-ready reporting, end to end.

## Install

```
/plugin marketplace add kalpmodi/akira-lite
/plugin install akira-lite@akira-lite
```

Drop-in alternative:

```
git clone https://github.com/kalpmodi/akira-lite.git
cp -r akira-lite/skills/security-review ~/.claude/skills/
```

## Use

```
/security-review              # reviews your current diff
deep security review of src/  # audits a component or repo
```

Say "fix the critical one" to apply a fix.

## What it does

- Runs scanners (secrets, CVEs, IaC) and reasons about cross-file taint and missing access control.
- Tiers every finding (Confirmed / Likely / Needs-verification); nothing is dropped silently.
- Prints a coverage ledger (what ran, what was skipped) so gaps are visible.
- Reviews the diff by default; goes deep when it touches auth or a data boundary.

```
### [HIGH][Confirmed] No auth on internal API
web/api.py:216  ->  every /api/* route served with no auth check.
Fix: add a fail-closed auth dependency.
```

## Optional tools

It runs without these; they improve recall:

```
pipx install semgrep pip-audit checkov
brew install gitleaks trufflehog osv-scanner trivy
```

## Links

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)
- License: MIT ([LICENSE](LICENSE))
