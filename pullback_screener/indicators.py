"""Low-level technical indicators used by the pullback screener.

All functions take/return pandas Series (or a DataFrame) and are written to be
NaN-safe for the warm-up period at the start of a series.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False, min_periods=window).mean()


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    tr = true_range(high, low, close)
    # Wilder's smoothing.
    return tr.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100 - (100 / (1 + rs))
    # When there are no losses at all, RSI is 100.
    out = out.where(avg_loss != 0.0, 100.0)
    return out


def stoch_k(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    lowest = low.rolling(window, min_periods=window).min()
    highest = high.rolling(window, min_periods=window).max()
    rng = (highest - lowest).replace(0.0, np.nan)
    return 100 * (close - lowest) / rng


def bollinger(close: pd.Series, window: int = 20, n_std: float = 2.0):
    mid = sma(close, window)
    std = close.rolling(window, min_periods=window).std(ddof=0)
    upper = mid + n_std * std
    lower = mid - n_std * std
    return mid, upper, lower, std


def rolling_high(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=window).max()


def rolling_low(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=window).min()


def slope(series: pd.Series, window: int) -> pd.Series:
    """Simple slope: value now minus value `window` bars ago, per bar."""
    return (series - series.shift(window)) / window


def down_streak(close: pd.Series) -> pd.Series:
    """Number of consecutive down-closes ending at each bar."""
    down = (close.diff() < 0).astype(int)
    # Reset the running count whenever an up (or flat) bar appears.
    grp = (down == 0).cumsum()
    return down.groupby(grp).cumsum()
