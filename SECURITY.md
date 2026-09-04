# Security Policy

akira<sup>LITE</sup> is a single Claude skill (`/security-review`) that reviews source code
for vulnerabilities. This document covers how to run it safely and how to report a
security issue in akira<sup>LITE</sup> itself.

## What akira<sup>LITE</sup> is (and is not)

- It is defensive. It reviews your own code before you ship it. It is not a pentest
  of a live target and it does not attack anything.
- It reads code and runs local scanners (semgrep, gitleaks, trufflehog, trivy, etc.)
  as subprocesses on your machine. It does not send your code to any third party
  beyond the model you are already using as your agent.
- It reports findings. It does not change your code, install packages, or apply
  fixes unless you explicitly ask it to.

## Safe use

- Review trusted code only. Like any LLM-driven review tool, akira<sup>LITE</sup> is not
  hardened against prompt injection. Source files (or a malicious PR) can contain
  text crafted to manipulate the model. Do not run it on untrusted code you would
  not otherwise open and read.
- Treat findings as leads, not verdicts. `Confirmed` findings include a
  source-to-sink path; still confirm before acting. `Likely` and
  `Needs-verification` findings require you to check the stated condition.
- Recall depends on the layers that ran. A missing or broken scanner is reported in
  the coverage ledger as a degraded layer. Install the recommended tool and re-run
  for full coverage before trusting a "clean" result.
- Do not paste secrets. The skill scans for secrets in your code; it does not need
  you to provide real credentials.

## Reporting a vulnerability in akira<sup>LITE</sup>

If you find a security issue in the skill itself (for example, a prompt-injection
bypass that suppresses findings, or unsafe command construction in the skill's
instructions):

1. Do not open a public issue.
2. Use GitHub private vulnerability reporting: the "Report a vulnerability" button
   under the Security tab of this repository
   (https://github.com/kalpmodi/akira-lite/security/advisories/new).
3. Include the skill version (commit), what you did, and the impact.

You can expect an initial response within a few days. Confirmed issues will be
fixed on the default branch and noted in the commit history.

## Scope

- In scope: the skill instructions (`skills/security-review/SKILL.md`), the plugin
  manifests, and anything that changes what the review does or reports.
- Out of scope: vulnerabilities in the third-party scanners themselves (report
  those upstream), and findings the skill produces about your code (those are
  output, not a vulnerability in akira<sup>LITE</sup>).
