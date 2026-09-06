---
name: code-understanding-pyramid
description: Use when code-understanding-pro needs the five-level framework for understanding, explaining, or reviewing existing code. Return findings to that parent Skill; do not operate as a standalone report writer.
version: "3.0.0"
---

# Code Understanding Pyramid Skill

Use the "Pyramid of Understanding" to build an evidence-based view of the code and its architectural context. Separate confirmed facts, inferences, and open questions.

## Role in the Suite

This skill is the reusable reasoning framework under `code-understanding-pro`.

- Do not create an independent output directory.
- Do not return a separate long-form chat answer.
- Return findings to the parent report contract that `code-understanding-pro` owns. Do not assume a filesystem path outside this Skill unless the parent has confirmed the sibling Skill layout.
- Preserve the five stages, but write them into the parent's common sections.
- Ask a question only when missing information materially blocks a correct explanation. Otherwise, state the assumption and continue.
- 親から「対象パスと質問」「確認済みの事実」「未確認点」「子にだけ求める観点」を受け取った場合は、その観点に必要なStageだけを実施し、すでに確認済みの資料を再読しない。

## 1 Preparation: Contextual Grounding (準備)

親から必要な文脈が渡されていない場合だけ、正確な説明に必要な環境・README・設定を読む。追加調査した場合は、親へ理由を返す。

完了条件: 親が依頼した理解の不足を、対象範囲、入力・出力、根拠、不明点で補える。調査範囲を広げた場合は、その理由も残す。

## 2 Overview: Structural Mapping (概要)

親が概要を不足として依頼した場合だけ実施する。

- **Bird's Eye View**: Explain the folder structure and system layering.
- **Data Flow**: Identify entry points (APIs, CLI triggers) and exit points (DB, external APIs).
- **Architecture Type**: Determine if it is Monolithic, Microservices, Clean Architecture, etc.

完了条件: 一文要約、主要要素、入口から出口までの流れ、アーキテクチャ上の仮説を示せる。複雑度が低ければ、Mermaidではなく文章の処理フローでよい。

## 3 Detail: Logic Audit (詳細)

親が詳細追跡を不足として依頼した場合だけ実施する。

- **Logic Trace**: Trace the execution path for specific logic blocks.
- **Variable Role Mapping**: Identify the purpose and scope of key data entities.
- **Constraint Identification**: Note limitations, dependencies, and external helper interactions.

完了条件: 少なくとも一つの入力例または代表経路について、値・状態の変化を根拠付きで追跡できる。

## 4 Deep Understanding: Intent, Tests & Boundaries (深い理解)

親が設計・契約・境界を不足として依頼した場合だけ実施する。

- **The "Why"**: Analyze the design intent behind the implementation. Why this pattern? コードや文書で確認できる事実、根拠からの推論、未確認事項を分離し、設計意図を断定しない。
- **Contract Verification**: When relevant tests exist, review them and compare their behavioral contract with the specifications and implementation. Treat tests as evidence, not the sole source of truth.
- **Edge Case Analysis**: Evaluate how boundary conditions and errors are handled.

完了条件: 設計意図の根拠、テストとの契約差分、境界値・異常系、残存リスクを分けて記載できる。テストがない場合も「未確認」として扱い、合格とは推定しない。

## 5 Utilization: Value Creation (活用)

親が指定した成果物に必要な発見だけを返す。

Transform understanding into output based on the user's need:

- **Refactoring**: Suggest structural improvements using the **Severity Classification** below.
- **Documentation**: Generate specs, Mermaid diagrams, or API docs.
- **Vulnerability Check**: Identify security/performance bottlenecks.

完了条件: 依頼された活用成果物に、根拠ファイル・行番号、重要度、必要なテスト、未確認事項が引き継がれている。

---

## Severity Classification (一般コードレビュー)

When providing feedback in Stage ④, label every point:

- **[Critical]**: Security flaws, data loss risks, correctness bugs, or spec violations. (Must address)
- **[Major]**: Likely user impact, missing critical tests, or high-risk maintainability issues. (Strongly recommended)
- **[Consider]**: Architectural or readability improvements. (Recommended)
- **[Nit]**: Stylistic preferences or minor naming. (Optional)
- **[FYI]**: Neutral technical context. (No action)

Use this vocabulary only for general code review. Quality Loop uses its own state vocabulary.

## Interaction Rules

- **Artifact-First**: Quick Mode以外は親Skillの `report.md` に結果を返し、チャットには要点だけを返す。
- **Complete the Requested Scope**: 対象が大きい場合も、ユーザーが段階停止を求めていなければ文脈から活用まで完遂する。
