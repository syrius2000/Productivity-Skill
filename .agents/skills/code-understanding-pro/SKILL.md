---
name: code-understanding-pro
description: Use when a user asks to understand, review, document, explain, or safely refactor existing code in Japanese.
version: "2.3.0-ja"
license: "Internal use"
---

# code-understanding-pro

## 目的 & コア原則

このSkillは、既存コードを段階的に理解し、レビュー・QA・ドキュメント化・安全なリファクタリングを支援する。

1. **事実と推論の厳格な分離**: コード上の直接事実、推論、未確認事項、リスクを峻別する。設計意図を根拠なく断定しない。
2. **プロジェクト文脈優先**: 一般論より、テスト、型、呼び出し元、設計メモ、Git履歴を証拠として最優先する。
3. **非破壊性と実行境界**: ユーザーの明示的承認なしにファイル変更・コード実行を行わない。テスト実行も副作用を確認後に行う。

## モード判定と成果物契約

開始時に対象、目的、許可された操作、対象外を短く固定する。対象の曖昧さが正確性を損なう場合だけ質問し、それ以外は仮定を明記して進める。呼び出し元、型、テスト、設定、Git履歴は、説明に必要な範囲だけ調査する。

依頼内容に基づき、上から最初に合致するモードを採用する。
| 優先 | モード | 判定条件 | 主な成果物・出力仕様 | 必読参照資料 |
|---:|---|---|---|---|
| 1 | Refactoring | 改善・構造修正・変更比較 | `assets/output-template-refactoring.md` | [安全確認](references/refactoring-safety-checklist.md) |
| 2 | Review | レビュー・QA・バグ・マージ判断 | `assets/output-template-review.md` | [重大度基準](references/review-severity-guide.md) |
| 3 | Documentation | README・仕様書・DocString | `report.md`（概要/API/フロー/入出力例/制約/本文） | [Python](assets/docstring-template-python.md) / [R](assets/docstring-template-r.md) |
| 4 | Full | 複数ファイル・深層読解・オンボーディング | `assets/output-template-full.md` | [ピラミッド](references/qiita-code-reading-pyramid.md) |
| 5 | Quick | 単一関数・短い質問（上記以外） | チャット回答のみ（成果物保存なし） | [Quickテンプレート](assets/output-template-quick.md) |

> **Documentation モードの保存要件**: `report.md` を保存する場合は、必須8節を満たした上で `## 詳細` 配下に生成ドキュメント本文および入出力例・制約を配置する。初学者向け解説を求められた場合は [assets/output-template-beginner.md](assets/output-template-beginner.md) を参照。

## 読解プロセス（5段階ピラミッド）

`Quick` は、対象・入力/出力・未確認点を Step 0 で確認し、質問へ直接必要な Step 2 だけを追跡する。直接事実と、該当する場合の未確認点をチャットで返し、保存・Mermaid・全体設計調査は要求しない。

`Full`、`Review`、`Documentation`、`Refactoring` は Step 0 から順に実施し、各ステップの完了条件を満たしてから次へ進む。共通の問いを持つ複数対象は、一つのレポートへまとめ、対象別の根拠を記載する。

- **Step 0: 文脈把握（地図作成）**:
  - 【調査項目】対象ファイル・行範囲、見かけ上の役割、入力と出力、呼び出し元、関連テスト/Doc/Issue、外部依存、不明点。
  - 【完了条件】対象コードの境界と前提条件が特定され、未確認事項が洗い出されていること。
- **Step 1: 概要理解（全体像把握）**:
  - 【調査項目】一文要約、主要処理3〜5ステップ、主な要素と責務、ラフなデータフロー。
  - 【完了条件】細部に立ち入る前に全体の入出力の流れを暫定把握できていること（断定は避ける）。
- **Step 2: 詳細追跡（挙動解明）**:
  - 【調査項目】インターフェース（引数/戻り値の型・意味）、重要変数・制御フロー（分岐/ループ）、副作用（ファイルI/O・DB・API・状態変更）、例外・境界値。
  - 【完了条件】代表的な入力値に対するデータ変化と副作用のリスクが具体的に追跡できていること。
- **Step 3: 深い設計理解（意図とリスク）**:
  - 【調査項目】設計選択理由の可能性、業務・性能・互換性制約、トレードオフ、潜在リスク（保守性・並行性・セキュリティ）、エッジケース。
  - 【判断基準】コード上の事実と推論を厳格に分離し、根拠のない設計意図は「推測」と明記すること。
- **Step 4: 活用（成果物生成）**:
  - 【完了条件】採用モードに応じた成果物を生成し、親Skillとして保存・事後検証を行う。

### Mermaid 複雑度判定基準

