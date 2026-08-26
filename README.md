<div align="center">

# akira-lite

One skill: a high-recall, token-light security review a developer can actually run.

</div>

`/security-review` your own code before you push. It finds the real, exploitable
bugs, filters the noise, and hands you the fix.

## Quick start

```bash
/plugin marketplace add kalpmodi/akira-lite
/plugin install akira-lite@akira-lite

/security-review              # quick: reviews your current diff
deep security review of src/  # deep: audits a component or the whole repo
```

Plain language works too: "is this safe to merge?", "audit this for security".
To apply a fix: "fix the critical one".

Drop-in install (any agent that reads `./skills`):

```bash
git clone https://github.com/kalpmodi/akira-lite.git
cp -r akira-lite/skills/security-review ~/.claude/skills/
```

## What you get

Findings ranked by confidence, led by a coverage ledger so blind spots stay visible:

```
## Security review: src/  [mode: deep]
- Tools: gitleaks ok | trivy ok | semgrep BROKEN    Entry points: 18/18 traced

### [HIGH][Confirmed] No auth on internal API
- File: web/api.py:216  ->  every /api/* route is served with no auth check.
- Fix: add a fail-closed auth dependency on the router.

Top fix: add fail-closed auth to the internal API.
SAST degraded: `pipx reinstall semgrep`, then re-run for full coverage.
```

## How it works

Three layers, each catching what the others miss: deterministic scanners (secrets,
CVEs, IaC), cross-file taint reasoning (source to sink), and a missing-control
audit (the access-control and logic bugs no scanner sees). Every finding is tiered
(Confirmed / Likely / Needs-verification) and never silently dropped.

It stays cheap by letting the scanners do the bulk (zero model tokens), using a
code graph when present, and reading narrowly instead of whole files. Quick mode
reviews your diff; it auto-escalates to a deep component review when the diff
touches auth or a data boundary.

Optional tools for full recall (it runs without them and tells you what is missing):

```bash
pipx install semgrep pip-audit checkov
brew install gitleaks trufflehog osv-scanner trivy
```

## Scope and limitations

akira-lite is a lightweight, developer-facing aid for shift-left code review. It is
expressly not a substitute for a professional Vulnerability Assessment and
Penetration Test (VAPT), a formal security audit, or any compliance certification,
and its output must not be represented or relied upon as such. It performs no
live-target testing, makes no warranty of completeness or fitness, and its findings
are advisory only. You remain responsible for validating every finding and for the
security of what you ship.

For an adversarial, engagement-grade assessment - full recon, exploit chaining, and
reporting, end to end - use the full offensive agent this project is derived from:
[akira](https://github.com/kalpmodi/akira).

## Contributing

Contributions are welcome and intentionally simple, because the whole tool is one
`SKILL.md`.

1. Fork, branch, and edit `skills/security-review/SKILL.md`.
2. Test it: install your copy (`cp -r skills/security-review ~/.claude/skills/`) and
   run `/security-review` against real code. Include, in the PR, the before/after
   behavior you observed.
3. Keep it lean. This skill loads into context on every run, so brevity is a
   feature; prefer sharpening existing steps over adding new ones.
4. Do not report security issues here. See [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
