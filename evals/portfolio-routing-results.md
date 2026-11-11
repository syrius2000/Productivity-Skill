# Portfolio Routing Smoke Evaluation Results

- Date: 2026-11-11 (Asia/Tokyo)
- Codex CLI: 0.167.1
- Model: `gpt-6-luna`
- Repetitions: 1 per case
- Parallelism: 3
- Candidate Skills: 14 repository Skills under `.agents/skills/`; user-global Skills may also be available, so isolation is not complete.
- Load evidence: command events calling `cat` on the focus Skill `SKILL.md`; supporting reference reads are not summarized here.
- Session mode: ephemeral; thread IDs retained below.
- Scoring: expected route compared with observed focus-Skill reads. Output quality is judged separately below; no aggregate quality score is inferred.
- Routing: 6/8 focus-positive cases read the expected Skill entrypoint; all 4 focus-negative cases read none of the four focus Skill entrypoints. Two positive cases returned relevant review-style answers without a verifiable Skill read, so they count as unconfirmed selection misses.
- Procedure: read-event evidence confirms only entrypoint loading, not complete procedure compliance. Reference-loading and detailed contract adherence were not scored systematically.
- Limitation: one repetition is exploratory evidence only. Do not generalize to other prompts, models, repositories, or agents.

| Case | Expected | Observed focus Skill read(s) | Routing | Thread ID |
|---|---|---|---|---|
| R01 | `falsify-me` | `falsify-me` | match | `01a1c94c-35da-7192-8c8f-a684ccfbca91` |
| R02 | `falsify-me` | `falsify-me` | match | `01a1c94c-3612-7892-8fe6-92c183046284` |
| R03 | `decision-plan-review` | None observed | mismatch | `01a1c94c-361f-7d62-ae43-6f4aef9c2f3b` |
| R04 | `decision-plan-review` | `decision-plan-review` | match | `01a1c94c-779d-7032-9710-e851ed4d4a25` |
| R05 | `implementation-readiness-review` | None observed | mismatch | `01a1c94c-77c5-7311-ad0a-b8720218e0f5` |
| R06 | `implementation-readiness-review` | `implementation-readiness-review` | match | `01a1c94c-7cfd-7e30-abe7-048c7b4e87c4` |
| R07 | `grilling` | `grilling` | match | `01a1c94c-e252-78a3-9ce1-3fb14bf0bb7c` |
| R08 | `grilling` | `grilling` | match | `01a1c94d-0958-7630-8659-3c5ed0348368` |
| R09 | `NONE` | None observed | match | `01a1c94d-1b11-7320-ad87-bd22d1c0b4f7` |
| R10 | `NONE` | None observed | match | `01a1c94d-21ef-7890-8be9-af8de84d25ce` |
| R11 | `NONE` | None observed | match | `01a1c94d-3361-7fb3-96e1-e1b49766ac4b` |
| R12 | `NONE` | None observed | match | `01a1c94d-43ad-7cb2-9475-a9fa49713869` |

## Output quality and procedure assessment

| Case | Procedure evidence | Output quality | Note |
|---|---|---|---|
| R01 | Skill and discourse reference read | Useful | Bounded the claim and labeled hypothetical counterexamples. |
| R02 | Skill entrypoint read | Useful | Found empty-input failure and distinguished iterator/type contract questions; fix was not executed. |
| R03 | No focus Skill entrypoint read | Useful, selection unconfirmed | Identified concurrency and scale assumptions; answer used a review-like verdict without verified Skill loading. |
| R04 | `decision-plan-review` entrypoint read | Useful | Named decision-changing deployment and operations constraints, with cited SQLite source. |
| R05 | No focus Skill entrypoint read | Useful, selection unconfirmed | Identified scope, token contract, acceptance, verification, and operations gaps; review behavior alone does not prove routing. |
| R06 | `implementation-readiness-review` entrypoint read | Useful | Named start blockers and minimum plan updates. |
| R07 | `grilling` entrypoint read | Useful | Asked one decision-focused question and waited for the answer. |
| R08 | `grilling` entrypoint read | Useful | Began an adaptive interview with one clarifying question. |
| R09 | No focus Skill entrypoint read | Useful | Performed the requested light edit. |
| R10 | No focus Skill entrypoint read | Useful | Diagnosed and fixed the indexing issue while noting empty-input behavior. |
| R11 | No focus Skill entrypoint read | Useful | Gave a concise explanation matching the request. |
| R12 | No focus Skill entrypoint read | Partially useful | Produced a plausible December plan but assumed this portfolio evaluation was the requested project scope. |

