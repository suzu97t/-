# 社内ヘルプデスクの一次対応をどこまで自動化するか（10枚）

架空の事例で作った経営会議向けのデッキ。数値はすべて仮置きで、各ページの出典行に断りを入れてある。

- `deck.html` — 成果物。16:9（338.67mm × 190.5mm）、1 section = 1スライド、単体HTML
- `deck.pdf` — Chrome で印刷したPDF（10ページ）
- `build.py` — 生成スクリプト。パーツ集のCSSを流用し、本文を差し替える

## 作り方

[consulting-pptx-skill](https://github.com/carnot-tech/consulting-pptx-skill) の規約（`references/slide-rules.md`）に沿って作成。

```bash
# 1. パーツ集からたたき台を組む（表紙・要約・チャート・比較表・リスク表・ロードマップ・軸のある表・裏表紙）
python3 scripts/new_deck.py --parts b01,m01,m05,b17,m08,m10,m12,m33,b09,b10 \
  --title "社内ヘルプデスク 一次対応の自動化" -o base.html

# 2. 本文を差し替える
python3 build.py

# 3. 機械チェック
python3 scripts/check_deck.py deck.html          # 0 FAIL
node scripts/check_layout.mjs deck.html          # layout OK

# 4. PDF化
chrome --headless --no-pdf-header-footer --print-to-pdf=deck.pdf deck.html
```

## ストーリーライン（タイトルの通し読み）

1. 一次対応は自動応答に寄せ、情報システム部は例外と承認に残る（要約）
2. 初回の回答は7月に11.8時間まで遅れ、翌営業日にずれ込む案件が出ている
3. 問い合わせの半分は、パスワード再発行と経費精算の差し戻しに集まる
4. 一次対応の工数は月160時間から116時間まで落ちるが、例外処理は残る
5. 既存のチャットに自動応答を足す案なら、費用も着手までの時間も小さい
6. どのリスクも先に兆候が出るため、基準値を決めて手前で止める
7. 対象はパスワード再発行から始め、12月に経費精算の差し戻しへ広げる
8. 今週決めるのは、対象とする種別と承認の持ち方と費用枠

## 残っている WARN（許容）

| WARN | 理由 |
| --- | --- |
| `.sub` ×2 | 表紙・裏表紙のサブタイトルのみ。コンテンツスライドには置いていない |
| p1 / p10 のタイトルが空 | 表紙・裏表紙 |
| ダッシュ「—」連結 p6 | 比較表の非該当セルの「—」。規約（§6）が非該当セルに「—」を求めるため |
