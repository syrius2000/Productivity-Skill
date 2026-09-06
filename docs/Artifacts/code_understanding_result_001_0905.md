# 段階1：コード理解3スキルの実装結果

created: 2026-09-05 23:10 (JST)
update: 2026-09-05 23:10 (JST)
author: Codex (GPT-5)

## 実施範囲

[段階1計画](implementation_plan_014_0905.md)に従い、次の3 Skillと契約テストを変更した。保存CLI、出力スキーマ、排他制御、対象外4 Skill、実DBへの接続は変更していない。

| 対象 | 実装内容 |
|---|---|
| `.agents/skills/code-understanding-pro/SKILL.md` | QuickはStep 0と質問に必要なStep 2だけを追跡する規則にした。Full、Review、Documentation、Refactoringは5段階を維持した。Mermaidを、モジュール間の受渡し、外部結果を変える分岐、非同期・時間順序・再試行に限定した。親から子への4項目の受渡しと、SQL・統計の条件付き統合を明記した。 |
| `.agents/skills/code-understanding-pyramid/SKILL.md` | 親から受け取る4項目を定義し、必要なStageだけを実施して既読資料を再読しない規則にした。 |
| `.agents/skills/stats-sql-comprehension/SKILL.md` | 独自の5段階説明を廃止し、SQL・統計で入力に現れた専門観点だけを確認する二表に置き換えた。無承認SQL実行禁止を維持した。 |
| `tests/test_code_understanding_suite_contract.py` | Quick、Mermaid、親子受渡し、条件付き専門確認、無承認実行禁止の契約を追加した。 |

`code-understanding-pro/SKILL.md` はこのラウンド開始前から大幅な未コミット短縮差分を含んでいた。保存契約の既存テストが求める `code_context.md`、曖昧な秘密形式の保存中止、信頼済み非共有ディレクトリ、`.incomplete` の利用者確認が短縮後の本文から欠けていたため、保存契約の補足として最小限で復元した。この復元は段階1の「安全契約を弱めない」条件に直接対応する。

## 検証結果

実行日時：2026-09-05 23:10 (JST)

```text
python3 -B -m pytest --assert=plain -p no:cacheprovider \
  tests/test_code_understanding_suite_contract.py \
  tests/test_skill_frontmatter.py \
  .agents/skills/code-understanding-pro/tests/test_report_writer.py \
  .agents/skills/code-understanding-pro/tests/test_report_validator.py
```

結果：52 passed。対象3 SkillのMarkdown相対リンクも全て解決した。`git diff --check` も合格した。

このテスト群はSkillの構造、保存契約、レポート検証を確認する。実際のLLM回答の正確性、説明の深さ、不要な往復の減少を証明するものではない。

## E1〜E4の評価

固定入力は[手動比較仕様](skill_evaluation_spec_001_0905.md)に保存した。独立コンテキストで同じモデルを反復起動する評価環境は確認できなかったため、Skillなし・現行・改善版の生成比較は未実施である。

| ID | 状態 | 結論 |
|---|---|---|
| E1 | 生成比較未実施 | Quickの短絡規則は本文・契約テストで確認したが、回答品質は未確認 |
| E2 | 生成比較未実施 | Mermaid条件と事実・推論分離は本文・契約テストで確認したが、回答品質は未確認 |
| E3 | 生成比較未実施 | SQLの粒度・JOIN・無承認実行禁止は本文・契約テストで確認したが、回答品質は未確認 |
| E4 | 生成比較未実施 | 統計の選択・交絡・未確認扱いは本文で規定したが、回答品質は未確認 |

したがって採否は「実装済み・生成比較未実施」であり、性能向上の採用判定は保留する。

## 保持した境界

- Quickは保存しない。
- Full、Review、Documentation、Refactoringは既存の保存・検証契約を維持する。
- 曖昧な秘密形式は保存を中止する。
- `.incomplete` や部分出力を自動削除しない。
- SQLは無承認で実行しない。
- 子Skillは独自成果物や長文回答を所有しない。

## 次の段階

段階2ではTeachとwriting-great-skillsの継続価値を扱う。Teachの実際の教材保存・再開を試す前に、`docs/learning/` とAGENTS.mdのArtifact規則の優先関係を決める必要がある。日本語利用案内の追加と、保存を伴わない静的確認はこの決定と切り分けられる。
