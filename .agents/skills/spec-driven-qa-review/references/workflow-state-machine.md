# Workflow State Machine

## Case states

```text
draft
  -> review-in-progress
  -> author-action-required
  -> author-response-submitted
  -> verification-in-progress
       -> author-action-required
       -> adjudication-required
       -> ready-for-closure
  -> closed
```

Additional states:

- `blocked`
- `needs-review`
- `deferred`
- `risk-accepted`
- `superseded`
- `cancelled`

## Required transitions

### draft -> review-in-progress
Requires explicit target and baseline metadata.

### review-in-progress -> author-action-required
Requires at least one issued finding or an explicit no-material-finding record.

### author-action-required -> author-response-submitted
Requires author response for every blocking author-action marker.

### author-response-submitted -> verification-in-progress
Reviewer must evaluate the actual result revision, not the author's prose alone.

### verification-in-progress -> ready-for-closure
Requires closure policy to be satisfied.

### any -> adjudication-required
Use when:

- material finding remains disputed;
- maximum automated cycles reached;
- policy requires human decision;
- Purpose/Spec conflict cannot be resolved by evidence;
- residual risk acceptance is outside AI authority.

### closed -> needs-review
Allowed after drift is detected (Purpose/Spec/interface/invariant/evidence revision changed).

## Terminal result vs workflow status

Workflow status and QA result are separate.

Example:

```yaml
status: closed
result: accepted-with-residual-risk
```
