# Implementation Plan: code-understanding スイートの精密な構造改善計画 (Implementation_agy_001)

created: 2026-09-04 18:25 (JST)  
update: 2026-09-04 19:10 (JST) (Revision 3: 再レビュー指摘の全件反映)  
author: Antigravity (AGY)  
target: `.agents/skills/code-understanding-pro/` 及び関連スイート  
status: Completed / All Tests Passed (20 tests PASS)  

---

## 1. 目的・背景・スコープ

### 1.1 目的
[code-understanding-pro/SKILL.md](../../.agents/skills/code-understanding-pro/SKILL.md) は、コード理解・レビュー・リファクタリング支援を担う中核Skillであるが、現状 **642行 / 21,730 bytes** に達している。  
本改修の主目的は、単なる行数削減ではなく、`writing-great-skills` の基本指針である **Progressive Disclosure（段階的詳細開示）**、**Single Source of Truth（正本の一元化）**、および **Duplication（二重定義）の徹底排除** に基づき、エージェントが迷いなく高精度に動作するようドキュメント構造を抜本的に再設計することである。

リポジトリ内の全契約テスト（キーワード存在、マニフェスト整合性）、出力互換性（`validate_report.py` が要求する8必須節）、およびセキュリティ境界（機密情報伏字化、ファイル操作権限）を **100% 維持した状態** で、`SKILL.md` 本文を中核指示に凝縮し、約180〜200行（約70%削減）へ最適化する。

### 1.2 変更対象（In Scope）
- `.agents/skills/code-understanding-pro/SKILL.md`（スリム化・構造再設計）
- `.agents/skills/code-understanding-pro/README.md`（ファイルツリー図に `references/interface.md` を追記）
- `.agents/skills/code-understanding-pro/VERSION`（`2.2.0-ja` への更新）
- `.agents/skills/code-understanding-pro/manifest.json`（version 更新および整合性検証）

### 1.3 変更しない対象（Out of Scope / 不変境界）
- スクリプト本体コード（[scripts/write_report.py](../../.agents/skills/code-understanding-pro/scripts/write_report.py), [scripts/validate_report.py](../../.agents/skills/code-understanding-pro/scripts/validate_report.py), [scripts/collect_code_context.py](../../.agents/skills/code-understanding-pro/scripts/collect_code_context.py)）
- 既存テストコード（`tests/` 配下および `.agents/skills/code-understanding-pro/tests/` 配下のテストアサーション）
- 他のSkill（`code-understanding-pyramid` や `stats-sql-comprehension` のコード本体）
- ユーザーの作業中差分、未追跡ファイル、Gitリモート操作（commit, push）

---

## 2. リポジトリ既存契約と技術的事実

### 2.1 実在するテストファイルと責務マトリクス

| テストファイル | 配置パス | 実在テスト件数 | テスト対象と検証内容 |
| --- | --- | ---: | --- |
| **`test_code_understanding_suite_contract.py`** | `tests/` | 5 tests | スイート全体の役割分担、出力契約キーワード、レビュー重大度語彙の一貫性、旧ファイル名の不在、マニフェストと版情報の一致を検証。 |
| **`test_skill_inventory_contract.py`** | `tests/` | 3 tests | 全SkillのREADME収録一覧、SKILL.md内の相対Markdownリンク解決性、マニフェスト記載ファイルの実在性を検証。 |
| **`test_skill_frontmatter.py`** | `tests/` | 1 test | front matter のサイズ（<=1024 bytes）、命名規則、`description` が `"Use when"` で始まることを検証。 |
| **`test_mutating_skill_boundaries.py`** | `tests/` | 2 tests | 変更系Skill（archiver, domain-modeling）の承認境界を検証。 |
| **`test_report_validator.py`** | `.agents/skills/code-understanding-pro/tests/` | 9 tests | `scripts/validate_report.py` のバリデーションロジック（必須8節、SQL/統計アダプター固有節、Mermaid構文、根拠ファイル形式、バンドルテンプレート全件検証）を検証。 |
| **`test_report_writer.py`** | `.agents/skills/code-understanding-pro/tests/` | 36 tests | `scripts/write_report.py` のアトミック書き込み、排他制御（`.incomplete`）、ディレクトリfsync、機密情報伏字化（`[REDACTED]`）、Context成果物生成を検証。 |

