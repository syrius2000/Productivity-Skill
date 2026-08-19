---
name: artifacts-archiver
description: Use when the user asks to "archive documents", "clean up old plans", "consolidate artifacts", "archive all", or organize files in ./docs/Artifacts/ and ./docs/Archives/. Consolidates past implementation plans and reports into 1-2 summary documents with specified date ranges while preserving active plan numbers.
---

# Artifacts Archiver (ドキュメント自動アーカイブ・整理スキル)

`./docs/Artifacts/` 内の実装計画書や報告書を整理し、過去のドキュメントを対象期間（XX日〜YY日）を明記した原則1本（最大2本）のまとめ文書へ統合して `./docs/Archives/` に退避するスキル。ユーザーが「アーカイブして」「古い書類を整理して」「全部アーカイブして」などと依頼した時に発動する。

## 概要

プロジェクト進行に伴い `./docs/Artifacts/` ディレクトリ内に増えた過去の実装計画書（`implementation_plan_*.md`）やWalkthrough（`walkthrough_*.md`）などの旧ドキュメントを、現状に合わせて精査・集約し、**対象期間を明記した原則 1 本（例外時のみ最大 2 本）のまとめ文書**として `./docs/Archives/` へ退避します。
アクティブな計画書のファイル名や番号（例: `003`）は勝手に書き換えず保持し、トレーサビリティとリンクの健全性を維持します。

---

## 適用タイミング（Triggers）

- ユーザーが「過去の計画書をアーカイブして」「Artifactsを整理して」「古い書類をまとめて」「全部アーカイブして」などと指示した場合
- 進行中のフェーズが切り替わり、古い計画書や報告書が複数貯まってきた場合

---

## ワークフローと手順（Workflow Steps）

### 1. アーカイブ対象の動的判定 (Target Detection)

ユーザーの指示のニュアンスに応じて対象範囲を決定する。

- **通常指示（「整理して」「アーカイブして」等）**:
  AIが各ドキュメントのタスク完了状況や進行フェーズを判別し、**完了済みの過去計画・報告書のみ**をアーカイブ対象とし、現在進行中のアクティブな計画書は `./docs/Artifacts/` に残す。
- **全件指示（「全部アーカイブして」「全消去整理」等）**:
  判定を挟まず、`./docs/Artifacts/` 内のすべての計画書・報告書をアーカイブ対象とする。

### 2. アクティブ計画書の番号保持 (Number Preservation)

- `./docs/Artifacts/` に残るアクティブな計画書のファイル名・番号（例: `implementation_plan_003_0725.md`）は**リセットや再採番を行わず、元の番号をそのまま維持**する。
- メタデータ（`updated: YYYY-MM-DD HH:MM (JST)` 等）が必要に応じて更新された場合のみ追記する。

### 3. 精査・まとめ文書の作成と退避 (Consolidation & Archiving)

1. `./docs/Archives/` ディレクトリが存在しない場合は作成する (`mkdir -p ./docs/Archives`)。
2. 対象となる過去ドキュメント群の内容・進捗・成果を精査し、**原則 1 本（内容が大きく多岐にわたり収まらない場合のみ例外的に最大 2 本）のまとめ文書**（例: `archived_summary_001_{MMDD}.md`）に統合・要約する。
3. **必須メタデータ**: まとめ文書のヘッダーおよび概要欄に、対象ドキュメント群の**対象期間（例: `対象期間: 2026-07-12 〜 2026-07-24`）**を必ず明記する。
4. まとめ文書を `./docs/Archives/` へ書き出す。
5. 集約完了後、元の個別旧ファイル群を `./docs/Artifacts/` から削除し、`./docs/Archives/` 配下もファイルが乱立しないようスッキリ保つ。

### 4. リンク・参照の自動調整 (Relative Link Repair)

1. Markdown 内のファイル間参照リンクが相対パス（`[text](../Archives/filename.md)` や `[text](./filename.md)`）になっていることを確認し、ディレクトリ移動に伴うリンク切れを補正する。
2. **絶対パス（`file:///...`）は使用しない**規約を遵守する。

---

## チェックリスト

- [ ] アーカイブ対象の選定はユーザー指示（通常 vs 全件）に合致しているか？
- [ ] アクティブな計画書のファイル名・連番は勝手にリセットされず維持されているか？
- [ ] まとめ文書は**原則 1 本（最大 2 本）**に集約されているか？
- [ ] まとめ文書に**対象期間（例: `対象期間: YYYY-MM-DD 〜 YYYY-MM-DD`）**が明記されているか？
- [ ] まとめ完了後、不要となった元ファイルは整理・削除されているか？
- [ ] 全ドキュメントの作成・更新日時が JST 表記になっているか？
- [ ] Markdown内リンクがすべて相対パスで記載されているか？
