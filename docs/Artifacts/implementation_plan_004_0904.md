# Productivity-Skill全体の機能向上計画

created: 2026-09-04 18:00 (JST)
update: 2026-09-04 18:07 (JST)
author: Codex (GPT-5)

## 目的

リポジトリ内の全Skillについて、不備・不足・改善余地を体系的に確認し、起動条件、指示の予測可能性、補助資料の参照性、出力契約、境界条件、版情報、テスト可能性を改善する。既存の有用な能力とユーザーの承認境界は維持する。

## 現状確認

- `.agents/skills/*/SKILL.md`は11個存在する。
- `README.md`は収録数を「10 Skills」と記載し、`spec-driven-qa-review`を一覧とディレクトリ例に含めていない。
- `code-understanding-pro/SKILL.md`は642行で、複数モード・出力契約・参照資料・スクリプトの説明が集中している。
- Skillのfront matter、manifest、VERSION、参照先、実行スクリプト、テストの横断的な整合性検証は限定的である。
- 現時点ではコード、Skill本文、設定、データ、外部システムへの変更は行っていない。

## 対象範囲

### 主対象

- `.agents/skills/*/SKILL.md`
- 各Skillの`agents/`、`references/`、`assets/`、`scripts/`、`templates/`、`schemas/`、`manifest.json`、`VERSION`
- `README.md`
- `tests/`および必要なSkill内テスト

### 対象Skill

- `artifacts-archiver`
- `code-understanding-pro`
- `code-understanding-pyramid`
- `domain-modeling`
- `grilling`
- `quality-response`
- `quality-review`
- `spec-driven-qa-review`
- `stats-sql-comprehension`
- `teach`
- `writing-great-skills`

### 変更しない対象

- ユーザーが作成した既存差分および無関係な未追跡ファイル
- 外部リポジトリ、リモート設定、GitHub上のIssue・PR・Release
- commit、push、デプロイ、公開、Skillのグローバル配置
- 実データ、認証情報、ユーザー環境の設定

## 実施方針

### 1. 全体インベントリと基準化

- 実在するSkillとREADME記載のSkillを突合する。
- 各Skillのfront matter、起動方式、責務、入力、出力、承認境界、補助資料、依存関係、版情報、テスト有無を表形式で整理する。
- READMEの件数・一覧・ディレクトリ例を実体に合わせる。
- 自動検証に適した不変条件と、人間またはLLMによる評価が必要な品質項目を分離する。

完了条件：11個すべてのSkillについて、対象ファイル・起動方式・責務・不足証拠が一覧化され、READMEとの不一致が列挙されている。

### 2. 起動・指示文・参照設計のレビュー

- descriptionが実際の適用条件を識別できるか確認する。
- model-invokedとuser-invokedの選択が責務と一致しているか確認する。
- 複数モードのSkillについて、常時読むべき手順と条件付き参照資料を分離できるか評価する。
- 重複、環境から取得できる情報の再掲、弱い禁止表現、完了条件の曖昧さ、不要な普遍ルールを確認する。
- Skill間のルーティング、親Skill・専門Skillの境界、単独起動時の扱いを確認する。

完了条件：各Skillについて、修正候補が「起動」「本文」「参照分割」「境界」「変更不要」のいずれかに分類され、根拠と優先度が付いている。

### 3. 契約・パッケージ・実行性のレビュー

- 参照リンクと参照先ファイルの存在を確認する。
- manifestのファイル一覧、front matter、manifest、VERSIONの版情報を突合する。
- スクリプトの入口、ヘルプ、エラー境界、生成物、キャッシュや一時ファイルの扱いを確認する。
- `spec-driven-qa-review`、`quality-review`、`quality-response`の状態機械・Role境界・外部操作境界を確認する。
- 生成物の保存先、相対リンク、既存差分保持、承認ゲートが本文とテストで一致しているか確認する。

