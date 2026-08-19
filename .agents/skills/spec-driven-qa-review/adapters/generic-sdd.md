# Generic SDD Adapter

Use when no supported framework is detected.

## Discovery order

Search narrowly around the explicit target and project root for files whose names or headings suggest:

- Purpose / Intent / Goals
- Requirements / Spec / Specification / Acceptance Criteria
- Plan / Design / Architecture
- Tasks / TODO / Work items
- Implementation Report / Completion Report
- Test Plan / Validation / Evidence
- ADR / decision records

## Rules

1. Do not assume filename alone establishes authority.
2. Record each discovered artifact and why it is considered Purpose, Spec, Plan, etc.
3. If multiple artifacts conflict, create `contradictory-evidence` rather than choosing silently.
4. If no adequate Purpose exists, use `intent-recovery` only as a draft and request human confirmation for material decisions.
