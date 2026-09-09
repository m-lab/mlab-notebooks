# M-Lab Monthly Stats — tutorial notebooks

A four-notebook tutorial on the [M-Lab](https://www.measurementlab.net/) Monthly Stats
datasets. Designed for a ~2 hour session: from "what are these numbers" to
"here is my country's story". Works for researchers, regulators, students, and
anyone new to the data — no statistics background assumed.

The whole tutorial can run in the browser via [MyBinder](https://mybinder.org/)
— click a link to launch.

| Notebook | Question it answers | Binder |
|----------|--------------------|--------|
| [00-introduction-and-catalog.ipynb](00-introduction-and-catalog.ipynb) | What are these data, and how do I load them? | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F00-introduction-and-catalog.ipynb) |
| [01-country-explorer.ipynb](01-country-explorer.ipynb) | How do I read one country's internet from its distribution shape? | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F01-country-explorer.ipynb) |
| [02-the-splits.ipynb](02-the-splits.ipynb) | Where does quality vary: between countries, regions, cities, or providers? | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F02-the-splits.ipynb) |
| [03-multiple-months.ipynb](03-multiple-months.ipynb) | Is my country getting better or worse over time? | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F03-multiple-months.ipynb) |

## How the notebooks load data

One pattern, everywhere in this folder:

```
manifest → pick month and slice → pd.read_parquet(url)
```

The manifest lives at `https://measurementlab.net/data/stats/manifest.json` and
lists every published file. Each notebook reads it, finds the URL for the
month/slice it needs, and opens the Parquet directly. No local cache, no build
step.

## About the data

Monthly Stats aggregate NDT speed tests into monthly, percentile-based summaries
(p1–p99) for four metrics — download, upload, latency, packet loss — at several
geographic granularities:

| Slice | One row per… |
|-------|--------------|
| `downloads_by_country` / `uploads_by_country` | country |
| `downloads_by_country_subdivision1` / … | state / province |
| `downloads_by_country_city` / … | city |
| `downloads_by_country_asn` / … | provider (ASN) |

> **Latency and loss polarity:** for latency and loss, lower is better, so the
> percentiles are *inverted* in the Parquet files: `latency_p95` is the 5% of
> connections with the *lowest* (best) latency. A higher percentile always means
> a better connection, whatever the metric.

## Setup

Python 3.12+ with pandas, pyarrow, requests, matplotlib, seaborn, ipywidgets:

```bash
pip install -r requirements.txt
```

Or via conda:

```bash
conda env create -f environment.yml
```

## Tutorial design notes

The set is deliberately small (4 notebooks, no shared modules). Every notebook
is self-contained; notebook 00 teaches the loading pattern the others reuse.
Design rationales and change history live in
[rewrite-plan.md](rewrite-plan.md).

## Further reading

- [M-Lab Knowledge Base](https://kb.measurementlab.net) — dataset docs and guides
- [IQB publications](https://www.measurementlab.net/publications/IQB_report_2025.pdf) — the Internet Quality Barometer composite-score view
- [M-Lab BigQuery Quickstart](https://www.measurementlab.net/data/docs/bq/quickstart/) — raw NDT data for deeper analysis