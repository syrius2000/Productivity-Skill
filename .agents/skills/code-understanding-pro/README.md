# code-understanding-pro 日本語版

既存コードの理解、レビュー、QA、ドキュメント化、リファクタリング支援を行うAgent Skillです。

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
│   ├── output-template-full.md
│   ├── output-template-review.md
│   ├── output-template-refactoring.md
│   ├── mermaid-patterns.md
│   ├── docstring-template-python.md
│   └── docstring-template-r.md
├── scripts/
│   └── collect_code_context.py
└── examples/
    ├── example-prompts.md
    └── expected-output-skeleton.md
```

## 使い方

Agent Skills互換の環境では、このディレクトリをSkill配置場所にコピーしてください。

例：

```bash
mkdir -p ~/.agent/skills
cp -R code-understanding-pro ~/.agent/skills/
```

プロジェクト配下に置く場合の例：

```bash
mkdir -p .agent/skills
cp -R code-understanding-pro .agent/skills/
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