> **変更しないWriterの確認範囲と安全条件**:
> - `write_report.py` 本体のコードは一切変更しない（不変境界）。そのため、36件の `test_report_writer.py` を別環境で網羅実行したり独立QAを必須化したりする必要はない（ローカル環境で実行可能な範囲で確認し、macOS Sandbox等の環境制約がある場合は未実施であることを記録する）。
> - ただし、軽量化後の `SKILL.md` から正本 [references/interface.md](../../.agents/skills/code-understanding-pro/references/interface.md) へのリンクを明記し、Quick Modeの保存禁止、機密情報の伏字化（`[REDACTED]`）、`.incomplete` による排他制御などの安全条件・事前確認は本文中に必ず保持する。

### 2.2 対象ファイルの現行スナップショット（実装前基準値）

| 対象ファイル | 現行行数 | 現行サイズ | 現行 SHA-256 ハッシュ値 |
| --- | ---: | ---: | --- |
| `code-understanding-pro/SKILL.md` | 642行 | 21,730 bytes | `7da5c3ed8a1bd176e4b6105b4746260e3934036b89bd1d05c80547db927117e3` |
| `code-understanding-pro/README.md` | 44行 | 2,139 bytes | `c282244a0ff4ce28b27fb0ea3a32b3f19f55ad5947d70e2b7617ae93f84db7d2` |
| `code-understanding-pro/VERSION` | 1行 | 9 bytes | `6abfaef386cc8ff762538f7eebe53dce557ecebb60e33c91cc8de8bc2e821504` |
| `code-understanding-pro/manifest.json` | 30行 | 1,079 bytes | `b91d58d00bcc042d0f7b34e4ca4b2d13349a4b6fe05a0374d66985b383e0ab54` |

### 2.3 バンドルテンプレートと Single Source of Truth
[tests/test_report_validator.py](../../.agents/skills/code-understanding-pro/tests/test_report_validator.py) の `test_bundled_templates_satisfy_contract` により、以下のテンプレートが `validate_report.py` の必須8節（COMMON_SECTIONS）を満たすことが**自動テストで恒常的に保証されている**。

- `assets/output-template-beginner.md`
- `assets/output-template-full.md`
- `assets/output-template-review.md`
- `assets/output-template-refactoring.md`
- `../stats-sql-comprehension/assets/output-template-sql.md`
- `../stats-sql-comprehension/assets/output-template-stats.md`

現行 `SKILL.md` 本文内のインライン Markdown 雛形（`## Step 0: 文脈` 等）は、バリデータが要求する `COMMON_SECTIONS` と見出しが異なっており、実質的な二重定義かつ乖離の原因となっていた。これを削除し `assets/` 配下のテンプレート参照に一本化することで、Single Source of Truth を確立する。

### 2.4 保持が絶対必須の契約トークン（Invariants）
`tests/test_code_understanding_suite_contract.py` により、以下のキーワードおよび文字列は `code-understanding-pro/SKILL.md` 内に**完全一致で存在しなければならない**。

1. **スイート契約キーワード**:
   - `"親Skill"`
   - `"references/interface.md"`
   - `"report.md"`
   - `"source_manifest.json"`
   - `"同じSkill配置ルート"`
   - `"親Skill単独の一般分析"`
2. **一般コードレビュー重大度語彙（完全一致）**:
   - `"[Critical]"`
   - `"[Major]"`
   - `"[Consider]"`
   - `"[Nit]"`
   - `"[FYI]"`
3. **旧レポート命名の禁止**:
   - `code_understanding_report.md`、`code_review_report.md`、`code_documentation.md`、`refactoring_proposal.md` を一切含めないこと。

---

## 3. 肥大化箇所の詳細内訳と削減マトリクス

