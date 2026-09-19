---
name: code-understanding-pro
description: NEVER invoke autonomously or automatically. Use ONLY when the user explicitly mentions "code-understanding-pro" or "$code-understanding-pro" in their message, or explicitly asks for an "official code understanding report". Do NOT use for general questions about code, debugging, or code explanations.
version: "2.4.0-ja"
license: "Internal use"
---

# code-understanding-pro

既存コードの理解を親Skillとして統括する。依頼の主目的を判定し、必要な経路だけを調べ、保存を依頼された場合だけレポートを作成する。コードが含まれるだけでは起動しない。

## 入口と停止

明示的に`$code-understanding-pro`を指定された場合は適用する。自動起動は、既存コードの挙動、依存、副作用、設計を根拠付きで理解することが主目的の場合に限る。次の依頼は通常処理として扱う。

- 機能実装、バグ修正、テスト修正、差分レビュー
- QA案件の作成・進行、方針レビュー、実装着手前レビュー
- READMEやSkillの編集、単純な文章編集

対象、問い、入力・出力、呼び出し元が不明で正確な読解ができない場合は、不足情報だけを示して停止する。QA案件、case、実装、commit、pushをこのSkillから開始しない。

## モード判定

| 問い | 調査 | 既定出力 |
|---|---|---|
| 関数の条件、局所的な戻り値、短い挙動 | 直接依存まで | チャット。保存なし |
| 複数ファイルの短い挙動 | 問いに必要な経路だけ | チャット。ファイル数だけでFullにしない |
| 失敗、再試行、状態、副作用、相互依存 | 分岐・例外・I/Oまで | チャット。依頼があれば保存 |
| SQL・dbt・BigQuery | 粒度、JOIN、CTE、行数変化 | `stats-sql-comprehension`へ観点を返す |
| R/Python統計コード | 母集団、欠測、推定量、バイアス | `stats-sql-comprehension`へ観点を返す |
| レポート保存・引継ぎ資料 | 必要な深度で調査 | `docs/reports/code-understanding-pro/`へ保存 |

Review、Documentation、Refactoringは依頼の目的が明示されている場合だけ選ぶ。複雑度は、複数モジュール間の状態受渡し、外部結果を変える分岐、非同期・再試行が理解の中心なら`complex`とし、必要な場合だけMermaidを使う。共通フレームは[code-understanding-pyramid](../code-understanding-pyramid/SKILL.md)、SQL・統計の専門観点は[stats-sql-comprehension](../stats-sql-comprehension/SKILL.md)へ返す。

## 読解手順

1. 文脈: 対象、目的、入出力、呼び出し元、関連テスト・設定・資料、未確認点を特定する。
2. 概要: 一文要約、主要処理、責務、データフローを暫定整理する。
3. 詳細: 引数・戻り値、制御分岐、例外、I/O、状態変更、境界値を追跡する。
4. 設計: コードで確認できる事実と推測を分け、制約、トレードオフ、リスクを記す。
5. 活用: 依頼されたチャット回答またはレポートへ、根拠、未確認、必要なテストをまとめる。

各段階は対象経路と未確認点が記録されて初めて完了とする。必要な範囲を超えて全ファイルを読む、保存を自動開始する、未確認を推測で埋めることはしない。

## 保存

保存依頼がある場合だけ、`scripts/write_report.py`を使い、呼出し元プロジェクトの`./docs/reports/code-understanding-pro/<target>/run_<id>/`へ`report.md`、`run_meta.json`、`source_manifest.json`を保存する。レポートの安全契約、秘密情報の伏字、競合時の停止は[interface.md](references/interface.md)を読む。Quickはチャットで完結し、保存しない。

```bash
python3 .agents/skills/code-understanding-pro/scripts/write_report.py \
  --mode full --target src/example.py --content-file /tmp/report.md \
  --output-root ./docs/reports/code-understanding-pro --run-id example \
  --adapter generic --audience beginner --source src/example.py
python3 .agents/skills/code-understanding-pro/scripts/validate_report.py \
  ./docs/reports/code-understanding-pro/example/run_example/report.md --adapter generic
```

保存レポートは、結論、対象と前提、全体像、処理フロー、詳細、初学者向け用語、注意点・リスク、根拠ファイル・行番号を含める。`sql`／`stats`では対応する専門必須節も満たす。検証が成功するまで保存完了を報告しない。

## 出力と安全境界

- チャットの結論を先に示し、事実、推測、未確認、リスクを分ける。
- 一般レビューでは`[Critical]`、`[Major]`、`[Consider]`、`[Nit]`、`[FYI]`を使い、要求違反と仕様外提案を分ける。
- 保存依頼なしの短い問いにはレポート、図、空ディレクトリを生成しない。
- レポート本文の変更は対象ファイルとその関連資料に限定し、既存成果物を移動・削除しない。
- 既存コードを変更する依頼では、通常の実装ワークフローへ戻り、このSkillのレポートを強制しない。
- 事実確認に必要なテスト・コマンドは、ユーザーの依頼と副作用を確認してから提案する。無承認の外部書込み、QA状態更新、Gitリモート操作を行わない。

一般レビューの重大度は[review-severity-guide.md](references/review-severity-guide.md)、リファクタリングの安全確認は[refactoring-safety-checklist.md](references/refactoring-safety-checklist.md)、保存契約は[interface.md](references/interface.md)を必要な分岐で参照する。保存契約の`code_context.md`はContext成果物であり検証CLIの対象外、曖昧な秘密形式は保存を中止し、`.incomplete`や部分出力は内容確認後に利用者が削除する。出力rootは信頼済み非共有ディレクトリとし、同一UIDの親ディレクトリ差し替えは保護境界外である。
