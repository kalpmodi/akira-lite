---
name: Bug report
about: The akira-review skill behaved incorrectly (missed a bug, false-flagged safe code, or errored)
title: ""
labels: bug
assignees: ""
---

## What happened
A clear description of the incorrect behavior.

## Category
- [ ] Missed a real vulnerability (false negative)
- [ ] Flagged safe code (false positive)
- [ ] Wrong severity or confidence tier
- [ ] Crash / error / did not run
- [ ] Other

## Minimal repro
The smallest code or diff that reproduces it. If you can, paste it as a snippet so
it could become an eval fixture under `skills/akira-review/evals/`.

## Expected vs actual
- Expected:
- Actual:

## Environment
- Which scanners were installed (from the coverage ledger, if shown):
- Quick or deep mode:
