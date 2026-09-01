---
name: quality-review
description: 明示されたQuality Loop案件で、statusがnext_role=reviewerを示し、review、review-plan、verify、assess-riskを行う場合だけ使用する。一般的なコードレビュー、一般的なQA、OpenSpec案件一般、回答代筆、実装、Owner裁定、自己クローズには使用しない。申告外変更はundeclared-change-detectedとして拒否する。
---

# Quality Review

案件正本を直接編集せず、`quality-loop`の公開CLIだけを使ってReviewer工程を完了する。

## Runtimeと依存関係

- このSkillは`runtime/quality_loop/`を同梱し、Skill自身のディレクトリを基準にCLIから解決する。
- 外部pipパッケージを要求せず、Python 3.10以上の標準ライブラリだけで動作する。
- 配置後の版は同梱の`VERSION`で確認する。

## 最優先の判定境界

- Reviewerの検証結果語彙は `remediated`、`verified`、`not-verified`、`unverified`、`finding-withdrawn`、`converted-to-suggestion`、`not-applicable` に従う。
- Implementerの反証Evidenceが正当な場合、Reviewerは `finding-withdrawn` や `converted-to-suggestion` を選択して自己訂正する。
- 申告外変更を観測した場合は`undeclared-change-detected`で拒否する。理由説明だけで許容せず、変更を戻すかImplementer提出を訂正させる。
- `accepted`、`rejected`、`不受入`、`closed`をReviewer判定として使わない。

## 手順

1. `status`を実行し、案件ID、revision、`next_role`、`next_action`、handoff IDを確認する。
2. `next_role`が`reviewer`でなければ変更せず停止し、表示された次Roleを案内する。
3. `next_action`に応じて適切な操作を行う（同じ応答で複数操作を実行しない）:
   - `review`: 初回レビュー
   - `review-plan`: Implementerの提出したResponse Plan評価・合意
   - `verify`: 修正提出後の独立検証
   - `assess-risk`: サイクル上限到達後または残余リスクの最終評価（Final Risk Assessment）。Coreが算出する全material unresolved Findingをcoverageする
4. baselineのPurpose、Intended Use、Risk Context、要求、受入基準、対象revisionを先に固定する。基準を推測、追加、勝手に緩和しない。
5. **比例性（Proportionality Gate）の確認**: 指摘がIntended UseやRisk Contextに見合っているかを評価し、過剰な完全性を押し付けず、軽微な仕様外改善は`improvement-proposal`へ分離する。
6. 対象と利用可能なEvidenceを自分で確認する。確認できない事項は`unverified`または`evidence-gap`とする。
7. 入力JSONを準備し、`previous_handoff_id`と`expected_case_revision`にstatusの現在値を使う。Invocation IDはこの操作専用の新しい値にする。
8. このSkillディレクトリ内の`bin/quality-review-cli`を、呼出し元の作業ディレクトリを変更せずに実行する。

```text
<quality-review-skill-dir>/bin/quality-review-cli --case-root <case-root> review --case-id <case-id> --input <json/file>
<quality-review-skill-dir>/bin/quality-review-cli --case-root <case-root> review-plan --case-id <case-id> --input <json/file>
<quality-review-skill-dir>/bin/quality-review-cli --case-root <case-root> verify --case-id <case-id> --input <json/file>
<quality-review-skill-dir>/bin/quality-review-cli --case-root <case-root> assess-risk --case-id <case-id> --input <json/file>
```

9. 成功JSONの`next_role`、`next_action`、`handoff`をそのまま次工程へ示す。失敗時は`error_code`と`remediation`を示し、正本を迂回編集しない。

実案件、case-root、現在handoffが提供されていない評価・相談ではCLI成功やhandoffを捏造しない。必要入力と実行すべき次操作だけを示す。

## 初回レビュー

- Findingは要求またはPurpose/Risk Context、観測事実、影響、期待状態、検証方法、Evidence参照へ追跡可能にする。
- Critical/HighのFindingはCoreがPlan必須として扱い、Finding自身のPlanが承認されるまでResponseを提出しない。Mediumは波及リスクや曖昧性がある場合にPlan必須、単純修正は直接`submit-response`とする（Adaptive Plan Gate）。
- 人、能力、意図、責任をFindingにしない。
- 仕様外の改善案は`improvement-proposal`（`plan_required: false`）へ分離し、強制しない。
- Findingが0件でも確認範囲とEvidenceを説明する。

## 独立検証

- 対象`submit-response`とは異なるInvocation IDを使用する。
- Implementerの自己申告だけで`remediated`/`verified`にしない。元の要求およびQuality Intentに対する有効性を再確認する。
- Implementerの反証EvidenceによってFindingの前提が崩れた場合、固執せず`finding-withdrawn`または`converted-to-suggestion`として処理する。
- 残余課題の追加修正による便益が小さく環境制約等がある場合、未解決のCritical指摘がなければ、3サイクルの反復を待たずに`early_risk_assessment: true`と`early_risk_rationale: "<理由>"`を指定して早期リスク評価へ移行できる。
- 変更がある場合、`changed_targets`、Owner許可範囲、独立した`change_observation.observed_changed_targets`を照合する。
- 申告外、許可外、観測不能を隠さない。修正で生じた別問題は新しいFindingにする。
- Reviewerは技術検証と残余リスクの客観的整理だけを記録し、Owner裁定を代行しない。

## 禁止事項

- baseline、Finding本文、Implementer回答、Owner裁定を代筆または改変しない。
- 対象成果物を修正しない。
- 自己受入、自己クローズを行わない。
- Evidenceを推測して作らない。
- 旧Skillの`Author Response`、二重digest、OpenSpec、Legacy互換の語彙や契約を持ち込まない。

品質語彙や比例性の判断に迷う場合だけ`references/qms-foundations.md`を読む。通常のstatus、Role確認、JSON操作では読まない。
