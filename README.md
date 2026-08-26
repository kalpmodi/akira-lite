<div align="center">

# akira-lite

A single Claude Code skill that reviews your own code for security bugs before you push.

</div>

> Lightweight developer aid, not a professional VAPT, audit, or compliance
> certification. Findings are advisory; validate them yourself.
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
- [SECURITY.md](SECURITY.md)
- License: MIT ([LICENSE](LICENSE))
