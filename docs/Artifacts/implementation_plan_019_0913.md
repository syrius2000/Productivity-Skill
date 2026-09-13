# Quality LoopのAI支援入口と次工程案内の改善計画

created: 2026-09-13 22:53 (JST)
update: 2026-09-13 23:09 (JST)
author: Codex (GPT-5)

## 状態・目的・承認範囲

計画策定済み、実装開始基準を確定、実装未着手。目的は、Quality Loopの開始時とReviewer／Implementer／Owner間の引継ぎ時に、人がJSON Schemaや内部状態を理解していなくても安全に次の操作へ進めるようにすることである。

ユーザー確認により、下記の実装方針を確定した。下書き入口の正式名称は `prepare-case` とし、QA-Loopのディレクトリ内に設置する。下書きはファイルとして保存し、人がファイルを確認し、追加質問を行い、必要に応じて内容を更新できるようにする。確認済みの入力だけを既存の正式CLIへ渡す。実際の運用で処理量・対話量を確認しながら開発する。

本計画の承認は、下記に列挙した配布Skill、同梱runtime、テスト、README、CHANGELOGの変更に限る。今回のコミットは開発開始時点を固定する計画書コミットであり、コード実装の完了を意味しない。以降のコード変更・依存関係変更・データ変更・case作成／更新は、今回の計画範囲内で段階的に実施する。remoteへのpushは別途明示指示が必要である。

## 現状の調査結果

### 直接確認できた事実

- `.agents/skills/quality-review/runtime/quality_loop/cli.py` の通常入口は `create-case`、`status`、`review`、`review-plan`、`verify` などである。`create-case` は入力JSONファイルを必須とする。
- `engine.py` の `create_case()` は、Ownerの認証情報、case ID、baseline、操作ID、Invocation IDを受け取り、初回handoffを `next_role=reviewer`、`next_action=review` として保存する。
- baselineにはPurpose、Intended Use、Risk Context、要求、受入基準、対象、対象revisionが必要である。現在の一般的な `create-case` には、これらを対話的に組み立てる補助がない。
- `review-standalone` は明示されたファイルから最小baselineを生成し、正式caseを作成できる既存のbootstrapである。ただし対象ファイルQA向けであり、依頼目的や本来の要求をAIと対話して整理する入口ではない。
- caseがない場合の `resolve_case_id()` は `no-cases-found` と `create-caseを実行してください` を返すだけである。複数caseの場合もcase IDの明示を求めるだけで、選択を支援する説明はない。
- Reviewer／ImplementerのSkill本文は `next_role` と `next_action` の確認を要求しているが、通常の成功JSONで人間向けの依頼文、回答テンプレート、Ownerターンの判断補助を一貫して返す契約はない。
- 状態遷移の安全境界は既に存在する。Reviewerは独立検証とOwner裁定を代行せず、Implementerは許可範囲外を変更せず、case.jsonを直接編集しない。

### 推論される主な使いにくさ

人が最初に入力すべき情報と、システムが生成・検証すべきメタデータが分離されていないため、利用者は品質目的を考える前に内部契約を埋める必要がある。また、機械向けのhandoffは状態として正しいが、会話の次のターンに貼り付けられる指示へ変換する責務がSkill利用者側へ残っている。

## 提案する利用フロー

### 1. AI支援によるcase作成

`prepare-case` という正式なcase準備入口を、case正本を作成する操作と分離して追加する。入口はQA-Loopのリポジトリ内に設置し、下書きファイルを人が閲覧・確認できるようにする。

1. Reviewerを対象ファイルまたは依頼文とともに起動する。
2. active caseが見つからなければ、CLI／Skillは停止して `case_setup_required` を返す。エラー扱いではなく、必要な入力と次の質問を示す。
3. AIは利用者から、少なくとも「何を確認したいか」「誰がどの環境で使うか」「失敗時に何が問題か」を聞き、対象・要求・受入基準・除外・criticalityの下書きを作る。未回答は推測せず「未確認」とする。
4. AIはcase JSON案、抜けている情報、推測していない項目、作成後の初回Reviewer操作を `prepare-case` の下書きファイルへ保存する。
5. 人は下書きファイルを確認し、追加質問を入力できる。AIは回答を反映して下書きを更新するが、確認前にcase正本を作成しない。
6. Ownerが内容を確認して明示的に承認した場合だけ、確認済みファイルを既存の正式 `create-case` CLIへ渡す。作成結果は `next_role=reviewer`、`next_action=review` を返す。

