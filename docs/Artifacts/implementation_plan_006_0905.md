# Quality Loop QAスキル正本統合・配布同期の実装計画

created: 2026-09-05 04:53 (JST)
update: 2026-09-05 05:17 (JST)
author: Codex (GPT-5)

## 1. 目的と問題認識

### 1.1 目的

Quality Loopの開発・検証の本丸である`/Users/myamaguchi/Programing/QA-products`を唯一の開発正本として扱い、先行して変更された`/Users/myamaguchi/Programing/Productivity-Skill`の利用成果物を、機能・版・履歴・Evidenceの面で再び整合させる。

今回の対象は、単発の実装結果QAを開始する`review-standalone`軽量入口の正本統合である。単にファイルをコピーするのではなく、QA-products側のQuality Loop契約、OpenSpec・テスト・独立QA・Owner裁定の履歴へ接続し、確定版だけをProductivity-Skillへ配布する。

### 1.2 確認できた不整合

2026-09-05時点の読み取り専用調査で、次を確認した。

| 観点 | QA-products（開発正本） | Productivity-Skill（利用成果物） |
|---|---|---|
| Git状態 | `master`、`21dc09d`、clean | `master`、`b44d47e`、多数の既存変更あり |
| Quality Loop版 | `1.4.0` | `quality-review`だけ`1.5.0` |
| `review-standalone` | CLI・engine・仕様に存在しない | CLI・engine・SKILL・CHANGELOG・schema・テストに存在する |
| runtime | 開発正本と両Skill同梱runtimeが一致 | QA-productsのruntimeと`cli.py`・`engine.py`が不一致 |
| schema | standalone用schemaなし | `references/standalone-review-input.schema.json`のみ存在 |
| `quality-response` | front matterに版項目なし | `version: "1.4.0"`を追加済み |
| 時系列 | 9月1日のv1.4.0配布・同期記録が最新 | 9月2日以降にProductivity-Skill側だけでv1.5.0相当を実装 |

2026-09-01の[Quality Loop同期記録](/Users/myamaguchi/Programing/QA-products/docs/Artifacts/quality_loop_sync_001_0901.md)では、QA-productsの`7ce9a6b`からProductivity-Skillへ`quality-review`と`quality-response`を同期し、両者のtree SHA-256が一致していた。その後、Productivity-Skill側だけで`review-standalone`が追加されたため、現在は同期元と同期先が分岐している。

### 1.3 正本に関する確定事項

