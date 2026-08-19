# Spec-Driven QA Review

`spec-driven-qa-review` は、AI実装を別AIが独立レビューし、Purpose / Spec / Plan / Tasks / Implementation / Implementation Report / Tests / Evidence の整合性を追跡するためのSkill一式です。

## 中核思想

> Purposeを最上位に置き、Spec・Plan・Implementation・Evidenceを相互に批判可能な証拠として扱う。

このSkillは「コードを説明して理解したことにする」ためのものではありません。AI-1が実装した成果物について、AI-2が独立にQA Findingを作成し、AI-1が回答・修正し、AI-2が再検証する反復可能なQAワークフローを提供します。

## 典型フロー

```text
Purpose / Spec / Plan
        ↓
AI-1 Implementation
        ↓
AI-2 Blind-first Independent Review
        ↓
QA Findings
        ↓
AI-1 Author Response / Correction
        ↓
AI-2 Reviewer Verification
        ↓
Closure / Rework / Human Adjudication
```

## 対象範囲

- デフォルトは明示されたファイルまたはディレクトリのみ。
- 指定モジュールを優先し、リポジトリ全体は明示依頼時のみ。
- 理解に必要な関連テスト・型・Spec等は参照できますが、勝手に主対象へ広げません。

## 出力先

```text
docs/ADR/QA/QA-XXXX-short-title/
```

主要ファイル:

- `review.md`: 現在状態、QA Pulse、次の担当者とアクション
- `findings.yaml`: Findingの機械可読状態
- `traceability.yaml`: Purpose/Spec/Implementation/Evidenceの対応
- `events.jsonl`: append-only進捗ログ
- `cycles/`: 各サイクルの独立レビュー、作成者回答、再検証

## REQUIREDバリデーション

未処理の必須項目には `REQUIRED:` を付けます。

```text
REQUIRED:AUTHOR-RESPONSE:QA-0007-F05:CYCLE-2
```

`validate_review_case.py` および `detect_unresolved_markers.py` は、残存タグや矛盾した状態を検出します。

検証済みの履歴マーカーは `RESOLVED:REQUIRED:<元のマーカー>` として残します。`scripts/validate_package.py` は `MANIFEST.txt` を基準に、生成物を除いたパッケージ整合性を検証します。

## QA Profile

- `lite`: 低リスク変更向け
- `standard`: 通常の機能実装向け（既定）
- `strict`: 高リスク・規制・統計ロジック・データ破壊・認証等

詳細は `references/risk-profiles.md`。

## SDD Adapter

Skill自体はOpenSpec等へ固定しません。

- `adapters/openspec.md`
- `adapters/spec-kit.md`
- `adapters/generic-sdd.md`

SDD成果物の場所や命名がプロジェクトで異なる場合はAdapterの探索規則を調整します。

## Python補助スクリプト

ランタイム依存はPython標準ライブラリのみです。

```bash
python scripts/create_review_case.py --root . --title "patient normalization" --target src/normalization --profile standard
python scripts/detect_unresolved_markers.py docs/ADR/QA
python scripts/validate_review_case.py docs/ADR/QA/QA-0001-patient-normalization
```

pytestを使うテストは開発用です。

Skill自身を改善する場合は `references/evaluation-contract.md` を読み、改善前後で同じシナリオを実行して証拠を比較します。

## pre-commit / CI

`integrations/` に例があります。ローカルpre-commitは即時フィードバック用であり、`--no-verify` で回避できます。強制する場合はCI/branch protection側でも検証してください。

## 重要な限界

- 2つのAIの合意は正しさを保証しません。
- Spec自体が誤っている可能性があります。
- AI間レビューは人間の規制上の承認や安全責任を代替しません。
- AI-2はAI-1の説明を先に読まず、可能な限りblind-firstで評価します。
