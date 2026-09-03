# Evidence Evaluation

## Evidence classes

| Type | Typical strength | Main limitation |
|---|---|---|
| Executed acceptance test | High | Only proves tested scenario and environment |
| Integration test | High–Medium | Mocks/stubs may omit real integration behavior |
| Unit test | Medium | Does not prove integrated system behavior |
| Runtime observation/log/benchmark | High–Medium | Reproducibility and environment matter |
| Static analysis/type checking | Medium | Limited runtime semantics |
| Code inspection | Medium–Low | Existence/reachability/correctness differ |
| Existing ADR / authoritative spec | Requirement evidence | May be stale or internally wrong |
| Implementation Report | Low | Author claim, not independent verification |
| README/comment | Low | Drift-prone |
| AI explanation | Low | Inference, not independent evidence |

## Four questions for every important evidence item

1. **Relevance** — does it actually bear on the claim?
2. **Directness** — how directly does it measure/observe the claim?
3. **Reproducibility** — can it be recreated with known conditions?
4. **Sufficiency** — is it enough to justify the stated conclusion?

## Execution evidence metadata

Prefer recording:

```yaml
execution:
  command: "pytest tests/test_patient_validation.py -q"
  exit_code: 0
  working_directory: "."
  started_at: "2026-08-13T09:00:00+09:00"
  completed_at: "2026-08-13T09:00:10+09:00"
  environment:
    os: "Ubuntu 24.04"
    runtime: "Python 3.12"
    dependency_lock: "uv.lock"
    dependency_lock_hash: "..."
```

Do not store secrets or huge logs by default. Store a summary plus file reference/hash when appropriate.
