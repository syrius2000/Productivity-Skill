# Quality Review変更履歴

## 1.5.0

- `review-standalone`を追加し、明示対象からrevision 1の正式caseとReviewer向けhandoffをbootstrapできるようにした。
- Finding、Evidence判定、実装許可、Owner裁定は既存の正式Quality Loop操作へ委譲する。
- 対象成果物を変更せず、既存case schema、Role境界、undeclared-change検出を維持する。
- 対象manifestは通常ファイルを明示指定し、SHA-256はストリーミング計算する。1ファイル10 MiB、全体50 MiB、最大32対象を上限とする。
- LLMによるFinding本文の動的品質評価は未実施である。

## 1.4.0

- Quality Loop v1.4.0のReviewer Skillとして、同梱runtimeとCLIラッパーを提供する。
- Python 3.10以上の標準ライブラリのみで動作する。
