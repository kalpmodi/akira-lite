# akira-review evals

Measures whether the skill actually finds real vulnerabilities (recall) without
flagging safe code (precision). Format follows Anthropic's skill-creator
`evals.json` schema, so it runs under skill-creator benchmark mode as-is.

> Warning: `files/` contains intentionally vulnerable code for testing only.
> Never deploy it, and exclude `evals/files/` from the repo's own security
> scanning so these fixtures do not appear as real findings.

## Layout

```
evals/
  evals.json        # 12 functional evals: prompts + graded expectations (skill-creator schema)
  triggering.json   # 11 trigger checks: {query, should_trigger} for the trigger harness
  GROUND_TRUTH.md   # maintainer answer key (CWE, file, expected tier); line numbers advisory
  files/            # fixtures: 01-09 positives, 10-12 safe traps (no hint comments)
```

The fixtures deliberately carry no answer-leaking comments. If a fixture said
`# SQL injection here`, the skill would trigger on the comment, not the code, and
the eval would prove nothing.

## What is measured

- Recall: positives 01-09 each plant one known CWE. Target 9/9 reported as Confirmed.
- Precision: traps 10-12 are safe but tempting (parameterized query, ownership
  check, bcrypt). Target 3/3 not flagged. A false Confirmed on a trap is worse
  than a miss, it means the disprove/tiering logic failed.
- Cross-file taint: eval 09 splits source and sink across two files; it passes
  only if the finding traces routes.py into store.py.
- Value over baseline: run each eval with and without the skill. The behavior
  expectations (coverage ledger, confidence tiers) should pass with the skill and
  fail without it, that delta is the skill's value.

## Running

Benchmark mode (recommended, gives baseline delta and variance):

```
# with skill-creator installed; runs with_skill vs without_skill, N runs each
run the skill-creator benchmark against skills/akira-review using evals/evals.json
```

Trigger rate (separate harness): `triggering.json` is in the trigger-eval format
(`{query, should_trigger}`) and measures whether the skill's description fires on
realistic prompts and stays quiet on unrelated ones. Run it with skill-creator's
`run_eval.py --eval-set evals/triggering.json --skill-path .`. This, not the
functional prompts below, is what measures trigger rate (the functional prompts
say "security review" and would trigger 100% by construction).

Manual protocol (no tooling):

1. For each eval, start a clean Claude Code session and `cd` into this skill's
   directory (`skills/akira-review/`) so the `evals/files/...` paths in the
   prompts resolve.
2. Paste the eval `prompt`. It points at the fixture under `evals/files/`.
3. Score each `expectations[]` statement pass/fail against the output.
4. Record: recall (positives Confirmed / 9), precision (traps clean / 3), and
   tool-call count per run.
5. Repeat 3x per eval; report mean and note any eval with high variance.

## Pass criteria

| Metric | Target |
|---|---|
| Recall (positives Confirmed) | 9 / 9 |
| Precision (traps not flagged) | 3 / 3 |
| Cross-file trace (eval 09) | pass |
| Trigger rate (triggering.json) | >= 90% of should-fire prompts trigger; should-not prompts stay quiet |
| Beats no-skill baseline on ledger/tier expectations | yes |

Add a new eval whenever the skill misses a real bug in the wild or false-flags
safe code: reproduce it as a minimal fixture here first, then fix the skill until
the eval passes. That keeps recall from regressing.
