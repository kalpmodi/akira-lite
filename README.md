<div align="center">

# akira-lite

One skill. A titanium, high-recall security review a developer can actually run.

</div>

akira-lite is the developer edition of akira. Where akira is a full autonomous
offensive agent, akira-lite ships a single, focused skill: `/security-review`.
It is built for recall. The goal is to catch as much as possible in the code you
just wrote, then rank it so the noise stays manageable.

## How it stays hard (three layers)

Each layer catches what the others miss:

1. Deterministic scanners for ground truth (semgrep, gitleaks/trufflehog,
   osv-scanner/npm audit/pip-audit, trivy/checkov).
2. Cross-file taint reasoning, source to sink, for the flows scanners miss.
3. A missing-control audit for the access-control and logic bugs no scanner sees.

Then it merges everything and reports by confidence tier.

## What makes it high-recall, not just noisy

- Nothing is silently dropped. Every finding gets a tier: Confirmed, Likely, or
  Needs-verification. Only pure no-impact noise is suppressed, and it is counted,
  not hidden.
- Nothing is silently skipped. A missing scanner is a reported coverage gap. Files
  not reviewed are listed. Every entry point is marked traced or not-traced by
  name before the report is emitted.
- Quick mode auto-escalates to a deep component review when the diff touches auth,
  access control, or a data boundary, so it does not miss cross-file logic bugs.

## Lightweight by design

High recall does not mean expensive. The hybrid pattern (deterministic scanners
plus LLM reasoning only where it is needed) runs at a fraction of the tokens of a
model reading everything itself. akira-lite keeps it light by:

- letting scanners (subprocesses, zero model tokens) do the bulk of detection,
- preferring a code graph when available (e.g. codegraph): it answers "who calls
  this", "what does this reach", and "trace source to sink" as near-zero-token
  queries instead of file reads, which is the biggest single token saving,
- reading narrowly (a finding's region and its call chain, never whole files),
- deriving severity from a class table instead of re-reasoning it,
- budgeting and triaging deep-mode work by risk, and delegating bulk reads to a
  subagent when one is available.

Parallelism (scanners run concurrently) cuts wall-clock time; the token savings
come from reading less, not from threading.

## Two modes, one skill

- Quick (default): fast pre-push review of your current diff.
- Deep: exhaustive audit of a component or the whole repo. Triggered by "audit",
  "deep review", or naming a path.

## Install

Plugin marketplace (recommended):

```
/plugin marketplace add kalpmodi/akira-lite
/plugin install akira-lite@akira-lite
```

Drop-in skill (Claude Code, and any agent that reads `./skills`):

```bash
git clone https://github.com/kalpmodi/akira-lite.git
cp -r akira-lite/skills/security-review ~/.claude/skills/
```

For full recall, install the deterministic layer:

```
semgrep      pipx install semgrep      # or: brew install semgrep
gitleaks     brew install gitleaks
osv-scanner  brew install osv-scanner
trivy        brew install trivy
pip-audit    pipx install pip-audit
```

## Use

```
/security-review              # quick, on your diff
deep security review of src/  # exhaustive audit of a path
```

Or in plain language: "is this safe to merge?", "audit this for security".
Then, to apply fixes: "fix the critical one".

## License

MIT. See [LICENSE](LICENSE).
