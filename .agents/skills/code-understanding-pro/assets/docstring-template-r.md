# R roxygen2テンプレート

```r
#' 関数の目的を一文で説明する
#'
#' 詳細説明。処理の背景、制約、副作用、想定ユースケースを記述する。
#'
#' @param arg1 引数の意味。
#' @param arg2 引数の意味。
#'
#' @return 戻り値の意味と構造。
#'
#' @details
#' - 入力契約
#' - 出力契約
#' - 境界条件
#' - 副作用
#'
#' @examples
#' function_name("x", 1)
#'
#' @export
function_name <- function(arg1, arg2) {
  # ...
}
```

## Rコード理解時の追加観点

- `NA`, `NaN`, `NULL` の扱い
- factorのlevel
- tidy evaluation
- group_by状態
- rowwise処理の有無
- data.tableの参照更新
- 乱数seed
- locale/encoding
- Windows/Linuxのpath差
