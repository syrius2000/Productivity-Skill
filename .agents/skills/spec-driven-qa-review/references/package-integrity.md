# Skillパッケージ整合性

`MANIFEST.txt`をSkillパッケージの正本ファイル集合とする。配置前後でManifestと実ファイルを比較し、欠落と余剰を区別する。

```bash
python scripts/validate_package.py .
```

検証対象からは、実行で生成される`__pycache__`、`.pytest_cache`、`*.pyc`、`.DS_Store`、`Thumbs.db`を除外する。除外規則を変更する場合は、スクリプトとテストを同時に更新する。

Manifestにないファイルを自動的に正本へ追加してはならない。新しい参照資料、スクリプト、テストを追加した場合は、内容確認後に`MANIFEST.txt`へ明示的に登録する。
