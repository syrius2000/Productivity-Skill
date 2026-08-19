# QA Principles

## 1. Purpose is highest-level intent, not unquestionable truth

Purpose frames why the work exists. QA may still identify a Purpose as ambiguous, contradictory, infeasible, unmeasurable, or incomplete.

## 2. Mutually criticizable evidence

Evaluate both directions, not only top-down traceability:

- Purpose ↔ Spec
- Spec ↔ Plan / Tasks
- Plan ↔ Implementation
- Implementation ↔ Evidence
- Evidence ↔ Purpose

An implementation may reveal defects in the Spec. A test may reveal that a stated Purpose cannot be operationalized. A Plan may introduce constraints not justified by the Spec.

## 3. Claimed is not observed

Keep four layers distinct:

1. **Intended** — Purpose / Spec
2. **Planned** — Plan / Tasks
3. **Claimed** — Implementation Report / author explanation
4. **Observed / Verified** — code, runtime behavior, tests, measurable evidence

## 4. Do not confuse existence with sufficiency

Evidence exists ≠ evidence is relevant ≠ evidence is sufficient ≠ claim is proven.

## 5. Make uncertainty explicit

Valid outcomes include:

- `not-assessable`
- `insufficient-context`
- `insufficient-evidence`
- `conflicting-sources`
- `outside-scope`

## 6. Independent review before reconciliation

AI-2 should create an independent view before reading AI-1's self-justification. Reconciliation occurs only after the first findings are frozen.

## 7. Author cannot self-close findings

AI-1 may accept, reject with evidence, fix, defer, or request risk acceptance. AI-2 verifies. A human or AI-3 adjudicates unresolved disagreements when required.

## 8. Preserve history

Never overwrite prior review cycles just to make the latest state look clean. The review case is an audit trail.

## 9. Risk-based burden

Do not apply a Strict process to every trivial change. Excessive process becomes ritual and reduces signal.

## 10. Human accountability is explicit

This Skill can support review and evidence management. It does not certify that a person understood the code, and it does not replace regulatory, security, safety, or clinical accountability.
