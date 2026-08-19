# Finding Taxonomy

## Categories

### purpose-gap
Purpose is missing, ambiguous, internally inconsistent, non-measurable, or not represented downstream.

### spec-drift
Observed implementation behavior conflicts with a Specification requirement or acceptance criterion.

### plan-drift
Implementation differs materially from the Plan without an explicit, justified decision update.

### coverage-gap
A requirement, task, or promised behavior has no identifiable implementation.

### evidence-gap
Implementation may exist, but evidence is missing, irrelevant, weak, stale, or insufficient.

### unspecified-implementation
Implementation introduces material behavior not represented in Purpose/Spec/Plan.

### unverified-assumption
Implementation relies on an unstated assumption: ordering, data volume, idempotency, timezone, concurrency, encoding, null semantics, platform behavior, etc.

### contradictory-evidence
Spec, code, test, ADR, report, or runtime evidence disagree.

### maintainability-risk
Responsibilities, boundaries, invariants, or change impact are unclear enough to create maintenance risk.

### security-risk
Security-relevant behavior or unsafe assumptions are identified.

### portability-risk
Behavior depends unexpectedly on OS, filesystem, shell, encoding, locale, line endings, case sensitivity, package environment, or runtime version.

### regression
A previously fixed/verified semantic fingerprint reappears.

## Severity

### Critical
Immediate catastrophic, security, integrity, regulatory, destructive, or unrecoverable risk; or release must not proceed without adjudication.

### High
Material Purpose/Spec failure, significant data integrity issue, unhandled destructive edge case, or evidence gap for a critical requirement.

### Medium
Meaningful correctness, maintainability, testability, observability, or portability deficiency not normally release-blocking by itself.

### Low
Minor issue, clarity improvement, low-impact edge case, or non-blocking maintainability improvement.

## Severity rationale

Severity must include an explicit rationale. Do not infer severity merely from category.

## Finding statuses

- `new`
- `open`
- `accepted`
- `rejected-with-evidence`
- `fix-submitted`
- `fixed-and-verified`
- `partially-fixed`
- `disputed`
- `deferred`
- `risk-accepted`
- `not-applicable`
- `duplicate`
- `reopened`
- `regression`
- `closed`
