# Installation / Placement

Copy the entire `spec-driven-qa-review/` directory into the Skill directory used by your agent environment.

A common project-local layout is:

```text
.agents/skills/spec-driven-qa-review/
```

If your tool uses another Skill root, keep the directory contents unchanged and place it under that root.

The reviewed project's QA records are **not** stored inside the Skill. They are written to:

```text
docs/ADR/QA/
```

Recommended multi-agent operation:

- AI-1: implementation environment (e.g. Codex)
- AI-2: reviewer environment (e.g. Cursor)
- optional human/AI-3: adjudication

For stronger separation, do not share implementation chat transcripts with AI-2 before the first independent review.

Optional integrations:

- copy/merge `integrations/pre-commit.example.yaml` into `.pre-commit-config.yaml`
- adapt `integrations/github-actions.example.yml` into `.github/workflows/`

The helper scripts require Python 3.10+ and use only the standard library at runtime.
