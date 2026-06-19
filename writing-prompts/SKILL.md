---
name: writing-prompts
description: >-
  Structures vague requests into precise prompts using the PACE method (Purpose, Audience,
  Constraints, Examples) plus plan-first execution. Use proactively whenever the user is about
  to hand off a non-trivial task: coding work, writing assignments, multi-step requests,
  sub-agent prompts, skill authoring, or any task where the output could miss the mark. Also
  use when a user's prompt is vague, lacks success criteria, or risks wrong assumptions.
---

# Writing Prompts

## Core Principle

Most "the model got it wrong" moments are briefing failures, not model failures. The model guessed because the work order was unclear. The fix is usually a sharper brief.

## PACE

Build the minimum viable brief:

- **Purpose**: State the desired outcome in one sentence. Define what success looks like.
- **Audience**: Name who the output is for and what they already know or need.
- **Constraints**: List limits, rules, tone, length, required sources, tools, exclusions, and things to avoid.
- **Examples**: Include one or two concrete samples when format, voice, or style matters.

## Workflow

1. Convert the user's rough request into a PACE brief.
2. Call out missing information, risky assumptions, and success criteria.
3. For multi-step or fragile work, ask for or propose a plan before producing the deliverable.
4. Let the user edit the plan, constraints, or assumptions.
5. Produce the final prompt, draft, code handoff, sub-agent instruction, or skill brief only after the plan is accepted or the assumptions are safe.

## Match Specificity To Fragility

- **High freedom**: Many valid paths exist. Give general direction and a clear outcome.
- **Low freedom**: Exact sequence, format, or behavior matters. Give specific instructions, constraints, and verification steps.

## Few-Shot Guidance

When consistency matters, include two or three input/output pairs. Keep examples short, realistic, and structurally similar to the target output.

## When The Tool Cannot Know

Change the workflow instead of guessing:

- Pull or inspect the data directly when accuracy depends on external or project-specific facts.
- Use code or deterministic tools for exact correctness.
- Run a second pass, validator, reviewer, or test suite for high-stakes outputs.

## Anti-Patterns

- "Just fix this" with no context.
- No examples for stylistic or format-sensitive work.
- Asking for the deliverable before agreeing on the plan.
- Vague success criteria.

## Quick Checklist

- Purpose stated in one sentence.
- Audience identified.
- Constraints listed.
- Examples provided when format or style matters.
- Plan-first sequence used for multi-step work.
- Success criteria defined when stakes are high.
