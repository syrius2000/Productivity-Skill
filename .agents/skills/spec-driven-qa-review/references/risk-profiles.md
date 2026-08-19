# QA Profiles

## Lite

Use for clearly low-risk, non-behavioral or very localized changes.

Minimum:

- explicit target
- short `review.md`
- unresolved `REQUIRED` marker check
- obvious Spec conflict check
- test/evidence status

Do not create heavy cycle machinery unless a finding requires it.

## Standard (default)

Use for ordinary feature work and module changes.

Required:

- baseline
- `review.md`
- `findings.yaml`
- `traceability.yaml`
- `events.jsonl`
- cycle records
- independent reviewer
- author response + reviewer verification for blocking findings

## Strict

Use for high-impact areas such as:

- authentication/authorization
- data deletion or irreversible migrations
- financial/payment logic
- transaction/idempotency boundaries
- regulated or submission-facing data
- statistical estimation logic
- missing-data transformation
- safety-critical decisions
- security-sensitive code
- high-cost or externally destructive automation

Additional expectations:

- stronger baseline integrity (revision + hashes when practical)
- execution evidence for important claims
- explicit rollback/containment review
- human adjudication for unresolved Critical/High findings
- High findings cannot be silently auto-risk-accepted
- environment reproducibility details
