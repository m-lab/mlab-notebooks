---
marp: true
theme: default
paginate: true
header: "M-Lab Monthly Stats — a hands-on tutorial"
style: |
  section { padding: 1.5em; }
  h1 { font-size: 2.2em; }
  li { font-size: 0.85em; line-height: 1.3; }
  code { font-size: 0.8em; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1em; }
  a { color: #2a7de1; }
math: mathjax
---

<!-- _class: lead -->
# M-Lab Monthly Stats

## What gets measured, how to read it, and how **you** can explore it — today.

A 5-minute walk-through before a hands-on session.

Jonah Duckles · <jonah@measurementlab.net> · M-Lab

---

<!-- _class: lead -->
## The whole talk, in one number

Every month, **millions of people** run an open speed test against
[M-Lab](https://www.measurementlab.net/).

We take **every** one of those tests and squeeze it into a **small, pre-computed
file you can download in seconds**.

The notebooks in this tutorial turn that file into answers about any country,
region, city, or provider in the world.

---

## Where the data come from

- **NDT** — the Network Diagnostic Tool — the open speed test platform M-Lab runs.
- **Millions** of tests every month, from real user devices worldwide.
- **BigQuery** stores the raw rows; the full archive is **petabytes** of measurements.

The **Monthly Stats** dataset is M-Lab's curated, summarized view of all that:
- **2009 → present**, every month
- **240 countries**, plus regions, cities, and providers
- **one small Parquet file per month, per geography** (a few MB each)

> Instead of querying petabytes of raw rows, each month you download one small
> file with pre-computed percentile values — for each metric, geography, and month.

**`manifest → pick month & slice → pd.read_parquet(url)`**

---

## What's inside each file: the four metrics

| Metric | Column prefix | Unit | Better |
|---|---|---|---|
| Download throughput | `download_p*` | Mbit/s | ↑ higher |
| Upload throughput | `upload_p*` | Mbit/s | ↑ higher |
| Latency (min RTT) | `latency_p*` | ms | ↓ lower |
| Packet loss rate | `loss_p*` | fraction | ↓ lower |

- **download** — how fast pages and files arrive at your computer
- **upload** — how fast you send data away from your computer
- **latency** — round-trip responsiveness: how long a message takes to reach the server and be acknowledged at your computer
- **loss** — percentage of dropped packets (reliability)

---

## Percentiles: line everyone up

**Line all the tests in a month up, slowest → fastest:**

- **p50** — the median, the test in the exact middle — the typical user's experience
- **p95** — 95 tests out of every 100 — near the front
- **p1** — near the very back

No mean (average) exists here — only percentiles. One very fast connection cannot
drag the summary upward the way it drags an average.

> **A wide p50→p95 gap shows how different experiences can be** in a region or country.
> It is a statement about the *shape* of the distribution: most tests sit in a band,
> and a minority run much faster or much slower.

> **Before believing any of it — ask how many tests went in.** 100 tests wiggle; 100 000 are solid.

---

## The splits: "one row per what" is the only difference

| Slice | One row per… |
|---|---|
| `downloads_by_country` / `uploads_by_country` | country |
| `downloads_by_country_subdivision1` | state / province |
| `downloads_by_country_city` | city |
| `downloads_by_country_asn` | provider (ASN) |

Every slice keeps the **same four metrics** across their percentiles — only the
geography changes.

---

## One polarity gotcha, then you know the whole schema

For **latency and loss**, *lower* is better, so the data **flip the percentiles**:

- `latency_p95` — the 5% of connections with the **lowest** (best) latency
- `latency_p5` — the slowest (worst) latency

A higher percentile always means a **better** connection, whatever the metric.

Notebook 01 makes this visible on real curves — the latency curve slopes the
*other* way.

---

<!-- _class: lead -->
## What the numbers look like — June 2026, country medians

<div class="cols">

<div>

**Download p50, Mbit/s** (240 countries on file)

| 🇺🇸 US | 🇧🇷 BR | 🇩🇽 MX | 🇰🇪 KE |
|---|---|---|---|
| **125.9** | 16.9 | 15.3 | 9.4 |

<!-- (illustrative) -->

</div>

<div>

**What shape means here**

- A **median** is one point — the typical user.
- The **distribution** is the whole curve: p5, p25, p50, p75, p95, p99.
- The notebook 01 **percentile sweep** shows whether a ranking
  survives at p95 vs p50 — often it does not.

</div>

</div>

> We use **"Highest N"**, not "Top N": a position on a scale, not a prize. Sample
> counts are shown on every chart — check the test count before believing a rank.

---

## The four notebooks

| | Question it answers |
|---|---|
| **00 · introduction & catalog** | What are these data? |
| **01 · country explorer** | How do I read a country's distribution shape? |
| **02 · the splits** | Where does it vary: countries, regions, cities, providers? |
| **03 · multiple months** | How do measurements change over months? |

Each is **self-contained** — start anywhere. 00 teaches the one loading pattern
the others reuse: **`manifest → URL → pd.read_parquet`**.

---

## Try it right now — MyBinder

Click a notebook — it launches in your browser in seconds. No local install.

| Notebook | Binder |
|---|---|
| 00 · introduction & catalog | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F00-introduction-and-catalog.ipynb) |
| 01 · country explorer | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F01-country-explorer.ipynb) |
| 02 · the splits | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F02-the-splits.ipynb) |
| 03 · multiple months | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/m-lab/mlab-notebooks/HEAD?urlpath=%2Fdoc%2Ftree%2Fmonthlystats%2F03-multiple-months.ipynb) |

**Your country.** Look up your own — median, shape, regions, and whether it improves.

---

## What to try first, in the hands-on session

1. **00** — open the catalog, pick your country and month.
2. **01** — read your country's curve aloud; run the **percentile sweep**.
3. **02** — your regions vs your cities vs your providers; "between or within".
4. **03** — pull 12 months: is your country trending **up or down**?

The whole point: **you can redo every chart yourself** — same cells, your country,
your slice, your question. No raw BigQuery needed.

---

## A realistic path through the notebooks

```python
# the ONLY pattern you need to remember
manifest → pick month and slice → pd.read_parquet(url)
```

Notebook 00 shows the few lines behind this; 01–03 reuse it verbatim.

**Questions you can now answer overnight:**

- What is the typical download speed in my country vs Brazil vs Germany?
- Does my city punch above or below my country's median?
- Is the gap between the top 5% and the median growing?
- Is my country's median improving month over month?

---

<!-- _class: lead -->
## Recap

- **Percentiles, not averages** — and the shape of the distribution is the story.
- **Four metrics** × **the same slices** — country, region, city, provider.
- **One loading pattern**, four notebooks, zero installs: launch any in MyBinder.

**Thanks! Questions? Hands-on time — open a notebook and make it about your country.**