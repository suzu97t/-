"""Data loading.

Primary source is yfinance. In sandboxes where the egress policy blocks Yahoo
Finance (or offline), `load_prices` transparently falls back to a synthetic
OHLCV generator that plants realistic uptrends with periodic pullbacks, so the
screener and its evaluation can be exercised end-to-end without a network.
"""

from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

_OHLCV = ["Open", "High", "Low", "Close", "Volume"]


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Return a clean single-ticker OHLCV frame from yfinance output."""
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance returns (field, ticker); collapse to fields.
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    df = df[[col for col in _OHLCV if col in df.columns]].dropna()
    return df


def download_yfinance(ticker: str, period: str = "3y", interval: str = "1d") -> pd.DataFrame:
    import yfinance as yf  # imported lazily so the fallback works without it

    raw = yf.download(
        ticker, period=period, interval=interval, progress=False, auto_adjust=True
    )
    if raw is None or raw.empty:
        raise RuntimeError(f"yfinance returned no data for {ticker!r}")
    return _normalize(raw)


def synthetic_prices(
    ticker: str,
    n: int = 750,
    seed: int | None = None,
    end: str = "2026-07-15",
) -> pd.DataFrame:
    """Generate an uptrending OHLCV series with recurring pullbacks.

    The regime alternates between trend legs (positive drift, low vol) and
    pullback legs (negative drift, higher vol) so that genuine 押し目 events
    exist for the evaluator to label.
    """
    if seed is None:
        # Stable across processes (built-in hash() is salted per run).
        seed = int(hashlib.md5(ticker.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)

    dates = pd.bdate_range(end=pd.Timestamp(end), periods=n)
    log_price = np.log(rng.uniform(20, 120))
    closes = np.empty(n)

    # Regime machine.
    in_pullback = False
    leg_left = rng.integers(20, 60)
    trend_mu, trend_sd = 0.0009, 0.010     # ~+22%/yr drift, calm
    pull_mu, pull_sd = -0.004, 0.018       # sharp, short dips

    for i in range(n):
        if leg_left <= 0:
            in_pullback = not in_pullback
            leg_left = rng.integers(5, 12) if in_pullback else rng.integers(25, 70)
        mu, sd = (pull_mu, pull_sd) if in_pullback else (trend_mu, trend_sd)
        log_price += rng.normal(mu, sd)
        closes[i] = np.exp(log_price)
        leg_left -= 1

    closes = pd.Series(closes, index=dates)
    # Build OHLC around the close path with intrabar noise.
    prev = closes.shift(1).fillna(closes.iloc[0])
    opens = prev * (1 + rng.normal(0, 0.004, n))
    span = np.abs(rng.normal(0, 0.010, n)) + 0.002
    highs = np.maximum(opens, closes.values) * (1 + span)
    lows = np.minimum(opens, closes.values) * (1 - span)
    vol = rng.integers(5_00_000, 5_000_000, n).astype(float)

    df = pd.DataFrame(
        {
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes.values,
            "Volume": vol,
        },
        index=dates,
    )
    return df[_OHLCV]


def load_prices(
    ticker: str,
    period: str = "3y",
    interval: str = "1d",
    allow_synthetic: bool = True,
    verbose: bool = True,
) -> tuple[pd.DataFrame, str]:
    """Load prices, returning (frame, source) where source is 'yfinance' or 'synthetic'."""
    try:
        df = download_yfinance(ticker, period=period, interval=interval)
        return df, "yfinance"
    except Exception as exc:  # network blocked, bad ticker, offline, etc.
        if not allow_synthetic:
            raise
        if verbose:
            print(f"  [warn] yfinance failed for {ticker} ({exc}); using synthetic data")
        return synthetic_prices(ticker), "synthetic"
