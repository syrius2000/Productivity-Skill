# スキル改善の基準スナップショット

created: 2026-09-05 22:13 (JST)
update: 2026-09-05 22:13 (JST)
author: Codex (GPT-5)

## 用途

本書は、段階1〜3で変更前後を取り違えないための基準である。対象Skillの本文・直接参照・既存差分を特定する。性能評価の結果、変更の承認、実装完了を意味しない。

## Git基準

| 項目 | 値 |
|---|---|
| ブランチ | `codex/decision-readiness-qa-exploration` |
| HEAD | `8934c17ae76cca1693420e37d23ca8e1795115ea` |
| 基準日時 | 2026-09-05 22:13 (JST) |
| ステージ済み差分 | なし |
| 未ステージ差分 | 93ファイル、145行追加、5,878行削除 |
| 未追跡 | 新規2 Skill、既存の計画・集約文書、`qms-cases/`、本段階で追加する2文書 |

未ステージ差分には、`code-understanding-pro`、`domain-modeling`、`stats-sql-comprehension`、README、テスト、旧QA Skillの削除などが含まれる。これらは今回の段階0の成果ではない。以降の段階では、各ラウンドの開始・終了時に差分を比較し、既存差分を上書き・復元・再整理しない。

## 対象とファイル基準

| Skill | ファイル | SHA-256 | 現在の差分 |
|---|---|---|---|
| artifacts-archiver | `.agents/skills/artifacts-archiver/SKILL.md` | `d6334121782db5a7f53028ee9dee54a7e2db9d61281b6eb29cd48117767de329` | なし |
| code-understanding-pro | `.agents/skills/code-understanding-pro/SKILL.md` | `4f380c5454ff511656d8830174224273bf93021109d6417c2f079a0f930e20f0` | あり |
| code-understanding-pro | `references/interface.md` | `6d11edec8a5705a3507384e3400f19e739bbcd24746a49a7d3a4891b0eff8c5f` | なし |
| code-understanding-pro | `references/refactoring-safety-checklist.md` | `de48b9f018e0290e2074ca0dcd35e81df09d095c5d96797d32bce7abc0027fb8` | なし |
| code-understanding-pyramid | `.agents/skills/code-understanding-pyramid/SKILL.md` | `745fc7835d67123fbe26df605622ad72464167c026ce06b318934aafe30650b3` | なし |
| domain-modeling | `.agents/skills/domain-modeling/SKILL.md` | `db9d2bc70bbd3e359c27fe13aa8ca3b6e075b0469313f857c2c418c3b8c96489` | あり |
| domain-modeling | `ADR-FORMAT.md` | `f1f36cd3f8d3b6474ddd5855da4e233bfc4ae1a1c5024909ccf11871819a41b2` | なし |
| domain-modeling | `CONTEXT-FORMAT.md` | `b8cc318f2a4285b530e908b6bc43901c3c5cd11100362636bbc4216639bef597` | なし |
| grilling | `.agents/skills/grilling/SKILL.md` | `10ff989e7498b23b5acb49d5048f11dcd906757d2f79c5cdf8a00001381296f2` | なし |
| stats-sql-comprehension | `.agents/skills/stats-sql-comprehension/SKILL.md` | `3bacca68e583499cb7e6ab964b0638ff66445d1557413d8df05d8aba8c0152c3` | あり |
| stats-sql-comprehension | `references/stats-validation-checklist.md` | `cc259483d4995c1b545b2d5393d1f6523a0508584297062867ed4252fa5eb896` | なし |
| teach | `.agents/skills/teach/SKILL.md` | `9fdb5281fb4159d14ac3f9645ed21c14d71709fb84c6437de365305765b8c179` | なし |
| writing-great-skills | `.agents/skills/writing-great-skills/SKILL.md` | `677f190c77e08c1173ebf09fbd13ea9183d92c5069b4db5a86398a9bed3c245d` | なし |
| writing-great-skills | `GLOSSARY.md` | `cccd684c73fb7a06f523497b0121765f92d2b33d6ef9c51602294849233451d6` | なし |

相対パスの基準はリポジトリルートである。表中で省略した相対パスは対象Skillディレクトリ内とする。

## 対象外

| Skill | 理由 |
|---|---|
| quality-review | QA-productsが正本の配布物。今回の変更・評価対象外 |
| quality-response | QA-productsが正本の配布物。今回の変更・評価対象外 |
| decision-plan-review | 直近に新規追加されたSkill。今回の変更・評価対象外 |
| implementation-readiness-review | 直近に新規追加されたSkill。今回の変更・評価対象外 |

## 検証入口

| 確認対象 | コマンド | 確認できる範囲 |
|---|---|---|
| Skill一覧・frontmatter・リンク・manifest | `python3 -B -m pytest --assert=plain -p no:cacheprovider tests/test_skill_inventory_contract.py tests/test_skill_frontmatter.py` | ファイル構造・宣言・リンク。LLMの判断品質は確認しない |
| コード理解スイート | `python3 -B -m pytest --assert=plain -p no:cacheprovider tests/test_code_understanding_suite_contract.py .agents/skills/code-understanding-pro/tests/test_report_writer.py .agents/skills/code-understanding-pro/tests/test_report_validator.py` | 親子境界、保存契約、レポート検証。回答内容の有用性は確認しない |
| 変更系Skill境界 | `python3 -B -m pytest --assert=plain -p no:cacheprovider tests/test_mutating_skill_boundaries.py` | archiverとdomain-modelingの文字列契約。実アーカイブや実書込みは確認しない |

## 保存契約の未決定事項

Teachは教材を `docs/learning/` に保存するよう指定する。一方、このリポジトリのAGENTS.mdは生成Artifactを `docs/Artifacts/` に保存し、日本語Markdown・連番・ヘッダーを要求する。学習教材をArtifactとして扱うかは未決定である。

段階0では教材、HTML、学習記録、`docs/learning/` を生成しない。段階2でTeachの保存機能を実測する前に、この扱いをユーザーが決める必要がある。
