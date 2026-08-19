# Agent Separation

## Goal

Reduce correlated self-review and post-hoc rationalization. Separation does not make the review independent in a statistical sense, but it creates a stronger procedure than self-review.

## Preferred separation

Strongest practical pattern:

- AI-1 implementer in one tool/context/workspace
- AI-2 reviewer in another tool/context/workspace
- optional AI-3 or human adjudicator for disputed/high-risk findings

Examples include Codex vs Cursor or other materially separated agent environments.

## Blind-first review

Before issuing first findings, AI-2 should receive:

### Include
- Purpose
- Spec
- Plan / Tasks
- target implementation
- tests
- existing relevant ADRs
- required environment/config contracts

### Exclude when practical
- AI-1 self-review
- AI-1 implementation chat transcript
- AI-1 explanation of why its code is correct
- prior author responses

After the initial independent review is frozen, reveal author claims for reconciliation.

## Metadata

Record:

```yaml
review_independence:
  blind_phase: true
  implementer_agent_id: codex-implementer
  reviewer_agent_id: cursor-reviewer
  inputs_excluded:
    - implementation_chat_history
    - author_self_review
```

## Conflict rule

If implementer and reviewer IDs are identical where policy requires separation, validation should fail or produce a policy error.
