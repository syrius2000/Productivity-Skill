# Productivity-Skill 正本化・重複Skill統合 実装計画

created: 2026-07-24 03:21 (JST)
author: AI Agent (Codex GPT-5)

> **実行担当Agentへの必須事項:** 本計画は承認後にタスク単位で実行する。各タスクの開始前後で `git status` と `git diff` を確認し、別タスクの変更を混在させない。

**目的:** `Productivity-Skill` を汎用Skillの正本とし、`rwd-mysql-skill-toolkit` に混在する重複Skillの最新版を安全に昇格・一本化する。

**アーキテクチャ:** Skillの正本を責任領域で分離する。汎用Skillは `Productivity-Skill`、VCD・エビデンス分析Skillは `agentic-evidence-analysis` を正本とし、`rwd-mysql-skill-toolkit` は両者とDB固有Skillを接続する「RWDデータワークフローの実行・統合ハブ」とする。`rwd-mysql-skill-toolkit` は汎用Skillを複製管理せず、外部依存として参照する。

**技術要素:** Git、Agent Skills、Markdown、Python 3、pytest、R、`npx skills`

---

## 1. 今回確認した現状

### 1.1 Gitの状態

- `Productivity-Skill`
  - ブランチ: `master`
  - HEAD: `07f24db`
  - リモート: `origin/master`
  - 現在のREADME修正が未コミットで存在する。
  - 本計画Artifactが未追跡ファイルとして追加される。
  - `rwd-mysql-skill-toolkit/` は外側repoから見ると未追跡の入れ子Gitリポジトリである。
- `rwd-mysql-skill-toolkit`
  - ブランチ: `main`
  - HEAD: `e844807`
  - `origin/main` と一致している。
  - リモートブランチ `origin/cursor/fix-run-output-overwrite-2961` は `main` にマージ済みである。
  - 未マージのローカルブランチは確認されなかった。

したがって、現在の問題は「未マージブランチが複数残っている」ことより、過去の統合履歴、正本の所在、複製Skillの責任境界が混在していることにある。履歴を書き換えるより、現行HEADを監査元として固定し、新しい統合ブランチで所有権を整理する。

### 1.2 重複Skill

両repoに存在するSkillは次の5個である。

| Skill | 推奨する正本 | 判断 |
| :--- | :--- | :--- |
| `code-understanding-pro` | `Productivity-Skill` | 内包repo版 `2.0.0-ja` を昇格する |
| `code-understanding-pyramid` | `Productivity-Skill` | 親Skillとの契約を含む内包repo版 `3.0.0` を昇格する |
| `stats-sql-comprehension` | `Productivity-Skill` | SQL・統計アダプター化された内包repo版 `2.0.0` を昇格する |
| `teach` | `Productivity-Skill` | 内包repo側の発動条件改善を取り込む |
| `writing-great-skills` | `Productivity-Skill` | 内包repo側の発動条件改善を取り込む |

`rwd-mysql-skill-toolkit` のREADMEは「20個」と記載しているが、実体は19ディレクトリであり、一覧にある `grilling` は存在しない。5個の重複を除くと、同repoが直接管理する候補は14個になる。

### 1.3 最新の code-understanding スイート

内包repoの次のコミットを最新版の基準とする。

- `e9eb045`: 3Skillの出力契約統合
- `7a17fb5`: pyramid重複翻訳の整理
- `e844807`: README・AGENTSの現状同期

`code-understanding-pro` だけをコピーすると契約が壊れるため、次を一つの変更単位として扱う。

1. `code-understanding-pro`
2. `code-understanding-pyramid`
3. `stats-sql-comprehension`
4. `code-understanding-pro` の単体テスト
5. 3Skill間の契約テスト

一般コードは `generic`、SQLは `sql`、R/Python統計コードは `stats` へ分岐し、成果物は親Skillの `report.md`、`run_meta.json`、`source_manifest.json` に統合する。

### 1.4 `.agent/shared` の状態

次の4ファイルは整理候補だが、現時点では削除・単純移動できない。

