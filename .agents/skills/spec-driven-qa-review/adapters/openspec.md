# OpenSpec Adapter

Use when the repository contains an OpenSpec-style specification/change structure.

## Intent

Map OpenSpec artifacts into this Skill's neutral model:

- overarching rationale / change intent -> Purpose or Purpose-supporting evidence
- specification requirements / scenarios -> Spec
- design/proposal material -> Plan / Design
- task list -> Tasks
- source changes -> Implementation
- tests / validation results -> Evidence

## Discovery

Do not hard-code a single version-specific layout. Prefer:

1. locate the repository's OpenSpec configuration or documented root;
2. identify active change artifacts relevant to the explicit target;
3. locate linked/current specification material;
4. record exact discovered paths in the QA baseline.

Common projects may use paths resembling `openspec/` with spec/change subtrees, but always verify the repository's actual layout.

## QA cautions

- OpenSpec material is requirement/design evidence, not automatically true.
- If implementation diverged intentionally, require a recorded design/spec update or finding.
- Do not import unrelated changes merely because they share the same OpenSpec root.
