---
name: security-review
description: Use when a developer wants a hard, high-recall security review of their own code before committing, pushing, or opening a PR, or a full audit of a component/repo. Pairs deterministic scanners with cross-file taint reasoning and a missing-control audit, then reports every finding by confidence tier with fixes. Triggers on "security review", "deep security review", "audit this for security", "is this safe to merge", "review my code for vulnerabilities", or "/security-review".
---

# Security Review (akira-lite)

## Overview
A titanium-grade, high-recall security review that a developer can still run in
their own loop. The goal is to catch as much as possible, not to look tidy. It
does that by combining three layers that each catch what the others miss:

1. Deterministic scanners (ground truth: known signatures, secrets, CVEs, IaC).
2. Cross-file taint reasoning (source to sink, the flow SAST misses).
3. A missing-control audit (the authz and logic gaps no scanner sees).

Then it merges everything and reports by confidence tier. It optimizes for
recall first, and manages noise with tiering, not by deleting findings.

## Prime directives (non-negotiable)
- Never silently drop a finding. Suspicious-but-unproven goes to a lower
  confidence tier; it does not disappear.
- Never silently skip a tool. If a scanner is missing, that is a reported
  coverage gap, not an invisible one.
- Never silently skip code. Any file not reviewed (too large, out of scope,
  binary) is listed in the coverage ledger.
- A finding is never marked Confirmed without a concrete source-to-sink path.

## Step 0: Tool inventory (always runs first, always printed)

Detect the deterministic layer. Presence is not enough: a tool that is installed
but broken (wrong deps, no rules, needs login) reports a working layer while
producing nothing. Smoke-test each tool by running it, and mark it found only if
it actually executes.

```bash
for t in semgrep gitleaks trufflehog osv-scanner trivy checkov pip-audit npm; do
  if ! command -v "$t" >/dev/null 2>&1; then echo "$t: MISSING"; continue; fi
  if "$t" --version >/dev/null 2>&1; then echo "$t: ok"; else echo "$t: BROKEN"; fi
done
```

Treat BROKEN exactly like MISSING in the ledger: it is a degraded layer, not a
working one. If the smoke test passes but a real scan errors out mid-run, downgrade
that tool to BROKEN in the ledger too and continue with the other layers.

- Map tools to the layer they cover: SAST = semgrep; secrets = gitleaks or
  trufflehog; dependencies = osv-scanner or `npm audit` or pip-audit; IaC/config
  = trivy or checkov.
- If a layer has zero tools available, say so loudly in the report ledger:
  "secrets layer: no scanner - recall degraded".
- If NO scanners are available at all, print at the top of the report:
  "LLM-reasoning only, deterministic layer absent - recall degraded" and continue
  with layers 2 and 3.

Install one-liners to give the developer (offer, do not auto-install):
```
semgrep      pipx install semgrep      # or: brew install semgrep
gitleaks     brew install gitleaks
trufflehog   brew install trufflehog
osv-scanner  brew install osv-scanner
trivy        brew install trivy
checkov      pipx install checkov
pip-audit    pipx install pip-audit
```

## Step 1: Choose mode and scope

Quick mode (default) - fast pre-push check on the change:
```bash
git diff HEAD -- . 2>/dev/null || git diff main...HEAD 2>/dev/null
```

Deep mode - exhaustive audit of a component or the whole repo. Use when the user
says "audit", "deep", "full review", or names a component/path.

Auto-escalation rule (this is what makes quick mode safe):
- If the diff touches authentication, authorization/access control, session
  handling, or a data-access boundary (routes, ORM queries, object lookups,
  permission checks), quick mode MUST escalate to deep mode FOR THE AFFECTED
  COMPONENT. A diff-only review is structurally blind to a bug whose two halves
  live in unchanged code the diff merely connects. Read the whole handler, its
  middleware chain, and the models it touches, not just the changed lines.

State which mode ran and why in the report.

## Step 2: The engine (multi-pass)

Run these passes in order. Do not shortcut to line-scanning.

Pass A - Map the attack surface and build the entry-point ledger.
Enumerate every entry point in scope, by name, into a list you will close against:
routes/handlers, GraphQL resolvers, event/queue consumers, CLI/cron entry, file
read/write, subprocess/exec, deserializers, template renders, outbound HTTP,
auth/session boundaries, and any use of raw SQL. This list is the termination
condition for Pass F.

Pass B - Run the deterministic scanners over the scope, capture raw output.
```bash
# examples; scope to changed files in quick mode, to the path/repo in deep mode
semgrep --config auto --json --quiet <scope>
gitleaks detect --no-banner --redact            # or: trufflehog git file://. --only-verified
osv-scanner scan <scope>                          # or: npm audit --json / pip-audit
trivy fs --scanners vuln,secret,misconfig <scope> # or: checkov -d <scope>
```
Keep every raw hit. Deduplicate against Pass C/D, do not discard.

Pass C - Taint tracing (cross-file). For each entry point in the ledger, trace
untrusted input from source to sink across files. Follow the call chain into
other modules; a diff line is not exploitable in isolation, the code around and
downstream of it decides. This is the layer that finds what scanners cannot.

Pass D - Missing-control audit. For each ASVS-style control category (Step 3),
ask "is the control present on this path?" A missing control on a reachable path
is a finding even if no scanner flagged it. This is where broken access control,
IDOR/BOLA, and logic flaws are caught.