- `.agent/shared/analysis_quality_contract.md`
- `.agent/shared/inspect_data.R`
- `.agent/shared/run_scope.R`
- `.agent/shared/run_scope.py`

VCD、設問バッチ、ダッシュボード、テスト、README、AGENTSから参照されている。第一段階では現状維持し、Skill正本化が完了した後に別の変更単位として再配置する。

---

## 2. 選択肢

### 案A: 責任領域で正本を分離する（推奨）

- `Productivity-Skill`: 汎用Skillの正本
- `rwd-mysql-skill-toolkit`: DB固有Skillの正本かつRWDデータワークフローの実行・統合ハブ
- `agentic-evidence-analysis`: VCD・エビデンス分析Skillの正本
- toolkitから汎用Skillの追跡コピーを削除し、導入依存として案内する

**利点:** 正本が明確で、今後の改善先を迷わない。repo固有のテストや資産を無理に一か所へ集めない。

**注意点:** toolkit単独clone時は `Productivity-Skill` の導入手順が必要になる。

### 案B: すべてのSkillを `Productivity-Skill` に移す

**利点:** Skillファイルは一か所に集まる。

**欠点:** DB、R、SQL、テストデータ、プロジェクト固有スクリプトまで移動対象になり、`Productivity-Skill` が汎用ポートフォリオではなくモノレポ化する。今回の目的に対して範囲が大きすぎる。

### 案C: 両repoにコピーを残して同期スクリプトで管理する

**利点:** 各repo単独で全Skillを発見できる。

**欠点:** 同期漏れ、パス差分、どちらを編集すべきかという混乱が残る。今回の「このリポジトリを主にする」という目的に合わない。

**採用案:** 案A。

---

## 3. 全体制約

- 本計画の承認前にSkill本体、ブランチ、リモートを変更しない。
- `Productivity-Skill/rwd-mysql-skill-toolkit/` を外側repoへ `git add` しない。
- 既存のREADME修正は統合作業と別コミットにする。
- `rwd-mysql-skill-toolkit` の `main` をrebase、reset、force-pushしない。
- 削除前に対象パス、基準コミット、ファイルハッシュを記録する。
- 3Skillスイートは部分移行せず、一括で検証する。
- `.agent/shared` は第一段階で移動・削除しない。
- `rwd-mysql-skill-toolkit` は整理と全回帰テストの完了後、作業ブランチをリモートへPUSHし、確認後に `main` へ反映してPUSHする。
- PUSH直前にリモートが先行していた場合は処理を止め、force-pushで上書きしない。
- リモートブランチ削除は最終検証後の個別承認事項とする。
- 生成する文書は日本語、repo内リンクは相対パスとする。

---

## 4. 目標構成

### 4.1 `Productivity-Skill`

```text
.agents/skills/
├── code-understanding-pro/          # 親ルーター、成果物、検証
├── code-understanding-pyramid/      # 汎用理解フレーム
├── stats-sql-comprehension/         # SQL・統計アダプター
├── teach/
├── writing-great-skills/
└── ...                              # その他の既存汎用Skill
tests/
├── test_code_understanding_suite_contract.py
└── test_skill_frontmatter.py
docs/Artifacts/
└── implementation_plan_007_0724.md
```

### 4.2 `rwd-mysql-skill-toolkit`

```text
.agent/
├── skills/
│   ├── flat-file-mysql-*/
│   ├── mysql-*/
│   ├── anomaly-detection/
│   ├── questionnaire-batch-analysis/
│   ├── security-vulnerability-check/
│   └── vcd-*/                       # 統合検証用ミラー
└── shared/                          # 第二段階までは現状維持
```

次の5ディレクトリは検証完了後にtoolkitの追跡対象から外す。

```text
.agent/skills/code-understanding-pro/
.agent/skills/code-understanding-pyramid/
.agent/skills/stats-sql-comprehension/
.agent/skills/teach/
.agent/skills/writing-great-skills/
```

---

## 5. 実行タスク

### Task 0: 編集境界と監査基準を固定する

**対象:**