### 3.1 行数内訳と改修方針

| 行範囲 | セクション名 | 現行行数 | 現状の課題 | 改修方針 | 改修後予定行数 |
| --- | --- | ---: | --- | --- | ---: |
| 1〜6 | front matter | 6行 | `license` が存在 | バージョンを更新（`2.2.0-ja`）し、`license` は維持 | 6行 |
| 8〜40 | 目的・起動条件 | 33行 | 冗長な表現 | 目的とトリガー表現を整理し Leading Words を強化 | 約20行 |
| 42〜110 | コア原則 | 69行 | 自明ルールの重複 | 事実/推論の分離、証拠優先、非破壊性の3原則に凝縮 | 約20行 |
| 112〜134 | 開始ゲート・モード判定・境界 | 23行 | 良好 | 優先度判定と実行境界ルールを維持 | 約20行 |
| 135〜345 | 5段階ピラミッド詳細 (Step 0〜4A) | 211行 | **最大肥大要因**。Step毎のMarkdown出力雛形がベタ書き | ピラミッド概念とコア調査項目のみ残し、雛形は `assets/output-template-full.md` を参照 | 約35行 |
| 347〜363 | スイート内の役割分担 | 17行 | アダプター表の縮退リスク | 必須トークンに加え、SQL/Stats アダプターの固有節・テンプレート参照先を明確化 | 約20行 |
| 365〜450 | 出力契約・保存・CLI・機密伏字化 | 86行 | `references/interface.md` と重複 | 必須トークン、最小CLI構文、機密伏字化チェックリストを残し、詳細は `interface.md` へ委譲 | 約30行 |
| 451〜486 | 4B(リファクタ), 4C(レビュー) | 36行 | レビュー語彙・フォーマット | 重大度語彙（`[Critical]`〜`[FYI]`）と指摘の必須項目（場所、根拠、修正案、テスト）を維持 | 約20行 |
| 488〜554 | モード選択 (Quick〜Refactor) | 67行 | 他セクションと二重定義 | モード判定表と成果物マトリクスに統合。Documentation モードの構成要件を明記 | 約15行 |
| 556〜608 | 特別ルール (Mermaid等) | 53行 | 冗長だが基準が必要 | 複雑度判定基準（`complex` / `simple` の5条件）を保持 | 約15行 |
| 610〜642 | 禁止事項・追加参照ファイル | 33行 | 良好 | 相対リンク一覧を整理・維持 | 約15行 |
| **合計** | | **642行** | | | **約190〜210行** |

### 3.2 Step 0〜4 の分解と移行先対応表

現行の Step 0〜4（135〜345行）は肥大化の主因（約211行）であるが、単なる機械的削除ではなく、**「出力形式の重複」**、**「読解手順・調査観点の指示」**、および **「親Skill固有の保存・検証手順」** の3要素に明確に分解して再配置する。

| 分解区分 | 現行の具体例 | 課題・分析 | 移行先・再配置方針 |
| --- | --- | --- | --- |
| **① 出力形式の重複** | `## Step 0: 文脈` 〜 `## Step 3: 深い設計理解` のインライン雛形ブロック（約120行） | バリデータの必須8節（`COMMON_SECTIONS`）と見出しが乖離し、二重定義と出力不整合の原因となっていた | **完全削除し正本へ集約**。`assets/output-template-full.md` 等のバンドルテンプレート参照に一本化 |
| **② 読解手順・調査観点の指示** | 「確認するもの（入出力・外部依存・副作用）」「分析するもの（トレードオフ・リスク）」 | コード理解・調査の思考順序・完了判断基準として不可欠なドメイン知見であり、削除してはならない | **調査順序・完了条件・判断基準として凝縮保持**。`## 読解プロセス（5段階ピラミッド）` に体系的に集約（詳細は下位Skill `code-understanding-pyramid` にも存在） |
| **③ 親Skill固有の保存・検証手順** | Step 4 の成果物生成、CLIコマンド、機密マスキング、事後検証 | レポート永続化と品質保証を担う親Skillの責務 | **独立セクションとして明確化**。`## 成果物の保存・検証・安全運用` に集約し、正本 `references/interface.md` へ委譲 |