Pass E - Merge and tier. Combine scanner hits + taint findings + missing controls,
deduplicate by file:line + class, then assign each a confidence tier and severity
(Step 4).

Pass F - Completeness gate (termination condition). Walk the Pass A ledger. Every
entry point must be marked traced or not-traced BY NAME before the report emits.
If any are not-traced, go back and trace them. The loop ends when the enumeration
is exhausted, not when it "feels" done. Report the count: "18/18 entry points
traced" or list the ones you could not reach and why.

## Step 3: Coverage taxonomy (what to look for)

Cover all of these. Do not stop at the common ones.

OWASP Web Top 10: broken access control; cryptographic failures; injection
(SQL/NoSQL/command/LDAP/XPath/SSTI/XXE); insecure design; security
misconfiguration; vulnerable components; identification/auth failures; software
and data integrity (deserialization, unsigned updates); logging/monitoring gaps;
SSRF.

OWASP API Top 10: BOLA/IDOR; broken auth; broken object property authorization
(mass assignment, excessive data exposure); resource consumption; broken function
level authorization; unrestricted business flows; SSRF; misconfiguration;
improper inventory; unsafe consumption of third-party APIs.

OWASP LLM/AI Top 10 (if the code calls an LLM or builds prompts): prompt
injection, insecure output handling, training-data/tooling trust, excessive
agency, sensitive-info disclosure via prompts, and unbounded tool/function access.

ASVS-style control categories (used for Pass D): access control; authentication;
session management; input validation and encoding; cryptography and key
management; error handling and logging (no secrets/PII in logs); data protection
and PII exposure; communications (TLS, cert validation); business logic (race
conditions, TOCTOU, replay, limit bypass); configuration and hardening.

Secrets and credentials: hardcoded keys/tokens/passwords/private keys; secrets in
logs, responses, or error bodies; secrets committed to history.

Infra and supply chain: Dockerfile/k8s/terraform/CI-workflow misconfig;
unpinned, abandoned, or typosquat-shaped dependencies; workflow token/permission
over-scope.

Language and framework footguns: `eval`/`exec`, `pickle`/`yaml.load`,
`dangerouslySetInnerHTML`/`innerHTML`, `Math.random`/`rand()` for tokens, weak
hashes (MD5/SHA1) for passwords, permissive CORS with credentials, missing CSRF
on state-changing routes, debug mode / verbose stack traces shipped on.

## Step 4: Confidence tiers and severity (this replaces filtering-by-deletion)

Assign every finding a tier. Nothing real is deleted.
- Confirmed: concrete source-to-sink path OR a verified scanner hit. Exploit is
  named.
- Likely: strong indicator, one gap in the proof (e.g. reachability not fully
  traced). Say what confirms it.
- Needs-verification: suspicious pattern or a control that appears missing but the
  guard could be elsewhere. Say exactly what to check to promote or drop it.

Suppress only pure theoretical no-impact noise (e.g. a rate-limit nit with no
security consequence), and even then print a one-line suppressed count so it is
visible, not hidden.

Severity (independent of tier):
- Critical: unauth RCE, auth bypass, SQLi with data access, live secret exposed.
- High: IDOR/BOLA, stored XSS, SSRF to internal, missing auth on sensitive route,
  mass assignment of privileged fields.
- Medium: reflected XSS, CSRF, weak crypto, verbose errors, over-broad CORS.
- Low: hardening gaps, missing headers, info disclosure.

## Step 5: Output

Findings only (no edits). Lead with the ledger so blind spots are visible.

```
## Security review: <scope>  [mode: quick|deep, escalated: yes/no]

Coverage ledger
- Tools:   semgrep BROKEN | gitleaks ok | osv-scanner MISSING | trivy ok
- Layers:  SAST DEGRADED (scanner broken) | secrets ok | deps DEGRADED (no scanner) | IaC ok
- Entry points: 18/18 traced   (or: 16/18, untraced: worker.py:consume [no repro path])
- Files reviewed: <n> | skipped: <list + why>
- Suppressed (no-impact): <n>

Findings  (most severe first; each tagged with tier)
### [CRITICAL][Confirmed] <title>
- File: path:line   Class: <e.g. SQL injection>
- Path: input X (source) -> ... -> sink Y. Attacker gains Z.
- Fix: the specific change, with a code snippet.

### [HIGH][Likely] <title>
- ... What confirms it: <the one missing check>.

### [MEDIUM][Needs-verification] <title>
- ... To verify: <exact thing to check>.
```

End with two lines: the single highest-impact fix first, and any layer that ran
degraded so the developer knows where recall was weak.

## Step 6: Fix mode (only if asked)
If the user says "fix it": change only the lines needed to close the finding, no
refactors or drive-by edits. Show the diff and the finding it closes, then
re-review the changed lines to confirm no new hole was opened.

## Notes and limits
- This reviews your own code. It is defensive, not a pentest of a live target.
- Recall is only as strong as the layers that actually ran. A degraded layer
  (missing scanner) is stated, never hidden.
- Quick mode is diff-scoped by design; the auto-escalation rule is what keeps it
  from missing cross-file auth/logic bugs. When in doubt, run deep.
