# Portfolio Skill Routing Smoke Evaluation

## Purpose and limits

Check whether ordinary, naturally phrased requests select the intended repository Skill among the 14 Skills in `.agents/skills/`, with particular attention to `falsify-me`, `decision-plan-review`, `implementation-readiness-review`, and `grilling`. This is a small routing smoke evaluation, not a quality guarantee or a release gate.

## Fixed scoring

For each case, record separately:

1. **Selection:** expected Skill selected, another Skill selected, or no Skill selected.
2. **Procedure:** whether the response follows the selected Skill's entry conditions and boundaries.
3. **Output quality:** whether the response helps with the request, independent of selection.

For negative cases, the expected selection is no Skill from the four-skill focus set unless the prompt independently meets another Skill's entry condition. Record the actual Skill and rationale. Do not infer a Skill load from response style; use session load events if available, otherwise mark load evidence unavailable.

## Cases and expected outcomes

| ID | User request | Expected route | Expected non-route / reason |
| --- | --- | --- | --- |
| R01 | この説明の根拠が弱いところを探し、反例も出したうえで文章を直して。 | `falsify-me` | `decision-plan-review`: no choice or implementation plan is being reviewed. |
| R02 | 次のコードを批判的に検討して、動作を壊す条件と最小修正を示して。 | `falsify-me` | `implementation-readiness-review`: this is critique of code, not readiness of a planned change. |
| R03 | 提案した保存方式に見落とした前提がないか、後戻りにつながる点だけ確認して。 | `decision-plan-review` | `falsify-me`: the request asks for a bounded decision review, not explicit falsification and revision. |
| R04 | SQLiteからPostgreSQLへ移す方針で進めようと思う。判断を変えるほどの制約や未知点があるか見て。 | `decision-plan-review` | `implementation-readiness-review`: no concrete implementation plan or start decision is supplied. |
| R05 | この変更計画で実装を始めてよいか、受入条件と検証方法の不足を見て判定して。 | `implementation-readiness-review` | `decision-plan-review`: the request is a readiness decision on a concrete plan. |
| R06 | APIの認証方式を更新する計画を書いた。着手前にブロッカーが残っていないか確認して。 | `implementation-readiness-review` | `falsify-me`: no explicit request to attack the plan's claims; asks for implementation readiness. |
| R07 | 新しい社内検索の設計を考えている。決めるべきことを一問ずつ質問して掘り下げて。 | `grilling` | `decision-plan-review`: user asks for an iterative interview, not a one-pass review. |
| R08 | 私の移行計画を面接するように質問して、回答に応じて次の論点を選んで。 | `grilling` | `implementation-readiness-review`: user has not asked for a readiness verdict. |
| R09 | この段落の誤字と表記ゆれだけ直して。 | None of focus set | Proofreading only; no critique request. |
| R10 | この関数が空配列を返す原因を調べて、直して。 | None of focus set | Ordinary debugging and implementation; no explicit critical review or readiness decision. |
| R11 | この設計案を読んで、利用者向けに要点を説明して。 | None of focus set | Explanation request; no review, falsification, or interview request. |
| R12 | 来月の開発計画を作って。作業を週ごとに並べて。 | None of focus set | Planning request only; no assessment or grilling requested. |

## Run record

The initial single-pass measurement is recorded in [portfolio-routing-results.md](./portfolio-routing-results.md). It used all 14 repository Skills visible in this checkout. User-global Skills may also have been available, so the candidate set was not fully isolated. Codex JSON events exposed commands that read focus Skill entrypoints; those reads are the selection evidence. A response that resembles a Skill workflow without an observed entrypoint read is not counted as a confirmed Skill selection. The next run should repeat the cases that missed and use a second pass for stability before editing triggers.

| Date | CLI version | Model | Skill availability | Repetitions | Parallelism | Load evidence | Results |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-11 | 0.167.1 | `gpt-6-luna` | 14 repository Skills; user-global availability not isolated | 1 | 3 | JSON command events for focus Skill entrypoint reads | [Results](./portfolio-routing-results.md) |
