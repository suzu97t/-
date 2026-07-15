"""Evaluation: label true pullbacks, then measure Recall/Precision.

Label definition (as proposed in the task):
    A bar is a *good pullback entry* if, within the next `horizon` bars,
    the price rises at least `up` (max high return >= +up) while never drawing
    down more than `dd` first-ish (min low return >= -dd over the window).

We treat every bar (across all tickers, all history) as one sample: it is a
positive if it carries that forward label, and it is *flagged* if the screener
marks it a candidate. Then:

    Recall    = flagged positives / all positives
    Precision = flagged positives / all flagged

We sweep the candidate `min_score` cutoff to trace the Recall/Precision curve and
pick the loosest score that keeps the average daily candidate count under a
viewing cap (default: you can eyeball ~30 names/day).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .screener import compute_signals, ScreenerConfig, SIGNAL_COLS


def label_pullbacks(
    df: pd.DataFrame, horizon: int = 10, up: float = 0.05, dd: float = 0.03
) -> pd.Series:
    """Forward-looking boolean label per bar. NaN near the right edge is False."""
    c = df["Close"]
    h = df["High"]
    l = df["Low"]

    # Future extremes over the next `horizon` bars (excluding the current bar).
    fut_high = _forward_extreme(h, horizon, "max")
    fut_low = _forward_extreme(l, horizon, "min")

    max_up = fut_high / c - 1.0
    max_dn = fut_low / c - 1.0

    label = (max_up >= up) & (max_dn >= -dd)
    # The last `horizon` bars have no full forward window -> not labelable.
    label.iloc[-horizon:] = False
    return label.fillna(False)


def _forward_extreme(series: pd.Series, horizon: int, kind: str) -> pd.Series:
    vals = series.to_numpy()
    n = len(vals)
    out = np.full(n, np.nan)
    for i in range(n - 1):
        j = min(i + 1 + horizon, n)
        window = vals[i + 1 : j]
        if window.size:
            out[i] = window.max() if kind == "max" else window.min()
    return pd.Series(out, index=series.index)


@dataclass
class Metrics:
    min_score: int
    recall: float            # over ALL positives (trend-agnostic denominator)
    recall_in_trend: float   # over positives that occurred while layer-1 trend held
    precision: float
    flagged: int
    positives: int
    positives_in_trend: int
    tp: int
    avg_daily_candidates: float


def evaluate_frames(
    frames: dict[str, pd.DataFrame],
    cfg: ScreenerConfig | None = None,
    horizon: int = 10,
    up: float = 0.05,
    dd: float = 0.03,
    score_grid: range | None = None,
) -> pd.DataFrame:
    """Run the screener over many tickers and sweep the score cutoff.

    Returns a DataFrame of Metrics rows, one per candidate `min_score` threshold.
    """
    cfg = cfg or ScreenerConfig()
    score_grid = score_grid if score_grid is not None else range(1, len(SIGNAL_COLS) + 1)

    all_scores = []
    all_labels = []
    all_trend = []
    all_dates = []

    for ticker, df in frames.items():
        enriched = compute_signals(df, cfg)
        label = label_pullbacks(df, horizon=horizon, up=up, dd=dd)
        label = label.reindex(enriched.index).fillna(False)
        all_scores.append(enriched["pullback_score"].to_numpy())
        all_trend.append(enriched["trend_ok"].to_numpy())
        all_labels.append(label.to_numpy())
        all_dates.append(enriched.index.to_numpy())

    scores = np.concatenate(all_scores)
    trend = np.concatenate(all_trend)
    labels = np.concatenate(all_labels)
    dates = np.concatenate(all_dates)

    # Only bars that are labelable (have a full forward window) count as the
    # evaluation universe; unlabelable right-edge bars are dropped from both
    # numerator and denominator to avoid biasing Precision.
    n_days = len(pd.unique(dates))
    positives_total = int(labels.sum())
    # Positives that occurred while the layer-1 uptrend gate was open. This is
    # the fair denominator for the layer-2 (dip-detection) job: entries in a
    # downtrend are ones we deliberately do NOT want, so excluding them isolates
    # how well the score picks up the dips we actually care about.
    positives_in_trend = int((labels & trend).sum())

    rows = []
    for s in score_grid:
        flagged = trend & (scores >= s)
        tp = int((flagged & labels).sum())
        n_flagged = int(flagged.sum())
        recall = tp / positives_total if positives_total else float("nan")
        recall_in_trend = tp / positives_in_trend if positives_in_trend else float("nan")
        precision = tp / n_flagged if n_flagged else float("nan")
        rows.append(
            Metrics(
                min_score=s,
                recall=recall,
                recall_in_trend=recall_in_trend,
                precision=precision,
                flagged=n_flagged,
                positives=positives_total,
                positives_in_trend=positives_in_trend,
                tp=tp,
                avg_daily_candidates=n_flagged / n_days if n_days else float("nan"),
            )
        )
    return pd.DataFrame([r.__dict__ for r in rows])


def choose_threshold(metrics: pd.DataFrame, max_daily: float = 30.0) -> int:
    """Loosest (lowest) score whose avg daily candidates <= cap -> max Recall."""
    ok = metrics[metrics["avg_daily_candidates"] <= max_daily]
    if ok.empty:
        # Nothing fits the cap; take the strictest (fewest candidates) row.
        return int(metrics.sort_values("avg_daily_candidates").iloc[0]["min_score"])
    # Lowest score under the cap maximizes Recall.
    return int(ok.sort_values("min_score").iloc[0]["min_score"])
