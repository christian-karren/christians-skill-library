#!/usr/bin/env python3
"""prd-writer automation script.

Deterministic helpers for the prd-writer skill. The AI handles judgment
(discovery questions, PRD content, decisions); this script handles mechanics.

Usage:
    script.py load-template --type comprehensive|minimal   # Load a PRD template
    script.py validate-prd --input <path>                  # Run 13 quality checks
    script.py backup-prd --input <path>                    # Timestamped backup

All commands output JSON.

Derived from the PRD-generation core of `anombyte93/prd-taskmaster` (MIT).
TaskMaster integration, autonomous execution, and tracking have been removed;
this is a focused PRD writer + validator. See NOTICE for attribution.
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent
TEMPLATE_DIR = SKILL_DIR / "templates"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def emit(data: dict) -> None:
    print(json.dumps(data, indent=2, default=str))
    sys.exit(0)


def fail(message: str, **extra) -> None:
    print(json.dumps({"ok": False, "error": message, **extra}, indent=2, default=str))
    sys.exit(1)


def word_count(text: str) -> int:
    return len(text.split())


def count_requirements(text: str) -> int:
    """Count unique REQ-NNN patterns in PRD text."""
    return len(set(re.findall(r'REQ-\d{3}', text)))


def has_section(text: str, heading: str) -> bool:
    """Check if a markdown heading exists (case-insensitive)."""
    pattern = r'^#{1,3}\s+.*' + re.escape(heading) + r'.*$'
    return bool(re.search(pattern, text, re.MULTILINE | re.IGNORECASE))


def get_section_content(text: str, heading: str) -> str:
    """Extract content under a markdown heading until the next same-or-higher heading."""
    lines = text.split('\n')
    capturing = False
    level = 0
    content = []
    heading_re = re.compile(r'^(#{1,6})\s+(.*)')
    for line in lines:
        m = heading_re.match(line)
        if m and heading.lower() in m.group(2).lower():
            capturing = True
            level = len(m.group(1))
            continue
        if capturing:
            if m and len(m.group(1)) <= level:
                break
            content.append(line)
    return '\n'.join(content).strip()


# ─── Vague-language detection (for testability check) ─────────────────────────

VAGUE_WORDS = [
    "fast", "quick", "slow", "good", "bad", "poor",
    "user-friendly", "easy", "simple", "secure", "safe",
    "scalable", "flexible", "performant", "efficient",
]

VAGUE_PATTERN = re.compile(
    r'\b(?:should\s+be\s+|must\s+be\s+|needs?\s+to\s+be\s+)?'
    r'(' + '|'.join(VAGUE_WORDS) + r')\b',
    re.IGNORECASE
)


# ─── Subcommands ──────────────────────────────────────────────────────────────

def cmd_load_template(args: argparse.Namespace) -> None:
    """Load a PRD template by type."""
    template_map = {
        "comprehensive": TEMPLATE_DIR / "prd-comprehensive.md",
        "minimal": TEMPLATE_DIR / "prd-minimal.md",
    }
    tpl_path = template_map.get(args.type)
    if not tpl_path or not tpl_path.is_file():
        fail(f"Template not found: {args.type}", available=list(template_map.keys()))

    content = tpl_path.read_text()
    emit({
        "ok": True,
        "type": args.type,
        "path": str(tpl_path),
        "content": content,
        "line_count": content.count('\n') + 1,
    })


def cmd_validate_prd(args: argparse.Namespace) -> None:
    """Run 13 quality checks on a PRD file.

    9 'required' checks (5 pts each) + 4 'quality' checks (3 pts each) = 57 pts.
    A vague-language penalty (up to 5 pts) is deducted from the total.
    """
    prd_path = Path(args.input)
    if not prd_path.is_file():
        fail(f"PRD file not found: {args.input}")

    text = prd_path.read_text()
    checks = []
    warnings = []

    # ─── Required Elements (9 checks, 5 points each) ─────────────────────

    # 1: Executive summary exists (20–500 words)
    exec_summary = get_section_content(text, "Executive Summary")
    wc = word_count(exec_summary)
    checks.append({
        "id": 1, "category": "required",
        "name": "Executive summary exists",
        "passed": has_section(text, "Executive Summary") and 20 <= wc <= 500,
        "detail": f"Found {wc} words" if exec_summary else "Section missing",
        "points": 5,
    })

    # 2: Problem statement includes user impact
    problem = get_section_content(text, "Problem Statement")
    has_user_impact = bool(
        re.search(r'user\s+impact|who\s+is\s+affected|pain\s+point', problem, re.IGNORECASE)
        or has_section(text, "User Impact")
    )
    checks.append({
        "id": 2, "category": "required",
        "name": "Problem statement includes user impact",
        "passed": has_user_impact,
        "detail": "User impact found" if has_user_impact else "No user impact section",
        "points": 5,
    })

    # 3: Problem statement includes business impact
    has_biz_impact = bool(
        re.search(r'business\s+impact|revenue|cost|strategic', problem, re.IGNORECASE)
        or has_section(text, "Business Impact")
    )
    checks.append({
        "id": 3, "category": "required",
        "name": "Problem statement includes business impact",
        "passed": has_biz_impact,
        "detail": "Business impact found" if has_biz_impact else "No business impact section",
        "points": 5,
    })

    # 4: Goals have SMART metrics
    goals_section = get_section_content(text, "Goals")
    has_smart = bool(re.search(
        r'(metric|baseline|target|timeframe|measurement)', goals_section, re.IGNORECASE))
    checks.append({
        "id": 4, "category": "required",
        "name": "Goals have SMART metrics",
        "passed": has_smart,
        "detail": "SMART elements found" if has_smart else "Goals lack measurable metrics",
        "points": 5,
    })

    # 5: User stories have acceptance criteria (min 3 each)
    stories_section = get_section_content(text, "User Stories")
    story_blocks = re.split(r'###\s+Story\s+\d+', stories_section)
    ac_counts = []
    for block in story_blocks[1:]:
        ac_counts.append(len(re.findall(r'- \[[ x]\]', block)))
    stories_ok = all(c >= 3 for c in ac_counts) if ac_counts else False
    checks.append({
        "id": 5, "category": "required",
        "name": "User stories have acceptance criteria (min 3)",
        "passed": stories_ok or not ac_counts,  # pass if no stories (minimal PRD)
        "detail": f"Stories: {len(ac_counts)}, AC counts: {ac_counts}" if ac_counts else "No user stories found (may be minimal PRD)",
        "points": 5,
    })

    # 6: Functional requirements are testable (no vague language)
    reqs_section = get_section_content(text, "Functional Requirements") or get_section_content(text, "Requirements")
    vague_in_reqs = VAGUE_PATTERN.findall(reqs_section)
    checks.append({
        "id": 6, "category": "required",
        "name": "Functional requirements are testable",
        "passed": len(vague_in_reqs) == 0,
        "detail": f"Vague terms found: {vague_in_reqs}" if vague_in_reqs else "All requirements are specific",
        "points": 5,
    })

    # 7: Requirements have priority labels
    has_priority = bool(re.search(
        r'(must\s+have|should\s+have|could\s+have|nice\s+to\s+have|P0|P1|P2)',
        reqs_section, re.IGNORECASE))
    checks.append({
        "id": 7, "category": "required",
        "name": "Requirements have priority labels",
        "passed": has_priority,
        "detail": "Priority labels found" if has_priority else "No priority classification found",
        "points": 5,
    })

    # 8: Requirements numbered (REQ-NNN)
    req_count = count_requirements(text)
    checks.append({
        "id": 8, "category": "required",
        "name": "Requirements are numbered (REQ-NNN)",
        "passed": req_count > 0,
        "detail": f"Found {req_count} numbered requirements" if req_count else "No REQ-NNN numbering found",
        "points": 5,
    })

    # 9: Technical considerations address architecture
    tech_section = get_section_content(text, "Technical")
    has_arch = bool(re.search(
        r'(architecture|system\s+design|component|integration|diagram)',
        tech_section, re.IGNORECASE))
    checks.append({
        "id": 9, "category": "required",
        "name": "Technical considerations address architecture",
        "passed": has_arch,
        "detail": "Architecture content found" if has_arch else "No architectural detail found",
        "points": 5,
    })

    # ─── Quality checks (4 checks, 3 points each) ────────────────────────

    # 10: Non-functional requirements have specific targets
    nfr_section = get_section_content(text, "Non-Functional")
    has_nfr_targets = bool(re.search(
        r'\d+\s*(ms|seconds?|minutes?|%|MB|GB|requests?/s)', nfr_section, re.IGNORECASE))
    checks.append({
        "id": 10, "category": "quality",
        "name": "Non-functional requirements have specific targets",
        "passed": has_nfr_targets or not nfr_section,
        "detail": "Specific targets found" if has_nfr_targets else "No measurable NFR targets",
        "points": 3,
    })

    # 11: Requirements have task breakdown hints
    has_task_hints = bool(re.search(
        r'task\s+breakdown|implementation\s+step|~\d+h', text, re.IGNORECASE))
    checks.append({
        "id": 11, "category": "quality",
        "name": "Requirements have task breakdown hints",
        "passed": has_task_hints,
        "detail": "Task breakdown hints found" if has_task_hints else "No task breakdown hints",
        "points": 3,
    })

    # 12: Dependencies identified
    has_deps = bool(re.search(
        r'(dependenc|depends\s+on|blocked\s+by|prerequisite)', text, re.IGNORECASE))
    checks.append({
        "id": 12, "category": "quality",
        "name": "Dependencies identified for sequencing",
        "passed": has_deps,
        "detail": "Dependencies documented" if has_deps else "No dependency information found",
        "points": 3,
    })

    # 13: Out of scope defined
    has_oos = has_section(text, "Out of Scope")
    oos_content = get_section_content(text, "Out of Scope")
    checks.append({
        "id": 13, "category": "quality",
        "name": "Out of scope explicitly defined",
        "passed": has_oos and len(oos_content.strip()) > 10,
        "detail": "Out of scope section found" if has_oos else "No Out of Scope section",
        "points": 3,
    })

    # ─── Vague-language warnings + penalty ───────────────────────────────
    all_vague = VAGUE_PATTERN.findall(text)
    vague_penalty = min(len(all_vague), 5)
    for match in set(all_vague):
        warnings.append({
            "type": "vague_language",
            "term": match,
            "suggestion": f"Replace '{match}' with a specific, measurable target",
        })

    if not has_section(text, "Validation Checkpoint"):
        warnings.append({
            "type": "missing_detail",
            "item": "Validation checkpoints",
            "suggestion": "Add validation checkpoints for each implementation phase",
        })

    # ─── Scoring ─────────────────────────────────────────────────────────
    score = sum(c["points"] for c in checks if c["passed"]) - vague_penalty
    score = max(0, score)
    max_score = sum(c["points"] for c in checks)
    pct = (score / max_score * 100) if max_score else 0
    if pct >= 91:
        grade = "EXCELLENT"
    elif pct >= 83:
        grade = "GOOD"
    elif pct >= 75:
        grade = "ACCEPTABLE"
    else:
        grade = "NEEDS_WORK"

    emit({
        "ok": True,
        "score": score,
        "max_score": max_score,
        "percentage": round(pct, 1),
        "grade": grade,
        "checks_passed": sum(1 for c in checks if c["passed"]),
        "checks_total": len(checks),
        "checks": checks,
        "warnings": warnings,
        "vague_penalty": vague_penalty,
    })


def cmd_backup_prd(args: argparse.Namespace) -> None:
    """Create a timestamped backup of a PRD before overwriting it."""
    src = Path(args.input)
    if not src.is_file():
        fail(f"PRD file not found: {args.input}")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = src.parent / f"prd-backup-{ts}.md"
    shutil.copy2(str(src), str(backup_path))
    emit({"ok": True, "original": str(src), "backup_path": str(backup_path), "timestamp": ts})


# ─── Argument parsing ─────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prd-writer",
        description="prd-writer: deterministic helpers for PRD generation and validation.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("load-template", help="Load a PRD template")
    p.add_argument("--type", required=True, choices=["comprehensive", "minimal"])

    p = sub.add_parser("validate-prd", help="Run 13 quality checks on a PRD")
    p.add_argument("--input", required=True, help="Path to PRD file")

    p = sub.add_parser("backup-prd", help="Timestamped PRD backup")
    p.add_argument("--input", required=True, help="Path to PRD file")

    return parser


DISPATCH = {
    "load-template": cmd_load_template,
    "validate-prd": cmd_validate_prd,
    "backup-prd": cmd_backup_prd,
}


def main():
    args = build_parser().parse_args()
    DISPATCH[args.command](args)


if __name__ == "__main__":
    main()
