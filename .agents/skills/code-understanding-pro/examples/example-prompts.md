# 依頼例

## Quick Mode

```text
この関数が何をしているか、短く説明して。
```

```text
@src/utils/parser.py L20-L80 をQuick Modeで説明して。
```

## Full Mode

```text
このモジュールを5段階コード理解ピラミッドで解析して。
```

```text
この処理を、文脈・概要・詳細・設計意図・活用まで分けて説明して。

深い解析結果は `skill_out/code_understanding/example/run_full_demo/report.md` に保存し、チャットには要点と保存先だけを返して。
```

## Review Mode

```text
このPRをQAしてください。Critical/Major/Consider/Nit/FYIで分類して。
```

```text
バグ、テスト不足、副作用、境界条件の観点でレビューして。

レビュー結果は `skill_out/code_understanding/example/run_review_demo/report.md` に保存し、チャットにはCritical/Majorの要点と保存先だけを返して。

## SQL Mode

```text
このSQLを初学者向けに説明してください。1行の粒度、CTE、JOIN前後の行数変化、検証SQLを含め、code-understanding-proのsqlアダプターでreport.mdへ保存してください。SQL自体は実行しないでください。
```

## Statistics Mode

```text
このR解析コードを初学者向けに説明してください。対象母集団、欠測・除外、推定量・前提、バイアス、再現コードを含め、statsアダプターでreport.mdへ保存してください。
```
```

## Documentation Mode

```text
この関数にPythonのGoogle style DocStringを書いて。
```

```text
このR関数をroxygen2形式でドキュメント化して。
```

## Refactoring Mode

```text
挙動を変えずにリファクタリング案を出して。変更前後とテスト案もください。
```

```text
この1000行程度の処理を安全に分割する案を出して。ただし行数削減自体は目的にしないで。
```
