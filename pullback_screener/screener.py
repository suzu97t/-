"""Pullback (押し目) screener.

Two-layer design tuned for high Recall / lower Precision, as requested:

  Layer 1 - Uptrend confirmation (loose):
      close > MA200 with a positive MA200 slope, OR price within 25% of the
      1-year high with a positive MA200 slope. Falls back to MA50 when there is
      not enough history for MA200. This only gates *whether* we look for a dip;
      it is intentionally forgiving so it does not kill Recall.

  Layer 2 - Pullback candidate signals (OR / score sum, NOT AND):
      each signal is 0/1; a bar becomes a candidate when the score >= min_score
      (default 2). Requiring every signal (AND) would throw away most real
      pullbacks, so we sum instead.

  Ranking (does not filter):
      reversal-confirmation features (bullish engulfing, close over prior high,
      volume dry-up then pick-up) are combined into a rank score used only to
      order the surviving candidates for eyeballing. They never remove a
      candidate, so Recall is preserved.

The public entry point is `compute_signals(df)`, which returns the input frame
enriched with every intermediate value plus the boolean `candidate` column and
the `rank_score`. `screen_latest(df)` returns just the most recent bar's verdict
for a single ticker.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict

import numpy as np
import pandas as pd

from . import indicators as ind


@dataclass
class ScreenerConfig:
    # --- Layer 1: trend ---
    ma_long: int = 200
    ma_long_fallback: int = 50
    ma_slope_window: int = 20
    high_lookback_1y: int = 252
    max_off_high: float = 0.25  # within 25% of the 1y high

    # --- Layer 2: pullback signals ---
    ma_fast: int = 25
    ma_mid: int = 50
    ma_dev_low: float = -0.08   # 0% .. -8% below the MA
    ma_dev_high: float = 0.01   # allow a touch just above (noise tolerance)

    dd_lookback: int = 20
    dd_low: float = -0.15       # -3% .. -15% off the 20d high
    dd_high: float = -0.03

    atr_window: int = 14
    atr_dd_low: float = 1.0     # (20d high - close) / ATR14 in [1, 3]
    atr_dd_high: float = 3.0

    rsi_window: int = 14
    rsi_low: float = 40.0
    rsi_high: float = 55.0
    rsi_fast_window: int = 2
    rsi_fast_max: float = 10.0

    stoch_window: int = 14
    stoch_k_max: float = 25.0
    boll_window: int = 20
    boll_touch_sigma: float = 1.0  # close <= mid - 1*std counts as a lower-band touch

    down_streak_min: int = 2
    down_streak_max: int = 3

    support_lookback: int = 60  # prior swing-high (breakout retest) proximity
    support_tol: float = 0.03   # within +/-3% of a prior swing high

    min_score: int = 2  # candidate when summed signals >= this


SIGNAL_COLS = [
    "sig_ma_dev",
    "sig_drawdown",
    "sig_atr_dd",
    "sig_rsi",
    "sig_stoch_boll",
    "sig_down_streak",
    "sig_support",
]


def compute_signals(df: pd.DataFrame, cfg: ScreenerConfig | None = None) -> pd.DataFrame:
    """Enrich an OHLCV frame with trend/pullback signals.

    `df` must have columns: Open, High, Low, Close, Volume (indexed by date).
    """
    cfg = cfg or ScreenerConfig()
    out = df.copy()

    o, h, l, c, v = out["Open"], out["High"], out["Low"], out["Close"], out["Volume"]

    # ---------------- Layer 1: trend ----------------
    ma_long = ind.sma(c, cfg.ma_long)
    ma_long_slope = ind.slope(ma_long, cfg.ma_slope_window)
    # Fallback MA when history is too short for MA200.
    ma_fb = ind.sma(c, cfg.ma_long_fallback)
    ma_fb_slope = ind.slope(ma_fb, cfg.ma_slope_window)

    use_long = ma_long.notna()
    trend_ma = ma_long.where(use_long, ma_fb)
    trend_slope = ma_long_slope.where(use_long, ma_fb_slope)

    high_1y = ind.rolling_high(c, cfg.high_lookback_1y)
    # If 1y history is missing, use the longest available high so the "near high"
    # branch can still contribute instead of silently going NaN->False.
    high_1y = high_1y.fillna(c.expanding(min_periods=1).max())
    off_high_1y = c / high_1y - 1.0

    above_ma = c > trend_ma
    slope_up = trend_slope > 0
    near_high = off_high_1y >= -cfg.max_off_high

    trend_ok = (above_ma & slope_up) | (near_high & slope_up)

    out["ma_long"] = trend_ma
    out["ma_long_slope"] = trend_slope
    out["off_high_1y"] = off_high_1y
    out["trend_ok"] = trend_ok.fillna(False)

    # ---------------- Layer 2: pullback signals ----------------
    ma_fast = ind.sma(c, cfg.ma_fast)
    ma_mid = ind.sma(c, cfg.ma_mid)
    dev_fast = c / ma_fast - 1.0
    dev_mid = c / ma_mid - 1.0
    in_band = lambda d: (d >= cfg.ma_dev_low) & (d <= cfg.ma_dev_high)
    sig_ma_dev = in_band(dev_fast) | in_band(dev_mid)

    high_dd = ind.rolling_high(h, cfg.dd_lookback)
    drawdown = c / high_dd - 1.0
    sig_drawdown = (drawdown >= cfg.dd_low) & (drawdown <= cfg.dd_high)

    atr = ind.atr(h, l, c, cfg.atr_window)
    atr_dd = (high_dd - c) / atr.replace(0.0, np.nan)
    sig_atr_dd = (atr_dd >= cfg.atr_dd_low) & (atr_dd <= cfg.atr_dd_high)

    rsi = ind.rsi(c, cfg.rsi_window)
    rsi_fast = ind.rsi(c, cfg.rsi_fast_window)
    sig_rsi = ((rsi >= cfg.rsi_low) & (rsi <= cfg.rsi_high)) | (rsi_fast < cfg.rsi_fast_max)

    k = ind.stoch_k(h, l, c, cfg.stoch_window)
    mid_b, _, lower_b, std_b = ind.bollinger(c, cfg.boll_window)
    lower_touch = c <= (mid_b - cfg.boll_touch_sigma * std_b)
    sig_stoch_boll = (k < cfg.stoch_k_max) | lower_touch

    streak = ind.down_streak(c)
    sig_down_streak = (streak >= cfg.down_streak_min) & (streak <= cfg.down_streak_max)

    # Support proximity: a prior swing high (resistance turned support) that we
    # are now retesting from above. We look back over `support_lookback` bars,
    # excluding the most recent `dd_lookback` bars so "the high we just made"
    # doesn't count as its own support.
    prior_high = h.shift(cfg.dd_lookback).rolling(
        cfg.support_lookback, min_periods=cfg.dd_lookback
    ).max()
    near_support = (c >= prior_high * (1 - cfg.support_tol)) & (
        c <= prior_high * (1 + cfg.support_tol)
    )
    sig_support = near_support.fillna(False)

    out["dev_fast"] = dev_fast
    out["dev_mid"] = dev_mid
    out["drawdown_20d"] = drawdown
    out["atr14"] = atr
    out["atr_drawdown"] = atr_dd
    out["rsi14"] = rsi
    out["rsi2"] = rsi_fast
    out["stoch_k"] = k
    out["down_streak"] = streak

    out["sig_ma_dev"] = sig_ma_dev.fillna(False)
    out["sig_drawdown"] = sig_drawdown.fillna(False)
    out["sig_atr_dd"] = sig_atr_dd.fillna(False)
    out["sig_rsi"] = sig_rsi.fillna(False)
    out["sig_stoch_boll"] = sig_stoch_boll.fillna(False)
    out["sig_down_streak"] = sig_down_streak.fillna(False)
    out["sig_support"] = sig_support

    out["pullback_score"] = out[SIGNAL_COLS].sum(axis=1)
    out["candidate"] = out["trend_ok"] & (out["pullback_score"] >= cfg.min_score)

    # ---------------- Ranking (does not filter) ----------------
    out["rank_score"] = _rank_score(out, o, h, l, c, v)

    return out


def _rank_score(out, o, h, l, c, v) -> pd.Series:
    """Reversal-confirmation features -> ordering only. Never filters."""
    prev_h = h.shift(1)
    prev_o = o.shift(1)
    prev_c = c.shift(1)

    bullish_engulfing = (c > o) & (prev_c < prev_o) & (c >= prev_o) & (o <= prev_c)
    over_prev_high = c > prev_h

    vol_ma = v.rolling(20, min_periods=5).mean()
    vol_dryup_then_up = (v.shift(1) < vol_ma.shift(1)) & (v > v.shift(1))

    # Shallower ATR-drawdowns are preferable (closer to the trend, less broken).
    depth_bonus = (3.0 - out["atr_drawdown"].clip(0, 3)) / 3.0

    score = (
        bullish_engulfing.fillna(False).astype(float)
        + over_prev_high.fillna(False).astype(float)
        + vol_dryup_then_up.fillna(False).astype(float)
        + depth_bonus.fillna(0.0)
    )
    return score


@dataclass
class Verdict:
    ticker: str
    date: pd.Timestamp
    close: float
    trend_ok: bool
    pullback_score: int
    candidate: bool
    rank_score: float
    signals: dict = field(default_factory=dict)

    def as_row(self) -> dict:
        d = asdict(self)
        sigs = d.pop("signals")
        d.update(sigs)
        return d


def screen_latest(df: pd.DataFrame, ticker: str, cfg: ScreenerConfig | None = None) -> Verdict:
    enriched = compute_signals(df, cfg)
    last = enriched.iloc[-1]
    return Verdict(
        ticker=ticker,
        date=enriched.index[-1],
        close=float(last["Close"]),
        trend_ok=bool(last["trend_ok"]),
        pullback_score=int(last["pullback_score"]),
        candidate=bool(last["candidate"]),
        rank_score=float(last["rank_score"]),
        signals={col: bool(last[col]) for col in SIGNAL_COLS},
    )