- `Productivity-Skill` HEAD `07f24db`
- `rwd-mysql-skill-toolkit` HEAD `e844807`
- 現在の `Productivity-Skill/README.md` 差分

- [ ] `Productivity-Skill` で `git status --short --branch` と `git diff -- README.md` を保存する。
- [ ] README修正だけをレビューし、統合変更と別コミットにするか、未コミットのまま保持するかを決める。
- [ ] 入れ子repoを外側repoのステージ対象にしないため、ローカル除外設定を確認する。
- [ ] 両repoで `git branch -avv`、`git worktree list --porcelain`、`git log --all --graph --oneline` を記録する。
- [ ] `rwd-mysql-skill-toolkit` の基準コミットを `e844807` に固定し、移行対象ファイルのSHA-256一覧を作る。

**検証コマンド:**

```bash
git -C /Users/myamaguchi/Programing/Productivity-Skill status --short --branch
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit status --short --branch
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit rev-parse HEAD
```

**期待結果:** 内側repoは `e844807` かつclean、外側repoではREADME差分、本計画Artifact、入れ子repoだけが既知の変更として識別される。

### Task 1: 統合ブランチを分離する

**対象ブランチ:**

- 外側repo: `codex/consolidate-productivity-skills`
- 内側repo: `codex/remove-duplicated-generic-skills`

- [ ] 両repoで最新リモート状態を取得し、基準コミットが変わっていないか再確認する。
- [ ] 外側repoで `codex/consolidate-productivity-skills` を作成する。
- [ ] 内側repoで `codex/remove-duplicated-generic-skills` を作成する。
- [ ] `rwd-mysql-skill-toolkit` の現在の `main` を保全用タグ候補として記録する。
- [ ] タグ作成、リモートブランチ削除、pushはこの時点では行わない。

**期待結果:** 既存の `master` / `main` を直接編集せず、repoごとに独立した差分を確認できる。

### Task 2: 最新の code-understanding スイートを `Productivity-Skill` へ昇格する

**変更元:**

- `rwd-mysql-skill-toolkit/.agent/skills/code-understanding-pro/`
- `rwd-mysql-skill-toolkit/.agent/skills/code-understanding-pyramid/`
- `rwd-mysql-skill-toolkit/.agent/skills/stats-sql-comprehension/`

**変更先:**

- `.agents/skills/code-understanding-pro/`
- `.agents/skills/code-understanding-pyramid/`
- `.agents/skills/stats-sql-comprehension/`

**追加・変更する主要ファイル:**

- Modify: `.agents/skills/code-understanding-pro/SKILL.md`
- Modify: `.agents/skills/code-understanding-pro/README.md`
- Modify: `.agents/skills/code-understanding-pro/VERSION`
- Modify: `.agents/skills/code-understanding-pro/manifest.json`
- Create: `.agents/skills/code-understanding-pro/references/interface.md`
- Create: `.agents/skills/code-understanding-pro/assets/output-template-beginner.md`
- Create: `.agents/skills/code-understanding-pro/scripts/write_report.py`
- Create: `.agents/skills/code-understanding-pro/scripts/validate_report.py`
- Create: `.agents/skills/code-understanding-pro/tests/test_report_writer.py`
- Create: `.agents/skills/code-understanding-pro/tests/test_report_validator.py`
- Modify: `.agents/skills/code-understanding-pyramid/SKILL.md`
- Delete: `.agents/skills/code-understanding-pyramid/code-understanding-pyramid-ja.md`
- Modify: `.agents/skills/stats-sql-comprehension/SKILL.md`
- Modify: `.agents/skills/stats-sql-comprehension/assets/`
- Modify: `.agents/skills/stats-sql-comprehension/manifest.json`

- [ ] 元と先のファイル一覧、サイズ、SHA-256を比較する。
- [ ] 既存の外側repo独自変更がないかファイル単位で確認する。
- [ ] `code-understanding-pro` を `2.0.0-ja` へ更新する。
- [ ] `code-understanding-pyramid` を `3.0.0` へ更新する。
- [ ] `stats-sql-comprehension` を `2.0.0` へ更新する。
- [ ] `generic`、`sql`、`stats` の分岐と共通出力契約を一括移行する。
- [ ] `.agent/` 固有パスを `.agents/` へ機械置換せず、各参照の意味を確認して修正する。
- [ ] マニフェストのファイル一覧と実体を同期する。

