# GitHub Spec Kit Adapter

Use when the repository follows a Spec-Driven Development flow with artifacts such as specification, implementation plan, and tasks.

## Neutral mapping

- feature/business intent and success criteria -> Purpose
- `spec`-like artifact -> Spec
- `plan`-like artifact -> Plan
- `tasks`-like artifact -> Tasks
- resulting source/config/migrations -> Implementation
- tests, validation, benchmark, logs -> Evidence

## Discovery

Do not assume a single version-specific directory. Detect the feature/spec directory used by the repository, then locate relevant `spec`, `plan`, `tasks`, and related artifacts for the explicit target.

## QA questions

- Does every material acceptance criterion have implementation and evidence?
- Did the plan omit a requirement?
- Did implementation introduce material behavior absent from the Spec?
- Did plan changes get reflected back into the Spec/decision record?
- Are completed tasks actually observable in code/evidence?