---

## 4. 改訂版 `code-understanding-pro/SKILL.md` の設計仕様案

```markdown
---
name: code-understanding-pro
description: Use when a user asks to understand, review, document, explain, or safely refactor existing code in Japanese.
version: "2.2.0-ja"
license: "Internal use"
---

# code-understanding-pro

## 目的 & コア原則
このSkillは、既存コードを段階的に理解し、レビュー・QA・ドキュメント化・安全なリファクタリングを支援する。
1. **事実と推論の厳格な分離**: コード上の直接事実、推論、未確認事項、リスクを峻別する。設計意図を根拠なく断定しない。
2. **プロジェクト文脈優先**: 一般論より、テスト、型、呼び出し元、設計メモ、Git履歴を証拠として最優先する。
3. **非破壊性と実行境界**: ユーザーの明示的承認なしにファイル変更・コード実行を行わない。テスト実行も副作用を確認後に行う。

## モード判定と成果物契約
依頼内容に基づき、上から最初に合致するモードを採用する。
| 優先 | モード | 判定条件 | 主な成果物・出力仕様 | 必読参照資料 |
|---:|---|---|---|---|
| 1 | Refactoring | 改善・構造修正・変更比較 | `assets/output-template-refactoring.md` | [安全確認](references/refactoring-safety-checklist.md) |
| 2 | Review | レビュー・QA・バグ・マージ判断 | `assets/output-template-review.md` | [重大度基準](references/review-severity-guide.md) |
| 3 | Documentation | README・仕様書・DocString | `report.md`（概要/API/フロー/入出力例/制約/本文） | [Python](assets/docstring-template-python.md) / [R](assets/docstring-template-r.md) |
| 4 | Full | 複数ファイル・深層読解・オンボーディング | `assets/output-template-full.md` | [ピラミッド](references/qiita-code-reading-pyramid.md) |
| 5 | Quick | 単一関数・短い質問（上記以外） | チャット回答のみ（成果物保存なし） | [Quickテンプレート](assets/output-template-quick.md) |

> **Documentation モードの保存要件**: `report.md` を保存する場合は、必須8節を満たした上で `## 詳細` 配下に生成ドキュメント本文および入出力例・制約を配置する。

## 読解プロセス（5段階ピラミッド）
分析は必ず Step 0 から順に実施し、各ステップの完了条件を満たしてから次へ進む。
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
以下に該当する場合は複雑度を `complex` と判定し、Mermaid図（`flowchart TD` 等）を作成する。非該当の場合は `simple` とし文章フローで記載する。
- 主要ステップが3つ以上ある
- 分岐やループがある
- 複数クラス/モジュールが相互作用する
- データ変換が理解の中心である
- 非同期処理やシーケンスが重要である

## スイート連携（親Skill契約）
`code-understanding-pro` はコード理解スイートの親Skillであり、成果物の所有・保存・検証・チャット要約を集約する。
- **共通理解フレーム**: 下位Skill `code-understanding-pyramid` を同一セッション内で参照し、理解の順序として利用する。下位Skill単独の成果物ディレクトリや独立回答は作成させない。
- **SQL / 統計アダプター委譲**:
  - SQL（dbt/CTE/ウィンドウ関数）: `stats-sql-comprehension` へ委譲（`--adapter sql`）。テンプレートは `../stats-sql-comprehension/assets/output-template-sql.md` を使用し、データ粒度・CTE一覧・JOIN変化・検証SQLを必須統合。
  - 統計解析（R/Python）: `stats-sql-comprehension` へ委譲（`--adapter stats`）。テンプレートは `../stats-sql-comprehension/assets/output-template-stats.md` を使用し、対象母集団・欠測除外・推定量前提・バイアス・再現コードを必須統合。
- **配置境界**: 下位Skillが同じSkill配置ルートに存在しない場合は、利用不可を明記した上で親Skill単独の一般分析として続行する。

