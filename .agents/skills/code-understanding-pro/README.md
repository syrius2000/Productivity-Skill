# code-understanding-pro 日本語版

既存コードの理解、レビュー、QA、ドキュメント化、リファクタリング支援を行うAgent Skillです。軽い質問はチャットで返し、深い解析はMarkdownレポートとして保存します。

## 内容

```text
code-understanding-pro/
├── SKILL.md
├── README.md
├── VERSION
├── LICENSE.txt
├── manifest.json
├── references/
│   ├── qiita-code-reading-pyramid.md
│   ├── review-severity-guide.md
│   ├── refactoring-safety-checklist.md
│   └── test-first-caveats.md
├── assets/
│   ├── output-template-quick.md
│   ├── output-template-beginner.md
│   ├── output-template-full.md
│   ├── output-template-review.md
│   ├── output-template-refactoring.md
│   ├── mermaid-patterns.md
│   ├── docstring-template-python.md
│   └── docstring-template-r.md
├── scripts/
│   ├── collect_code_context.py
│   ├── validate_report.py
│   └── write_report.py
└── examples/
    ├── example-prompts.md
    └── expected-output-skeleton.md
```

## 使い方

Agent Skills互換の環境では、このディレクトリをSkill配置場所にコピーしてください。

例：

```bash
mkdir -p ~/.agents/skills
cp -R code-understanding-pro ~/.agents/skills/
```

プロジェクト配下に置く場合の例：

```bash
mkdir -p .agents/skills
cp -R code-understanding-pro .agents/skills/
```

## 想定される依頼例

- この関数を5段階で説明して
- このPRをQAして
- このコードの副作用を洗い出して
- 初学者向けに処理フローを説明して
- DocStringとMarkdown仕様を書いて
- 挙動を変えないリファクタリング案を出して

## 設計思想

このSkillは、レビュー指摘を先に出すのではなく、次の順にコード理解を深めます。

1. 文脈把握
2. 概要理解
3. 詳細追跡
4. 深い設計理解
5. 活用

軽い質問ではQuick Mode、深い解析ではFull Mode、レビュー/QAではReview Modeを使います。

## 3Skillの構成

| Skill | 役割 |
|---|---|
| `code-understanding-pro` | 依頼判定、成果物保存、チャット要約 |
| `code-understanding-pyramid` | 5段階の汎用理解フレーム |
| `stats-sql-comprehension` | SQL・統計コードの専門観点 |

## 出力方式

| モード | 出力 |
|---|---|
| Quick | チャットのみ |
| Full | `report.md` とチャット要約 |
| Review | `report.md` とチャット要約 |
| Documentation | `report.md` とチャット要約 |
| Refactoring | `report.md` とチャット要約 |

深い解析では `report.md`、`run_meta.json`、`source_manifest.json` を `skill_out/code_understanding/<target>/run_<id>/` に保存します。同一runの再実行では上書きしません。

```bash
python3 scripts/write_report.py \
  --mode full \
  --target src/example.py \
  --content-file /tmp/report.md \
  --output-root ./skill_out/code_understanding \
  --run-id example \
  --adapter generic \
  --audience beginner \
  --source src/example.py
```

保存後はレポート契約を検証します。

```bash
python3 scripts/validate_report.py \
  ./skill_out/code_understanding/example/run_example/report.md \
  --adapter generic
```

保存前に一般的なAPIキー、パスワード、Bearerトークン、秘密鍵は伏せ字にします。詳細な出力契約は `references/interface.md` を参照してください。
