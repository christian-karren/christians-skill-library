# prd-writer

A self-contained agent **skill** that writes high-quality, engineer-ready Product Requirements
Documents and validates them against 13 automated quality checks. No task runners, no autonomous
execution, no external services — just a great PRD.

## What it does

1. **Discovery** — a short structured Q&A (plan-first for non-trivial work).
2. **Template** — fills a proven comprehensive or minimal PRD template.
3. **Validate** — grades the result (EXCELLENT / GOOD / ACCEPTABLE / NEEDS_WORK) and lists
   exactly what to fix, then iterates to a high grade.

## Contents

```
prd-writer/
├── SKILL.md                  # the skill instructions an agent follows
├── script.py                 # load-template · validate-prd · backup-prd (Python 3, no deps)
├── templates/
│   ├── prd-comprehensive.md  # full PRD template
│   └── prd-minimal.md        # lightweight PRD template
├── LICENSE                   # MIT
├── NOTICE                    # attribution to the upstream project
└── README.md
```

## Install

**Claude Code / agents that read `SKILL.md`:** drop this folder into your skills directory
(e.g. `~/.claude/skills/prd-writer/`). It is then invokable as `/prd-writer`.

**Codex / other agents:** point the agent at this folder, or copy it into your skill library.
The skill is fully self-contained; the only runtime requirement is Python 3.

## Use the script directly

```bash
python3 script.py load-template --type comprehensive
python3 script.py validate-prd --input path/to/prd.md
python3 script.py backup-prd  --input path/to/prd.md
```
All commands print JSON.

## The 13 checks

**Required (5 pts):** executive summary · user impact · business impact · SMART goals ·
story acceptance criteria · testable requirements · priority labels · `REQ-NNN` numbering ·
architecture detail.
**Quality (3 pts):** measurable non-functional targets · task-breakdown hints · dependencies ·
out-of-scope. A vague-language penalty (−5 max) discourages adjectives without measurable targets.

## License & attribution

MIT — see [LICENSE](LICENSE). Derived from the PRD core of
[`anombyte93/prd-taskmaster`](https://github.com/anombyte93/prd-taskmaster) (MIT), with the
TaskMaster integration and autonomous execution removed. See [NOTICE](NOTICE) for details.