## レビュー重大度語彙（一般コードレビュー）
Review モードでは指摘を以下に分類し、各指摘に **[分類 / 場所(ファイルと行番号) / 根拠 / 修正案 / 実行すべきテスト]** を必ず明記する。
- **[Critical]**: マージ不可。セキュリティ脆弱性、データ損失、重大な正確性バグ、契約違反。
- **[Major]**: 強く修正推奨。実害リスクの高いバグ、重要テスト不足、重大な保守性問題。
- **[Consider]**: 検討価値あり。設計・可読性・構造改善。
- **[Nit]**: 任意修正。スタイル、軽微な命名、フォーマット。
- **[FYI]**: 情報提供のみ。アクション不要。

## 成果物の保存・検証・安全運用
Full、Review、Documentation、Refactoring では `report.md`、`run_meta.json`、`source_manifest.json` を保存する。
詳細な排他制御・機密伏字化規則は正本 [references/interface.md](references/interface.md) を参照。

### 保存前安全チェックリスト（必須）
1. **機密情報の伏字化**: 保存前にAPIキー、Bearerトークン、パスワード、秘密鍵を必ず `[REDACTED]` に置換する。未閉じクォート等の曖昧な形式は保存を中止する（fail-closed）。
2. **Quick Modeの分離**: Quick Modeを保存CLIへ渡してはならない（チャットのみで完結）。
3. **事後検証**: 保存後は必ず `validate_report.py` を実行し、合格するまで完了報告しない。

```bash
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
```

---

## 5. タスクリスト

### Phase 0: 実装前スナップショットの退避（Pre-mutation Snapshot）
- [x] **Task 0.1**: 対象ディレクトリ（`.agents/skills/code-understanding-pro/`）について `git diff` を実行し、既存の未コミット変更の有無を確認（存在する場合は `.tmp_pre_mutation_backup/pre_existing.patch` として退避）。
- [x] **Task 0.2**: 対象4ファイル（`SKILL.md`, `README.md`, `VERSION`, `manifest.json`）を一時退避ディレクトリ（`.tmp_pre_mutation_backup/`）にコピー退避し、実装前SHA-256ハッシュ値を記録。

### Phase 1: 参照ドキュメントとマニフェストの整合性確認
- [x] **Task 1.1**: [references/interface.md](../../.agents/skills/code-understanding-pro/references/interface.md) が出力契約の正本として、`run_meta.json`、`source_manifest.json`、機密マスキング、排他制御要件を漏れなく網羅していることを確認。
- [x] **Task 1.2**: [code-understanding-pro/README.md](../../.agents/skills/code-understanding-pro/README.md) のファイルツリー図に `references/interface.md` を追加。

### Phase 2: `code-understanding-pro/SKILL.md` の改訂
- [x] **Task 2.1**: Step 0〜3 内のインライン Markdown 出力例を削除し、`assets/output-template-full.md` への参照に一本化。
- [x] **Task 2.2**: モード判定表を整備し、Documentation モードの構成仕様（8必須節との統合）を明記。
- [x] **Task 2.3**: 契約テスト必須トークン（`親Skill`, `references/interface.md`, `report.md`, `source_manifest.json`, `同じSkill配置ルート`, `親Skill単独の一般分析`, `[Critical]`, `[Major]`, `[Consider]`, `[Nit]`, `[FYI]`）が完全に含まれていることを確認。
- [x] **Task 2.4**: 保存前マスキング責務（`[REDACTED]`）、Mermaid判定5条件、レビュー指摘フォーマット（場所・根拠・修正案・テスト）を明記。
- [x] **Task 2.5**: front matter の version を `2.2.0-ja` に更新し、`license: "Internal use"` を維持。

### Phase 3: バージョン・マニフェスト整合性の更新
- [x] **Task 3.1**: `.agents/skills/code-understanding-pro/VERSION` を `2.2.0-ja` に更新。
- [x] **Task 3.2**: `.agents/skills/code-understanding-pro/manifest.json` の version を `2.2.0-ja` に更新し、`files` 一覧が実ファイルと完全一致していることを確認。