**期待結果:** 外側repoだけで3Skillスイートのルーティング、成果物作成、検証が完結する。

### Task 3: テスト契約を `Productivity-Skill` へ移す

**追加・変更ファイル:**

- Create: `tests/test_code_understanding_suite_contract.py`
- Create: `tests/test_skill_frontmatter.py`
- Modify: `.agents/skills/code-understanding-pro/tests/test_report_writer.py`
- Modify: `.agents/skills/code-understanding-pro/tests/test_report_validator.py`

- [ ] テスト内のSkillルートを `.agents/skills` に変更する。
- [ ] `generic`、`sql`、`stats` の必須見出しを検証する。
- [ ] Quick Modeがファイル保存を拒否することを検証する。
- [ ] 同一run IDで上書きしないことを検証する。
- [ ] シークレットが保存前に伏字化されることを検証する。
- [ ] `manifest.json` と `SKILL.md` のバージョン一致を検証する。
- [ ] 全Skillのfrontmatterで `name`、`description`、ディレクトリ名を検証する。

**検証コマンド:**

```bash
python3 -m pytest \
  .agents/skills/code-understanding-pro/tests \
  tests/test_code_understanding_suite_contract.py \
  tests/test_skill_frontmatter.py -q
```

**期待結果:** 全テスト成功。出力上書き、契約欠落、マニフェスト不整合を検出できる。

### Task 4: `teach` と `writing-great-skills` の発動条件を昇格する

**変更ファイル:**

- Modify: `.agents/skills/teach/SKILL.md`
- Modify: `.agents/skills/writing-great-skills/SKILL.md`

- [ ] `teach` のdescriptionを `Use when` 形式へ更新する。
- [ ] `writing-great-skills` のdescriptionを `Use when` 形式へ更新する。
- [ ] 本文は同一であることを差分確認する。
- [ ] frontmatterテストを再実行する。

**期待結果:** 内容の複製ではなく、内側repoで改善された発動条件だけが正本へ反映される。

### Task 5: `Productivity-Skill` の正本ポリシーを文書化する

**変更ファイル:**

- Modify: `README.md`
- Create: `docs/Artifacts/skill_ownership_inventory_008_0724.md`

- [ ] READMEに「汎用Skillの正本はこのrepo」という節を追加する。
- [ ] `code-understanding-pro` が一般コード、SQL、統計コードを分岐する親Skillであることを記載する。
- [ ] 3Skillスイートの役割とバージョンを更新する。
- [ ] `rwd-mysql-skill-toolkit` と `agentic-evidence-analysis` の責任範囲を相対・外部リンクで明示する。
- [ ] 移行元SHA、移行ファイル、検証結果を日本語Artifactへ記録する。

**期待結果:** READMEを読むだけで、どのrepoのどのSkillを編集すべきか判断できる。

### Task 6: toolkitから重複汎用Skillを外す

**変更repo:** `rwd-mysql-skill-toolkit`

**削除候補:**

- `.agent/skills/code-understanding-pro/`
- `.agent/skills/code-understanding-pyramid/`
- `.agent/skills/stats-sql-comprehension/`
- `.agent/skills/teach/`
- `.agent/skills/writing-great-skills/`

**変更ファイル:**

- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `tests/test_skill_frontmatter.py`
- Delete or relocate: `tests/test_code_understanding_suite_contract.py`

- [ ] Task 2からTask 5の検証が完了するまで削除しない。
- [ ] toolkit READMEの「20個」を実体に合わせて修正する。
- [ ] 存在しない `grilling` の記載を削除するか、外部依存として明示する。
- [ ] 汎用Skillの正本を `Productivity-Skill` と明記する。
- [ ] toolkitを使う前提として、次の導入コマンドを記載する。

