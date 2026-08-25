<div align="center">

# akira-lite

One skill. Security-review your own code before you push.

</div>

akira-lite is the developer edition of akira. Where akira is a full autonomous
offensive agent, akira-lite ships a single, focused skill any developer can use:
`/security-review`. It reviews the code you just wrote, finds real exploitable
bugs, filters out the noise, and hands you the fix.

## What it does

- Reviews your current git diff by default (fast, cheap, relevant to the change).
- Focuses on the bug classes developers actually introduce: broken access control
  and IDOR, injection, auth gaps, SSRF, leaked secrets, weak crypto, XSS, unsafe
  deserialization, and risky dependencies.
- Verifies every finding before reporting it. If it cannot describe a concrete
  exploit, it does not call it Critical.
- Returns a prioritized report: severity, file:line, exploit scenario, and a fix.
- Optional fix mode applies the change surgically when you ask.

It is defensive. It complements SAST and dependency scanners by catching the
authorization and logic flaws those tools miss.

## Install

Option A, plugin marketplace (recommended):

```
/plugin marketplace add kalpmodi/akira-lite
/plugin install akira-lite@akira-lite
```

Option B, drop-in skill (works in Claude Code, and any agent that reads `./skills`):

```bash
git clone https://github.com/kalpmodi/akira-lite.git
cp -r akira-lite/skills/security-review ~/.claude/skills/
```

## Use

In your project, when you have changes staged or on a branch:

```
/security-review
```

Or in plain language:

- "security review my changes before I push"
- "is this safe to merge?"
- "review src/api/ for security issues"

Then, if you want the fixes applied:

- "fix the critical one"

## Why akira-lite

- Best-of-the-best, kept small: one skill, no setup, no external services.
- Signal over noise: it disproves its own findings before reporting them.
- Shift-left: it runs on the diff, in the developer's own loop, before merge.

## License

MIT. See [LICENSE](LICENSE).