### Phase 4: 静的契約テストおよび検証コマンド実行
- [x] **Task 4.1**: 契約テストスイート（20 tests）の実行
  ```bash
  python3 -B -m pytest -p no:anyio --assert=plain -p no:cacheprovider \
    tests/test_code_understanding_suite_contract.py \
    tests/test_skill_inventory_contract.py \
    tests/test_skill_frontmatter.py \
    tests/test_mutating_skill_boundaries.py \
    .agents/skills/code-understanding-pro/tests/test_report_validator.py -q
  ```
- [x] **Task 4.2**: `git diff --check` による空白・構文エラーの確認。
- [x] **Task 4.3**: 行数確認（`wc -l .agents/skills/code-understanding-pro/SKILL.md` で約180〜210行以内であることを確認）。

### Phase 5: 代表ケースによる動的受入検証（隔離環境・普段利用する3ケース）
- [x] **Task 5.1**: TC-01（Quick Mode）: チャットのみで要約、主要ロジック、入出力を返し成果物保存を行わないことを確認。
- [x] **Task 5.2**: TC-02（Full Mode）: `--output-root` に一時ディレクトリ（例: `/tmp/code_understanding_eval`）を指定してレポートを生成し、`validate_report.py` が PASS することを確認。
- [x] **Task 5.3**: TC-03（Review Mode）: 既知の軽微な問題を含む固定サンプルを目視確認し、重要度、場所、根拠、修正案、テストが自然に出力されることを確認。
- [x] **Task 5.4**: 検証完了後、一時出力ディレクトリ（`/tmp/code_understanding_eval` 等）およびバックアップディレクトリ（`.tmp_pre_mutation_backup/`）を安全に清掃。

---

## 6. 動的受入基準と代表ケース比較検証

目標行数の達成や静的テストの通過だけでなく、エージェントの分析・出力機能が日常業務で劣化していないことを、**作業ツリーを汚さない隔離出力先（`--output-root /tmp/...`）** を用いて確認する。

### 6.1 代表ケース比較マトリクス（普段利用する範囲に集約）

| ケースID | 対象モード | 入力対象コード例 | 検証項目（受入基準） | 隔離出力先・確認方法 | 合否判定条件 |
|---|---|---|---|---|---|
| **TC-01** | Quick Mode | 単一のユーティリティ関数（例: 文字列フォーマット関数） | チャットのみで要約、主要ロジック、入出力、注意点を回答すること。 | ファイル保存CLIを実行しない | ファイル生成なし、要約と入出力が明確 |
| **TC-02** | Full Mode | 複数クラス・分岐を含むアルゴリズム | `assets/output-template-full.md` に基づき8必須節を満たすレポートを作成。 | `--output-root /tmp/code_understanding_eval` を指定 | `validate_report.py` が PASS |
| **TC-03** | Review Mode | 下記の固定サンプルコード（ゼロ除算・空リストリスク） | `[Critical]`〜`[FYI]` の語彙を用い、指摘に「場所（行番号）、根拠、修正案、テスト」が含まれること。 | 目視確認 | 指摘フォーマット（重要度・場所・根拠・修正案）が自然に出力される |

#### TC-03 固定サンプルコード（目視確認用）
```python
# sample_for_review.py
def calculate_ratio(values: list[float], divisor_override: float | None = None) -> float:
    total = divisor_override if divisor_override is not None else sum(values)
    # [Major] values が空リストの場合に IndexError、total が 0 の場合に ZeroDivisionError のリスク
    return values[0] / total
```
- **期待される出力**:
  - 重大度: `[Major]`（または実害度に応じた `[Critical]`）
  - 場所: `sample_for_review.py:4`（または該当行）
  - 根拠: `total == 0` 時の `ZeroDivisionError` および `not values` 時の `IndexError`
  - 修正案: ガード節（例: `if not values or total == 0: return 0.0`）の追加
  - テスト: 空リスト `[]` および合計が0のリスト `[0.0, 0.0]` を渡すユニットテストの提示

