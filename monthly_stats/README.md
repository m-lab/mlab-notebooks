# M-Lab Monthly Stats Notebooks

Jupyter notebooks for exploring [M-Lab](https://www.measurementlab.net/) Monthly Stats. These notebooks are intended for researchers, network analysts, and community members who want to understand how internet quality varies across countries, ISPs, regions, and cities.

## Notebooks

### [01-exploring-iqb-data.ipynb](01-exploring-iqb-data.ipynb)

**No special library required — just pandas, requests, and matplotlib.**

Introduces the Monthly Stats dataset and covers all geographic granularities:

- Discovering available data via the manifest at `https://measurementlab.net/data/iqb/manifest.json`
- Country-level download/upload/latency/loss comparisons
- ISP (ASN) analysis within a country
- State/province (subdivision) breakdowns
- City-level exploration
- Time series tracking of metrics across months
- Understanding the percentile distribution (p5 through p99)

**Install:**
```
pip install pandas pyarrow requests matplotlib seaborn
```

### [02-iqb-scores.ipynb](02-iqb-scores.ipynb)

**Uses the `iqb` Python library.**

Shows how to compute the IQB composite score (0–1) and interpret it:

- Computing IQB scores for individual countries
- Comparing countries with a color-coded bar chart
- Per-use-case breakdown (web browsing, video streaming, gaming, etc.) as a heatmap
- Sensitivity to percentile choice (p50 vs. p95)
- ISP-level IQB scores within a country
- Time series of IQB scores over multiple months
- Introduction to customizing quality thresholds

**Install:**
```bash
# Clone the iqb repository and install
git clone https://github.com/m-lab/iqb.git
cd iqb
uv sync --dev
uv run jupyter notebook

# Or install just the library
pip install git+https://github.com/m-lab/iqb.git#subdirectory=library
```

## About the Data

Monthly Stats are published at `https://measurementlab.net/data/iqb/` as monthly Parquet files. Each file covers one calendar month and one geographic granularity. The available slices are:

| Slice | Geographic dimensions |
|-------|-----------------------|
| `downloads_by_country` | country |
| `uploads_by_country` | country |
| `downloads_by_country_asn` | country + ASN (ISP) |
| `uploads_by_country_asn` | country + ASN |
| `downloads_by_country_subdivision1` | country + state/province |
| `uploads_by_country_subdivision1` | country + state/province |
| `downloads_by_country_subdivision1_asn` | country + state/province + ASN |
| `uploads_by_country_subdivision1_asn` | country + state/province + ASN |
| `downloads_by_country_city` | country + city |
| `uploads_by_country_city` | country + city |
| `downloads_by_country_city_asn` | country + city + ASN |
| `uploads_by_country_city_asn` | country + city + ASN |

Download files include columns for `download_p{N}`, `latency_p{N}`, and `loss_p{N}`. Upload files include `upload_p{N}`. Percentile values N ∈ {1, 5, 10, 25, 50, 75, 90, 95, 99}.

> **Latency and loss polarity:** In the parquet files, latency and packet loss percentiles are *inverted* so that p95 = best 5% (lowest latency/loss). This normalizes the "top 5% performance" slice to always be p95 regardless of metric.

## Further Reading

- [IQB Library and source code](https://github.com/m-lab/iqb)
- [IQB Framework Report (PDF)](https://www.measurementlab.net/publications/IQB_report_2025.pdf)
- [IQB Executive Summary (PDF)](https://www.measurementlab.net/publications/IQB_executive_summary_2025.pdf)
- [M-Lab Knowledge Base](https://kb.measurementlab.net)
- [M-Lab BigQuery Quickstart](https://www.measurementlab.net/data/docs/bq/quickstart/)
