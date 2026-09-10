#!/usr/bin/env python3
"""Regenerate plot-p1p99.png for the Monthly Stats talk deck.

Draws the p1-p99 download-speed distribution for US, BR, MX, KE for one
month (default: the month shown on the deck's slides) and saves the plot
next to this script as plot-p1p99.png.

Usage:
    python makeplot.py                 # regenerate for the default month
    python makeplot.py 2026-07-01      # use a different month

If the deck's median table (talk-slides.md, "What the numbers look like")
drifts from the plot, the monthly data refresh is the cause — re-run this
script and update the table with the printed medians.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless: no display needed
import matplotlib.pyplot as plt
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "plot-p1p99.png"

MANIFEST_URL = "https://measurementlab.net/data/stats/manifest.json"
MONTH = sys.argv[1] if len(sys.argv) > 1 else "2026-06-01"
COUNTRIES = ["US", "BR", "MX", "KE"]
PERCENTILES = [1, 5, 10, 25, 50, 75, 90, 95, 99]
COLORS = {"US": "#1f77b4", "BR": "#2ca02c", "MX": "#ff7f0e", "KE": "#d62728"}


def month_url(slice_name: str, start: str) -> str:
    """Direct download URL for one month of one slice."""
    manifest = requests.get(MANIFEST_URL, timeout=30).json()
    for path, meta in manifest["files"].items():
        parts = path.split("/")
        # cache/v1/{start_ts}/{end_ts}/{slice_name}/data.parquet
        if len(parts) == 6 and parts[5] == "data.parquet":
            # start is 'YYYY-MM-DD'; the path encodes the same day as YYYYMMDD.
            if parts[4] == slice_name and start.replace("-", "") in parts[2]:
                return meta["url"]
    raise ValueError(f"No {slice_name} file for {start}")


def main() -> None:
    df = pd.read_parquet(month_url("downloads_by_country", MONTH))
    pcols = [f"download_p{n}" for n in PERCENTILES]

    print("Medians for the month", MONTH, "- keep the deck table in sync:")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for cc in COUNTRIES:
        row = df[df["country_code"] == cc].iloc[0]
        print(f"  {cc}: p50={row['download_p50']:.0f} "
              f"p95={row['download_p95']:.0f} n={row['sample_count']:,}")
        ax.plot(PERCENTILES, [row[c] for c in pcols], marker="o", markersize=4,
                label=f"{cc} (median {row['download_p50']:.0f})", color=COLORS[cc])

    ax.set_xlabel("Percentile")
    ax.set_ylabel("Download speed (Mbit/s)")
    ax.set_title(f"Download speed distribution (p1\u2013p99), {MONTH}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()