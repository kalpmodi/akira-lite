# Contributing

akira<sup>LITE</sup> is one skill file: `skills/security-review/SKILL.md`. Keep changes small
and tested.

## Making a change

1. Fork and branch.
2. Edit `skills/security-review/SKILL.md`.
3. Install your copy and run it against real code:
   ```
   cp -r skills/security-review ~/.claude/skills/
   /security-review
   ```
4. In the PR, describe the before/after behavior you saw on real code.

## Guidelines

- Keep it lean. The skill loads into context on every run, so brevity is a feature.
  Prefer sharpening an existing step over adding a new one.
- One skill only. Broader tooling belongs in [akira](https://github.com/kalpmodi/akira),
  the full professional-grade VAPT platform this project is derived from.
- Match the format. Findings stay tiered (Confirmed / Likely / Needs-verification)
  with `file:line` and a fix.
- No new required dependencies. Scanners are optional and detected at runtime.

## Security issues

Do not open a public issue or PR for a vulnerability in the skill itself. See
[SECURITY.md](SECURITY.md).
