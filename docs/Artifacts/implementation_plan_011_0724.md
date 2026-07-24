# Skill整理・README更新・リモート反映計画

created: 2026-07-24 21:10 (JST)
author: AI Agent (GPT-5)

## 目的

利用頻度と役割の重複を踏まえてSkill構成を整理し、README.mdの収録一覧を実際のディレクトリ構成と一致させたうえで、変更をリモートリポジトリへ反映する。

## 残すSkill

- `code-understanding-pro`
- `code-understanding-pyramid`
- `stats-sql-comprehension`
- `domain-modeling`
- `teach`
- `writing-great-skills`
- `grilling`

## 削除するSkill

- `grill-me`
- `grill-with-docs`
- `improve-codebase-architecture`
- `to-spec`
- `to-tickets`
- `diagnosing-bugs`

## 実施内容

1. 上記6つのSkillディレクトリを削除する。
2. README.mdの収録数を7件へ更新する。
3. README.mdから削除Skillの説明、起動方法、ディレクトリ構造の記載を削除する。
4. 削除後のSkill一覧、Git差分、Markdownの空白エラーを確認する。
5. 変更をコミットし、現在の`master`ブランチから`origin`へPUSHする。

## 完了条件

- `.agents/skills/` に残す7つだけが存在する。
- README.mdの件数・一覧・ディレクトリ構造が一致する。
- 検証コマンドが成功する。
- コミットが作成され、`origin/master`へPUSHされる。