次のいずれかに該当する場合は複雑度を `complex` と判定し、Mermaid図（`flowchart TD` 等）を作成する（作図パターンは [assets/mermaid-patterns.md](assets/mermaid-patterns.md) を参照）。非該当の場合は `simple` とし文章フローで記載する。

- 複数クラスまたはモジュール間で、状態またはデータが受け渡される。
- 分岐の選択により、外部結果または状態変更が変わる。
- 非同期処理、時間順序、再試行が理解の中心である。

主要ステップ数だけ、または局所的な分岐・ループだけでは `complex` としない。

## スイート連携（親Skill契約）

`code-understanding-pro` はコード理解スイートの親Skillであり、成果物の所有・保存・検証・チャット要約を集約する。

- **共通理解フレーム**: 下位Skill `code-understanding-pyramid` を同一セッション内で参照し、理解の順序として利用する。下位Skill単独の成果物ディレクトリや独立回答は作成させない。親は子へ「対象パスと質問」「確認済みの事実」「未確認点」「子にだけ求める観点」を渡す。
- **SQL / 統計アダプター委譲**:
  - SQL（dbt/CTE/ウィンドウ関数）: `stats-sql-comprehension` へ委譲（`--adapter sql`）。テンプレートは [../stats-sql-comprehension/assets/output-template-sql.md](../stats-sql-comprehension/assets/output-template-sql.md) を使用する。入力に現れる場合だけ、データ粒度・CTE一覧・JOIN変化・検証SQLを統合し、情報がなければ未確認と明記する。
  - 統計解析（R/Python）: `stats-sql-comprehension` へ委譲（`--adapter stats`）。テンプレートは [../stats-sql-comprehension/assets/output-template-stats.md](../stats-sql-comprehension/assets/output-template-stats.md) を使用する。入力に現れる場合だけ、対象母集団・欠測除外・推定量前提・バイアス・再現コードを統合し、情報がなければ未確認と明記する。
- **配置境界**: 下位Skillが同じSkill配置ルートに存在しない場合は、利用不可を明記した上で親Skill単独の一般分析として続行する。

## レビュー重大度語彙（一般コードレビュー）

Review モードでは指摘を以下に分類し、各指摘に **[分類 / 場所(ファイルと行番号) / 根拠 / 修正案 / 実行すべきテスト]** を必ず明記する。

- **[Critical]**: マージ不可。セキュリティ脆弱性、データ損失、重大な正確性バグ、契約違反。
- **[Major]**: 強く修正推奨。実害リスクの高いバグ、重要テスト不足、重大な保守性問題。
- **[Consider]**: 検討価値あり。設計・可読性・構造改善。
- **[Nit]**: 任意修正。スタイル、軽微な命名、フォーマット。
- **[FYI]**: 情報提供のみ。アクション不要。

## 成果物の保存・検証・安全運用

Full、Review、Documentation、Refactoring では `report.md`、`run_meta.json`、`source_manifest.json` を保存する。保存が必要になった時点で、排他制御・機密伏字化・必須節・失敗時の扱いの正本 [references/interface.md](references/interface.md) を読む。利用先の保存規則と衝突する場合は上位規則を確認し、黙って保存先を変えない。

### 保存契約の補足

- `collect_code_context.py` の `code_context.md` は `Context` 補助成果物であり、通常レポートの必須見出しを持たず、検証CLIの対象外である。
- 未閉じ引用符、複数行引用符、YAML block scalar、command substitutionなどの曖昧な秘密形式は、出力予約前に保存を中止する。
- 出力rootは信頼済み非共有ディレクトリとする。同一UIDの別プロセスによる親ディレクトリ差し替えは保護境界外である。
- 失敗時は `.incomplete` または部分出力を残し、自動削除しない。内容確認後に利用者が削除するか、別のrun IDで再実行する。
- 保存に失敗した場合は理由と未保存であることを簡潔に報告する。検証に合格するまで完了を報告しない。

```bash
# コンテキスト収集（必要時）
python3 .agents/skills/code-understanding-pro/scripts/collect_code_context.py \
  <path> [<path> ...]

# レポート保存
python3 .agents/skills/code-understanding-pro/scripts/write_report.py \
  --mode <full|review|documentation|refactoring> \
  --target <target_path> \
  --content-file <path_to_content.md> \
  --adapter <generic|sql|stats> \
  --source <source_file>

# レポート検証（PASSするまで完了報告禁止）
python3 .agents/skills/code-understanding-pro/scripts/validate_report.py \
  skill_out/code_understanding/<target>/run_<id>/report.md \
  --adapter <generic|sql|stats> \
  --complexity <simple|complex>
```

## 禁止事項

- `write_report.py` を介さず直接レポート成果物ディレクトリを作成・上書きすること。
- ユーザーの明示的承認のないコード変更、外部実行、Gitリモート操作（commit/push）。
- 根拠のない設計意図の断定や、不確実性の隠蔽。