```bash
npx skills add syrius2000/Productivity-Skill
```

- [ ] toolkit内の14個のSkillと、外部正本・ミラーの区分を一覧化する。
- [ ] 削除後に、toolkit固有Skillから削除対象への相対パス参照が残っていないか確認する。

**検証コマンド:**

```bash
rg -n \
  'code-understanding-pro|code-understanding-pyramid|stats-sql-comprehension|teach|writing-great-skills|grilling' \
  README.md AGENTS.md .agent tests
```

**期待結果:** 参照は外部依存の説明だけになり、toolkit内に追跡コピーが残らない。

### Task 7: toolkit固有テストを回帰確認する

- [ ] PythonのSkill契約・セキュリティ・MySQL資産テストを実行する。
- [ ] Rの代表的なVCD・設問バッチテストを実行する。
- [ ] `.agent/shared` の参照が壊れていないことを確認する。
- [ ] README記載のSkill数と実ディレクトリ数を比較する。

**検証コマンド:**

```bash
python3 -m pytest \
  tests/test_mysql_create_query_support_assets.py \
  tests/test_security_report.py \
  tests/test_analysis_quality_contract_docs.py \
  tests/test_run_scope.py -q

Rscript tests/test_questionnaire_batch_smoke.R
Rscript tests/test_vcd_categorical_smoke.R
```

**期待結果:** 汎用Skill削除後もDB/RWD/VCD統合機能のテストが成功する。

### Task 8: `.agent/shared` 整理の第二段階計画を作る

第一段階の正本化とは別の承認ゲートにする。

**推奨再配置案:**

```text
.agent/shared/
├── README.md
├── contracts/
│   └── analysis_quality_contract.md
└── runtime/
    ├── inspect_data.R
    ├── run_scope.R
    └── run_scope.py
```

- [ ] 4ファイルごとに参照元Skill、スクリプト、テストを機械抽出する。
- [ ] 外部利用者が旧パスを直接呼んでいないかGit履歴と文書から確認する。
- [ ] 一括移動、互換ラッパー付き移行、現状維持の3案を比較する。
- [ ] `run_scope.R` と `run_scope.py` の契約差をテストで固定する。
- [ ] `analysis_quality_contract.md` の正本が toolkit と `agentic-evidence-analysis` のどちらかを決定する。
- [ ] 専用の `implementation_plan_NNN_MMDD.md` を作り、再承認を得る。

**期待結果:** `.agent/shared` を整理する前に、破壊される参照と移行方法が確定している。

### Task 9: `rwd-mysql-skill-toolkit` の整理結果をコミット・PUSHする

- [ ] 両repoで `git diff --check` を実行する。
- [ ] 両repoで変更ファイルとコミット境界を確認する。
- [ ] `Productivity-Skill` 側を先にコミット・pushする。
- [ ] 公開された `Productivity-Skill` から汎用Skillを導入できることを確認する。
- [ ] toolkit側の変更を「重複Skill削除」と「README・AGENTS同期」の2コミットに分ける。
- [ ] toolkitの作業ブランチ `codex/remove-duplicated-generic-skills` を `origin` へPUSHする。
- [ ] GitHub上の作業ブランチについて、削除対象5Skill、残存14Skill、README、テスト結果を確認する。
- [ ] リモート `main` が基準コミット以降に進んでいないことを確認する。
- [ ] 作業ブランチをローカル `main` へfast-forwardで反映する。
- [ ] 更新済み `main` を `origin/main` へPUSHする。
- [ ] ローカル `main`、`origin/main`、GitHub上の最新コミットSHAが一致することを確認する。

**toolkit作業ブランチのPUSHコマンド:**

```bash
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit \
  push -u origin codex/remove-duplicated-generic-skills
```

**`main` 反映前の確認コマンド:**

```bash
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit fetch origin
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit \
  rev-list --left-right --count main...origin/main
```

**期待結果:** `0 0`。`origin/main` が先行している場合はマージ・PUSHせず、差分を再監査する。

**`main` のPUSHコマンド:**

