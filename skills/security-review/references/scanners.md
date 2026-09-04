# Scanner cheatsheet

The deterministic layer: exact commands, install one-liners, and what each tool
covers. Loaded on demand from Step 0 and Pass B of SKILL.md. Scanners are
subprocesses and cost zero model tokens, so let them find what they can and spend
model reasoning only on what they cannot.

## Layers and tools

| Layer | Tool (pick one) | Covers |
|---|---|---|
| SAST | semgrep | injection, XSS, deserialization, taint patterns |
| Secrets | gitleaks or trufflehog | hardcoded keys, tokens, credentials |
| Dependencies | osv-scanner, `npm audit`, or pip-audit | known-CVE dependencies |
| IaC / config | trivy or checkov | Docker/k8s/terraform/CI misconfig, secrets |

If a layer has no working tool, it is degraded: say so in the ledger and, at the
end, give the install one-liner and note that re-running gives full coverage.

## Install one-liners (offer, never auto-install)

```
pipx install semgrep pip-audit checkov
brew install gitleaks trufflehog osv-scanner trivy
```

For a tool that is present but BROKEN (smoke test fails), recommend a reinstall,
e.g. `pipx reinstall semgrep`.

## Commands

Scope to changed files in quick mode, to the path/repo in deep mode. Run them in
parallel (background jobs) and keep every raw hit; deduplicate later, do not drop.

```bash
# SAST
semgrep --config auto --json --quiet <scope>

# Secrets (filesystem, no git needed)
gitleaks dir <scope> --report-format json --report-path gl.json --redact --no-banner
trufflehog filesystem <scope> --only-verified --no-update --json

# Dependencies
osv-scanner scan <scope>
npm audit --json           # if a package-lock.json is present
pip-audit                  # if a requirements.txt / poetry.lock is present

# IaC / config (trivy config is local, no DB download)
trivy config --quiet --severity HIGH,CRITICAL <scope>
checkov -d <scope> --quiet
```

## Parsing notes
- semgrep `--config auto` needs network the first run to fetch rules; if it errors,
  mark SAST degraded rather than reporting clean.
- gitleaks writes an empty report file when there are zero findings; read the JSON,
  do not infer from exit code alone.
- trufflehog `--only-verified` cuts noise to secrets it could validate; drop the
  flag for a broader (noisier) sweep.
- Deduplicate scanner hits against the taint (Pass C) and missing-control (Pass D)
  findings by file:line + class before tiering.
