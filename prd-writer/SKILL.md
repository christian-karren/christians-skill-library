---
name: prd-writer
description: >-
  Writes high-quality, engineer-ready Product Requirements Documents. Runs a short discovery
  pass, fills a proven PRD template, and validates the result against 13 automated quality
  checks (graded EXCELLENT/GOOD/ACCEPTABLE/NEEDS_WORK). Use when the user asks for a "PRD",
  "product requirements", "spec a feature", or "write requirements". Pure document generation —
  no task runners, no autonomous execution, no external services required.
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
  - AskUserQuestion
---

# prd-writer

Turns a product idea into a comprehensive, validated PRD. The model supplies judgment
(questions, content, decisions); the bundled `script.py` supplies mechanics (template
loading, validation, backups). No installation or external tools required — only Python 3.

**Script:** `script.py` (next to this file). All commands print JSON.

---

## Workflow (6 steps)

### Step 1 — Locate the target & check for an existing PRD
Decide where the PRD should live. Default to `./prd.md`, or `docs/prd.md` if the project keeps
docs in a `docs/` folder. Use Glob to check whether a PRD already exists there.

If one exists, ask the user (AskUserQuestion) whether to:
- **Update/refine** it (back it up first — Step 5b — then edit and re-validate), or
- **Replace** it (back it up first, then start fresh), or
- **Review only** (validate the existing file and report the grade, then stop).

If none exists, continue.

### Step 2 — Discovery
Gather what the PRD needs. Prefer AskUserQuestion for structured input; skip anything the user
has already supplied in the conversation. Use smart defaults for anything minor and **record the
assumptions** in the PRD rather than blocking.

Essential:
1. What problem does this solve? (user pain + business/impact angle)
2. Who is the target user/audience?
3. What is the proposed solution?
4. What does success look like? (measurable metric, baseline → target → timeframe)
5. Constraints (technical, legal, timeline, resources)

Technical:
6. Greenfield or existing codebase?
7. Tech stack / platform?
8. Integrations & external dependencies?
9. Performance / scale expectations?

Scope:
10. Explicit non-goals / out of scope?
11. Complexity: simple / typical / complex?
12. Anything else — edge cases, risks, prior art?

If the task is non-trivial, **propose a brief outline + your assumptions first** and let the user
correct them before drafting (plan-first).

### Step 3 — Load a template
```bash
python3 <skill-dir>/script.py load-template --type comprehensive   # default
python3 <skill-dir>/script.py load-template --type minimal         # small/simple features
```
Returns JSON with a `content` field holding the template.

### Step 4 — Generate the PRD
Fill the template with the discovery answers. Replace every placeholder; expand examples with
project-specific detail; add real technical depth. Each functional requirement should be
**numbered `REQ-NNN`**, carry a **priority** (P0/P1/P2 or Must/Should/Could), **acceptance
criteria**, a **task-breakdown hint** (with rough `~Xh` estimates), and **dependencies**.
Write the completed PRD to the target path.

Writing rules that keep the grade high:
- Quantify goals (not "improve UX" → "cut median capture time from 8s to <1s").
- Avoid vague adjectives in requirements (fast, easy, secure, scalable, simple, safe…) — the
  validator penalizes them. State a measurable target instead.
- Include a **Non-Functional Requirements** section with concrete numbers (ms, %, MB, req/s).
- Include **Out of Scope**, **Dependencies**, and **Validation Checkpoints** sections.

### Step 5 — Validate & iterate
```bash
python3 <skill-dir>/script.py validate-prd --input <path-to-prd>
```
Returns `score`, `max_score`, `percentage`, `grade`, the 13 `checks`, and `warnings`.
Grades: EXCELLENT ≥ 91% · GOOD ≥ 83% · ACCEPTABLE ≥ 75% · NEEDS_WORK < 75%.

Fix any failed check and any vague-language warnings, then re-validate. Aim for **GOOD or
EXCELLENT** before finishing. Report the final grade to the user.

**Step 5b — Backup (only when overwriting an existing PRD):**
```bash
python3 <skill-dir>/script.py backup-prd --input <path-to-prd>
```

### Step 6 — Hand off
Report the PRD location and final grade. Summarize the key requirements and any open questions
or assumptions you recorded. Stop — this skill does not break the PRD into tasks or implement it.

---

## The 13 quality checks

**Required (5 pts each):** executive summary · user impact · business impact · SMART goals ·
user-story acceptance criteria · testable (non-vague) requirements · priority labels ·
`REQ-NNN` numbering · architecture detail.

**Quality (3 pts each):** measurable non-functional targets · task-breakdown hints ·
dependencies identified · out-of-scope defined.

A vague-language penalty (up to −5) is deducted for adjectives without measurable targets.

---

## Notes
- Self-contained: the templates and validator live in this skill folder; nothing else is needed.
- Portable: copy this folder into any skill library or agent that reads `SKILL.md`.
- Derived from the PRD core of `anombyte93/prd-taskmaster` (MIT) with TaskMaster integration
  removed. See `NOTICE` for attribution.
