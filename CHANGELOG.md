# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-04

### Added
- `security-review` skill: three-layer review (deterministic scanners, cross-file
  taint reasoning, missing-control audit) that is high-recall and token-light,
  reports findings by confidence tier (Confirmed / Likely / Needs-verification),
  and prints a coverage ledger.
- Quick and deep modes; quick mode auto-escalates to a deep component review when
  the diff touches auth, access control, or a data boundary. Non-git targets fall
  back to reviewing a path or the whole tree.
- Recall and precision eval suite: 12 functional evals (9 planted-CWE positives,
  3 safe traps, 1 cross-file taint test), a triggering set, and a ground-truth key.
- Progressive-disclosure reference files: `references/checklist.md` (full CWE-mapped
  taxonomy) and `references/scanners.md` (scanner cheatsheet).
- Brand assets (theme-aware wordmark, monogram), plugin and marketplace manifests,
  CI (manifest/frontmatter validation and a self-dogfood security review), and
  community docs (contributing, security policy, code of conduct, templates).

[Unreleased]: https://github.com/kalpmodi/akira-lite/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kalpmodi/akira-lite/releases/tag/v0.1.0
