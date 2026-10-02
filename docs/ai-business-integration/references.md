# 参考資料

[← 目次へ](./README.md)

> 本ハンドブック作成時、作業環境から各ブログ本文へ直接アクセスできなかったため、
> 記事の要点は検索結果の要約に基づいています。案件で引用する前に、必ず原文を確認してください。

## LayerX

| 記事 | このハンドブックで参照した考え方 | 参照章 |
|---|---|---|
| [LLMの不確実性との付き合い方：AIワークフロー開発におけるケーススタディ](https://tech.layerx.co.jp/entry/2025/03/06/102234) | 複数サンプル・E2Eでの検証、誤りの影響は体験設計次第、リカバリーしやすいワークフロー | 03, 04, 06 |
| [評価駆動開発（Eval-driven development）：LLMアプリケーション開発における課題とアプローチ](https://tech.layerx.co.jp/entry/2024/12/12/191131) | 評価を先に作る開発の進め方 | 03 |
| [AI Agent時代における「使えば使うほど賢くなるAI機能」の開発](https://tech.layerx.co.jp/entry/2025/10/23/222742) | ドロップダウンでの修正による構造化データ収集、定期的な更新 | 06, 07 |
| [Langfuse の Datasets 機能を利用したAIエージェント機能の性能評価のためのデータセット構築](https://tech.layerx.co.jp/entry/2025/10/02/200000) | 評価データセットの構築 | 03 |
| [Langfuse の Experiment Runner SDK を利用した AIエージェント機能の性能評価と実験管理](https://tech.layerx.co.jp/entry/2025/10/22/133654) | 実験管理 | 04 |
| [安定したAIエージェント開発・運用を実現するLangfuse活用方法](https://tech.layerx.co.jp/entry/stable-ai-agent-dev-with-langfuse) | プロンプト管理、データセットでの回帰テスト | 04, 06 |
| [LLMによる「非定型見積書の明細抽出タスク」の精度を約80%→約95%に改善した話](https://tech.layerx.co.jp/entry/2026/01/14/125350) | 明細抽出の典型的な失敗、工程分割とモデルの使い分け | 04 |
| [エージェント的ワークフローで業務自動化の精度を改善する取り組みについて](https://tech.layerx.co.jp/entry/2025/05/12/132212) | ワークフローの中でエージェント的処理を使い精度を上げる | 00, 04 |
| [経費科目推薦機能の機械学習アークテクチャ](https://tech.layerx.co.jp/entry/2024/07/25/173317) | 会社ごとに異なる科目体系、推薦問題としての設計 | 02 |
| [LayerX インボイスにおける請求書AI-OCRの概要](https://tech.layerx.co.jp/entry/invoice-ai-ocr) | 多面的な精度モニタリング | 03 |
| [【Data-centric AI】Confident Learningによるデータセットの品質改善](https://tech.layerx.co.jp/entry/2024/10/08/164119) | 正解データの誤りの発見 | 03 |
| [AIエージェント「AI明細仕訳」リリース（バクラク）](https://bakuraku.jp/news/20250822/) | 既存手段で解けない領域にLLMを使う例 | 00, 02, 05, 付録A |
| [LayerX、「バクラク請求書受取」にAIエージェントを追加（IT Leaders）](https://it.impress.co.jp/articles/-/28280) | 同上 | 00, 付録A |
| [業務自動運転は5段階で起こる——LayerX 松本氏（BRIDGE）](https://thebridge.jp/2025/04/layerx-discusses-the-future-of-white-collar-work-with-generative-ai-hot100-accenture-ventures-vol-2) | 業務の自動化を段階で捉える | 00, 01, 06 |
| [「コード化できない課題をLLMで解く」LayerX松本氏（@IT）](https://atmarkit.itmedia.co.jp/ait/articles/2507/23/news006.html) | LLMの価値は言語で問題を解けること、コード化しきれない業務への対応 | 00, 02 |

## Algomatic

| 記事 | このハンドブックで参照した考え方 | 参照章 |
|---|---|---|
| [「生成AIこんなものか」と諦める前に — 営業AIエージェント開発現場から学ぶLLM品質保証テクニック](https://tech.algomatic.jp/entry/2025/03/26/182954) | 誤りパターンの言語化と人の検証による改善、生成と評価の分離、判断保留 | 03, 04, 付録B |
| [LLMのシステム導入時に行いたい動作検証について](https://tech.algomatic.jp/entry/column/prompt/behavioral-testing-01) | チェックリスト型の動作検証（Behavioral Testing） | 04 |
| [LLM評価ツールpromptfooとアサーションの解説](https://tech.algomatic.jp/entry/2024/04/10/183001) | 評価の自動化 | 04 |
| [そろそろ実務で使えるローカルLLM](https://tech.algomatic.jp/entry/2026/08/21/165305) | クラウドLLMが使えない場合の選択肢 | 03 |
| [AIエージェントの解釈について整理してみる](https://tech.algomatic.jp/entry/agents/interpretation-of-ai-agents) | AIエージェントの解釈が立場によって異なること | 00 |
| [生成AIスタートアップが現場で培った"成功するAI活用"の実践知（大野峻典 / note）](https://note.com/ono_shunsuke/n/n8f872e58ed69) | 業務へのAI活用の実践 | ― |

## 題材（経理・仕訳）の税制・制度（2026年10月時点）

| 資料 | 内容 | 参照章 |
|---|---|---|
| [インボイス制度の経過措置の見直し（freee）](https://www.freee.co.jp/kb/kb-invoice/invoice_transitional_measures/) | 免税事業者からの仕入の控除割合 80% → 70% → 50% → 30% | 付録A, 07 |
| [インボイス経過措置は8割から70%控除へ（小谷野税理士法人）](https://koyano-cpa.gr.jp/nobiyo-kaikei/column/8872/) | 同上 | 付録A |
| [少額減価償却資産とは？特例の対象も解説【令和8年度税制改正】（マネーフォワード）](https://biz.moneyforward.com/accounting/basic/63113/) | 中小企業者等の特例 30万円未満 → 40万円未満 | 付録A |
| [少額減価償却資産が40万円未満へ拡大（MJS）](https://keiridriven.mjs.co.jp/180803/) | 同上 | 付録A |