The two positive cases without entrypoint reads merit repeated measurement before changing descriptions: their answers were on-purpose, and the sample is too small to determine whether the trigger boundary is unstable.

## Case outputs

### R01 output quality note

Expected route: `falsify-me`. Exit code: 0.

**判定：FAILS** — 「すべてのチーム」「毎日」「必ず」という断定を支える根拠が示されておらず、反例も成り立ちます。

たとえば、作業が独立していて頻繁な同期が不要なチームでは、毎日のペア作業が集中時間を削り、かえって遅延や疲労を招くことがあります。また、知識や視点が似た二人だけで作業すると、同じ見落としを共有して欠陥を見逃す可能性もあります。これらは反例として十分あり得ますが、特定チームで実際に起きたと確認した事例ではありません。

ペア作業が役立つ場合がある、という趣旨は残せます。ただし、効果は作業内容や進め方、チームの状況に左右されます。

**改稿案：**

> ペア作業は、複雑な課題の検討や知識共有に役立つことがある。チームの作業内容や負担を見ながら対象を選び、品質への効果を振り返って頻度を調整する。

改稿案は断定を弱め、適用条件と効果の確認を加えました。文面上の見直しであり、ペア作業の効果を実証したものではありません。チームや作業内容が特定されていないため、最適な頻度は未確定です。

### R02 output quality note

Expected route: `falsify-me`. Exit code: 0.

**対象・前提:** `xs` を数値の集まりとして平均する関数、と解釈します。入力の型や空入力時の仕様は指定されていません。

**判定: FAILS** — 空のリスト `[]` では `sum(xs)` が `0`、`len(xs)` も `0` なので、ゼロ除算になります（コードから導ける結果）。また、整数と浮動小数点数の混在では通常の算術平均になりますが、`Decimal` など異なる数値型を混ぜると演算が失敗する場合があります。

空入力を許容するなら、最小修正は仕様に応じて次のどちらかです。

```python
def average(xs):
    if not xs:
        return None
    return sum(xs) / len(xs)
```

空入力をエラーとして明示するなら、次のようにします。

```python
def average(xs):
    if not xs:
        raise ValueError("xs must not be empty")
    return sum(xs) / len(xs)
```

どちらを選ぶかは呼び出し側の契約次第です。なお、`xs` が一度しか読めないイテレータだと、`sum(xs)` の後に `len(xs)` を呼べず失敗します。任意のイテレータも受け取る仕様なら、先にリスト化するなど別の変更が必要です。

修正案は未実行です。少なくとも空入力、単一値、通常の数値列を確認してください。

### R03 output quality note

Expected route: `decision-plan-review`. Exit code: 0.

**判定: READY-WITH-ASSUMPTIONS**

単一JSONは、小規模で、書き込みが単純なアプリなら妥当です。後戻りにつながりやすい前提は、主に次の2点です。

- **複数の書き手が同じファイルを更新するか**：並行更新があると、最後の保存で他の更新を消す競合が起きます。該当するなら、排他制御や競合検出が必要です。
- **データ量や更新単位が大きくなるか**：毎回ファイル全体を読み書きするため、データ増加や頻繁な部分更新で性能・破損時の影響が問題になり、DBなどへの移行が必要になり得ます。

これらが当面ない前提なら進めてよさそうです。特に並行更新があり得るなら、保存方式を決める前に確認してください。

### R04 output quality note

Expected route: `decision-plan-review`. Exit code: 0.

## 判定: **判定保留**

このリポジトリ内には、SQLite/PostgreSQLを使うアプリの実装・DB設定・移行計画が見当たりません。READMEの既存変更もDB方針とは無関係です。そのため、移行で解決したい問題や運用条件を確認できず、方針を変えるほどの制約があるかは判断できません。

