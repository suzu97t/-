"""CLI: screen a list of tickers for pullback (押し目) long-entry candidates.

Usage:
    python -m pullback_screener.run_screen AAPL MSFT NVDA 7203.T 6758.T
    python -m pullback_screener.run_screen --period 2y --min-score 2 AAPL MSFT

With no network access to Yahoo Finance, each ticker transparently falls back to
synthetic data (a warning is printed) so the pipeline still runs.
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from .data import load_prices
from .screener import ScreenerConfig, screen_latest, SIGNAL_COLS

DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "JPM", "XOM"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Pullback long-entry screener")
    p.add_argument("tickers", nargs="*", default=DEFAULT_TICKERS)
    p.add_argument("--period", default="3y")
    p.add_argument("--interval", default="1d")
    p.add_argument("--min-score", type=int, default=2)
    p.add_argument("--no-synthetic", action="store_true",
                   help="fail instead of falling back to synthetic data")
    args = p.parse_args(argv)

    cfg = ScreenerConfig(min_score=args.min_score)
    rows = []
    for t in args.tickers:
        df, source = load_prices(
            t, period=args.period, interval=args.interval,
            allow_synthetic=not args.no_synthetic,
        )
        v = screen_latest(df, t, cfg)
        row = v.as_row()
        row["source"] = source
        rows.append(row)

    res = pd.DataFrame(rows)
    # Candidates first, then by descending rank score for eyeballing order.
    res = res.sort_values(["candidate", "rank_score"], ascending=[False, False])

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 30)

    show = ["ticker", "date", "close", "trend_ok", "pullback_score",
            "candidate", "rank_score", "source"] + SIGNAL_COLS
    print("\n=== Screen results (candidates first) ===")
    print(res[show].to_string(index=False))

    cands = res[res["candidate"]]
    print(f"\nCandidates: {len(cands)} / {len(res)}")
    if not cands.empty:
        print("Eyeball order:", ", ".join(cands["ticker"].tolist()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
