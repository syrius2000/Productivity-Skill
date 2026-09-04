# quality-review単発QA軽量入口の追加実装計画

created: 2026-09-05 02:10 (JST)
update: 2026-09-05 02:10 (JST)
author: Codex (GPT-5)

## 1. 目的と承認境界

### 1.1 目的

Quality Loopの正式案件情報がまだ存在しない単発の実装結果QAについて、対象Artifactまたは対象ファイルから正式案件を開始するまでの入力負担を下げる。軽量入口は、対象の存在確認、最小限のQuality Intentの準備、正式なcase作成、Reviewer向けhandoffの発行だけを補助する。

実際のFinding作成、Evidenceの品質判定、Implementerへの修正許可、Ownerの受入・却下・クローズは既存の正式操作へ渡す。これにより、単発QAの開始を簡単にしつつ、品質判定の責任境界は変更しない。

### 1.2 今回の承認対象

- `quality-review` Skillの軽量入口に関する設計、実装、契約テスト、局所的なドキュメント更新。
- 実装先は明示された `/Users/myamaguchi/Programing/Productivity-Skill` 内の配布Skillとする。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/` は現行CLI、schema、テストの読み取り専用の比較元とする。
- 実装、テスト変更、テスト実行、外部配置、commit、push、公開は、ユーザーが本計画を明示承認するまで開始しない。
- 未コミットのファイルを開始前にコミットし、コミットメッセージは計画実行まえがわかるようにする。
- 実装完了後、再度コミットする
  
### 1.3 比例的な完了条件

- 明示したファイルパスから、既存のcase schemaに適合するrevision 1の案件を作成できる。
- 初回準備の結果が `case_id`、`case_revision`、`next_role`、`next_action`、`handoff` を含むJSONで返る。
- 準備後に既存の `review` を実行すると、Findingの有無にかかわらず正式なcase状態とhandoffが返る。
- 対象成果物を変更せず、実装許可を初期値falseとして、既存の原子更新・Evidence・Role・revision・handoff契約を維持する。
- 既存の正式CLI操作と既存回帰テストに影響がないことを確認する。

個人利用向けの変更であるため、CLI契約、安全性、再現性、代表的な実行経路を必須確認とする。LLMが作成するFinding本文の品質、外部配布、エンタープライズ向け認証・負荷試験は今回の必須完了条件に含めない。

## 2. 現状の問題と根拠

### 2.1 現行CLIの公開範囲

現行の同梱CLI `quality-review-cli` は、`quality_loop.cli` の次の9操作を公開している。

| 操作 | 現行の役割 |
| --- | --- |
| `create-case` | Ownerが完全な案件初期化JSONを投入する |
| `review` | Reviewerが既存caseのhandoffとrevisionを受けて初回レビューする |
| `submit-plan`、`review-plan`、`submit-response`、`verify`、`assess-risk`、`adjudicate` | 既存の状態機械に従って後続工程を進める |
| `status` | 既存caseの状態と最新handoffを読み取る |

現行の `cli.py` は `create-case` 以外の更新操作に `--case-id` と `--input` を要求し、`create-case`にも完全な入力JSONを要求する。したがって、case-root、case-id、baseline、Owner入力、handoff、revisionを手作業で揃えない限り、対象Artifactを直接指定して初回QAを開始できない。

### 2.2 現行case作成契約

`engine.py` の `create_case` はrevision 1のcaseを作成し、状態を `reviewer-action`、次Roleを `reviewer`、次操作を `review` とするhandoffを発行する。作成時には、次のQuality Intentが必要である。

- `purpose`
- `intended_use`
- `risk_context`
- `requirements`
- `acceptance_criteria`
- `targets`
- `target_revision`

同じ入力を使っても、通常の `review` は `operation_id`、`actor_id`、`invocation_id`、`previous_handoff_id`、`expected_case_revision`、`findings`、`evidence` を必須とする。つまり、単発QAの負担は「Findingを作ること」だけでなく、初期baselineと初回handoffを作ることにもある。

### 2.3 現行の安全契約

確認した現行契約は次のとおりであり、軽量入口でも不変とする。

- `case.json`がcanonical stateであり、`resume.md`は派生表示である。
- 更新操作は現在のRole、handoff、revision、状態を照合し、不一致なら `state_changed: false` で拒否する。
- `review` のFindingは要求参照、観測事実、影響、期待状態、検証方法、Evidence参照を持つ。
- Critical/Highおよびリスク条件に該当するMediumは、CoreがPlan必須として扱う。
- Reviewerは対象成果物を変更せず、申告外変更は `undeclared-change-detected` で拒否する。
- Reviewerは `accepted`、`rejected`、`closed` を判定語として使わず、Owner裁定を代行しない。
- Evidence不足は `unverified` または `evidence-gap` として扱い、CLIが成功や受入を補完しない。

### 2.4 調査時点の実体とテスト

- `.agents/skills/quality-review/bin/quality-review-cli` はSkill自身の `runtime/` を `PYTHONPATH` に設定し、呼出し元の作業ディレクトリを変更しない。
- Productivity-Skill内のquality-review runtimeと、QA-products側のQuality Loop runtimeは調査時点で同一内容だった。
- `quality-review` の現行版は `VERSION` とfront matterが `1.4.0` である。front matterのversion行は作業開始時点の既存差分であり、今回の計画作成では変更していない。
- QA-products側の `schemas/case.schema.json` はschema version `1.0`のcaseについて、baseline、implementation authorization、change observation、findings、Evidence、履歴、handoffを要求する。軽量入口はこのcase形状を拡張しない。
- 読み取り確認したQA-products側の関連テストは、CLI 3件、Safety 15件、Schema 7件、Skill契約3件、Pilot実行1件である。特に、Role・stale revision・undeclared change・idempotency・原子書込み失敗・case schema適合を検証している。

## 3. 提案する軽量入口のCLI/API設計

### 3.1 推奨コマンド

新しい補助サブコマンドを `review-standalone` とする。これは正式なReviewer判定操作ではなく、正式な `create-case` を安全に開始するbootstrap操作である。

```text
<quality-review-skill-dir>/bin/quality-review-cli \
  --case-root <case-root> review-standalone \
  --target <file> [--target <file> ...] \
  --owner <owner> \
  [--case-id <case-id>] \
  [--baseline-input <json/file>]
