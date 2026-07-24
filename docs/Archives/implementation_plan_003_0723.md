# インプリメンテーションプラン: mattpocock-skills からの有用スキルのコピー

created: 2026-07-23 00:31 (JST)
author: AI Agent (Gemini 3.6 Flash)

## 1. 概要

`mattpocock-skills` リポジトリから、ユーザーの開発生産性向上および思考・設計・デバッグ強化に役立つ有用なスキル群（grilling 関連含む）を抽出して本リポジトリの `.agents/skills/` 配下へコピーし、配置・統合を行います。

---

## 2. コピー対象スキル一覧 (箇条書き報告)

以下の 10 個のスキルを本リポジトリの `.agents/skills/` ディレクトリにコピーします。

### 🌶️ Grilling 関連スキル（質問・面接・思考整理）

1. **`grilling`** (`mattpocock-skills/skills/productivity/grilling`)
   - アイデアや設計に対する多角的・妥協のない1問1答面接スキル。
2. **`grill-me`** (`mattpocock-skills/skills/productivity/grill-me`)
   - `/grill-me` コマンドで `grilling` を迅速発元するショートカットスキル。
3. **`grill-with-docs`** (`mattpocock-skills/skills/engineering/grill-with-docs`)
   - 面接を行いながら、同時にドキュメント（ADRおよびドメイン用語集）を自動生成する拡張スキル。

### 🛠️ 開発・設計・デバッグ支援スキル

4. **`diagnosing-bugs`** (`mattpocock-skills/skills/engineering/diagnosing-bugs`)
   - 確実な再現ループと仮説検証による構造的バグ診断スキル。
5. **`to-spec`** (`mattpocock-skills/skills/engineering/to-spec`)
   - 対話履歴から再質問なしで完全な仕様書（Spec / PRD）を自動生成するスキル。
6. **`to-tickets`** (`mattpocock-skills/skills/engineering/to-tickets`)
   - 仕様書から実行可能なタスク・チケットへ自動分割するスキル。
7. **`improve-codebase-architecture`** (`mattpocock-skills/skills/engineering/improve-codebase-architecture`)
   - 既存コードベースの複雑性を診断し、安全なリファクタリング計画を立案するスキル。
8. **`domain-modeling`** (`mattpocock-skills/skills/engineering/domain-modeling`)
   - プロジェクト固有の用語集（Glossary）およびドメイン構造モデルを維持・管理するスキル。

### 📚 教育・スキル構築支援スキル

9. **`teach`** (`mattpocock-skills/skills/productivity/teach`)
   - インタラクティブな対話形式で技術やコード構造をわかりやすく教育するスキル。
10. **`writing-great-skills`** (`mattpocock-skills/skills/productivity/writing-great-skills`)
    - エージェント用スキルの作成・テスト・抜け穴塞ぎ（Bulletproofing）を行うスキル。

---

## 3. 実施手順

1. **ディレクトリの作成**:
   - 本リポジトリの `.agents/skills/` ディレクトリ配下に、各スキルのフォルダを作成します。
2. **ファイルコピー**:
   - `mattpocock-skills/skills/` 内の対象スキルフォルダ（およびその配下のサブフォルダ・ファイル含む）を `.agents/skills/<skill-name>/` にコピーします。
3. **動作・認識確認 (`npx skills`)**:
   - コピー完了後、ローカル環境で `npx skills list` を実行し、すべての新スキルがプロジェクトスキルとして正しく認識されるか検証します。

---

## 4. 承認のお願い

上記コピー対象リストをご確認の上、コピー作業を開始してよろしければ**「承認」**または**「実行してください」**とお知らせください。
