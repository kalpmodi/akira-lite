---
name: security-review
description: Use when a developer wants a hard, high-recall but token-light security review of their own code before committing, pushing, or opening a PR, or a full audit of a component/repo. Deterministic scanners do the bulk; the model reasons only about cross-file taint and missing controls; findings are reported by confidence tier with fixes. Triggers on "security review", "deep security review", "audit this for security", "is this safe to merge", "review my code for vulnerabilities", or "/security-review".
---

# Security Review (akira-lite)

High recall, low cost. Three layers, each catching what the others miss:
scanners (signatures, secrets, CVEs, IaC), cross-file taint (source to sink),
and a missing-control audit (access-control and logic gaps no scanner sees).
Findings are ranked by confidence, not deleted.

## Prime directives
- Never silently drop a finding: unproven goes to a lower tier, it does not vanish.
- Never silently skip a tool or a file: it goes in the coverage ledger.
- Confirmed requires a concrete source-to-sink path.

## Cost model (stay lightweight)
Token cost = code read into context + text generated. Minimize both:
- Deterministic-first. Scanners are subprocesses and cost zero model tokens. Let
  them find what they can; spend model reasoning only on what they cannot.
- Read narrow, never whole files. Start from a scanner hit or an entry point and
  read only that region plus its call chain. Loading whole files is how these
  reviews go heavy.
- Use the code graph for structure, not for framework semantics. A code graph
  (e.g. codegraph MCP with the repo indexed) is the single biggest token lever for
  "where is X", "who calls this", "what does this reach", and "trace source to sink
  between two named symbols" (it bridges dynamic hops) in near-zero-token calls.
  BUT it models symbols, not framework concepts: HTTP routes, decorators, and
  auth/middleware are usually NOT graph nodes, so a natural-language context query
  for "routes and auth" returns noise (often the frontend router). For route and
  auth mapping, use the graph only to get the backend file set, then grep the
  actual decorators/middleware in those files:
  `grep -nE '@app\.(get|post|put|delete|patch)|Depends|middleware|Authorization' <file>`.
  Use codegraph_search/codegraph_files for named symbols and codegraph_trace
  between two names; do not rely on a prose context query to find the attack surface.
  Fall back to grep + `sed -n` ranges when no graph is present.
- Derive, do not re-reason. Severity comes from the class table below, once.
- Budget and triage (deep mode). Rank entry points by risk, reason the top ones
  first, stop at the budget, and list the rest as scanner-only in the ledger.
- Delegate bulk reads (deep mode). If a subagent tool exists, hand whole-repo
  reading to a subagent and keep only its findings, so the driver context stays small.
- Parallelism cuts time, not tokens: run scanners concurrently, but that only
  speeds wall-clock.

Also check for a code graph: if the codegraph MCP is present and the target repo
has a `.codegraph/` index (confirm with codegraph_status), use it for pass A and
pass C below and note "code graph: ok" in the ledger. If absent, offer
`codegraph init -i` once, then fall back to grep/sed and note "code graph: none".

## Step 0: Tool inventory (parallel smoke-test, always printed)
Presence is not enough; a broken tool reports a working layer while producing
nothing. Run each tool; found means it actually executes. Backgrounded for speed.
```bash
for t in semgrep gitleaks trufflehog osv-scanner trivy checkov pip-audit npm; do
  { command -v "$t" >/dev/null 2>&1 \
      && ("$t" --version >/dev/null 2>&1 && echo "$t: ok" || echo "$t: BROKEN") \
      || echo "$t: MISSING"; } &
done; wait
```
Treat BROKEN like MISSING: a degraded layer. If a layer has no working tool, say
so in the ledger ("secrets: no scanner - recall degraded").

Recommend-and-rerun rule: whenever any tool is MISSING or BROKEN, do NOT block.
Complete the review with the layers that work, then, at the end, tell the developer
exactly which layer was degraded, the one-liner to fix it, and that re-running the
scan afterwards gives full coverage. If every tool is present and working, say
nothing about installs. Install one-liners (offer, never auto-install):
`pipx install semgrep pip-audit checkov`,
`brew install gitleaks trufflehog osv-scanner trivy`.
For a broken (not missing) tool, recommend a reinstall, e.g. `pipx reinstall semgrep`.

## Step 1: Mode, scope, budget
- Quick (default): `git diff HEAD`; if empty, diff against the repo's default
  branch (main, master, or whatever `origin/HEAD` points to). Cheap.
- Deep: a component or repo. Triggered by "audit"/"deep" or a named path.
- Auto-escalate: if the diff touches auth, access control, session, or a data
  boundary (routes, object lookups, ORM, permission checks), escalate to deep FOR
  THAT COMPONENT only. A diff-only review is blind to a bug split across unchanged
  code. Read the handler + its middleware + the models it touches, nothing wider.
