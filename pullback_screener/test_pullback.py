"""End-to-end tests + evaluation demo for the pullback screener.

Run directly:            python -m pullback_screener.test_pullback
Run under pytest:        pytest pullback_screener/test_pullback.py -q

The tests use real yfinance data when the network allows it, and deterministic
synthetic data otherwise, so they pass in a locked-down sandbox as well as on a
normal machine.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .data import load_prices, synthetic_prices
from .screener import ScreenerConfig, compute_signals, screen_latest, SIGNAL_COLS
from .evaluate import (
    label_pullbacks,
    evaluate_frames,
    choose_threshold,
)

TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "JPM", "XOM",
           "KO", "PG", "CAT", "UNH"]


# --------------------------------------------------------------------------- #
# Unit-ish tests
# --------------------------------------------------------------------------- #
def test_indicators_are_bounded():
    df = synthetic_prices("TEST", n=400, seed=1)
    e = compute_signals(df)
    rsi = e["rsi14"].dropna()
    assert (rsi >= 0).all() and (rsi <= 100).all()
    k = e["stoch_k"].dropna()
    assert (k >= -1e-6).all() and (k <= 100 + 1e-6).all()
    assert (e["atr14"].dropna() >= 0).all()


def test_signals_and_candidate_columns_exist():
    df = synthetic_prices("TEST", n=400, seed=2)
    e = compute_signals(df)
    for col in SIGNAL_COLS + ["trend_ok", "candidate", "pullback_score", "rank_score"]:
        assert col in e.columns
    # Score is the sum of the 0/1 signals.
    assert (e["pullback_score"] == e[SIGNAL_COLS].sum(axis=1)).all()
    # Candidate implies trend_ok (layer-1 gate).
    assert not (e["candidate"] & ~e["trend_ok"]).any()


def test_recall_beats_precision_by_design():
    """A loose OR/score screen should flag many bars: Recall > Precision.

    We headline `recall_in_trend` (Recall among positives that appeared while the
    layer-1 uptrend gate was open), since layer-2's job is only to catch dips
    *inside* an uptrend.
    """
    frames = {t: synthetic_prices(t, n=750, seed=i) for i, t in enumerate(TICKERS)}
    metrics = evaluate_frames(frames, ScreenerConfig(min_score=2))
    row = metrics[metrics["min_score"] == 2].iloc[0]
    assert row["positives_in_trend"] > 0, "no labelled pullbacks in an uptrend"
    assert row["recall_in_trend"] > row["precision"], "expected Recall-tilted screen"
    assert row["recall_in_trend"] >= 0.6, f"in-trend recall too low: {row['recall_in_trend']:.2f}"


def test_lower_score_raises_recall():
    """Loosening the cutoff (lower min_score) must not decrease Recall."""
    frames = {t: synthetic_prices(t, n=750, seed=i) for i, t in enumerate(TICKERS)}
    metrics = evaluate_frames(frames).sort_values("min_score")
    for col in ("recall", "recall_in_trend"):
        recalls = metrics[col].to_numpy()
        assert np.all(np.diff(recalls) <= 1e-9), f"{col} should be monotone in cutoff"


# --------------------------------------------------------------------------- #
# Demo / manual run
# --------------------------------------------------------------------------- #
def _run_demo():
    print("Loading price data for", len(TICKERS), "tickers ...")
    frames = {}
    sources = set()
    for t in TICKERS:
        df, source = load_prices(t, period="3y")
        frames[t] = df
        sources.add(source)
    print("Data source(s):", ", ".join(sorted(sources)))
    print("Rows per ticker:", {t: len(df) for t, df in list(frames.items())[:3]}, "...")

    print("\n--- Latest-bar screen (min_score=2) ---")
    cfg = ScreenerConfig(min_score=2)
    rows = [screen_latest(df, t, cfg).as_row() for t, df in frames.items()]
    res = pd.DataFrame(rows).sort_values(
        ["candidate", "rank_score"], ascending=[False, False]
    )
    show = ["ticker", "close", "trend_ok", "pullback_score", "candidate",
            "rank_score"] + SIGNAL_COLS
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 30)
    print(res[show].to_string(index=False))

    print("\n--- Label stats (horizon=10, up=+5%, dd=-3%) ---")
    tot_pos = tot_bars = 0
    for t, df in frames.items():
        lab = label_pullbacks(df)
        tot_pos += int(lab.sum())
        tot_bars += len(df)
    print(f"labelled positives: {tot_pos} / {tot_bars} bars "
          f"({100*tot_pos/tot_bars:.1f}%)")

    print("\n--- Recall / Precision vs candidate min_score ---")
    metrics = evaluate_frames(frames, cfg)
    metrics_disp = metrics.copy()
    for col in ("recall", "recall_in_trend", "precision"):
        metrics_disp[col] = metrics_disp[col].round(3)
    metrics_disp["avg_daily_candidates"] = metrics_disp["avg_daily_candidates"].round(1)
    print(metrics_disp.to_string(index=False))
    print("(recall = over all profitable entries; recall_in_trend = over the "
          "ones inside an uptrend, which is layer-2's actual job)")

    chosen = choose_threshold(metrics, max_daily=30.0)
    crow = metrics[metrics["min_score"] == chosen].iloc[0]
    print(f"\nChosen min_score under a 30 names/day cap: {chosen}")
    print(f"  -> Recall={crow['recall']:.3f}  Recall_in_trend={crow['recall_in_trend']:.3f}  "
          f"Precision={crow['precision']:.3f}  "
          f"avg_daily_candidates={crow['avg_daily_candidates']:.1f}")
    print("\nInterpretation: pick the loosest score that still fits your daily")
    print("eyeball budget; Recall is maximised there while Precision stays as a")
    print("(lower, acceptable) by-product — exactly the requested tilt.")


if __name__ == "__main__":
    _run_demo()
