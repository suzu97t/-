"""US employment data / US equity indices -> next-day Japanese equities (Nikkei 225).

Run `python src/fetch_data.py` first, then `python src/analysis.py`.
Outputs tables to ../results and charts to ../figures.

Timing convention
-----------------
A US session on calendar date D closes (16:00 ET) before the Tokyo session of
the next calendar day opens (09:00 JST). For every Nikkei trading day J we
therefore pair the Nikkei return (previous Nikkei close -> close on J) with the
US move over all US sessions dated in [previous Nikkei date, J - 1 day]. That
is exactly the US information that arrived while Tokyo was closed.

Employment releases (08:30 ET on US date D) are mapped to the first Nikkei
trading day J > D.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

# Reference palette (dataviz skill, light mode)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titlesize": 11, "axes.titleweight": "bold", "lines.linewidth": 2, "axes.axisbelow": True,
})


# --------------------------------------------------------------------------- data
def load_investing(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig", thousands=",")
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df = df.rename(columns={"Price": "Close"})[["Date", "Open", "Close"]]
    # The Nikkei file repeats 2024-08-13 once; keep a single row per date
    return df.drop_duplicates("Date", keep="last").set_index("Date").sort_index().astype(float)


def load_sp500(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["Date", "Close"], parse_dates=["Date"])
    return df.set_index("Date").sort_index()


def parse_value(s):
    """'241K' -> 241000, '5.6%' -> 5.6, '-1.2M' -> -1.2e6. Unparseable -> NaN."""
    if not isinstance(s, str) or not s.strip():
        return np.nan
    s = s.strip().replace(",", "")
    mult = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12, "%": 1.0}.get(s[-1], 1.0)
    if s[-1] in "KMBT%":
        s = s[:-1]
    try:
        return float(s) * mult
    except ValueError:
        return np.nan


def load_calendar() -> pd.DataFrame:
    frames = [pd.read_csv(p) for p in sorted((RAW / "calendar").glob("*.csv"))]
    cal = pd.concat(frames, ignore_index=True)
    cal = cal[cal["Currency"] == "USD"].copy()
    # 'Date' is malformed on Feb 29 rows ("Wed Feb 29"); the combined timestamp is always ISO.
    # Its clock is UTC+8, so 08:30 ET releases still fall on their US calendar date.
    cal["Date"] = pd.to_datetime(cal["Combined DateTime"]).dt.normalize()
    for col in ["Actual", "Forecast", "Previous"]:
        cal[col] = cal[col].map(parse_value)
    return cal.dropna(subset=["Actual", "Forecast"])


# ------------------------------------------------------------------- alignment
def build_panel() -> pd.DataFrame:
    nk = load_investing(RAW / "nikkei225.csv")
    nq = load_investing(RAW / "nasdaq.csv")
    fx = load_investing(RAW / "usdjpy.csv")
    sp = load_sp500(RAW / "sp500.csv")

    start, end = max(nk.index[0], nq.index[0]), min(nk.index[-1], nq.index[-1], sp.index[-1])
    sp = sp.loc[start - pd.Timedelta(days=10):end]

    us_dates = sp.index.intersection(nq.index)  # sessions present in both US series
    log_sp = np.log(sp["Close"].reindex(us_dates))
    log_nq = np.log(nq["Close"].reindex(us_dates))
    log_fx = np.log(fx["Close"])

    rows = []
    nk_dates = nk.loc[start:end].index
    for prev_j, j in zip(nk_dates[:-1], nk_dates[1:]):
        # US sessions that happened after Tokyo closed on prev_j and before it opened on j
        window = us_dates[(us_dates >= prev_j) & (us_dates < j)]
        if len(window) == 0:
            continue
        last_us = window[-1]
        before = us_dates[us_dates < window[0]]
        if len(before) == 0:
            continue
        base_us = before[-1]
        fx_before = log_fx.loc[:j - pd.Timedelta(days=1)]
        fx_base = log_fx.loc[:prev_j - pd.Timedelta(days=1)]
        rows.append({
            "jp_date": j,
            "us_date": last_us,
            "n_us_sessions": len(window),
            "nk_ret": np.log(nk.at[j, "Close"] / nk.at[prev_j, "Close"]),
            "nk_gap": np.log(nk.at[j, "Open"] / nk.at[prev_j, "Close"]),
            "nk_intraday": np.log(nk.at[j, "Close"] / nk.at[j, "Open"]),
            "sp_ret": log_sp[last_us] - log_sp[base_us],
            "nq_ret": log_nq[last_us] - log_nq[base_us],
            "fx_ret": fx_before.iloc[-1] - fx_base.iloc[-1] if len(fx_base) else np.nan,
            # same-calendar-day US session (happens AFTER Tokyo closes on j) - a timing placebo
            "sp_same_day": log_sp[j] - log_sp[us_dates[us_dates < j][-1]] if j in log_sp.index else np.nan,
        })
    panel = pd.DataFrame(rows).set_index("jp_date")
    # Investing.com sometimes reports Open == previous close / missing opens; drop impossible gaps
    panel.loc[panel["nk_gap"].abs() > 0.2, ["nk_gap", "nk_intraday"]] = np.nan
    return panel


# -------------------------------------------------------------------- analysis
def ols(y: pd.Series, X: pd.DataFrame):
    d = pd.concat([y, X], axis=1).dropna()
    return sm.OLS(d.iloc[:, 0], sm.add_constant(d.iloc[:, 1:])).fit(cov_type="HC1")


def market_linkage(panel: pd.DataFrame) -> pd.DataFrame:
    out = []
    specs = [
        ("S&P500(前夜) → 日経(終値ベース)", "nk_ret", ["sp_ret"]),
        ("NASDAQ(前夜) → 日経(終値ベース)", "nk_ret", ["nq_ret"]),
        ("S&P500(前夜) → 日経 寄付ギャップ", "nk_gap", ["sp_ret"]),
        ("S&P500(前夜) → 日経 寄引(日中)", "nk_intraday", ["sp_ret"]),
        ("S&P500 + ドル円(前夜) → 日経", "nk_ret", ["sp_ret", "fx_ret"]),
        ("[参考] 同日のS&P500(日経引け後) → 日経", "nk_ret", ["sp_same_day"]),
    ]
    for label, yname, xnames in specs:
        m = ols(panel[yname], panel[xnames])
        d = panel[[yname] + xnames].dropna()
        row = {
            "モデル": label, "N": int(m.nobs), "R2": m.rsquared,
            "相関": d[yname].corr(d[xnames[0]]),
            "方向一致率": (np.sign(d[yname]) == np.sign(d[xnames[0]])).mean(),
        }
        for x in xnames:
            row[f"β({x})"] = m.params[x]
            row[f"t({x})"] = m.tvalues[x]
        out.append(row)
    return pd.DataFrame(out)


def yearly_linkage(panel: pd.DataFrame) -> pd.DataFrame:
    g = panel.dropna(subset=["nk_ret", "sp_ret"]).groupby(panel.index.year)
    return pd.DataFrame({
        "N": g.size(),
        "相関": g.apply(lambda d: d["nk_ret"].corr(d["sp_ret"])),
        "β": g.apply(lambda d: np.polyfit(d["sp_ret"], d["nk_ret"], 1)[0]),
        "方向一致率": g.apply(lambda d: (np.sign(d["nk_ret"]) == np.sign(d["sp_ret"])).mean()),
    }).rename_axis("年")


def quantile_table(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel.dropna(subset=["nk_ret", "sp_ret"]).copy()
    d["bucket"] = pd.qcut(d["sp_ret"], 10, labels=[f"D{i}" for i in range(1, 11)])
    g = d.groupby("bucket", observed=True)
    return pd.DataFrame({
        "S&P500平均(%)": g["sp_ret"].mean() * 100,
        "翌日日経平均(%)": g["nk_ret"].mean() * 100,
        "翌日日経上昇確率": g["nk_ret"].apply(lambda s: (s > 0).mean()),
        "N": g.size(),
    }).rename_axis("S&P500前夜リターン十分位")


EVENTS = {
    "NFP": "Non-Farm Employment Change",
    "失業率": "Unemployment Rate",
    "平均時給": "Average Hourly Earnings m/m",
    "ADP": "ADP Non-Farm Employment Change",
    "新規失業保険申請": "Unemployment Claims",
    "JOLTS": "JOLTS Job Openings",
}
# sign so that a positive surprise always means "labour market stronger than expected"
STRONG_SIGN = {"失業率": -1, "新規失業保険申請": -1}


def event_study(panel: pd.DataFrame, cal: pd.DataFrame):
    jp_dates = panel.index
    tables, merged = [], {}
    for key, name in EVENTS.items():
        ev = cal[cal["Event"] == name][["Date", "Actual", "Forecast"]].drop_duplicates("Date").copy()
        ev["surprise"] = (ev["Actual"] - ev["Forecast"]) * STRONG_SIGN.get(key, 1)
        # z-score with a robust scale so the 2020 COVID prints don't dominate
        mad = stats.median_abs_deviation(ev["surprise"], scale="normal")
        ev["z"] = (ev["surprise"] / mad).clip(-3, 3)
        # keep releases inside the price sample, then map each to the next Tokyo session
        ev = ev[(ev["Date"] >= panel.index[0]) & (ev["Date"] <= panel["us_date"].iloc[-1])]
        ev["jp_date"] = jp_dates[jp_dates.searchsorted(ev["Date"], side="right")]
        # sp_ret / nq_ret on jp_date = the US move since Tokyo's previous close,
        # which includes the release-day session (the US reaction to the print)
        ev = ev.join(panel, on="jp_date")
        ev_ex = ev[~ev["Date"].dt.year.eq(2020)]
        merged[key] = ev

        m1 = ols(ev["nk_ret"], ev[["z"]])
        m2 = ols(ev["nk_ret"], ev[["z", "sp_ret"]])
        m_ex = ols(ev_ex["nk_ret"], ev_ex[["z"]])
        m_us = ols(ev["sp_ret"], ev[["z"]])
        rho, p_rho = stats.spearmanr(ev["z"], ev["nk_ret"], nan_policy="omit")
        m_fx = ols(ev["fx_ret"], ev[["z"]])
        # baseline volatility: non-event Tokyo days, re-weighted to the events' weekday mix
        # (NFP lands on Mondays, which carry a weekend of news anyway)
        non_event = panel.loc[~panel.index.isin(ev["jp_date"]), "nk_ret"].abs()
        dow_weights = ev["jp_date"].dt.dayofweek.value_counts(normalize=True)
        baseline = sum(w * non_event[non_event.index.dayofweek == dow].mean() for dow, w in dow_weights.items())
        tables.append({
            "指標": key, "N": int(m1.nobs),
            "β 日経(%/1σ)": m1.params["z"] * 100, "t": m1.tvalues["z"], "R2": m1.rsquared,
            "順位相関": rho, "p(順位相関)": p_rho,
            "β 2020除外": m_ex.params["z"] * 100, "t 2020除外": m_ex.tvalues["z"],
            "β S&P前夜を制御": m2.params["z"] * 100, "t S&P制御": m2.tvalues["z"],
            "β S&P500自体(%/1σ)": m_us.params["z"] * 100, "t S&P500": m_us.tvalues["z"],
            "β ドル円(%/1σ)": m_fx.params["z"] * 100, "t ドル円": m_fx.tvalues["z"],
            "発表翌日|日経|平均(%)": ev["nk_ret"].abs().mean() * 100,
            "同曜日の非発表日|日経|平均(%)": baseline * 100,
        })
    return pd.DataFrame(tables), merged


def nfp_by_period(ev: pd.DataFrame) -> pd.DataFrame:
    periods = {"2011-2019": (2011, 2019), "2020 (COVID)": (2020, 2020), "2021-2023": (2021, 2023)}
    rows = []
    for label, (a, b) in periods.items():
        d = ev[ev["Date"].dt.year.between(a, b)]
        m_nk, m_sp = ols(d["nk_ret"], d[["z"]]), ols(d["sp_ret"], d[["z"]])
        rows.append({"期間": label, "N": int(m_nk.nobs),
                     "β 日経(%/1σ)": m_nk.params["z"] * 100, "t 日経": m_nk.tvalues["z"],
                     "β S&P500(%/1σ)": m_sp.params["z"] * 100, "t S&P500": m_sp.tvalues["z"]})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------- charts
def chart_scatter(panel: pd.DataFrame) -> None:
    d = panel.dropna(subset=["nk_ret", "sp_ret"])[["nk_ret", "sp_ret"]] * 100
    fig, ax = plt.subplots(figsize=(6.4, 5))
    ax.scatter(d["sp_ret"], d["nk_ret"], s=9, color=BLUE, alpha=0.35, linewidths=0)
    b, a = np.polyfit(d["sp_ret"], d["nk_ret"], 1)
    xs = np.linspace(d["sp_ret"].min(), d["sp_ret"].max(), 50)
    ax.plot(xs, a + b * xs, color=ORANGE)
    r = d["sp_ret"].corr(d["nk_ret"])
    ax.text(0.03, 0.96, f"OLS slope {b:.2f}   r = {r:.2f}   n = {len(d):,}", transform=ax.transAxes,
            va="top", color=INK)
    ax.set_xlabel("S&P 500 return, prior US session (%)")
    ax.set_ylabel("Nikkei 225 return, next Tokyo session (%)")
    ax.set_title("Overnight S&P 500 move vs next-day Nikkei 225 (2011-2024)", loc="left")
    fig.tight_layout()
    fig.savefig(FIGURES / "01_sp500_vs_nikkei_scatter.png", dpi=150)
    plt.close(fig)


def chart_deciles(q: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    vals = q["翌日日経平均(%)"]
    colors = [BLUE if v >= 0 else ORANGE for v in vals]
    ax.bar(range(len(vals)), vals, color=colors, width=0.7)
    ax.axhline(0, color=INK2, linewidth=0.8)
    ax.set_xticks(range(len(vals)), [f"D{i}\n{v:+.1f}%" for i, v in enumerate(q["S&P500平均(%)"], 1)])
    ax.set_xlabel("S&P 500 prior-session return decile (D1 = worst, label = decile mean)")
    ax.set_ylabel("Mean next-day Nikkei return (%)")
    ax.set_title("Next-day Nikkei return by S&P 500 overnight decile", loc="left")
    ax.grid(axis="x", visible=False)
    ax.set_ylim(vals.min() * 1.25, vals.max() * 1.25)
    for i, v in enumerate(vals):
        if i in (0, len(vals) - 1):
            ax.annotate(f"{v:+.2f}%", (i, v), ha="center", va="bottom" if v >= 0 else "top",
                        xytext=(0, 3 if v >= 0 else -3), textcoords="offset points", color=INK)
    fig.tight_layout()
    fig.savefig(FIGURES / "02_nikkei_by_sp500_decile.png", dpi=150)
    plt.close(fig)


def chart_rolling(panel: pd.DataFrame) -> None:
    d = panel.dropna(subset=["nk_ret", "sp_ret", "sp_same_day"])
    roll = d["nk_ret"].rolling(250).corr(d["sp_ret"])
    roll_same = d["nk_ret"].rolling(250).corr(d["sp_same_day"])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(roll.index, roll, color=BLUE, label="S&P 500, prior US session (known before Tokyo opens)")
    ax.plot(roll_same.index, roll_same, color=ORANGE, label="S&P 500, same-date session (after Tokyo closes)")
    ax.set_ylim(-0.12, 0.75)
    ax.legend(frameon=False, loc="lower left", fontsize=9)
    ax.axhline(0, color=INK2, linewidth=0.8)
    ax.set_ylabel("Correlation (rolling 250 days)")
    ax.set_title("Rolling correlation with the Nikkei 225 daily return", loc="left")
    fig.tight_layout()
    fig.savefig(FIGURES / "03_rolling_correlation.png", dpi=150)
    plt.close(fig)


def chart_nfp(ev: pd.DataFrame) -> None:
    d = ev.dropna(subset=["nk_ret", "z"])
    fig, ax = plt.subplots(figsize=(6.4, 5))
    ax.scatter(d["z"], d["nk_ret"] * 100, s=22, color=BLUE, alpha=0.7, linewidths=0)
    b, a = np.polyfit(d["z"], d["nk_ret"] * 100, 1)
    xs = np.linspace(-3, 3, 20)
    ax.plot(xs, a + b * xs, color=ORANGE)
    ax.text(0.03, 0.96, f"OLS slope {b:+.2f}% per 1 sigma   n = {len(d)}", transform=ax.transAxes,
            va="top", color=INK)
    ax.axhline(0, color=INK2, linewidth=0.8)
    ax.axvline(0, color=INK2, linewidth=0.8)
    ax.set_xlabel("NFP surprise (actual - consensus, robust z, capped at +/-3)")
    ax.set_ylabel("Nikkei 225 return, next Tokyo session (%)")
    ax.set_title("US payrolls surprise vs next-day Nikkei (2011-2023)", loc="left")
    fig.tight_layout()
    fig.savefig(FIGURES / "04_nfp_surprise_vs_nikkei.png", dpi=150)
    plt.close(fig)


def chart_event_betas(ev_table: pd.DataFrame) -> None:
    d = ev_table.set_index("指標")
    labels_en = {"NFP": "Nonfarm payrolls", "失業率": "Unemployment rate (inverted)",
                 "平均時給": "Avg hourly earnings", "ADP": "ADP employment",
                 "新規失業保険申請": "Initial claims (inverted)", "JOLTS": "JOLTS openings"}
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(7.5, 4))
    h = 0.36
    ax.barh(y - h / 2, d["β S&P500自体(%/1σ)"], height=h - 0.04, color=BLUE, label="S&P 500, release day")
    ax.barh(y + h / 2, d["β 日経(%/1σ)"], height=h - 0.04, color=ORANGE, label="Nikkei 225, next Tokyo day")
    for yi, (tv_us, tv_jp, bu, bj) in enumerate(zip(d["t S&P500"], d["t"], d["β S&P500自体(%/1σ)"], d["β 日経(%/1σ)"])):
        for val, tv, off in ((bu, tv_us, -h / 2), (bj, tv_jp, h / 2)):
            ax.annotate(f"t={tv:+.1f}", (val, yi + off), xytext=(4 if val >= 0 else -4, 0),
                        textcoords="offset points", va="center", ha="left" if val >= 0 else "right",
                        color=INK2, fontsize=8)
    ax.set_yticks(y, [labels_en[k] for k in d.index])
    ax.invert_yaxis()
    ax.axvline(0, color=INK2, linewidth=0.8)
    ax.set_xlabel("Return per +1 sigma 'stronger labour market' surprise (%)")
    ax.set_title("Reaction to US employment surprises", loc="left")
    ax.grid(axis="y", visible=False)
    lo, hi = ax.get_xlim()
    ax.set_xlim(lo - 0.05, hi + 0.08)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES / "05_employment_surprise_betas.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------ main
def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    panel = build_panel()
    cal = load_calendar()

    linkage = market_linkage(panel)
    yearly = yearly_linkage(panel)
    q = quantile_table(panel)
    ev_table, merged = event_study(panel, cal)
    nfp_periods = nfp_by_period(merged["NFP"])

    panel.to_csv(RESULTS / "daily_panel.csv", float_format="%.6f")
    linkage.to_csv(RESULTS / "market_linkage.csv", index=False, float_format="%.4f")
    yearly.to_csv(RESULTS / "market_linkage_by_year.csv", float_format="%.4f")
    q.to_csv(RESULTS / "nikkei_by_sp500_decile.csv", float_format="%.4f")
    ev_table.to_csv(RESULTS / "employment_event_study.csv", index=False, float_format="%.4f")
    nfp_periods.to_csv(RESULTS / "nfp_by_period.csv", index=False, float_format="%.4f")
    merged["NFP"].to_csv(RESULTS / "nfp_events.csv", index=False, float_format="%.6f")

    chart_scatter(panel)
    chart_deciles(q)
    chart_rolling(panel)
    chart_nfp(merged["NFP"])
    chart_event_betas(ev_table)

    pd.set_option("display.width", 220, "display.max_columns", 30)
    print(f"Panel: {panel.index[0].date()} - {panel.index[-1].date()}, {len(panel)} Tokyo sessions\n")
    print(linkage.round(3).to_string(index=False), "\n")
    print(yearly.round(3).to_string(), "\n")
    print(q.round(3).to_string(), "\n")
    print(ev_table.round(3).to_string(index=False), "\n")
    print(nfp_periods.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