- Deep-mode budget: rank entry points by risk; reason the top ones first; stop
  when the budget is reached and record untraced ones in the ledger.

## Step 2: Engine (passes)
A. Map surface. List every entry point in scope BY NAME: routes/resolvers,
   queue/event consumers, CLI/cron, file I/O, subprocess/exec, deserializers,
   template renders, outbound HTTP, auth boundaries, raw SQL. With a code graph,
   query these by name instead of reading files. This list is the termination
   condition for pass F.
B. Scan (subprocesses, run in parallel, keep all raw hits):
   `semgrep --config auto --json`, `gitleaks detect`/`trufflehog`,
   `osv-scanner`/`npm audit`/`pip-audit`, `trivy fs`/`checkov`. Scope to changed
   files in quick mode, to the path in deep mode.
C. Taint. For each entry point (top-ranked first), trace untrusted input source
   to sink across files. With a code graph, trace source to sink in one call
   (it bridges dynamic hops grep misses), then read only the bodies on that path;
   otherwise follow the call chain with grep/sed. This finds what scanners cannot.
D. Missing-control audit. For each control category (Step 3), ask "is it present
   on this reachable path?" With a code graph, list a sensitive sink's callers and
   check each routes through an auth/ownership guard. A missing control is a
   finding even with no scanner hit.
E. Merge and tier. Dedup by file:line + class; assign tier + severity (Step 4).
F. Completeness gate. Mark every pass-A entry point traced or not-traced by name.
   Loop until the list is exhausted or the budget is hit. Report "N/M traced".

## Step 3: What to look for
- Access control: IDOR/BOLA, missing role check, mass assignment, excessive data
  exposure. (Highest priority; scanners miss these.)
- Injection: SQL/NoSQL, command, LDAP/XPath, SSTI, XXE, path traversal.
- Auth/session: missing auth middleware, weak/again unverified JWT, insecure session.
- SSRF and outbound fetch from user input; cloud metadata reachability.
- Secrets: hardcoded keys/tokens/passwords, secrets in logs/responses/history.
- Crypto: weak password hash (MD5/SHA1), missing salt, predictable randomness.
- Deserialization: pickle, yaml.load, native deserializers, XXE.
- Web/config: XSS (reflected/stored/DOM), CSRF on state change, permissive CORS,
  debug mode, verbose errors, missing headers.
- Supply chain/IaC: unpinned/abandoned/typosquat deps, Docker/k8s/terraform/CI misconfig.
- AI (if it builds prompts/calls an LLM): prompt injection, insecure output
  handling, excessive tool/agent access.

## Step 4: Tier and severity
Tier every finding; delete nothing real:
- Confirmed: concrete source-to-sink path or a verified scanner hit.
- Likely: strong indicator, one gap in the proof (say what confirms it).
- Needs-verification: suspicious, guard could be elsewhere (say what to check).
Suppress only pure no-impact noise, and print a one-line suppressed count.

Severity (derive from class, do not re-reason):
- Critical: unauth RCE, auth bypass, SQLi with data access, live secret exposed.
- High: IDOR/BOLA, stored XSS, SSRF to internal, missing auth on sensitive route,
  privileged mass assignment.
- Medium: reflected XSS, CSRF, weak crypto, verbose errors, broad CORS.
- Low: hardening gaps, missing headers, info disclosure.

## Step 5: Output (findings only, no edits)
```
## Security review: <scope>  [mode, escalated: y/n]
Coverage ledger
- Tools:  semgrep BROKEN | gitleaks ok | osv-scanner MISSING | trivy ok
- Layers: SAST degraded | secrets ok | deps degraded | IaC ok
- Code graph: ok (used for surface + taint)  |  or: none (grep fallback)
- Entry points: 18/18 traced   (or 16/18, untraced: worker.py:consume [budget])
- Files reviewed: <n> | skipped: <list + why> | suppressed: <n>

### [CRITICAL][Confirmed] <title>
- File: path:line   Class: <e.g. SQL injection>
- Path: input X (source) -> ... -> sink Y. Attacker gains Z.
- Fix: specific change, with a snippet.
### [HIGH][Likely] ...  (What confirms it: <the one check>)
### [MEDIUM][Needs-verification] ...  (To verify: <exact thing>)
```
End with: the single highest-impact fix. Then, only if a layer was degraded, one
line naming it, the install/reinstall one-liner to restore it, and that re-running
the scan afterwards gives full coverage. If nothing was degraded, omit that line.

## Step 6: Fix mode (only if asked)
Change only the lines needed to close the finding, no refactors. Show the diff and
the finding it closes, then re-review the changed lines for new holes.

## Limits
Reviews your own code (defensive, not a live-target pentest). Recall is only as
strong as the layers that ran; a degraded layer is stated, never hidden. When in
doubt on a diff that touches auth or data, run deep on that component.
