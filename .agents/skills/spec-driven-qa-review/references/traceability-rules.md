# Traceability Rules

## Core chain

`Purpose -> Spec -> Plan/Tasks -> Implementation -> Evidence`

Traceability is not only a chain of IDs. Each link should state why the downstream artifact supports the upstream claim.

## Claim model

Recommended representation:

```yaml
claims:
  - id: CLAIM-001
    statement: "Missing patient ID records are rejected before analysis"
    source:
      type: specification
      reference: REQ-014
    implementation:
      - path: src/validation/patient.py
        symbol: validate_patient
    evidence:
      - id: EVID-001
        type: test
        reference: tests/test_patient_validation.py::test_missing_patient_id_is_rejected
    assessment:
      result: supported
      confidence: high
```

## Valid assessment results

- `supported`
- `partially-supported`
- `unsupported`
- `contradicted`
- `not-assessable`
- `outside-scope`

## Drift checks

Mark affected traceability stale if any of these change materially:

- Purpose text or success criteria
- Requirement/acceptance criterion
- Plan or architectural decision
- public API / schema / database contract
- invariant or error behavior
- linked code revision
- linked test behavior
- evidence environment or benchmark conditions

## Avoid false precision

Line numbers are helpful but unstable. Prefer line numbers plus symbol names, test IDs, requirement IDs, and Git revision when available.
