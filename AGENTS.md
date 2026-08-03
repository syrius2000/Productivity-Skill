# AGENTS.md

## Cursor Cloud specific instructions

このリポジトリはサービス（Web/API/DB 等）を持たない、AIエージェントスキル集（Markdown）＋ Python ヘルパースクリプト＋ pytest です。ビルド工程やデプロイ対象はありません。README.md にスキルの概要、`.agents/skills/code-understanding-pro/references/interface.md` にスクリプトの契約が記載されています。

### 実行・テスト（要点のみ）

- テストは pytest。標準ライブラリ + pytest のみで動作し、外部サービス不要。
- 重要な落とし穴: `python3 -m pytest`（引数なし）はスキル配下のテストを**収集しません**。pytest が `.` 始まりディレクトリ（`.agents`）を無視するためです。全テストを走らせるには両方のパスを明示指定してください:
  ```bash
  python3 -m pytest tests/ .agents/skills/code-understanding-pro/tests/
  ```
- リンター/ビルド/CI の設定はリポジトリに存在しません。

### スキルの中核スクリプトを動かす（code-understanding-pro）

3つの CLI が中核機能です。エンドツーエンドの流れ（コンテキスト収集 → レポート生成 → 検証）:

```bash
# 1) 対象コードからコンテキスト Markdown を生成
python3 .agents/skills/code-understanding-pro/scripts/collect_code_context.py <paths> --ext .py --output-root /tmp/ctx --run-id demo

# 2) レポートを保存（本文はテンプレートを流用可能）
python3 .agents/skills/code-understanding-pro/scripts/write_report.py \
  --mode full --target <paths> \
  --content-file .agents/skills/code-understanding-pro/assets/output-template-full.md \
  --adapter generic --output-root /tmp/report --run-id demo

# 3) 生成レポートが契約を満たすか検証（PASS で成功）
python3 .agents/skills/code-understanding-pro/scripts/validate_report.py /tmp/report/scripts/run_demo/report.md --adapter generic
```

- `write_report.py` の本文は成果物契約に沿う必要があります。`assets/output-template-*.md` は契約を満たすため、動作確認やテンプレートとして利用できます。
- 各 run は `run_<id>` ディレクトリに隔離され、`run_meta.json` / `source_manifest.json` を伴います。同一 run-id への上書きは拒否されます。
