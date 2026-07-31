---
name: code-understanding-pyramid
description: Use when code-understanding-pro needs a structured five-level framework for understanding, explaining, or reviewing existing code.
version: "3.0.0"
---

# Code Understanding Pyramid Skill

Use the "Pyramid of Understanding" to build an evidence-based view of the code and its architectural context. Separate confirmed facts, inferences, and open questions.

## Role in the Suite

This skill is the reusable reasoning framework under `code-understanding-pro`.

- Do not create an independent output directory.
- Do not return a separate long-form chat answer.
- Return findings to the parent report defined by `code-understanding-pro/references/interface.md`.
- Preserve the five stages, but write them into the parent's common sections.
- Ask a question only when missing information materially blocks a correct explanation. Otherwise, state the assumption and continue.

## 1 Preparation: Contextual Grounding (準備)

Before providing answers, you must anchor yourself:

- **Environment Audit**: Identify language, framework, and project type (React, Go, Python, etc.).
- **Doc Parsing**: Read `README.md`, `package.json`, or environment configs to understand project goals.
- **Mindset Setup**: Adopt the mental model required for this specific domain (e.g., "High-performance API" vs "Quick MVP").

## 2 Overview: Structural Mapping (概要)

- **Bird's Eye View**: Explain the folder structure and system layering.
- **Data Flow**: Identify entry points (APIs, CLI triggers) and exit points (DB, external APIs).
- **Architecture Type**: Determine if it is Monolithic, Microservices, Clean Architecture, etc.

## 3 Detail: Logic Audit (詳細)

- **Logic Trace**: Trace the execution path for specific logic blocks.
- **Variable Role Mapping**: Identify the purpose and scope of key data entities.
- **Constraint Identification**: Note limitations, dependencies, and external helper interactions.

## 4 Deep Understanding: Intent, Tests & Boundaries (深い理解)

- **The "Why"**: Analyze the design intent behind the implementation. Why this pattern?
- **Contract Verification**: When relevant tests exist, review them and compare their behavioral contract with the specifications and implementation. Treat tests as evidence, not the sole source of truth.
- **Edge Case Analysis**: Evaluate how boundary conditions and errors are handled.

## 5 Utilization: Value Creation (活用)

Transform understanding into output based on the user's need:

- **Refactoring**: Suggest structural improvements using the **Severity Classification** below.
- **Documentation**: Generate specs, Mermaid diagrams, or API docs.
- **Vulnerability Check**: Identify security/performance bottlenecks.

---

## Severity Classification (マージ基準)

When providing feedback in Stage ④, label every point:

- **[CRITICAL]**: Security flaws, logic bugs, or spec violations. (Must address)
- **[CONSIDER]**: Architectural or readability improvements. (Recommended)
- **[NIT]**: Stylistic preferences or minor naming. (Optional)
- **[FYI]**: Praise for good code or neutral technical context. (No action)

## Interaction Rules

- **Artifact-First**: Quick Mode以外は親Skillの `report.md` に結果を返し、チャットには要点だけを返す。
- **Complete the Requested Scope**: 対象が大きい場合も、ユーザーが段階停止を求めていなければ文脈から活用まで完遂する。
