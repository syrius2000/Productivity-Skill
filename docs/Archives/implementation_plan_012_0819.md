# Skill配置・spec-driven-qa-review改善実装計画

created: 2026-08-19 21:55 (JST)
update: 2026-08-19 23:18 (JST)
author: Codex (GPT-5)

## 目的

グローバル配置されている `artifacts-archiver` と `spec-driven-qa-review` を、`Productivity-Skill` リポジトリの `.agents/skills/` 配下で正本として管理できる状態にする。あわせて、`spec-driven-qa-review` の現行パッケージを評価し、実利用時の再現性・検証可能性・運用上の不足を根拠付きで改善する。

## 現状確認

- 対象リポジトリ: `Productivity-Skill`
- 現在のブランチ: `master`
- ローカル追跡先: `origin/master`
- ローカルとリモート追跡ブランチ: ともに `bc05359`（`refine code understanding pyramid guidance`）
- 計画作成時の作業ツリー: クリーン（計画書作成後の現行差分は別途記録する）
- リモート: `https://github.com/syrius2000/Productivity-Skill.git`
- リモートリポジトリ: 公開、既定ブランチ `master`
- 現在のリポジトリ内Skill: 7件
- `~/.agents/skills/artifacts-archiver`: `SKILL.md`のみの1ファイル構成
- `~/.agents/skills/spec-driven-qa-review`: `MANIFEST.txt`で定義された生成物を除く正本55ファイル構成。確認時の56ファイルは生成物を含む一時的な件数である
- `spec-driven-qa-review`の提供元テスト: 3件成功

## 対象範囲

### 配置対象

1. `~/.agents/skills/artifacts-archiver/` の完全な内容を `.agents/skills/artifacts-archiver/` に配置する。
2. `~/.agents/skills/spec-driven-qa-review/` の完全な内容を `.agents/skills/spec-driven-qa-review/` に配置する。
3. `spec-driven-qa-review` の `__pycache__` 等の生成物は正本に含めない。

### リポジトリ文書・検証

1. `README.md` の収録件数、Skill一覧、ディレクトリ構造、説明を実体と一致させる。
2. `README.md` の現行状態参照を、現行Skill一覧と責任分担を含む現存文書またはアーカイブ概要への相対リンクへ修正する。アーカイブ済みの `repository_current_state_012_0724.md` は再作成しない。
3. 既存のフロントマター検証を新規Skillにも適用できるよう、必要最小限のテストを追加・調整する。
4. `MANIFEST.txt` を正本ファイル集合とし、`__pycache__`、`.pytest_cache`、`*.pyc`、OS固有ファイル等の生成物を除外して、配置前後の欠落・余剰を検出する検証を追加する。

### `spec-driven-qa-review` の改善

改善対象は、実装前に現行パッケージをベースラインとして評価したうえで確定する。初回候補は次のとおりとする。

- Skill自身をQA対象にした場合でも、対象範囲・基準リビジョン・役割分離・証拠の強度を取り違えない自己適用手順の明確化
- `MANIFEST.txt`、スキーマ、テンプレート、スクリプト、テストの構成整合性を確認するパッケージ自己検証の明文化
- `AUTHOR-CLAIM`、`CONFIRMED`、`INFERRED`、`UNVERIFIED` 等の証拠分類と、closure判定の対応をテスト可能な形に整理
- `REQUIRED:` の履歴記録と解消済み状態を区別し、過去サイクルの記録を残したまま検証できる運用例の強化
- README、インストール手順、SKILL.md、補助スクリプトの責任分担・実行例の不一致があれば修正

候補をすべて無条件に採用せず、ベースライン評価で再現する問題、回帰リスク、利用者にとっての効果を比較して採用範囲を決める。

改善評価は各シナリオについて、入力、期待動作、必須証拠、Assertionまたは定性的判定基準、旧版との比較方法、成果物保存先を定義する。判定不能な項目は`not-assessable`として記録し、合格扱いにしない。

## 実施手順

### 第1段階: 配置と正本化

