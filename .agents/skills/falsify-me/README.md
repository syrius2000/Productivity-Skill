# falsify-me

主張・会話、プロジェクトの初期案、コードを批判的に検討し、根拠のある最小の改善へつなぐスキルです。反対意見を増やすこと自体を目的にせず、結論や意思決定を変え得る論点に絞ります。

## 使いどころ

- 「この主張を批判的に検討して改善して」
- 「この計画の破綻条件と、先に行う最小の実験を示して」
- 「このコードの契約違反を調べ、最小の修正案を示して」

通常の説明、校正、デバッグ、一般的なレビューやブレインストーミングでは、明示的に批判・反証・ストレステストを求められた場合を除き起動対象にしません。詳細な用途選択、判定基準、安全境界は [SKILL.md](./SKILL.md) を参照してください。

## 検討の進め方

会話・主張には `references/discourse.md`、プロジェクト案には `references/project.md`、コードには `references/code.md` を使います。重大なリスク、医薬品品質、受容判断などでは `references/risk-management.md` も参照します。判定は各重要主張について `SURVIVES`、`REVISE`、`FAILS`、`INCONCLUSIVE` を使い、主張の判定、改善案の検証状態、リスク受容を混同しません。

## 正本と評価状態

この配布パッケージの正本はこのディレクトリです。開発履歴・ケース別評価・測定条件を含む開発プロジェクトは [falsify-me開発リポジトリ](https://github.com/syrius2000/falsify-me) にあります。

取り込み時点で、開発側の独立QAはHOLDで、正式配布準備は未達と記録されています。肯定ケース30/30、否定ケース25/25、曖昧ケース5/5のスキル本文読込を観測した探索測定もありますが、これは自動選択の保証、回答品質の再評価、独立QA合格を示しません。従来の自己評価にはC16の自動選択FAILが残り、OpenSpecタスク4.2・4.3も未完了です。詳細と更新後の状態は開発側の [評価サマリー](https://github.com/syrius2000/falsify-me/blob/main/evaluation/results/summary.md)、[選択測定](https://github.com/syrius2000/falsify-me/blob/main/evaluation/results/selection-exploratory-20261110.md)、[引き継ぎ](https://github.com/syrius2000/falsify-me/blob/main/HANDOFF-2026-11-06.md)を確認してください。

この記録は評価上の限界を利用者に伝えるもので、個別の用途で有用性や安全性を保証しません。重要な判断では一次資料、専門家、適用される手順と権限を確認してください。
