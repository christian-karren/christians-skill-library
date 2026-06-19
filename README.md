# Christian's Skill Library

A personal library of portable agent **skills** — self-contained tools that drop into Claude Code,
Codex, or any agent that reads `SKILL.md`. Each skill folder is independent: copy the one you want,
or the whole library.

## Skills

| Skill | What it does |
|-------|--------------|
| [`code-review-and-quality`](code-review-and-quality/) | Reviews code across correctness, readability, architecture, security, and performance quality gates. |
| [`prd-writer`](prd-writer/) | Writes high-quality, engineer-ready PRDs and grades them against 13 automated quality checks (EXCELLENT/GOOD/ACCEPTABLE/NEEDS_WORK). Pure document generation — no task runners, no external services. |
| [`refactor`](refactor/) | Guides surgical refactoring that improves maintainability without changing external behavior. |
| [`verification-before-completion`](verification-before-completion/) | Requires fresh verification evidence before claiming work is complete, fixed, or passing. |
| [`writing-prompts`](writing-prompts/) | Turns vague requests into precise PACE prompts, with plan-first execution for multi-step or fragile work. |

_More coming._

## Using a skill

**Claude Code / SKILL.md agents:** copy a skill folder into your skills directory
(e.g. `~/.claude/skills/<skill>/`). It becomes invokable as `/<skill>`.

**Codex / other agents:** point the agent at the skill folder, or copy it into your skill set.
Skills are self-contained; the only runtime requirement is Python 3 (for skills that ship a script).

## License & attribution

This library is MIT-licensed (see [LICENSE](LICENSE)). Individual skills that are derived from
or adapted from other open-source work carry their own `LICENSE`/`NOTICE` files crediting the
original authors — see each skill folder.