```

- `--target` は対象Artifactまたは対象ファイルを1個以上受け付ける。`--artifact` は同じ収集先へ入る読みやすい別名として提供する。
- 対象は明示された通常ファイルに限定し、ディレクトリの再帰展開は行わない。存在しない対象、読取り不能な対象、対象集合が空の場合はcaseを作らず終了コード3で拒否する。
- `--owner` は必須とし、caseの登録Ownerおよびbootstrapの監査Actorに使用する。CLIが無名のOwnerを捏造しない。
- `--case-id` は任意とする。省略時は、正規化済み対象パスと対象ファイルのSHA-256から安全な長さの `standalone-...` IDを生成する。対象内容が変われば別caseとなり、同じ入力の再送は同じcaseを再利用できる。
- `--baseline-input` は任意とし、Purpose、Intended Use、Risk Context、要求、受入基準、除外を指定するための補助JSONとする。入力がある場合は既存のbaseline検証を通し、CLIで指定した対象とbaselineの対象が不一致なら作成しない。
- `--baseline-input` がない場合は、対象範囲の確認だけを目的とする最小bootstrap baselineを生成する。原要求・原受入基準を持たないことを `exclusions` と `limitations` に明記し、Reviewerが全体適合を推測しないようにする。

### 3.2 生成する最小baseline

デフォルトbaselineは、次の意味に限定する。

- `purpose`: 指定対象の実装結果を単発で独立QAする。
- `intended_use`: 単発QAであることと、利用者・環境が未指定であることを明記する。
- `risk_context.criticality`: CLIオプションで指定でき、既定値は `low` とする。高リスク・規制対象を低リスクに自動変換しないため、利用者が指定した場合はその値を保持する。
- `requirements`: 指定対象の範囲と確認可能なEvidenceを明示するbootstrap要求を1件だけ置く。
- `acceptance_criteria`: レビュー範囲、確認結果、未確認事項が記録されることを置く。
- `targets`: 正規化した対象ファイル一覧。
- `target_revision`: 対象集合と内容から計算したbootstrap fingerprint。
- `exclusions`: 原要求・原受入基準が未提示の場合、ドメイン適合や受入を判定しないこと。

このデフォルトbaselineは、実装結果が正しいというEvidenceではない。原要求がない状態そのものを、必要に応じてReviewerが `evidence-gap` として記録できるようにするための開始条件である。

### 3.3 出力契約

成功時は既存の結果Envelopeを維持し、次の追加情報だけを返す。

```json
{
  "status": "ok",
  "entrypoint": "review-standalone",
  "case_id": "standalone-...",
  "case_revision": 1,
  "state_changed": true,
  "next_role": "reviewer",
  "next_action": "review",
  "handoff": {"case_id": "standalone-...", "issued_revision": 1},
  "review_context": {
    "targets": ["/absolute/path/to/artifact.md"],
    "baseline_source": "generated-minimum",
    "case_root": "/path/to/case-root"
  }
}
```

実際のFindingはこの操作では生成しない。Skillは対象を読み取り、Evidenceを確認した後、返された `case_id`、handoff ID、revisionを使って既存の `review --case-id ... --input ...` を1回実行する。その `review` の結果がFindingの有無、次Role、次操作、正式handoffの唯一の根拠となる。

### 3.4 実装方式

- `cli.py` に `review-standalone` と `--target`／`--artifact`／`--owner`／`--case-id`／`--baseline-input` を追加する。
- `engine.py` にbootstrap入力の正規化と対象検証を追加する。新しい状態名や後続状態遷移は追加せず、既存の `create_case` と同じrevision 1のcase構築・CaseStore・原子書込み経路を再利用する。
- 通常のcaseイベントはcanonicalな `create-case` として記録し、結果には `entrypoint` を付ける。Quality Loopの既存operation語彙とcase schemaを不要に変更しない。
- bootstrap用の内部生成値は、operation IDを対象fingerprintに基づき、invocation IDを専用の新規値にする。明示case-idとの衝突、対象fingerprint不一致、既存caseの別用途流用は安全側に拒否する。
- 対象ファイルのSHA-256はcaseのtarget revisionと再送判定に使うだけで、品質Evidenceとしては登録しない。レビュー時のEvidenceは既存 `review` 入力のEvidence契約で新たに登録する。
- `quality-response` のruntimeやSkill本文は変更しない。bootstrapで作成される実装許可は常にfalse・空配列とし、後続のImplementer操作は従来どおりOwner許可を要求する。

## 4. 正式案件との境界

| 観点 | `review-standalone` | 正式Quality Loop |
| --- | --- | --- |
| 起動条件 | case情報がない状態で、利用者が対象パスを明示する | case-root、case-id、現在handoff、revisionがある |
| 役割 | case作成のbootstrap補助 | Owner／Reviewer／Implementerの状態機械 |
| 生成物 | revision 1のcaseとReviewer向けhandoff | Finding、Plan、Response、Verification、Risk Assessment、Owner裁定 |
| Finding | 生成しない | `review` が生成し、必須要素・Evidence参照を検証する |
| Evidence | 対象存在確認とfingerprintは品質Evidenceにしない | Evidence ID、方法、結果、対象revisionを既存契約で登録する |
| 対象変更 | 行わない | Reviewerの対象変更禁止、ImplementerのOwner許可照合を維持する |
| 次工程 | 常に `reviewer` / `review` | 現行caseの状態機械が決定する |
| 受入・クローズ | 行わない | Ownerの `adjudicate` だけが行う |

正式caseが既にある場合、軽量入口は既存caseを自動選択しない。`--case-id`を要求する既存CLIを使う。これにより、複数案件の誤混入と、別の対象へのレビュー結果の付替えを防ぐ。

## 5. 既存契約への影響

### 5.1 影響を与えない契約

- case schema version `1.0`、canonical `case.json`のトップレベル構造、履歴配列、handoff構造は変更しない。
- `review`、`review-plan`、`verify`、`assess-risk`、`status`の引数・状態遷移・結果Envelopeは変更しない。
- Reviewerの結果語彙、Proportionality Gate、`improvement-proposal`、Evidence不足の扱いを変更しない。
- `undeclared-change-detected`、`unauthorized-change-detected`、stale revision、wrong Role、wrong handoff、idempotencyの拒否を変更しない。
- `quality-response` のPlan Before Fix、実装許可、Evidence、自己受入・自己クローズ禁止を変更しない。

### 5.2 追加される契約

- CLI helpに補助サブコマンドを追加する。
- `review-standalone` 固有の入力と出力追加項目を、Skill内の参照schemaで明文化する。
- 既存結果の利用者が未知の `entrypoint` や `review_context` を無視しても、既存のcase_id・revision・handoff処理が成立する後方互換を保つ。
- 既存の `create-case` は従来どおり完全入力を受け付け、Ownerが明示したbaselineを省略しない。

## 6. 変更対象ファイル

### 6.1 実装対象

- `.agents/skills/quality-review/runtime/quality_loop/cli.py`
  - parser、引数、bootstrap dispatch、エラー出力を追加する。
- `.agents/skills/quality-review/runtime/quality_loop/engine.py`
  - 対象パスの検証、fingerprint、最小baselineの組み立て、既存create経路との接続を追加する。
- `.agents/skills/quality-review/SKILL.md`
  - case情報がない場合の明示的なstandalone入口、実行順序、出力handoff、Finding生成を既存reviewへ渡す境界を追加する。
- `.agents/skills/quality-review/references/standalone-review-input.schema.json`
  - `baseline-input` の許可フィールド、型、criticality、対象指定の入力契約を追加する。
- `.agents/skills/quality-review/VERSION`
  - 新しいCLI入口を含む版として、実装承認後に `1.5.0` へ更新する。
- `.agents/skills/quality-review/CHANGELOG.md`
  - 1.5.0の追加内容、安全境界、未実施のLLM動的評価を記録する。
- `README.md`
  - quality-reviewの利用場面に、明示対象からstandalone bootstrapを開始できることを短く追加する。
- `tests/test_quality_review_standalone_cli.py`
  - 配布Skillのlauncherを経由した契約・安全性・正式review接続テストを追加する。

### 6.2 読み取り専用の比較元・変更しない対象

- `/Users/myamaguchi/Programing/QA-products/quality-loop/quality_loop/cli.py`
- `/Users/myamaguchi/Programing/QA-products/quality-loop/quality_loop/engine.py`
- `/Users/myamaguchi/Programing/QA-products/quality-loop/schemas/case.schema.json`
- `/Users/myamaguchi/Programing/QA-products/quality-loop/schemas/intake.schema.json`
- `/Users/myamaguchi/Programing/QA-products/quality-loop/schemas/review.schema.json`
- `/Users/myamaguchi/Programing/QA-products/quality-loop/tests/`
- `.agents/skills/quality-response/` 全体
- 対象Artifact、ユーザーの既存差分、既存未追跡ファイル、アーカイブ、Git設定、外部システム

QA-products側を実装元として更新する必要がある運用であれば、本計画の対象リポジトリ・変更経路が変わるため、実装開始前に別計画または本計画の改訂と再承認を行う。

## 7. テスト計画

### 7.1 新規契約テスト

1. `--help` に `review-standalone`、`--target`、`--artifact`、`--owner` が表示される。
2. 1ファイルを `--target` で指定するとcase rootにcaseが作成され、revision 1、状態 `reviewer-action`、`next_role=reviewer`、`next_action=review`、handoffが返る。
3. `--artifact`、複数の明示対象、相対パスの正規化が同じ対象集合として動作する。
4. `--baseline-input` ありでは、明示されたQuality Intentが保存され、対象不一致・必須項目不足・不正criticalityはcase無変更で拒否される。
5. `--baseline-input` なしでは、最小bootstrap baseline、原要求未提示のexclusion、実装許可false、空の許可対象が保存される。Reviewerが受入を推測できる品質要求を自動生成しない。
6. 準備結果のhandoffを使った通常の `review` がrevision 2へ進み、Finding 0件ならOwner裁定handoff、High FindingならImplementerのPlan handoffを返す。
7. 対象ファイルのSHA-256を前後で比較し、CLIが対象成果物を変更していないことを確認する。
8. 同じ対象・同じcase-idの再送、同じoperation IDの再送、既存caseとのfingerprint不一致を確認し、二重revisionや上書きが発生しない。
9. 対象不存在、ディレクトリ指定、空入力、不正case-id、既存case衝突、複数caseの暗黙選択を拒否し、失敗時は `state_changed=false` と安定した `error_code` を返す。

### 7.2 回帰確認

- `/Users/myamaguchi/Programing/QA-products/quality-loop/tests/test_cli.py`、`test_schemas.py`、`test_safety.py`、`test_pilot_execution.py`、`test_skill_contracts.py` を、Productivity-Skillの同梱runtimeを優先するPython pathで実行する。
- `quality-review` と `quality-response` のlauncherをclean environmentから `--help` で確認する。
- 新規参照schemaのJSON構文、既存case schemaとの形状整合、Skill内リンク、front matter、版情報を確認する。
- `python -B -m pytest --assert=plain -p no:cacheprovider tests -q` とSkill Creatorの `quick_validate.py` を実装後に実行し、生成キャッシュの有無も確認する。
- `git diff --check`、変更対象一覧、既存差分との差分境界を実装前後で確認する。

### 7.3 Evidenceと未実施範囲

- CLIの終了コード、stdout JSON、case.json、対象ハッシュ、case revision、handoffを機械Evidenceとする。
- テストで確認できないLLMのFinding品質、Reviewerが原要求を適切に解釈するか、実機環境での動的挙動は `unverified` または未実施として報告する。
- 既存Skillの全LLM評価、外部配布、性能試験、認証・認可の本番相当検証、commit、pushは今回の完了条件から除外する。

## 8. 互換性・安全性・Evidence設計

### 8.1 互換性

- 既存9操作の引数と状態遷移を変更せず、補助入口を追加するだけにする。
- 通常の `create-case` とstandalone bootstrapは同じcase初期状態を生成するため、後続の `quality-response` は既存handoffを処理できる。
- 出力の追加キーは後方互換の拡張として扱い、既存利用者が既知キーだけを読む場合の意味を変えない。
- 配布元とProductivity-Skillのruntimeが異なる場合は、無断で片側だけを公開版とみなさず、同期経路を別承認に戻す。

### 8.2 安全性

- 入力検証をcase作成前に完了し、無効な対象やbaselineで部分caseを作らない。
- 対象は通常ファイルの有限集合とし、ディレクトリ再帰、globの暗黙展開、case-root外への書込みを行わない。
- 実装許可はfalse・空配列で固定する。standalone入口から対象成果物を修正しない。
- CaseStoreのlock、atomic write、既存のcase.json正本、operation idempotencyを再利用する。
- 既存caseを自動選択・自動統合せず、衝突時は停止して利用者にcase-idを明示させる。
- bootstrap fingerprintは再送・衝突検出用であり、対象内容が要求適合することの証明とは扱わない。

### 8.3 Evidence設計

- 対象ファイルの存在・読取り確認は「bootstrap入力の妥当性Evidence」であり、品質適合Evidenceではない。
- 原要求または実装結果のテストEvidenceがない場合、通常の `review` でReviewerが `evidence-gap`／`unverified` を選べる。
- Findingが発生した場合は、通常の `review` の結果にFinding ID、分類、severity、Evidence参照、次工程handoffを記録する。軽量入口は別のFinding状態を作らない。
- 後続の変更提出は既存 `changed_targets`、Owner `allowed_targets`、独立 `change_observation` の三者照合を通し、申告外変更を従来どおり拒否する。

## 9. 実装しない範囲

- standaloneコマンド内でのLLM呼出し、Findingの自動生成、自動Severity判定、自動Evidence作成。
- baseline要求の推測による合格・受入・却下・クローズ。
- Ownerの実装許可、Reviewerの検証完了、ImplementerのResponse提出の自動化。
- 既存のcaseを検索して対象を自動付替えする機能。
- `quality-response` の変更、case schema versionの更新、Quality Loopの状態機械の再設計。
- QA-products側のruntime・schema・テスト、外部配置、commit、push、公開。
- ユーザーが作業開始時点で持つ変更、未追跡ファイル、アーカイブ文書の削除・復元・上書き。

## 10. 既存差分の保持と実装後の停止条件

作業開始時点で、次の既存変更がある。実装対象と重なる `quality-review/SKILL.md` は、既存のversion追加行を保持し、後続編集との差分を明確に分離する。

- `code-understanding-pro`関連の既存変更。
- `quality-response/SKILL.md` と `quality-review/SKILL.md` のfront matter version追加。
- `README.md`、Archives、既存Artifact、既存テスト、`.tmp_pytest/`の既存差分・未追跡状態。
- `docs/Artifacts/Implementation_agy_001.md`、`implementation_agy_review_001_0904.md`、`implementation_plan_004_0904.md`、`docs/Archives/archive_summary_004_0904.md`。

実装後に不具合があっても、ファイル全体の `git restore` は行わない。開始時のdiff・SHA-256と実装ラウンドのdiffを比較し、混在差分がある場合は自動復元せず停止して確認を求める。

本Artifact作成後の次工程はユーザー承認である。承認がない限り、上記変更対象の編集、新規テスト追加、テスト実行、外部リポジトリへの書込み、commit、pushへ進まない。