完了条件：機械検証へ追加する契約と、動的評価が必要で未検証として残す項目が分離される。

### 4. 改善案の優先順位付け

以下の順で優先する。

1. 誤起動、責務逸脱、データ損失、外部操作、承認境界の破綻
2. 参照先欠落、パッケージ不完全、版情報不整合、実行不能
3. README・一覧・ルーティングの不一致
4. 出力品質、再現性、テスト不足
5. 可読性、重複削減、細かな表現改善

完了条件：各候補に影響範囲、変更ファイル、検証方法、残余リスクが記載され、実装対象が確定している。

### 5. 承認後の実装

- 承認された対象と方式に限定して、Skill本文・補助資料・テスト・READMEを小さなラウンドに分けて編集する。
- 各編集ラウンドの開始時と終了時に`git diff`を確認する。
- 既存のユーザー変更を保持し、変更対象を明示する。
- 新規または改訂したSkillでは、必要に応じて独立した代表ケース評価を行う。

完了条件：承認済みの変更対象だけが編集され、各変更が対応する改善候補と検証項目に追跡可能である。

### 6. 検証と報告

- front matter、リンク、manifest、版情報、README一覧、境界契約を自動検証する。
- 変更したSkillのスクリプトと既存テストを実行する。
- 必要に応じて基準版と改訂版で同一の代表シナリオを比較する。
- 静的検証、ローカル実行結果、独立評価、未実施の動的LLM評価を区別して報告する。
- commit、push、公開は別途明示承認がある場合だけ行う。

完了条件：成功・失敗・未検証・残余リスクが混同されず、変更一覧と検証証拠を含む完了報告が作成されている。

## 想定される初回改善候補

監査で根拠を確認したうえで、次を候補とする。監査結果により採否を決める。

- READMEのSkill件数、一覧、ディレクトリ構造への`spec-driven-qa-review`追加
- 全Skillの実在ファイル・リンク・front matterを確認するリポジトリ契約テスト
- manifestまたはVERSIONを持つSkillの版情報・ファイル一覧検証の統一
- `code-understanding-pro`の共通手順とモード別詳細の再配置
- 各Skillのdescriptionと実際の単独起動可否の整合性改善
- Quality Loopおよびspec-driven QA系Skillの境界・状態遷移に対する回帰テスト拡充

## 実施しないこと

- 監査結果を待たずに全Skillを一括書き換えしない。
- 行数削減だけを品質改善の根拠にしない。
- 静的テスト成功だけでLLMの実動作や受入完了を断定しない。
- 承認されていないcommit、push、公開、削除、アーカイブを行わない。

## 承認と実施状態

本計画はユーザーの明示的な承認を受け、承認範囲内の実装と検証へ移行済みである。外部システムへの書き込み、commit、push、公開は引き続き未実施である。

## 今回の実施結果

ユーザー承認後、次の範囲を実装した。

- READMEの収録数を11へ修正し、欠落していた`spec-driven-qa-review`を一覧とディレクトリ例へ追加した。
- READMEの`code-understanding-pro`版表示を`2.1.0-ja`へ更新した。
- `quality-review`と`quality-response`のfront matterへ、既存の`VERSION`と一致する`1.4.0`を追加した。
- 全Skillの実在ディレクトリとREADME一覧の一致、Skill入口の相対Markdownリンク、manifest・VERSION・front matter・manifest掲載ファイルの整合性を検証する`tests/test_skill_inventory_contract.py`を追加した。

## 今回の検証結果

- `python -B -m pytest --assert=plain -p no:cacheprovider tests -q`：11件成功
- 全11Skillに対するSkill Creator標準の`quick_validate.py`：成功
- `git diff --check`：成功

## 未実施・残余リスク

- `code-understanding-pro`の本文分割・再配置は、今回の差分では未実施。機能変更を伴うため、モード別の代表ケース評価を先に行う必要がある。
- 全SkillのLLM動的評価、独立QA、commit、push、公開は未実施。
