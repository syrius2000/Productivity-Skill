# Python DocStringテンプレート

## Google style

```python
def function_name(arg1: str, arg2: int) -> dict:
    """関数の目的を一文で説明する。

    詳細説明。必要に応じて、処理の背景、制約、副作用、例外条件を記述する。

    Args:
        arg1: 引数の意味。
        arg2: 引数の意味。

    Returns:
        戻り値の意味と構造。

    Raises:
        ValueError: どの条件で発生するか。

    Side Effects:
        ファイルI/O、DB更新、API呼び出し、ログ出力など。

    Examples:
        >>> function_name("x", 1)
        {...}
    """
```

## レビュー時の注意

DocStringには以下を入れる。

- 何をするか
- 何をしないか
- 入力契約
- 出力契約
- 例外
- 副作用
- 代表例
- 境界条件
