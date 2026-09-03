# コード理解Skill二段構成の改良計画（再構成版）

created: 2026-09-02 18:39 (JST)
update: 2026-09-02 18:39 (JST)
author: Codex (GPT-5)

> 本文は、削除された未追跡の原本を完全復元したものではなく、会話履歴と実施結果に基づく再構成版である。改良内容の確認可能な記録として保存する。

## 目的

`code-understanding-pro`と`code-understanding-pyramid`の既存能力を維持しながら、モード選択、調査範囲、各段階の完了条件、事実と推論の分離、出力検証を明確にする。異なる依頼でも一貫した手順と品質で動作する実用Skillに近づける。

## 対象範囲

- `.agents/skills/code-understanding-pro/SKILL.md`
- `.agents/skills/code-understanding-pro/VERSION`
- `.agents/skills/code-understanding-pro/manifest.json`
- `.agents/skills/code-understanding-pro/assets/output-template-*.md`
- `.agents/skills/code-understanding-pro/scripts/validate_report.py`
- `.agents/skills/code-understanding-pro/tests/test_report_validator.py`
- `.agents/skills/code-understanding-pyramid/SKILL.md`
- `tests/test_code_understanding_suite_contract.py`
- `tests/test_mutating_skill_boundaries.py`

## 変更しない対象

- `quality-review`、`quality-response`の既存機能
- `grilling`、`teach`、`writing-great-skills`
- `stats-sql-comprehension`の専門機能
- commit・push以外の外部システム操作

## 改良内容

### 1. モードとスコープ

Refactoring、Review、Documentation、Full、Quickの判定表を追加し、複数該当時の優先順位を固定する。呼び出し元、型、テスト、設定、Git履歴への調査拡張は、説明に必要な場合だけ行い、理由を記録する。

### 2. Pyramidの完了条件

5段階それぞれに、対象・目的・入出力・全体フロー・値の追跡・設計意図・テスト契約・残存リスク・成果物引き継ぎの確認条件を追加する。事実、根拠に基づく推論、未確認事項を分離し、テストがないことを合格とは推定しない。

### 3. Mermaidと処理フロー

複数ステップ、分岐、ループ、複数モジュール、データ変換、非同期処理を含む対象を`complex`とし、Mermaidを必須にする。単純な対象は`simple`とし、非空の文章または箇条書きの処理フローを許容する。Validatorに`--complexity simple|complex`を追加する。

### 4. 出力と版情報

テンプレートのMermaid条件を更新し、一般コードレビューの重要度語彙を`[Critical]`、`[Major]`、`[Consider]`、`[Nit]`、`[FYI]`へ統一する。`SKILL.md`、`manifest.json`、`VERSION`の`code-understanding-pro`版を`2.1.0-ja`へ揃える。

## 検証

- `python3 -B -m pytest --assert=plain -p no:cacheprovider tests .agents/skills/code-understanding-pro/tests -q`
- 結果：53件成功
- `git diff --check`：成功（統合時にmaster側の既存アーカイブ文書の行末空白警告あり。履歴資料は改変せず保持）
- 複雑度別のMermaid・文章フロー・未閉鎖Mermaidをテスト
- Manifestのファイル存在と版情報整合性を契約テストで確認

## 実施・Git反映結果

- 改良実装を`feat: harden code understanding skills`としてcommitした。
- `agent/archive-qa-012`からPR #2を作成した。
- 競合を個別解決し、`master`へsquash mergeした。
- masterのmerge commit：`22ad2df`
- PR：https://github.com/syrius2000/Productivity-Skill/pull/2
- リモート作業ブランチ`agent/archive-qa-012`は削除済み。

## 残存事項

- 本文は削除された原本の完全復元ではなく再構成版である。
- LLM実呼び出しによる動的な代表ケース検証は未実施であり、残余リスクとして扱う。