判断を左右するのは主に次の点です。

- **複数プロセス・サーバーから同じDBへ書き込むか**：SQLiteは同時に書き込めるのが1接続なので、書き込み競合や複数サーバー構成が実際の課題ならPostgreSQL移行を支持します。単一ノードで書き込み量が小さければ、移行の理由としては弱くなります。[SQLiteの用途判断](https://www.sqlite.org/whentouse.html)
- **PostgreSQLを運用できる環境があるか**：サーバー、バックアップ・復旧、接続管理、監視をどう用意するかが未確認です。これが既存基盤で解決済みなら移行を妨げにくく、別途導入が必要なら運用負担が判断材料になります。
- **移行対象の依存範囲**：アプリの規模、SQLite固有SQLや型の利用、データ量、許容停止時間を確認できていません。ここが広ければ、DB選択そのものより移行方法が大きな手戻り要因になり得ます。

**現時点では「SQLiteの書き込み競合、複数インスタンス、ネットワーク越しの共有」が実際に問題ならPostgreSQL方針で進むのが自然**です。まず、対象プロジェクトと移行のきっかけ、実行・配置形態（単一端末／単一サーバー／複数インスタンス）、PostgreSQL運用基盤の有無を確認すれば、判断を反転させる制約があるか絞れます。

### R05 output quality note

Expected route: `implementation-readiness-review`. Exit code: 0.

## 判定：この計画のままでは実装開始不可

「APIの認証をトークン方式へ変更し、期限切れトークンを拒否する」だけでは、変更範囲と期待動作を一意に決められません。受入条件と検証方法が不足しています。これは計画文だけを対象にした判定で、リポジトリのAPI実装との照合はしていません。

実装開始前に、少なくとも次を計画へ追加してください。

- **対象範囲**：どのAPI・エンドポイントが対象か。既存認証方式との併用期間や移行方法、公開・除外する経路。
- **トークンの契約**：発行者、形式、署名・検証方法、期限の定義と判定境界、失効や鍵更新の扱い。トークンをどこから受け取り、どの利用者情報・権限に結び付けるか。
- **受入条件**：有効なトークンは許可されること、期限切れ・不正・未指定のトークンは拒否されること、拒否時のHTTPステータスとエラー形式、保護対象外のAPIや既存クライアントへの影響。
- **検証方法**：有効・期限切れ・期限境界・署名不正・形式不正・未指定のケースを含む自動テスト。認証が迂回できないことのエンドポイント別確認と、既存の正常系・互換性確認。
- **運用条件**：鍵や秘密情報の保管・更新方法、ログにトークンを出さないこと、導入・切替・ロールバック手順。

これらが明記され、既存APIの設計と整合すれば実装に進めます。特に期限の境界（期限時刻ちょうどを拒否するか）と、既存認証からの移行方針は、計画段階で決める必要があります。

### R06 output quality note

Expected route: `implementation-readiness-review`. Exit code: 0.

**判定：HOLD**

**評価対象：**「認証をトークン方式へ変更し、期限切れを拒否する」という計画。

提示された内容だけでは、本実装を始めるには情報が足りません。このリポジトリ内にも、対象APIやその既存認証仕様は見当たりませんでした。READMEでは、ここをエージェントスキルの管理リポジトリと説明しています。したがって、具体的なAPI仕様や実装との照合はできていません。

**主なブロッカー**

1. **トークンの仕様が未決定です。** トークンの種類・発行者・検証方法、期限の判定基準が分からず、実装方式や外部インターフェースが変わる可能性があります。
2. **移行の対象範囲と互換性が不明です。** 既存クライアントをいつ、どう切り替えるかが定まっておらず、認証方式の移行方針を決められません。
3. **受け入れ条件と確認方法がありません。** 有効なトークンを受理し、期限切れや不正なトークンを拒否することを、どのAPI・環境でどう確認するか未定です。

**HOLD解除に必要なこと：** 対象APIの既存仕様・利用クライアントを特定し、トークン方式と移行範囲を決めたうえで、有効・期限切れ・不正なトークンの受け入れ条件と検証方法を計画に加えてください。トークンの細部など、方式や契約を変えない局所的な実装選択は、着手後に決められます。

### R07 output quality note

Expected route: `grilling`. Exit code: 0.

❓ **Q1 — まず誰の、どんな検索課題を解決しますか？**

最初に使う人と、探したい情報の例をひとつ教えてください。たとえば「営業担当が、過去の提案書から特定業界向けの事例を見つけたい」のような形です。

➡️ **おすすめ:** まずは利用者を一つの主な職種に絞り、その人が検索を必要とする具体的な場面を決める。

### R08 output quality note

Expected route: `grilling`. Exit code: 0.

❓ **Q1 — 何をどこへ移行する計画ですか？**
対象と移行先を教えてください。たとえば、OpenCodeの設定、リポジトリや作業環境、別のシステムなどです。対象が決まったら、そこから先の論点を回答に合わせて掘り下げます。

➡️ **おすすめ:** 対象と移行先をひとことで指定する。

### R09 output quality note

Expected route: `NONE`. Exit code: 0.

昨日、会議を実施した。次回も会議を実施する予定です。

### R10 output quality note

Expected route: `NONE`. Exit code: 0.

`xs[1]`は2番目の要素を返すため、要素が1個以下だと`IndexError`になります。先頭要素を返すには`xs[0]`を使います。

```python
def first(xs):
    return xs[0]
```

空配列 `[]` を渡した場合は、引き続き`IndexError`になります。空配列も扱う必要があれば、期待する戻り値（例: `None`）に合わせて処理を追加できます。

### R11 output quality note

Expected route: `NONE`. Exit code: 0.

利用者が検索したい言葉を入力すると、その言葉に関係の深い結果から順に表示する設計です。

### R12 output quality note

Expected route: `NONE`. Exit code: 0.

# 2026年12月の開発計画

週の区切りは月曜〜日曜で組みました。リポジトリの未コミット変更にあるREADMEのSkill選択案内と、`evals/portfolio-routing.md`の評価案を起点に、**Skillの起動ルーティングを測定し、必要な修正までつなげる月**とします。

| 週 | 期間 | 作業 | 週末の成果・完了条件 |
|---|---|---|---|
| 第1週 | 12/1〜12/6 | 現在のREADME案と評価ケースを整理。評価環境で使えるSkill、モデル、起動記録の取得方法を確認し、測定手順を決める。 | 実行条件と記録形式が確定し、各ケースの期待ルートを説明できる。 |
| 第2週 | 12/7〜12/13 | `evals/portfolio-routing.md`の12ケースを使って初回測定。Skill選択、手順遵守、回答品質を分けて記録し、選択を確認できない場合はその制約も記録する。 | 再現可能な初回結果が揃い、誤選択・未選択・証拠不足を区別できる。 |
| 第3週 | 12/14〜12/20 | 初回結果を分析し、誤ルートの原因が入口条件・README説明・Skill本文のどこにあるか調べる。根拠のある箇所だけを修正し、必要に応じて境界ケースを追加する。 | 変更理由と対象ケースが対応づけられ、修正後の評価手順が更新されている。 |
| 第4週 | 12/21〜12/27 | 同じ条件で再測定し、修正前後を比較。通常の校正・説明・デバッグなど、対象外依頼が誤起動しないか確認する。 | 改善の有無と残る曖昧さをケース単位で報告できる。 |
| 第5週 | 12/28〜12/31 | 評価結果、制約、未解決事項をまとめる。README・Skill案内・評価記録の整合を取り、次期に持ち越す項目を整理する。 | 月次の評価記録と次の優先作業が揃い、完了扱いと未検証項目が明確。 |

## 進め方と判断基準

- 測定では、**選択結果・Skillの手順遵守・回答品質**を別々に記録します。回答の文体だけからSkillが起動したとは判定しません。
- モデル、CLI版、利用可能なSkill、反復回数などを記録し、初回と再測定の条件を揃えます。
- 評価結果が弱い場合は、すぐに本文を広く書き換えず、失敗ケースと入口条件の対応を確認してから修正します。
- この計画は、リポジトリ内の評価案と現状から作った作業計画です。測定後の結果に応じて第3週以降の範囲を調整します。
