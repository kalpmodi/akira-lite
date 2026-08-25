<div align="center">

# akira-lite

One skill: a high-recall, token-light security review a developer can actually run.

`/security-review` your own code before you push. It finds the real, exploitable
bugs, filters the noise, and hands you the fix.

</div>

## Quick start

```bash
# 1. install (plugin marketplace)
/plugin marketplace add kalpmodi/akira-lite
/plugin install akira-lite@akira-lite

# 2. run it
/security-review              # quick: reviews your current diff
deep security review of src/  # deep: audits a component or the whole repo
```

Plain language works too: "is this safe to merge?", "audit this for security".
To apply a fix afterwards: "fix the critical one".

Drop-in install (any agent that reads `./skills`, no marketplace):

```bash
git clone https://github.com/kalpmodi/akira-lite.git
cp -r akira-lite/skills/security-review ~/.claude/skills/
```

## What you get

Findings ranked by confidence, led by a coverage ledger so blind spots are visible:

```
## Security review: src/  [mode: deep]
Coverage ledger
- Tools:  gitleaks ok | trivy ok | semgrep BROKEN | osv-scanner MISSING
- Layers: SAST degraded | secrets ok | IaC ok | deps degraded
- Code graph: ok    Entry points: 18/18 traced    Files: 22 | skipped: 0

### [HIGH][Confirmed] No auth on internal API
- File: web/api.py:216   Class: broken access control
- Path: every /api/* route is served with no auth check -> org data is readable.
- Fix: add a fail-closed auth dependency on the router. <snippet>

### [MEDIUM][Needs-verification] Session token has no identity
- To verify: confirm whether the upstream gate enforces per-user auth.

Top fix: add fail-closed auth to the internal API.
SAST degraded: `pipx reinstall semgrep`, then re-run for full coverage.
```

## How it works

Three layers, each catching what the others miss:

| Layer | Catches | Cost |
|---|---|---|
| Deterministic scanners | known signatures, secrets, CVEs, IaC misconfig | zero model tokens (subprocess) |
| Cross-file taint | source-to-sink flows scanners can't follow | narrow reads only |
| Missing-control audit | access-control and logic bugs no scanner sees | reasoning only |

Every finding is tiered, never deleted:

| Tier | Meaning |
|---|---|
| Confirmed | concrete source-to-sink path or a verified scanner hit |
| Likely | strong indicator, one gap in the proof (says what confirms it) |
| Needs-verification | suspicious, guard may be elsewhere (says what to check) |

## Why it stays lightweight

High recall does not mean expensive. The hybrid pattern (scanners do the bulk, the
model reasons only where it must) runs at a fraction of the tokens of a model
reading everything itself:

- scanners (subprocesses) cost zero model tokens,
- a code graph (e.g. codegraph), when present, answers "who calls this / what does
  this reach / trace source to sink" as near-zero-token queries instead of reads,
- it reads narrowly (a finding's region and its call chain, never whole files),
- deep mode budgets and triages by risk, and delegates bulk reads to a subagent.

Parallelism cuts wall-clock time; the token savings come from reading less.

## Modes

- Quick (default): fast pre-push review of your diff. Auto-escalates to a deep
  component review when the diff touches auth, access control, or a data boundary.
- Deep: exhaustive audit of a component or repo. Triggered by "audit"/"deep" or a path.

## Full recall (optional tools)

The review runs without these, but installs the deterministic layer for full recall:

```bash
pipx install semgrep pip-audit checkov
brew install gitleaks trufflehog osv-scanner trivy
```

If a tool is missing or broken, the review still completes and tells you the exact
one-liner to restore that layer, then re-run.

## Security and license

- How to use it safely and how to report an issue: [SECURITY.md](SECURITY.md).
- MIT. See [LICENSE](LICENSE).