`prepare-case` は、下書きファイルの生成・表示・質問受付・更新を担う。AI下書きだけでcase正本やOwner権限を自動生成しない。既存 `review-standalone` は後方互換の単発bootstrapとして維持し、AI支援入口と統合する場合も、対象manifestとSHA-256の安全契約を弱めない。

### 2. Reviewer完了後の次工程案内

すべての成功結果と `no-cases-found` 等の回復可能な結果に、人間向けの `next_step` を追加する。少なくとも次を含める。

- 次の担当者を日本語で表示する（Reviewer、Implementer、Owner、人手確認）。
- 次の操作の目的を一文で表示する。
- 会話でそのまま送れる依頼文テンプレートを返す。
- 必要入力、参照すべきFinding／Evidence、case ID、revision、handoff IDを明示する。
- 人のターンでは、実行者が誰であるか、何を判断してよいか、判断してはいけないかを示す。
- 終端では、`next_role=null` と `next_action=null` を「完了」ではなく、Owner裁定済み等の状態とともに説明する。

例としてReviewerの初回レビュー完了後は、`findingなし → Ownerに裁定を依頼`、`plan_requiredあり → ImplementerにFinding別Response Planを依頼`、`単純修正 → Implementerに許可範囲内の修正とEvidence提出を依頼` を分ける。レビュー完了を「QA完了」や「受入」と表現しない。

### 3. Implementer／Response側の案内

Implementerが `submit-plan` または `submit-response` を受けた際も、次の行動を一つに絞って提示する。

- `submit-plan`: Findingごとの理解、方針、反証または修正予定、対象範囲を提出する。コード変更はまだ開始しない。
- `submit-response`: 承認された対象Findingと `allowed_targets` だけを変更し、`changed_targets` とEvidenceを提出する。
- baseline変更要求: Implementerが勝手にbaselineを変更せず、Owner裁定へ返す。
- Reviewerの `review-plan`／`verify` に返る場合: Reviewerに何を再確認してほしいかをFinding ID単位で示す。
- Ownerのターンの場合: Ownerが決める項目、判断材料、選択肢、実装を開始してはいけない条件を表示する。

## 実装対象と変更案

### 段階1: 入力準備の契約

- `quality-review` と `quality-response` のruntimeで共有する、case下書きの入力モデルと日本語の案内モデルを設計する。
- AIが生成するのは下書きであり、`operation_id`、`invocation_id`、case revision、handoff、Owner裁定、実装許可を発明できないことを明文化する。
- `prepare-case` の出力はcase正本を書き込まず、明示承認後に既存 `create-case` に渡せるpayloadまたは入力テンプレートを返す。
- 既存の `review-standalone`、正式 `create-case`、case schemaの互換性を確認し、必要な場合だけ後方互換フィールドを追加する。

### 段階2: caseなしReviewer入口

- `resolve_case_id()` の `no-cases-found` を、対象・目的・Ownerが不足している場合の回復案内へ拡張する。
- Reviewer Skillに、caseなし時の質問、下書き提示、Owner確認、create-case後の再起動手順を追加する。
- 対象が明示されていない場合は、caseを作らず、対象とOwnerを求める。対象を推測して既存caseへ自動接続しない。

### 段階3: handoff案内

- `engine.py` または専用の案内モジュールで、`next_role`／`next_action`から日本語の目的、担当、会話テンプレート、必要情報を決定する。
- `status`、各成功結果、回復可能なエラーで同じ案内構造を返す。内部JSONの既存フィールドは維持する。
- `resume.md` とSkill本文の例を、機械向け状態と人間向け依頼文の二層構造に更新する。
- Reviewer／Response双方のSkillで、返却された案内を次の担当へ渡す手順を明示する。同一応答で複数の状態遷移を実行しない規則は維持する。

