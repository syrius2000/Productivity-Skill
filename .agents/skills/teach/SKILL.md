---
name: teach
description: Use when the user wants to learn a skill or concept through a stateful, workspace-based teaching session. Always store teaching materials under ./docs/learning/, including when the user asks to create a lesson, reference, learning record, mission, resource list, or learning portal.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
---

The user has asked you to teach them something. Treat this as a stateful request: the goal is durable understanding across multiple sessions, not a one-off explanation.

## Teaching workspace

All learning materials MUST be kept under `./docs/learning/` so the repository root stays clean:

- `./docs/learning/MISSION.md`: why the user is learning the topic. Use [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `./docs/learning/RESOURCES.md`: curated, trusted sources. Use [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `./docs/learning/INDEX.html`: the central portal for all lessons, references, and records.
- `./docs/learning/lessons/*.html`: short, self-contained lessons; use zero-padded sequential names such as `0001-dash-case-name.html`.
- `./docs/learning/reference/*.html`: printable reference documents, cheat sheets, and glossaries.
- `./docs/learning/learning-records/*.md`: durable records of demonstrated understanding and important prior knowledge; use zero-padded sequential names such as `0001-dash-case-name.md`.
- `./docs/learning/assets/*`: reusable stylesheets, widgets, diagrams, and other lesson components.
- `./docs/learning/NOTES.md`: teacher scratchpad for preferences and session notes.

Before creating or migrating materials, inspect the existing `docs/learning/` tree and preserve user-authored content. If legacy files exist at the repository root, report them and propose a migration; do not silently move or overwrite them.

## Workflow and safety

### 1. Clarify the mission

Every lesson must connect to the user's mission. If `MISSION.md` is missing or unpopulated, ask why the user wants to learn the topic before designing a lesson. If the mission would change, confirm before editing it and record the change in a learning record.

### 2. Dry-run first

Do not silently generate directories or files. First present a concise plan listing the files to create or update, including the lesson, reference, learning record, assets, and `INDEX.html`. Wait for user confirmation before writing them.

### 3. Inspect and reuse assets

Before authoring a lesson, read the existing `./docs/learning/assets/` directory and reuse its components. A shared stylesheet is the default foundation. Add a new reusable component only when the need is genuinely reusable; link it from lessons instead of duplicating inline code.

### 4. Maintain the portal

Whenever a lesson, reference, or learning record is created or renamed, update `./docs/learning/INDEX.html`. Include each item's title, short summary, timestamp, and a valid repository-relative link. Keep links relative and never use `file:///` URLs.

### 5. Quality-check HTML

Before finalizing an HTML file:

- Escape placeholder examples such as `&lt;PID&gt;`, `&lt;PATH&gt;`, and `&lt;ROOT&gt;`.
- Inspect code blocks and prose for unintended unescaped `<` or `>` characters.
- Confirm all internal anchors point to existing relative files.
- Keep the lesson readable and printable, with concise sections and accessible contrast.

### 6. Controlled preview

Do not open a browser automatically. Only run `open <html-file>` when the user explicitly requests a preview, for example with `preview: true`, and the environment is a GUI desktop. Skip browser launch in CI, SSH, and other non-GUI environments.

## Learning design

Deep learning needs three complementary elements:

- **Knowledge** from high-quality, high-trust resources.
- **Skills** built through relevant practice and feedback.
- **Wisdom** tested through real-world interaction and reputable communities when appropriate.

Use `RESOURCES.md` to ground factual explainers in trusted sources rather than relying on unverified memory. Each lesson should recommend a primary source and link to related lessons and reference documents.

Design for durable storage strength, not only fluent repetition. Use retrieval practice, spacing, and interleaving where they fit the topic. Keep each lesson short enough to complete quickly and give the learner one tangible win.

For practice, use a tight feedback loop: interactive questions, small exercises, or concrete real-world steps. For quizzes, keep answer choices comparable in length and formatting so presentation does not reveal the answer.

## Mission and zone of proximal development

Use the mission, existing learning records, and stated prior knowledge to choose the next lesson. Scan `./docs/learning/learning-records/` and increment the highest existing record number when writing a new record.

Write a learning record only when the user demonstrates genuine understanding of a non-trivial concept, discloses relevant prior knowledge, or changes the mission. Mere exposure to a topic is not evidence of learning.

## Boundaries

- `INDEX.html`, `lessons/`, `reference/`, and reusable `assets/` are agent-maintained, subject to the dry-run confirmation.
- Preserve `NOTES.md` and user edits in `MISSION.md`; do not replace them with generated content.
- Keep all generated learning artifacts in `./docs/learning/`.
- Use repository-relative links for internal documents and avoid absolute filesystem paths.
