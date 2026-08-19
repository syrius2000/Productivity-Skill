---
id: QA-XXXX
title: "REQUIRED:HUMAN-INPUT:CASE-TITLE"
document_type: spec-driven-qa-review
status: draft
result: null
qa_profile: standard
risk_level: medium
current_cycle: 0
created_at: "REQUIRED:SYSTEM-TIMESTAMP"
updated_at: "REQUIRED:SYSTEM-TIMESTAMP"
subject:
  targets:
    - "REQUIRED:HUMAN-INPUT:TARGET"
  implementation_revision: "REQUIRED:SYSTEM-REVISION"
baseline:
  purpose: []
  spec: []
  plan: []
  tasks: []
participants:
  implementer:
    agent_id: "REQUIRED:HUMAN-INPUT:IMPLEMENTER-AGENT"
    role: implementer
    tool: null
  reviewer:
    agent_id: "REQUIRED:HUMAN-INPUT:REVIEWER-AGENT"
    role: reviewer
    tool: null
review_independence:
  blind_phase: true
  inputs_excluded:
    - implementation_chat_history
    - author_self_review
finding_summary:
  critical: {open: 0, resolved: 0}
  high: {open: 0, resolved: 0}
  medium: {open: 0, resolved: 0}
  low: {open: 0, resolved: 0}
---

# QA Pulse

| Item | Current |
|---|---|
| Status | `draft` |
| Cycle | 0 / 3 |
| Implementation revision | `REQUIRED:SYSTEM-REVISION` |
| Critical open | 0 |
| High open | 0 |
| Medium open | 0 |
| Next actor | `reviewer` |
| Next action | Independent review |
| Updated | `REQUIRED:SYSTEM-TIMESTAMP` |

## 1. Purpose and Review Objective

<!-- REQUIRED:REVIEWER:QA-PURPOSE
Summarize the Purpose being evaluated and what this QA case must determine.
-->

## 2. Scope

### Primary targets

- `REQUIRED:HUMAN-INPUT:TARGET`

### Referenced-only artifacts

- TBD

### Explicitly outside scope

- TBD

## 3. Baseline

Record Purpose, Spec, Plan, Task, Implementation and Evidence revisions/hashes used for this review.

## 4. Current Assessment

- Overall: `not-assessable`
- Main uncertainty: baseline not yet reviewed.

## 5. Open Material Findings

See `findings.yaml`.

## 6. Traceability Summary

See `traceability.yaml`.

## 7. Residual Risks

- TBD

## 8. Latest Events

| Timestamp | Cycle | Actor | Action | Result |
|---|---:|---|---|---|

## 9. Next Required Action

`REQUIRED:REVIEWER:INITIAL-REVIEW`
