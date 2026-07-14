# M-Lab Monthly Stats Notebooks

Jupyter notebooks for exploring [M-Lab](https://www.measurementlab.net/) Monthly Stats. These notebooks are intended for researchers, network analysts, and community members who want to understand how internet quality varies across countries, ISPs, regions, and cities.

## Notebooks

All notebooks can be run in the browser without any local installation via [MyBinder](https://mybinder.org/). Click a link below to launch.

| Notebook | Binder | Description |
|----------|--------|-------------|
| [00-introduction-and-catalog.ipynb](00-introduction-and-catalog.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F00-introduction-and-catalog.ipynb) | Dataset structure, available slices and dates |
| [01-country-level.ipynb](01-country-level.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F01-country-level.ipynb) | Compare countries, metric distributions |
| [02-asn-isp.ipynb](02-asn-isp.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F02-asn-isp.ipynb) | Provider-level comparison within a country |
| [03-subdivisions.ipynb](03-subdivisions.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F03-subdivisions.ipynb) | Sub-national breakdown by state/province |
| [04-subdivision-asn-drilldown.ipynb](04-subdivision-asn-drilldown.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F04-subdivision-asn-drilldown.ipynb) | Provider performance within a region |
| [05-cities.ipynb](05-cities.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F05-cities.ipynb) | City-level comparison (see geolocation caveats) |
| [06-time-series.ipynb](06-time-series.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F06-time-series.ipynb) | Multi-month trend analysis |


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

**M-Lab Knowledge Base articles for this dataset:**

- [M-Lab Monthly Stats: Pre-computed Parquet Summaries](https://kb.measurementlab.net/articles/monthly-stats-dataset) — what the dataset is, schema, slices, access, limitations
- [Understanding Monthly Stats Percentiles](https://kb.measurementlab.net/articles/monthly-stats-percentiles) — polarity inversion for latency/loss, which percentile to use
- [Working with Monthly Stats in Python](https://kb.measurementlab.net/articles/monthly-stats-python) — loading data, filtering, multi-month analysis, IQB score computation

**IQB:**

- [IQB Library and source code](https://github.com/m-lab/iqb)
- [IQB Framework Report (PDF)](https://www.measurementlab.net/publications/IQB_report_2025.pdf)
- [IQB Executive Summary (PDF)](https://www.measurementlab.net/publications/IQB_executive_summary_2025.pdf)

**M-Lab:**

- [M-Lab Knowledge Base](https://kb.measurementlab.net)
- [M-Lab BigQuery Quickstart](https://www.measurementlab.net/data/docs/bq/quickstart/)