1. 作業開始時に `git diff` と `git status --short --branch` を確認する。
2. 2つのグローバルSkillをリポジトリ内へ完全コピーする。
3. 配布元のマニフェストと配置先のファイル一覧を比較する。
4. Python生成物、OS固有ファイル、秘密情報が混入していないことを確認する。

### 第2段階: 改善前ベースライン

1. `spec-driven-qa-review` の既存テストを実行する。
2. `MANIFEST.txt`を基準に、正本55ファイルの欠落・余剰、JSONスキーマ、テンプレート、補助スクリプトを静的に検証する。
3. 2〜3件の実利用シナリオを、次の契約で評価する。
   - 明示ファイルを対象にした標準QA。期待結果は対象範囲、証拠分類、Finding、トレーサビリティが記録されること。
   - PurposeまたはSpecが不足する場合のintent-recovery。期待結果は`INSUFFICIENT-CONTEXT`または`SCOPE-LIMITATION`が記録され、推測を確定扱いしないこと。
   - REQUIREDマーカーを含む複数サイクルの再検証とclosure判定。期待結果は未解決マーカーがclosureを阻止し、解消済み履歴は`RESOLVED:REQUIRED:`として追跡可能であること。
   - 各シナリオのAssertion、判定結果、実行条件、成果物を`docs/ADR/QA/QA-0001-plan-012-skill-placement/evidence/`へ保存する。
4. 各シナリオで、対象範囲の逸脱、著者主張の過信、証拠不足、履歴破壊、検証漏れを記録する。
5. 改善前のSkillをスナップショットとして保存し、改善後との比較基準にする。

### 第3段階: 改善実装

1. 第2段階で再現した問題に限定して、SKILL.md、参照資料、テンプレート、補助スクリプト、テストを最小限修正する。
2. Skillの名称と既存の基本契約は維持する。
3. 互換性を壊す変更、対象範囲の拡大、外部システムへの書き込みは別計画・別承認とする。
4. `CHANGELOG.md` に変更理由、影響範囲、検証結果を追記する。

### 第4段階: 独立検証

1. 配置先のSkillテストとリポジトリ全体のテストを実行する。
2. マニフェストの全ファイル存在、フロントマター、JSONスキーマ、Python構文、Markdown空白を検証する。
3. 改善前スナップショットと改善後で同じ評価シナリオを再実行する。
4. 改善により解消した問題、未解決の制約、残余リスクを区別して記録する。
5. 実装差分と検証結果を確認し、必要なら完了報告Artifactを作成する。

## 完了条件

- `.agents/skills/artifacts-archiver/` が配布元と同じ正本内容で管理されている。
- `.agents/skills/spec-driven-qa-review/` が生成物を除く配布元の完全パッケージとして管理されている。
- READMEのSkill件数・一覧・説明・現行状態リンクが実体と一致している。アーカイブ済みの現行状態文書は再作成しない。
- 配置先のテスト、既存リポジトリテスト、パッケージ整合性検証が成功している。
- `spec-driven-qa-review` の改善内容が、改善前後の具体的な証拠とともに記録されている。
- 未解決のHigh/Critical相当の問題、closureを妨げる `REQUIRED:`、または証拠不足による判定不能が明示されている。
- `git diff --check` が成功している。
- コミット、push、公開、外部リポジトリへの書き込みは、別途明示承認を得るまで実施しない。

## 承認境界

この文書の作成と読み取り専用調査は承認前に実施してよい。以下は明示的な実行承認後にのみ行う。

- `.agents/skills/` への2Skillの配置
- `README.md`、現行状態Artifact、テスト、Skill本体・参照資料・スクリプトの変更
- 評価用ワークスペースやスナップショットのリポジトリ内作成
- Gitのstage、commit、push

対象範囲、改善方式、評価シナリオ、変更ファイルが変わる場合は、本計画を更新して再承認を得る。

## ロールバック方針

承認後の変更を取り消す場合は、当該実装ラウンドで追加したファイル・差分だけを対象にする。作業開始時点の既存変更が確認された場合は保持し、ファイル全体の復元や広範な削除は行わない。
