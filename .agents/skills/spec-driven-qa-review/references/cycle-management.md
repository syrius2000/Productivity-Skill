# Cycle Management

## Default maximum

`max_automated_cycles: 3`

Beyond three unresolved automated cycles, switch to `adjudication-required`. More AI discussion often adds prose rather than evidence.

## Cycle records

Each cycle record is historical and should not be overwritten.

Recommended sequence:

```text
cycle-01-independent-review.md
cycle-01-author-response.md
cycle-01-verification.md
cycle-02-author-response.md
cycle-02-verification.md
...
```

## Required metadata per action

- `case_id`
- `cycle`
- `action`
- `performed_by.agent_id`
- `performed_by.role`
- `performed_by.tool` when known
- `completed_at` with timezone
- input/base revision
- result revision when applicable
- outcome

## Event log

`events.jsonl` should be append-only. It exists for machine-readable chronology, while `review.md` shows the current state.

## Reopen behavior

If a semantic fingerprint reappears after `fixed-and-verified`, mark it `regression` or `reopened` rather than creating an unrelated issue when possible.
