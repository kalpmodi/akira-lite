# Ground truth (answer key)

Maintainer reference for what each fixture plants. Do NOT put any of this in the
fixture code itself, the skill must find these from the code, not from a comment.

Line numbers below are advisory (for maintainer orientation) and are not graded;
they drift if a fixture is edited, so trust the class and file, not the exact line.

Fixtures are intentionally vulnerable (positives) or intentionally safe (traps).
No real secrets are used: `04-hardcoded-secret` uses fake placeholders plus the
public AWS documentation example key (`AKIAIOSFODNN7EXAMPLE`).

## Positives (must be found, Confirmed)

| # | Fixture | File:line (sink) | Class | CWE | Expected tier / severity |
|---|---|---|---|---|---|
| 1 | 01-sqli | app.py:10 | SQL injection | CWE-89 | Confirmed / High-Critical |
| 2 | 02-command-injection | run.py:9 | OS command injection | CWE-78 | Confirmed / High-Critical |
| 3 | 03-idor | app.py:7-11 | IDOR / broken object level authz | CWE-639 | Confirmed / High |
| 4 | 04-hardcoded-secret | config.py:1-2 | Hardcoded credentials | CWE-798 | Confirmed / High |
| 5 | 05-ssrf | fetch.py:9 | SSRF | CWE-918 | Confirmed / High |
| 6 | 06-xss | render.js:3 | DOM XSS | CWE-79 | Confirmed / Medium-High |
| 7 | 07-deserialization | loader.py:8 | Insecure deserialization | CWE-502 | Confirmed / High-Critical |
| 8 | 08-weak-crypto | auth.py:4,7 | Weak password hash (MD5, unsalted) | CWE-327/916 | Confirmed / Medium-High |
| 9 | 09-crossfile-sqli | routes.py:9 -> store.py:5 | Cross-file SQL injection | CWE-89 | Confirmed / High-Critical |

## Traps (must NOT be flagged as Confirmed/High)

| # | Fixture | Why it is safe | Must not report |
|---|---|---|---|
| 10 | 10-safe-parameterized | Query uses `?` placeholder with a params tuple | SQL injection |
| 11 | 11-safe-authz | Ownership check `o["user_id"] != session["user_id"]` gates access | IDOR |
| 12 | 12-safe-bcrypt | `bcrypt.hashpw` with `gensalt()` | Weak crypto |

## Scoring intent

- Recall = positives found (1-9) / 9. Target: 9/9 Confirmed.
- Precision = traps correctly not flagged (10-12) / 3. Target: 3/3.
- A false Confirmed on any trap is a precision failure and is worse than a miss,
  it means the disprove/tiering logic is not working.
