# Pullback (押し目) Screener

ロングでエントリーする銘柄を探すための、押し目（または押し目に近い点）検出スクリーナー。
**Recall 重視・Precision 低め許容**（＝スクリーニング後に目視で確認する前提）で設計しています。

## 設計：2層 + ランキング

いただいた設計方針をそのまま実装しています。

### 1層目：上昇トレンドの確認（緩め）
`close > 200日MA` かつ `200日MAの傾きが正`、**または** `直近1年高値から -25%以内` かつ `200日MAの傾きが正`。
200日分の履歴が無い場合は 50日MA にフォールバック。パーフェクトオーダー等の厳しい条件は Recall を潰すので使いません。
これは「押し目を探しに行くかどうか」のゲートで、意図的に緩くしています。

### 2層目：押し目検出（AND ではなく OR / スコア合算）
各シグナルを 0/1 にして合計し、`pullback_score >= min_score`（既定 2）で候補化します。

| シグナル | 定義 |
|---|---|
| `sig_ma_dev` | 25日・50日MA乖離率が 0〜-8%（接近〜わずかに割れ） |
| `sig_drawdown` | 20日高値からの下落率が -3%〜-15% |
| `sig_atr_dd` | (20日高値 − 終値) / ATR14 が 1〜3（ボラ差を吸収、横断向き） |
| `sig_rsi` | RSI(14) が 40〜55、または RSI(2) < 10 |
| `sig_stoch_boll` | ストキャス %K < 25、またはボリンジャー -1σ以下タッチ |
| `sig_down_streak` | 連続陰線 2〜3日 |
| `sig_support` | 過去のスイング高値（ブレイク後の押し）への接近 ±3% |

### ランキング（候補を絞らない）
反転確認（包み足、前日高値超え、出来高の枯れ→増加、押しの浅さ）は**候補から外さず、並べ替えの `rank_score` にのみ使用**。
Recall を落とさずに目視の優先順位をつけます。

## 評価（Recall / Precision）
正解ラベル：**「その後10日以内に +5% かつ その間の最大DDが -3%以内」** を「良い押し目エントリー」と定義。
`min_score` を振って Recall/Precision 曲線を出し、1日に目視できる件数の上限（既定 30銘柄/日）の範囲で
Recall が最大になる閾値を選びます。

- `recall` … 全ての「良いエントリー」に対する再現率
- `recall_in_trend` … **1層目（上昇トレンド）を通過した中での**再現率＝2層目本来の仕事の指標
- `precision` … 候補のうち実際に良かった割合（低めで可）

## 使い方

```bash
pip install -r pullback_screener/requirements.txt

# 銘柄をスクリーニング（最新バーの判定）
python -m pullback_screener.run_screen AAPL MSFT NVDA 7203.T 6758.T

# テスト + Recall/Precision デモ
python -m pullback_screener.test_pullback
pytest pullback_screener/test_pullback.py -q
```

コードから使う場合：

```python
from pullback_screener import load_prices, screen_latest, ScreenerConfig

df, source = load_prices("AAPL", period="3y")
verdict = screen_latest(df, "AAPL", ScreenerConfig(min_score=2))
print(verdict.candidate, verdict.pullback_score, verdict.rank_score)
```

閾値はすべて `ScreenerConfig` で調整可能です。

## データソースについて（重要）

第一データソースは **yfinance**（Yahoo Finance）です。
ただし本リポジトリを検証したサンドボックス環境では、組織の egress ネットワークポリシーにより
Yahoo Finance のホスト（`query1/query2.finance.yahoo.com` 等）への接続が **403 で拒否**されていました。
そのため `load_prices` は、yfinance が失敗した場合に**合成OHLCV（上昇トレンド＋周期的な押し目を仕込んだ擬似データ）へ自動フォールバック**し、
パイプライン全体（シグナル計算・ラベリング・Recall/Precision 評価）をオフラインでも検証できるようにしています。

**ネットワーク制限のない環境（あなたのローカルPC等）ではそのまま実データで動作します。**
実データのみで走らせたい場合は `--no-synthetic` を付けてください（取得失敗時はエラーで停止）。

## ファイル構成

| ファイル | 役割 |
|---|---|
| `indicators.py` | SMA/EMA/ATR/RSI/ストキャス/ボリンジャー等の基礎指標 |
| `screener.py` | 2層スクリーナー本体（`compute_signals`, `screen_latest`, `ScreenerConfig`） |
| `data.py` | yfinance 取得 + 合成データフォールバック |
| `evaluate.py` | ラベリングと Recall/Precision スイープ |
| `run_screen.py` | 銘柄リストをスクリーニングする CLI |
| `test_pullback.py` | テスト + 評価デモ |
