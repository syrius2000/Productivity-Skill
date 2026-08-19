# Skill改善評価契約

Skill自身を改善するときは、改善前の版を基準版として保存し、改善後と同じ入力を実行する。評価は「改善した」という説明ではなく、入力、期待動作、実際の証拠、判定を追跡できる形で残す。

## シナリオ必須項目

各シナリオに次を記録する。

- `id`: 安定したシナリオ識別子
- `prompt_or_input`: 実際に与えた依頼または入力ファイル
- `target`: 明示したファイルまたはディレクトリ
- `expected_behavior`: 期待するSkillの行動
- `assertions`: 機械判定できる条件。定性的評価だけの場合は観察項目と判定者を記録する
- `evidence_outputs`: 保存するレビュー、Finding、イベント、ログ、差分
- `baseline_reference`: 改善前の版またはSHA-256
- `result`: `supported`、`partially-supported`、`unsupported`、`not-assessable` のいずれか

## 必須シナリオ

最低限、次の3種類を含める。

1. 明示ファイルを対象にした標準QA。対象範囲、証拠分類、Finding、トレーサビリティを確認する。
2. PurposeまたはSpecが不足するintent-recovery。推測を確定扱いせず、`INSUFFICIENT-CONTEXT`または`SCOPE-LIMITATION`を残すことを確認する。
3. REQUIREDマーカーを含む複数サイクル。未解決マーカーはclosureを阻止し、検証済みの履歴は`RESOLVED:REQUIRED:`で元のFindingと対応付けることを確認する。

## 判定規則

- 期待証拠が欠けた場合は成功扱いにせず、`not-assessable`または`partially-supported`とする。
- 改善前だけ、または改善後だけで実行した結果は比較証拠にならない。
- 実行環境、コマンド、終了コード、対象版を記録する。
- 人間の定性的評価を使う場合も、観察項目と判定理由を保存する。
