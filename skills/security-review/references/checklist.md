# Vulnerability checklist

The full taxonomy the review audits against, expanded from Step 3 of SKILL.md.
Load this when you need the complete list or the per-class hints. Ordered by how
often each class causes real incidents in application code, not by theory.

## 1. Broken access control (highest priority - scanners miss these)
- IDOR / BOLA: an object is fetched by an id from the request with no check that
  the caller owns or may access it. CWE-639.
- Missing function-level authorization: an admin-only action reachable by a normal
  user (no role check). CWE-285.
- Mass assignment: a request body bound straight to a model, letting the caller set
  fields like `role`, `is_admin`, `price`. CWE-915.
- Excessive data exposure: an endpoint returns more fields than the caller should
  see (internal ids, PII, other users' data). CWE-213.

## 2. Injection
- SQL / NoSQL built by string concatenation or f-strings instead of parameters. CWE-89/943.
- OS command execution with user input (`os.system`, `subprocess(..., shell=True)`,
  `child_process.exec`, backticks). CWE-78.
- Template injection (SSTI), LDAP, XPath, header injection. CWE-1336/90/643.
- Path traversal in file reads/writes (`../`, absolute paths from user input). CWE-22.

## 3. Authentication and session
- A new route or handler with no auth middleware / dependency. CWE-306.
- Weak or absent token verification: JWT `alg:none`, unverified signature,
  secret compared non-constant-time, tokens logged. CWE-347/208.
- Fixed, guessable, or non-rotating session identifiers. CWE-384.

## 4. SSRF and outbound requests
- Server fetches a URL derived from user input with no allowlist. CWE-918.
- Reachability of cloud metadata (169.254.169.254) or internal hosts from that fetch.

## 5. Secrets and sensitive data
- Hardcoded API keys, tokens, passwords, private keys in source. CWE-798.
- Secrets written to logs, returned in responses, or embedded in error bodies. CWE-532.
- Secrets committed to git history (even if later removed).

## 6. Cryptography and randomness
- Weak or fast hash for passwords (MD5/SHA1), missing salt. CWE-327/916.
- Home-rolled crypto; ECB mode; static IV/key.
- Predictable randomness (`Math.random`, `rand()`) for tokens, ids, or resets. CWE-338.

## 7. Deserialization and parsing
- Untrusted input into `pickle`, `yaml.load` (non-safe), native deserializers,
  or XML with external entities enabled (XXE). CWE-502/611.

## 8. Web output and configuration
- XSS: unescaped user input into HTML, `dangerouslySetInnerHTML`, `innerHTML`,
  `document.write`. Reflected, stored, and DOM-based. CWE-79.
- CORS reflecting an arbitrary origin with credentials. CWE-942.
- CSRF protection missing on state-changing routes. CWE-352.
- Debug mode, verbose stack traces, or misconfig shipped enabled. CWE-489/209.
- Missing security headers (CSP, HSTS, X-Content-Type-Options).

## 9. Supply chain and IaC
- New dependency that is unpinned, unmaintained, or typosquat-shaped. CWE-1104/427.
- Dockerfile / k8s / terraform / CI-workflow misconfig (root user, `:latest`,
  world-open security groups, over-scoped workflow tokens). CWE-250/732.

## 10. AI / LLM (when the code builds prompts or calls an LLM)
- Prompt injection: untrusted content concatenated into a prompt or tool call.
- Insecure output handling: LLM output used in a sink (SQL, shell, HTML) unchecked.
- Excessive agency: the model can call tools or reach data beyond the task's need.

## Using this list
In the missing-control audit (Pass D), for each reachable entry point ask "is the
control for this class present on this path?" A missing control on a reachable path
is a finding even when no scanner flagged it. Map each finding to its CWE in the
report where it helps the developer.