### 段階4: テストと文書

- caseなし、対象不足、Owner不足、下書き確認前、単一active case、複数active case、Reviewer完了、Plan提出、Response提出、Ownerターン、終端のfixtureを追加する。
- 下書き生成が正本を書き換えないこと、Owner確認前にcreate-caseを実行しないこと、case ID／revision／handoffを捏造しないことを確認する。
- 既存のRole firewall、revision conflict、undeclared-change、独立verify、case.json直接編集禁止のテストを維持する。
- README、Skill本文、CHANGELOGの日本語案内を実装仕様と一致させる。

## 受入基準

- 人がcreate-case用の内部メタデータを最初から手書きしなくても、AIの質問と下書き確認を経て正式caseを作成できる。
- caseなしでReviewerを起動したとき、単に失敗せず、必要な入力、質問、下書きから正式作成へ進む安全な手順が返る。
- AI下書きまたは案内生成だけでは、case正本、Owner裁定、実装許可、Finding、Evidence、revision、handoffを新規に確定しない。
- Reviewer、Implementer、Owner、人手確認それぞれの次ターンで、担当、目的、入力、禁止事項、送信文テンプレートが一貫して表示される。
- `review → submit-plan/submit-response → review-plan/verify → adjudicate` の既存のRole境界と状態遷移が変わらない。
- Reviewer完了を受入・クローズと誤表示せず、終端の `next_role=null`／`next_action=null` も状態とともに説明する。
- 既存のQuality Loopテスト、追加fixture、CLIのclean-room実行、`git diff --check` が合格する。テスト未実行の場合は未検証として扱う。

## 対象外・未決定事項

- Web UI、外部LLM API、永続的な会話履歴、Slack等への自動送信は対象外とする。
- case正本のスキーマを大きく変更すること、Owner権限をAIへ移すこと、Reviewerが自動でFindingを確定することは対象外とする。
- `prepare-case` の保存形式、質問・回答の追記形式、複数回更新時の版管理、Owner確認済みをどのフィールドで表すかは実装中に確定する。保存場所はQA-Loopのリポジトリ内とする。
- 複数active caseを対象ファイルや目的で自動選択できるかは、誤接続時の影響が大きいため、まずは候補一覧と人の明示選択を基本とする。

## 実装状況（2026-09-13）

- [x] `prepare-case` CLIを追加し、初回依頼からQA-Loopリポジトリ内の下書きファイルを生成できるようにした。
- [x] 下書きにOwner確認を記録し、`--confirm`で正式`create-case`入力ファイルへ変換できるようにした。case正本はこの操作では作成しない。
- [x] caseなしエラーに`case_setup_required`と`prepare-case`への人間向け案内を追加した。
- [x] Reviewer／Implementer／Owner向けの`next_step`（担当、目的、依頼文、必要入力、guardrails）を成功結果へ追加した。
- [x] 追加fixtureを含む22テスト、構文検査、`git diff --check`を実施し、合格した。

本段階の`prepare-case`は外部LLMを呼び出す機能ではなく、AIまたは人が作成した依頼JSONを受け取り、質問・未確認事項を含む下書きファイルとして保存する契約である。対話UIや自動的な質問送信は未実装であり、実運用で重さを確認する次段階の課題として残す。

## 実装時の確認コマンドと停止条件

作業開始時に `git status --short --branch`、対象ファイルの差分、現在のSkill版を再確認する。今回の計画書コミットを開発開始の基準点とし、以後の実装はこの基準点から進める。各編集ラウンドの開始・終了時に `git diff` を確認し、既存差分を保持する。

想定する検証は次のとおりである。

```text
python3 -B -m pytest --assert=plain -p no:cacheprovider tests
quality-review-cli --help
quality-response-cli --help
git diff --check
```

case正本を利用する統合fixtureが必要になった場合も、合成caseに限定する。実案件のcase作成・状態更新、commit、push、グローバル配布は本計画の承認だけでは許可されない。