> **スコープ外のケースについて**: SQL/Stats アダプター、委譲不能時フォールバック、run ID衝突処理は、今回の改修でルーティング規則やスクリプトコードに一切触れていないため、今回の実装前検証からは除外する（日常利用時または不具合検知時に必要に応じて確認）。

---

## 7. 残余リスクと対策（Residual Risks & Mitigations）

| リスク要因 | 潜在的影響 | 軽減・防止対策（Mitigations） |
|---|---|---|
| **外部参照の読み落とし** | テンプレートやリファレンスが別ファイル化されたことで、LLMが参照を怠り自己流の見出しで出力する。 | モード判定表および各セクションに「必読資料」としてリンクを明記し、事後検証CLI（`validate_report.py`）の実行とPASSを必須完了条件（Hard Gate）とする。 |
| **指示圧縮による推論粗雑化** | コア原則の要約により、推測の断定やエッジケースの看過が発生する。 | 「事実と推論の厳格な分離」および「推測時は必ず推測と明記する」ルールをコア原則の第1項に維持。読解プロセス各Stepに調査項目と完了条件を明記。 |
| **機密マスキング漏れ** | 手順の要約により、保存前の伏字化を怠る。 | 保存前チェックリストに「APIキー・シークレットの `[REDACTED]` 化」および未閉じクォート等の曖昧形式での fail-closed 処理を明示。 |

---

## 8. 安全なロールバック手順（Safe Rollback Plan）

### 8.1 ロールバック原則
- **ユーザー変更の保護**: 対象ファイル全体への安易な `git restore` は厳禁とする。作業開始前に退避したスナップショット（`.tmp_pre_mutation_backup/`）との差分を比較し、**本改修で追加された差分のみを反転** する。
- **コンフリクト検知時のフェイルセーフ**: 万が一、改修中に対象ファイルへユーザーによる追加変更が検知された場合は、自動復元を実行せず、差分（diff）を表示して即座に停止し、ユーザーの指示を仰ぐ。

### 8.2 ロールバック実行コマンド例

```bash
# 1. バックアップディレクトリの存在確認
if [ ! -d ".tmp_pre_mutation_backup" ]; then
  echo "エラー: 事前バックアップディレクトリが見つかりません。手動で差分を確認してください。" >&2
  exit 1
fi

# 2. 現在の差分を確認（予期せぬユーザー変更の有無を点検）
echo "=== 現在の変更差分 ==="
git diff -- .agents/skills/code-understanding-pro/

# 3. 事前バックアップから本改修対象の4ファイルのみを安全に復元
cp .tmp_pre_mutation_backup/SKILL.md .agents/skills/code-understanding-pro/SKILL.md
cp .tmp_pre_mutation_backup/README.md .agents/skills/code-understanding-pro/README.md
cp .tmp_pre_mutation_backup/VERSION .agents/skills/code-understanding-pro/VERSION
cp .tmp_pre_mutation_backup/manifest.json .agents/skills/code-understanding-pro/manifest.json

# 4. SHA-256 ハッシュ値が事前スナップショットと完全一致することを確認
shasum -a 256 \
  .agents/skills/code-understanding-pro/SKILL.md \
  .agents/skills/code-understanding-pro/README.md \
  .agents/skills/code-understanding-pro/VERSION \
  .agents/skills/code-understanding-pro/manifest.json

# 5. 事前バックアップの清掃
rm -rf .tmp_pre_mutation_backup

# 6. 復元後の契約テストスイート実行による正常性確認（全20 tests PASS）
python3 -B -m pytest -p no:anyio --assert=plain -p no:cacheprovider \
  tests/test_code_understanding_suite_contract.py \
  tests/test_skill_inventory_contract.py \
  tests/test_skill_frontmatter.py \
  tests/test_mutating_skill_boundaries.py \
  .agents/skills/code-understanding-pro/tests/test_report_validator.py -q
```