```bash
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit switch main
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit \
  merge --ff-only codex/remove-duplicated-generic-skills
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit push origin main
```

**PUSH後の確認コマンド:**

```bash
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit fetch origin
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit \
  rev-parse main origin/main
git -C /Users/myamaguchi/Programing/Productivity-Skill/rwd-mysql-skill-toolkit \
  status --short --branch
```

**期待結果:** `main` と `origin/main` のSHAが一致し、作業ツリーがcleanである。

### Task 10: PUSH後のブランチとローカルcloneを整理する

- [ ] マージ済みリモートブランチの削除候補を一覧化する。
- [ ] リモートブランチ削除はユーザーの個別承認後に行う。
- [ ] 入れ子cloneの削除・移動もユーザーの個別承認後に行う。

**推奨コミット境界:**

```text
docs: correct Productivity-Skill repository guidance
feat: promote code understanding suite as canonical skills
test: add canonical skill contract checks
docs: define cross-repository skill ownership
chore: remove duplicated generic skills from rwd toolkit
docs: align rwd toolkit with external skill ownership
```

**期待結果:** toolkitの整理結果が `origin/main` に残り、ブランチ削除やローカルclone削除は本体PUSHと分離されている。

---

## 6. 検証基準

### `Productivity-Skill`

- Skillディレクトリ数とREADMEの一覧が一致する。
- 5個の重複Skillについて、最新版が外側repoに存在する。
- 3Skillスイートのテストが成功する。
- `npx skills` からSkillを認識できる。
- `code-understanding-pro` が `generic`、`sql`、`stats` を正しく分岐する。
- 成果物の上書き拒否、伏字化、マニフェスト生成が成功する。

### `rwd-mysql-skill-toolkit`

- 汎用5Skillの追跡コピーが存在しない。
- READMEのSkill数と実体が一致する。
- DB/RWD固有テストが成功する。
- `.agent/shared` の既存依存が第一段階では維持される。
- VCD系の正本が `agentic-evidence-analysis` であることが明示される。

### Git

- `master` / `main` へのforce-pushを行わない。
- toolkit整理後の `origin/main` がローカル `main` と同じSHAになる。
- 作業ブランチ以外に変更を混ぜない。
- 入れ子repoを外側repoへ登録しない。
- 削除前の基準SHAと移行記録がArtifactに残る。

---

## 7. ロールバック

- `Productivity-Skill` への昇格が失敗した場合は、統合ブランチを破棄し、`master` は変更しない。
- toolkitからの重複削除は、外側repoの公開・導入検証後に行う。
- toolkit削除後に問題が出た場合は、削除コミットだけをrevertし、外側repoの改善は維持する。
- `origin/main` へのPUSH後に問題が判明した場合は、resetやforce-pushではなくrevertコミットを作成し、通常のPUSHで復旧する。
- `.agent/shared` は第一段階で触らないため、分析Skillの共有依存を巻き込まない。
- リモートブランチ、タグ、入れ子cloneは明示承認なしに削除しない。

---

## 8. 承認ゲート

本計画の承認後も、次の順番で段階的に確認する。

1. **Gate A:** README差分の境界固定と統合ブランチ作成
2. **Gate B:** 3Skillスイートを `Productivity-Skill` へ昇格し、テスト
3. **Gate C:** toolkitから重複5Skillを削除し、回帰テスト
4. **Gate D:** `Productivity-Skill` 公開確認後、toolkit整理ブランチをPUSH
5. **Gate E:** toolkit整理内容を `main` へfast-forwardし、`origin/main` へPUSH
6. **Gate F:** PUSH後の不要ブランチ・入れ子clone整理
7. **Gate G:** `.agent/shared` 整理の別計画をレビュー

この計画の承認はGate AからEまで、すなわち両repoの整理、検証、コミット、および `rwd-mysql-skill-toolkit` の `origin/main` へのPUSHまでを許可するものとする。リモートブランチ削除、履歴書き換え、入れ子clone削除、`.agent/shared` 移動は別途明示承認を必要とする。
