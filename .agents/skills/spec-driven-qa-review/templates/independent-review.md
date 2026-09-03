---
case_id: QA-XXXX
cycle: 1
action: independent-review
performed_by:
  agent_id: "REQUIRED:HUMAN-INPUT:REVIEWER-AGENT"
  role: reviewer
  tool: null
started_at: "REQUIRED:SYSTEM-TIMESTAMP"
completed_at: "REQUIRED:SYSTEM-TIMESTAMP"
input_revision: "REQUIRED:SYSTEM-REVISION"
blind_first: true
outcome: findings-issued
---

# Independent Review — Cycle 1

## Inputs actually reviewed

### Included
- Purpose
- Spec
- Plan / Tasks
- target implementation
- tests/evidence

### Excluded during blind phase
- author self-review
- implementation chat history

## Observed implementation intent

<!-- REQUIRED:REVIEWER:OBSERVED-INTENT
Describe observed behavior/architecture independently of the author's self-explanation.
-->

## Purpose / Spec / Plan / Implementation / Evidence comparison

Summarize material alignments and gaps.

## Findings issued

Reference IDs from `findings.yaml`.

## Reviewer limitations

State scope limitations, evidence limitations, and anything not safely verifiable.
