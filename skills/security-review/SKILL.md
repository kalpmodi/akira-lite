---
name: security-review
description: Use when a developer wants to security-review their own code before committing, pushing, or opening a PR. Reviews the current git diff (or a named file/path) for real, exploitable vulnerabilities, filters out false positives, and returns a prioritized report with concrete fixes. Triggers on "security review", "review my code for security", "check this before I push", "is this safe to merge", or "/security-review".
---

# Security Review (akira-lite)

## Overview
A developer-first, shift-left security review. It reviews the code YOU wrote,
before it merges. Default target is the current diff, so it is fast, cheap, and
relevant. Every finding is verified before it is reported, so the output is
signal, not noise.

Two things this skill will not do:
- It will not report a vulnerability it cannot explain how to exploit.
- It will not change your code unless you ask for fix mode.

## Step 1: Pick the scope

Choose the smallest scope that covers the change. Ask the user only if none is obvious.

```bash
# Preferred: uncommitted work (staged + unstaged)
git diff HEAD -- . 2>/dev/null

# Branch vs main (use before opening a PR)
git diff main...HEAD 2>/dev/null

# A specific file or directory the user named
#   review src/api/  ->  read those files directly
```

Rules:
- Default to `git diff HEAD`. If that is empty, fall back to `git diff main...HEAD`.
- If the user names a path, review that path instead.
- Read enough surrounding context (the function, the route, the caller) to judge
  each change. A diff line is not exploitable in isolation; the code around it decides.

## Step 2: Review against the classes developers actually introduce

Walk the changed code against this checklist. These are ordered by how often they
cause real incidents in application code, not by theory.

1. Broken access control / IDOR / BOLA
   - Does every object lookup check that the current user owns or may access it?
   - Are IDs taken from the request trusted without an ownership check?
   - Is an admin-only action reachable by a normal user (missing role check)?
   - Mass assignment: is a request body bound straight to a model (role, is_admin, price)?

2. Injection
   - SQL/NoSQL built with string concatenation instead of parameters.
   - Command execution with user input (`exec`, `system`, `child_process`, `subprocess`).
   - Template injection (SSTI), LDAP, XPath.
   - Path traversal in file reads/writes (`../`, absolute paths from user input).

3. Authentication and session
   - Missing auth middleware on a new route or handler.
   - Weak/absent token verification, JWT `alg:none` or unverified signature.
   - Secrets or password compared non-constant-time; tokens logged.

4. SSRF and outbound requests
   - Server fetches a URL derived from user input without an allowlist.
   - Reachability of cloud metadata (169.254.169.254) or internal hosts.

5. Secrets and sensitive data
   - Hardcoded API keys, tokens, passwords, private keys in the diff.
   - Secrets printed to logs or returned in responses/error bodies.
   - PII returned to a caller who should not see it (excessive data exposure).

6. Crypto and randomness
   - Weak hash for passwords (MD5/SHA1), missing salt, home-rolled crypto.
   - Predictable randomness (`Math.random`, `rand()`) for tokens/IDs.

7. Deserialization and parsing
   - Untrusted input into `pickle`, `yaml.load`, native deserializers, XXE-enabled XML.

8. Web output and config
   - XSS: unescaped user input into HTML, `dangerouslySetInnerHTML`, `innerHTML`.
   - CORS reflecting arbitrary origin with credentials.
   - CSRF protection missing on state-changing routes.
   - Debug mode, verbose stack traces, or misconfig shipped on.

9. Dependencies
   - New dependency added: flag if it is unpinned, unmaintained, or typosquat-shaped.

## Step 3: Verify before reporting (false-positive filter)

For each candidate finding, before it goes in the report, do this:

1. State the exact input and the exact code path that reaches the sink.
2. Try to disprove it. Look for the guard you may have missed: an auth
   middleware higher up, a framework default that escapes, a validator, an ORM
   that parameterizes. If a real control neutralizes it, drop the finding.
3. Only keep it if you can name a concrete exploit scenario.

If you are not sure it is exploitable, do not rank it Critical/High. Put it under
"Worth a look" with your uncertainty stated. Never pad the report.

## Step 4: Output

Print findings only (do not edit files). Order most severe first.

```
## Security review: <scope>
<N> confirmed, <M> worth a look. <clean statement if zero>.

### [CRITICAL] <short title>
- File: path/to/file.ext:line
- Class: <e.g. IDOR / SQL injection>
- What: one sentence on the flaw.
- Exploit: concrete scenario. Input X reaches sink Y, attacker gains Z.
- Fix: the specific change (parameterize / add ownership check / allowlist), with a code snippet.

### [HIGH] ...
### [MEDIUM] ...

## Worth a look (unverified)
- path:line - why it is suspicious, what would confirm it.
```

Severity guide:
- Critical: unauthenticated RCE, auth bypass, SQLi with data access, secret exposed live.
- High: IDOR/BOLA, stored XSS, SSRF to internal, missing auth on sensitive route.
- Medium: reflected XSS, CSRF, weak crypto, verbose errors, over-broad CORS.
- Low: hardening gaps, missing headers, info disclosure.

End with one line: the single highest-impact thing to fix first.

## Step 5: Fix mode (only if asked)

If the user says "fix it" / "apply the fixes":
- Change only the lines needed to close the finding. No refactors, no drive-by edits.
- Show the diff for each fix and the finding it closes.
- Re-review the changed lines to confirm the fix did not open a new hole.

## Notes
- This reviews your own code. It is defensive. It is not a pentest of a live target.
- It complements, not replaces, SAST/dependency scanners: it catches the authz and
  logic flaws those tools miss, and it explains the ones they find.
- Keep scopes small. A tight diff review beats a whole-repo sweep for both speed and signal.
