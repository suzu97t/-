"""Download the raw data used by the analysis into ../data/raw.

Sources (public GitHub repositories, fetched via raw.githubusercontent.com):
  - Daily index / FX prices (Investing.com format, 2011-2024):
      https://github.com/nikhilchandra-stats/asset_data
  - S&P 500 daily close (1885-2025, built from FRED / Yahoo Finance):
      https://github.com/SteelCerberus/us-market-data
  - Forex Factory economic calendar with actual / forecast values (2010-2023):
      https://github.com/spoluan/forex-factory-scraper
"""
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

RAW = "https://raw.githubusercontent.com"
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

PRICE_FILES = {
    "nikkei225.csv": "nikhilchandra-stats/asset_data/main/Nikkei 225 Historical Data.csv",
    "nasdaq.csv": "nikhilchandra-stats/asset_data/main/NASDAQ Composite Historical Data.csv",
    "usdjpy.csv": "nikhilchandra-stats/asset_data/main/USD_JPY Historical Data.csv",
    "sp500.csv": "SteelCerberus/us-market-data/main/data/us_market_data.csv",
}
CALENDAR_YEARS = range(2010, 2024)
CALENDAR_PATH = "spoluan/forex-factory-scraper/master/datasets/forex_factory_calendar_{year}.csv"


def download(repo_path: str, dest: Path) -> None:
    if dest.exists():
        print(f"skip  {dest.name} (already downloaded)")
        return
    url = f"{RAW}/{quote(repo_path)}"
    with urlopen(url, timeout=120) as resp:
        dest.write_bytes(resp.read())
    print(f"saved {dest.name}")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, path in PRICE_FILES.items():
        download(path, DATA_DIR / name)
    cal_dir = DATA_DIR / "calendar"
    cal_dir.mkdir(exist_ok=True)
    for year in CALENDAR_YEARS:
        download(CALENDAR_PATH.format(year=year), cal_dir / f"forex_factory_calendar_{year}.csv")


if __name__ == "__main__":
    main()