- `/Users/myamaguchi/Programing/QA-products/quality-loop/quality_loop/`をPython runtimeの開発正本とする。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/skills/`を利用者向けSkillパッケージの配布元とする。
- `/Users/myamaguchi/Programing/Productivity-Skill/.agents/skills/quality-review/`および`quality-response/`は、QA-productsから確定版を同期する利用成果物とする。
- Productivity-Skill側の先行実装は捨てず、差分・テスト・schema・文書をQA-products側へ移植する際の入力とする。
- 全体コピー、ファイル全体の盲目的な上書き、既存差分の復元は行わない。

### 1.4 今回の補足で追加する設計要件

- standaloneの入力schemaはProductivity-Skill側だけに置かず、QA-productsの`quality-loop/schemas/`を正本とする。配布Skill内の`references/`版は、その正本から同期する。
- `quality-loop/FUNCTIONAL_SPEC.md`に「単発QA Bootstrap（`review-standalone`）」の章を追加し、v1.5.0の補助入口としてOpenSpec・機能仕様上も正式に位置付ける。正式9操作の契約は変更しない。
- 移植元を抽出するときはProductivity-Skill全体の差分を使用せず、`git diff -- .agents/skills/quality-review/`と、移植対象として個別に確認した未追跡schema・テストだけを入力にする。`code-understanding-pro`、README、Archive、他Skillの差分は移植パッチへ含めない。
- 移植前後に対象パスのmanifestを記録し、QA-products側で意味単位の差分レビューを行う。パッチ抽出の狭さは、QA-products側の正本実装が不足しないことより優先しないため、standaloneに必要なテスト・schema・仕様差分は別途明示して追加する。

## 2. 承認境界

### 2.1 この計画の対象

- 両リポジトリの機能・版・schema・runtime・ドキュメント・テストの整合化設計。
- QA-products側への`review-standalone`の正本実装。
- QA-products側のSkillパッケージ、機能仕様、README、CHANGELOG、版情報の更新。
- QA-products側の単体・契約・CLI・配布同期検証。
- 明示的に承認された場合だけ、QA-productsからProductivity-Skillへ管理対象Skillを限定同期すること。
- Productivity-Skill側の同期後検証と、既存のREADME・Artifact・テスト差分の保持。

### 2.2 この計画だけでは許可しない操作

- この計画作成中のQA-productsまたはProductivity-Skillのコード・Skill・schema・テスト編集。
- QA-productsの既存v1.4.0案件を自動的に`accepted`や完了へ変更すること。
- 外部Skill配置、グローバル配置、旧版削除。
- commit、tag、branch削除、remoteへのpush、公開。
- Productivity-Skill側の既存未コミット変更、未追跡Artifact、Archive、`.tmp_pytest/`の削除・復元。
- 対象Artifactそのものの内容変更。

QA-products側の実装承認、Productivity-Skillへの配布同期承認、commit、pushは、それぞれ別のゲートとして扱う。Productivity-Skillは作業開始時点でdirtyであるため、通常の同期スクリプトが要求するclean条件を満たさない場合は、対象差分を明示したうえで限定`--force`または隔離作業木を選択する。

## 3. 実装設計

### 3.1 `review-standalone`の位置付け

`review-standalone`は正式Reviewer判定操作ではなく、正式な`create-case`を安全に開始するbootstrap操作とする。既存の正式公開seamである9操作は維持し、standalone入口は補助操作として仕様上明示する。

処理順序は次のとおりとする。

1. `--target`または`--artifact`で通常ファイルを1個以上指定する。
2. `--owner`、任意の`--case-id`、任意のbaseline、criticalityを検証する。
3. 対象ファイルの有限manifestとSHA-256を計算し、対象の存在・読取り不能・ディレクトリ指定を安全側で拒否する。
4. baseline未指定時は、単発QAの範囲だけを示す最小baselineを生成する。原要求・原受入基準がないことを`exclusions`または`limitations`へ記録する。
5. 既存の`create_case`経路でrevision 1のcanonical `case.json`とReviewer向けhandoffを作成する。
6. `case_id`、`case_revision`、`next_role=reviewer`、`next_action=review`、handoff、対象、baseline sourceをJSONで返す。
7. Finding、Evidenceの品質判定、実装許可、Owner裁定は生成せず、通常の`review`へ渡す。

### 3.2 維持する正式契約

- `case.json`を唯一の正本とし、`resume.md`などの派生表示を正本扱いしない。
- 既存caseを自動選択せず、case IDの再送時は対象・baselineの不一致を拒否する。
- Reviewerの判定語彙、Evidence参照、Proportionality Gate、`undeclared-change-detected`を維持する。
- `accepted`、`rejected`、`closed`をReviewerが決定しない。
- Evidence不足は`unverified`または`evidence-gap`として扱い、bootstrap成功を品質適合や受入と解釈しない。
- 対象Artifactや対象ファイルを変更しない。
- 既存のrevision、handoff、idempotency、atomic write、拒否時`state_changed: false`を維持する。

### 3.3 版とmetadata

- `quality-review`はstandalone機能を含む版として、QA-products側で検証後に`1.5.0`へ更新する。
- `quality-response`は機能変更なしのため`1.4.0`を維持する。
- Productivity-Skillのインベントリ契約とQA-productsの配布契約を一致させるため、両Skillの`SKILL.md` front matterに対応する`version`をQA-products側の正本へ追加する。これは`quality-response`の機能変更ではない。
- QA-productsの`AGENTS.md`に記載されたv1.4.0 CoreのOwner裁定待ち状態と、standalone v1.5.0の実装・検証状態を混同しない。v1.5.0は実装・静的検証・独立QA・Owner判断を分けて記録する。

### 3.4 対象境界と性能・メモリ方針

- v1.5.0の対象は、明示された通常ファイル（Artifactまたは対象パス）に限定する。ディレクトリの再帰展開、シンボリックリンク経由の意図しない範囲拡張、特殊ファイルは対象外とする。
- 対象manifestのSHA-256計算はストリーミング読み込みを基本とし、対象ファイル全体を`read_bytes()`で一括保持しない。これによりメモリ使用量を対象ファイル最大サイズに比例させない。
- 対象数・総バイト数・1ファイルの上限値と、上限超過時の安定したエラーEnvelope（caseを作成せず`state_changed: false`）を実装前に固定する。上限値は1 MiB・10 MiB級の検証データを用いて、実行時間と最大メモリを測定したうえで決定する。
- 受入基準には、通常サイズ、1 MiB級、10 MiB級、上限超過、読取り不能、ディレクトリ指定を含める。大規模負荷試験や無制限サイズ対応はv1.5.0の範囲外とする。

## 4. 変更対象ファイル

### 4.1 QA-products側（開発正本）

- `/Users/myamaguchi/Programing/QA-products/quality-loop/quality_loop/cli.py`
  - `review-standalone`の引数、入力読込み、結果Envelopeを正本へ追加する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/quality_loop/engine.py`
  - standalone入力正規化、対象manifest、baseline生成、既存`create_case`接続、再送不一致拒否を追加する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/schemas/standalone-review-input.schema.json`
  - standaloneの入力・任意baseline・出力前提を、既存schemaとの責務を分けて追加する。QA-products側の仕様正本として配置する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/skills/quality-review/SKILL.md`
  - standaloneの起動条件、通常reviewへのhandoff、正式操作との境界を追加する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/skills/quality-review/references/standalone-review-input.schema.json`
  - 配布Skill単独で参照可能なschemaとして、QA-products側schemaと同一内容を配置する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/skills/quality-review/CHANGELOG.md`
  - v1.5.0の追加内容、安全境界、未検証範囲を記録する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/skills/quality-review/VERSION`
  - 検証後に`1.5.0`へ更新する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/skills/quality-response/SKILL.md`
  - `VERSION`と一致するfront matterの版項目だけを追加し、機能責務は変更しない。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/FUNCTIONAL_SPEC.md`
  - 正式9操作を維持したまま、「単発QA Bootstrap（`review-standalone`）」章を追記する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/README.md`
  - 開発正本、補助入口、利用手順、正式reviewへの接続を追記する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/tests/test_cli.py`
  - help、正常系、入力拒否、case作成、再送・不一致、対象非変更を追加する。
- `/Users/myamaguchi/Programing/QA-products/quality-loop/tests/test_schemas.py`
  - 新schemaの構造と既存schemaとの境界を検証する。
- `/Users/myamaguchi/Programing/QA-products/tests/test_distribution_tools.py`
  - source、Skill同梱runtime、Productivity-Skill同期先の一致検査とstandalone schemaの配布を検証する。
- `/Users/myamaguchi/Programing/QA-products/docs/Artifacts/`
  - 実装計画、実装報告、同期記録をQA-products側の時系列で追加する。

### 4.2 Productivity-Skill側（配布先）

- `/Users/myamaguchi/Programing/Productivity-Skill/.agents/skills/quality-review/`
  - QA-products側の検証済みSkillパッケージを限定同期する。手編集で正本化しない。
- `/Users/myamaguchi/Programing/Productivity-Skill/.agents/skills/quality-response/`
  - QA-products側metadataと一致させる必要がある場合だけ限定同期する。
- `/Users/myamaguchi/Programing/Productivity-Skill/README.md`
  - 現在のstandalone案内が確定版の利用方法と一致するか確認する。必要な場合だけ局所修正する。
- `/Users/myamaguchi/Programing/Productivity-Skill/tests/test_quality_review_standalone_cli.py`
  - 配布先のCLI smoke・対象非変更・case bootstrap検証として位置付けを確認する。QA-products側へ移した場合も、既存ファイルを無承認で削除しない。
- `/Users/myamaguchi/Programing/Productivity-Skill/tests/test_skill_inventory_contract.py`
  - Skill配布先の版・入口・manifest契約を維持する。

Productivity-Skillの既存`docs/Artifacts/`、`docs/Archives/`、code-understanding関連差分、`quality-response`の既存変更、`.tmp_pytest/`は今回の同期対象外とする。

## 5. 実装手順

### 第1段階：開始点の固定

1. QA-productsとProductivity-Skillの`git status --short --branch`、HEAD、対象ファイル一覧を記録する。
2. Productivity-Skillの`git diff -- .agents/skills/quality-review/`を移植候補として記録し、全体差分とは分離する。未追跡のstandalone schema・テスト・Artifactも個別に記録する。
3. `code-understanding-pro`、README、Archive、他Skillを含む差分が移植候補へ混入していないことを確認する。
4. QA-productsのsource runtime、両Skill同梱runtime、Productivity-Skillの対象SkillのSHA-256を記録する。
5. 作業開始前の証跡を保存し、以後の復元は今回の追加差分に限定する。

### 第2段階：QA-productsでの正本化

1. Productivity-Skill側の`cli.py`・`engine.py`の差分を読み、QA-productsの`quality_loop/`へ意味単位で移植する。
2. `quality-loop/quality_loop/`を正本として、両Skill同梱runtimeへ反映する。
3. standalone schemaをQA-productsの`schemas/`へ追加し、同じ内容をSkillの`references/`へ配布する。
4. `FUNCTIONAL_SPEC.md`へ「単発QA Bootstrap」章を追加し、README・Skill本文・CHANGELOG・VERSIONと用語・版・境界を一致させる。
5. `quality-response`はfront matterの版整合だけを確認し、standaloneの公開入口として扱わない。
6. 対象manifest計算をストリーミング方式で実装し、対象数・サイズ上限と超過時Envelopeをテストで固定する。

### 第3段階：QA-products内の検証

1. Quality Loop既存テストとstandalone契約テストを実行する。
2. source runtimeと両Skill同梱runtimeの相対パス・SHA-256を比較する。
3. CLIの正常系、空対象、ディレクトリ対象、未存在対象、baseline不一致、case再送、対象非変更を確認する。
4. 通常サイズ、1 MiB級、10 MiB級、上限超過の対象で、実行時間・最大メモリ・case未作成を確認する。
5. standalone bootstrapのあと、返却handoffとrevisionを使った通常`review`接続を一時case rootで確認する。
6. 失敗、未検証、残余リスクをQA-products側の実装報告へ記録する。

### 第4段階：Productivity-Skillへの限定同期

1. QA-products側で確定したSkill treeと同期対象パスを固定する。
2. `scripts/sync_productivity_skills.py --dry-run`で差分、追加、変更、削除、SHA-256を確認する。
3. Productivity-Skillの既存dirty状態を保護したまま、同期対象2Skill以外を変更しないことを確認する。
4. 配布同期が別途承認された場合だけ、限定同期を実行する。同期対象外のREADME、tests、docsは手動で上書きしない。
5. 同期後のtree SHA-256、launcher、help、standalone smoke、既存テストを確認する。
6. QA-products側に同期元revision、同期先revision、版、日時、SHA-256、未検証事項を記録する。

## 6. テスト計画

### 6.1 QA-products側の必須テスト

- `cd /Users/myamaguchi/Programing/QA-products/quality-loop && python3 -B -m unittest discover -s tests -v`
- QA-productsルートの配布ツール契約テスト
- `python3 -B -m quality_loop.cli --help`でstandaloneが補助入口として表示されること
- standalone schemaのJSON構造検証
- `review-standalone`の正常系でrevision 1、`reviewer-action`、`next_role=reviewer`、`next_action=review`、handoffを確認
- 対象ファイルのSHA-256がbootstrap前後で不変であることを確認
- 1 MiB級・10 MiB級・上限超過で、性能測定値、最大メモリ、安定エラー、`state_changed: false`を確認
- 通常`review`へhandoff・revisionが接続できることを確認
- 既存の9操作、既存case、旧v1.4.0入力が変わらないことを確認

### 6.2 Productivity-Skill側の必須テスト

- `python3 -B -m pytest --assert=plain -p no:cacheprovider tests -q`
- 配布Skill launcherの`--help`
- 一時case rootでのstandalone bootstrap smoke
- `test_quality_review_standalone_cli.py`の対象非変更、入力拒否、再送不一致の確認
- `test_skill_inventory_contract.py`の版、README、相対リンク、manifest整合確認
- `git diff --check`
- 移植候補の差分が`git diff -- .agents/skills/quality-review/`および明示した未追跡対象に限定され、他Skill差分を含まないことを確認

### 6.3 Evidenceの扱い

- source・package・distributionのtree SHA-256は、同一性Evidenceとして記録する。
- CLIの終了コード、JSON結果、case revision、handoff、対象SHA-256は実行Evidenceとして記録する。
- `review-standalone`成功は品質適合、Findingなし、受入、実装許可のEvidenceではない。
- 性能Evidenceには対象サイズ、対象数、実行時間、最大メモリ、実行環境、終了コード、case作成有無を記録し、単発測定を一般的な性能保証へ拡張しない。
- LLMが作成するFinding本文の自然さ・網羅性は、契約テスト成功から推定しない。
- 独立QAとOwner裁定が未実施なら、`unverified`または`evidence-gap`として明記する。

## 7. 互換性・安全性

- 既存の9操作の引数、状態遷移、結果Envelope、エラーコードを変更しない。
- standalone固有の追加フィールドは、既存利用者が無視してもcase ID・revision・handoff処理が成立する後方互換な追加とする。
- baseline未指定時に自動生成する要求は、受入判定を作らず、対象範囲と未確認事項だけに限定する。
- `--target`と`--artifact`は同じ対象指定の別名とし、再帰的なディレクトリ展開を行わない。
- 対象数・総バイト数・1ファイル上限を超えた場合は、caseを作成せず、再現可能なエラーコードと`state_changed: false`を返す。
- SHA-256計算はストリーミング方式とし、上限内の測定対象で最大メモリがファイル全体サイズに比例しないことを確認する。
- 既存caseを自動選択せず、誤案件へのFinding付替えを防止する。
- 対象ファイル、Artifact、QA案件正本をCLIが変更しない。
- 同期スクリプトのdirty拒否、宛先リポジトリ確認、backup、失敗時復元を維持する。
- Productivity-Skill側の既存差分が混在する場合は、全体復元や全体上書きを行わず、差分を提示して停止する。
- `__pycache__`、`*.pyc`、`.pytest_cache`、一時case rootを配布物・commit対象へ混入させない。

## 8. 完了条件

### 正本側

- QA-productsのsource runtime、両Skill同梱runtime、standalone schemaが意図した範囲で一致する。
- QA-productsの正式9操作が既存テストで維持される。
- standaloneの正常系・拒否系・再送系・対象非変更がテストで確認される。
- `schemas/standalone-review-input.schema.json`がQA-productsの正本として存在し、Skill内`references/`へ同一内容で配布される。
- `FUNCTIONAL_SPEC.md`に「単発QA Bootstrap（`review-standalone`）」章があり、README、Skill本文、CHANGELOG、VERSIONの版・境界・利用方法が一致する。
- 性能・メモリ方針、上限値、上限超過時のエラー、1 MiB級・10 MiB級の測定Evidenceが実装報告に記録される。
- v1.5.0の実装結果、未検証事項、独立QA状態、Owner裁定状態が混同なく記録される。

### 配布先

- Productivity-Skillの管理対象SkillだけがQA-productsの確定版と一致する。
- 既存のREADME、Artifact、Archive、code-understanding関連差分、未追跡ファイルが保持される。
- 配布先CLI smoke、既存契約テスト、相対リンク、版情報が成功する。
- 同期記録にsource revision、destination revision、tree SHA-256、実施日時、未検証事項が残る。

## 9. 実装しない範囲

- `quality-response`の機能仕様、状態遷移、実装責務の変更。
- Quality Loop正式9操作の再設計、Finding語彙、Evidence契約、Owner裁定の変更。
- v1.4.0 Coreの既存案件の再判定、再QA、Owner裁定の代行。
- `review-standalone`自身によるFinding生成、品質適合判定、実装許可、受入、クローズ。
- 対象成果物の自動修正、Artifact本文の書換え。
- QA-productsとProductivity-Skill以外への配置、グローバルSkill更新、旧版削除。
- 本計画でのcommit、tag、push、公開、branch整理。
- LLM動的品質評価、負荷試験、エンタープライズ認証、外部規格適合宣言。
- 上限値を超える大規模ファイルの実用性能保証、長時間・高並列の負荷試験、全体作業木の差分統合。

## 10. 承認後の停止条件

本計画の承認後も、まずQA-products側の正本化と検証だけを実施する。QA-productsの検証が成功しない場合、Productivity-Skillへの同期へ進まない。同期後に既存差分との混在、対象外パスの変更、tree SHA-256不一致、CLI smoke失敗、リンク切れがあれば、追加上書きや復元を行わず停止する。

QA-products内の実装・テスト完了、独立QA、Owner裁定、Productivity-Skillへの配布同期、commit、pushは、個別のEvidenceと明示承認をもって段階的に進める。
