# Monthly Stats notebooks — rewrite plan

Status: draft for team review (Simone, Pavlos) — no notebook files changed yet.
Scope: simplify `monthlystats/` from **7 notebooks + 1 helper module** into **4 notebooks, zero helpers**, reframed as a data-literacy tutorial with two focus areas:
1. **The metrics** — download, upload, latency, loss — and what the **shape of the percentile distribution** tells you.
2. **The splits** — country, country×ASN, country×subdivision, country×city — and **what you can (and cannot) learn from each**.

Design intent: the four notebooks double as a **~2-hour tutorial** that takes a participant from "what are these numbers" to "here is my country's story" — with developing-country and statistical-literacy constraints as first-class requirements, not afterthoughts (see §12).

Out of scope, explicitly agreed: **no IQB score calculations** in these notebooks. Also agreed: **the tutorial never uses the IQB library's cache machinery** — multi-month analysis uses the same simple direct-download pattern as the rest of the set (see §8). IQB is mentioned only as a one-line pointer in notebook 00.

---

## 1. Why rewrite

The current set has three structural problems:

1. **Maintenance burden with zero added insight.** Notebooks 02–05 (ASN, subdivisions, subdivision×ASN, cities) duplicate ~50 lines of manifest + loader + country-lookup boilerplate each, and only differ in the join key and one plot. That is the worst cost-benefit ratio in the repo: four files of copy-pasted plumbing that must all be updated together (precisely what happened with the manifest URL).
2. **The teaching content is scattered and buried.** The conceptual story of this dataset — four metrics, nine percentiles per metric, a polarity inversion, six geographic splits — is told once as a table dump in notebook 00 and never *demonstrated*. The interactive explorers exist, but a new user must first wade through duplicated setup cells, a local helper module, and a 20-line hand-rolled cache before seeing a single number.
3. **The distribution and split concepts are implied, never taught.** Nothing in the current set makes a reader *feel* the difference between p5 and p95, or asks "is the spread *within* Sweden or *between* Sweden and Nigeria?" — which is the entire point of having these splits.

The rewrite makes each notebook answer **one question** with the **minimum code that can answer it**, and moves data volume *up the chain*: intro → simple load + metrics → splits → multi-month loops with the same one pattern they already know.

---

## 2. Code review findings (grounded in current files)

### Blockers / correctness

| # | Finding | Evidence |
|---|---------|----------|
| R1 | **Manifest URL is dead.** `MANIFEST_URL = "https://measurementlab.net/data/iqb/manifest.json"` returns an HTML 404 page (`requests.get(...).json()` now raises JSONDecodeError). Live URL: `https://measurementlab.net/data/stats/manifest.json` (verified 2026-09-08; returns `{"v": …, "files": …}`, includes new `stats.json` sidecars per entry, months 2009-01 → 2026-06). | Cells: 00:c7, 01:c4, 02:c4, 03:c4, 04:c4, 05:c4, 06:c4 |
| R2 | **Hardcoded example date.** 01's sample loads `'2025-09-01'` by hand; 06's loop assumes the newest month is first. Any future data gap breaks these silently. | 01:c8, 06:c7 |
| R3 | **"Check out our data catalog" link is 404.** `https://measurementlab.net/datasets` → 404 (verified). `https://measurementlab.net/data` → 200. | 00:c0 |
| R4 | **Typo bug in deleted code** (evidence of low polish, will die with 05): `filt["sample_count"].clip(upper=5000)` — should be `upper`. | 05:c9 |

### Dead code / cruft

- **Unused imports in every notebook**: `json` (module never used; only `requests.get(...).json()` calls), `mticker` (dead in 00, 01, 03, 05), `BytesIO`/`Path` (dead in 00 where nothing touches the loader), `matplotlib.pyplot` in 00 only sets `rcParams` and never plots. Verified by symbol scan.
- **`countrylookup.py`** — 9 KB, three-tier resolution (pycountry → network call → 249-code dict) to format `US` → `United States`. Only benefit is in chart labels; adds an install-time import, a network dependency, and per-notebook `sys.path` surgery.
- **Requirements/env drift**: `requirements.txt` (iqb + viz deps) vs `environment.yml` (python 3.12, same deps) vs `.python-version` (3.14) disagree. With the IQB library out of the tutorial, `requirements.txt` becomes just pandas/pyarrow/requests + matplotlib/seaborn/ipywidgets — same things as `environment.yml`, so both stay in sync trivially. Two manifests to maintain, but now for one trivial feature list.
- **00's "On-Disk Cache" section describes `./cache/v1/…` but 00 never touches the cache** — a reader cannot see the mechanism from the notebook that explains it. (Decision: the cache concept dies entirely, see §8.)
- **The hand-rolled cache adds ~20 lines for a tutorial.** All five notebooks 01–06 ship the same `_mem_cache` + `local_path.write_bytes` machinery. For a teaching set whose files are ~1–5 MB each, the whole cache layer is overhead — plain `pd.read_parquet(url)` is simpler and honest. (R5, new)

### Quality issues flagged by review (from team feedback, confirmed in text)

- Typos in 00:c0: "milliona or billions of raw rows of test **daate**".
- "Better direction" (00:c1) is confusing phrasing — it reads as "which way is the arrow pointing" rather than "which end is good". → "Better connectivity".
- "The most meaningful single-number summary in this dataset" (01:c9) is an unsupported claim about a dataset with known cleaning caveats.
- Country explorer (01) produces implausible rankings for some country/month combos — small-sample noise with no minimum-sample filter.
- 01's Download-vs-Upload scatter plots 200+ unlabelled points; the "which country is which" information cannot be recovered. Confirmed weak.
- 06's p25–p75 band section derives distribution claims from uncleaned data; misleading (e.g., band width driven by noise).
- ISP notebooks risk promoting providers from un-cleaned data (team checked several countries and found misleading results) — a caution that must be carried into the consolidated splits notebook.

---

## 3. Decisions adopted (feedback × action)

| Feedback item | Decision |
|---------------|----------|
| Change MANIFEST_URL to `…/data/stats/manifest.json` | **Applied** in all four notebooks |
| Clean up unused imports | **Applied** — each notebook imports only what it uses |
| 00 too thin → add sections | **Applied** — sample data, median/filtering recipes, interactive month picker (see §5) |
| 01 must become the simplest possible data-loading notebook (direct URL, no cache) | **Applied** — 3-cell loader; the same loader serves every notebook, including 03 |
| 02, 03, 04, 05: remove as standalone notebooks | **Consolidated** — their teaching content (what each split reveals) merges into ONE splits notebook (new `02`), so the concepts survive without the boilerplate |
| 06 = the cache example | **Replaced** — per review, the cache example adds no tutorial value; multi-month goes the direct way in 03; p25–p75 removed regardless |
| New notebook: monthly stats × IQB library | **Out of scope** — tutorial stays at metrics/distributions/splits level; IQB is one pointer line in 00 |
| "What is the monthly stats dataset and how to use it" framing | **Applied** |
| Interactive catalog: month dropdown that prints the dataset URL | **Applied** — replaces the month-list printout |
| Minimum sample count filter in country explorer | **Applied** — with a `[verify]` on `sample_count` availability (see §6.3) |
| "Look at a sample of the data" from 01 → 00 | **Applied** |
| Remove country-name lookup | **Applied** — plain ISO codes in dropdowns |

---

## 4. Target structure

New lineup (4 notebooks, no helper modules, no cache dir committed):

| # | File | One-sentence job | Complexity tier |
|---|------|------------------|-----------------|
| 00 | `00-introduction-and-catalog.ipynb` | What these data are, the four metrics + polarity, the splits catalog, interactive URL picker, first look at real rows | plain pandas: dicts + DataFrames |
| 01 | `01-country-explorer.ipynb` (rename from `01-country-level`) | Load a month **directly from the manifest URL**; the four metrics; **how the percentile distribution's shape** describes a country | pandas + widgets |
| 02 | `02-splits.ipynb` (new — consolidates old 02–05) | The same month through the country → subdivision → city → ISP lenses: **what each split reveals, with sample-count guardrails** | one loader, three interactive sections |
| 03 | `03-multiple-months.ipynb` (rework of `06-time-series`) | Loop over months with the SAME direct load as 01/02; track trends; keep exploratory-caveat framing | the simplest loader, applied N times |

Deletions: `02-asn-isp.ipynb`, `03-subdivisions.ipynb`, `04-subdivision-asn-drilldown.ipynb`, `05-cities.ipynb`, `countrylookup.py`.

> **Renumbering.** The final set is 00–03 with no gaps (old `06-time-series` → `03-multiple-months`); README/Binder links update in the same pass. Flag at review if a reviewer prefers a different numbering.

---

## 5. Notebook 00 — Introduction & data catalog (rewrite detail)

Goal: *"understand the dataset well enough to load it and ask a first question — in under five minutes."*

### 5.1 Restructure (markdown flow)

1. **What is the Monthly Stats dataset and how to use it** (replaces "How does M-Lab use the Monthly Stats Data")
   - We aggregate NDT results into monthly, percentile-based summaries at several geographic granularities. Instead of [typo-fixed: "querying millions or billions of raw rows of test data in BigQuery"], download a small file (~1–5 MB) containing p1–p99 per metric per geography per month.
   - Fix typos ("milliona" → "millions", "daate" → "data").
   - One sentence only, at the end: *the Internet Quality Barometer (IQB) project builds on this dataset — see the IQB publications if you want the composite-score view* (side note, not a tutorial promise).
2. **The four metrics** — keep the table, rename column "Better direction" → "Better connectivity" (values: ↑ Higher / ↓ Lower).
   - Add one plain-English line per metric: download = how fast pages/files arrive; upload = how fast you send; latency = responsiveness (gaming/video calls); loss = dropped packets (reliability).
   - Keep the polarity caveat block verbatim — it is the single most important concept in the dataset and notebook 01 will make it visible.
3. **The percentile distribution** — new, short, and deliberately plain-statistics: *each cell is not one number but a distribution summarized at nine percentiles (p1, p5, p10, p25, p50, p75, p90, p95, p99). p50 is the median user — the middle of the pack; p95 is where the top 5% of connections sit. No mean exists in this dataset — percentiles only.* Then the framing line that matters: *a wide p50→p95 gap is not automatically "inequality" — it is a statement about the **shape** of the distribution. Connections are not spread evenly: most tests sit in a band, and a minority run much faster or much slower. Being lower in the distribution is just different from being upper in it, and how different depends on the shape — where the median sits, how long the tail stretches, how flat or steep the middle is. A big gap means the top stretches far past the typical user; why (fibre rollouts, a data-centre-heavy country, small samples) is a question the data alone do not answer.* Notebook 01 makes the same point visible on real curves. Also bake the intuition in here, jargon-free: *line up all the tests in a month from slowest to fastest — p50 is the person in the exact middle, p95 is 95 out of every 100, near the front. Before believing any of it, ask how many tests went in: 100 tests wiggle, 100 000 tests are solid.* Sample count may be the single most important idea in this Tutorial for small countries (see §12.4).
4. **The splits** — keep the slice table, but rework the messaging around **what each split lets you learn**:

   | Split (slice prefix) | Adds dimension | What you can learn | Taught in |
   |---|---|---------|----------|
   | `by_country` | country | Cross-national benchmarking; how the distribution's shape differs across countries | 01 |
   | `by_country_subdivision1` | state/province | Geography of quality *within* a country (urban vs rural) | 02 |
   | `by_country_city` | city | City-level benchmarking; which cities punch above their country | 02 |
   | `by_country_asn` | ISP (ASN) | Provider competition within a country — **caution: un-cleaned, do not use to rank/promote ISPs** | 02 |

   Upload slices mirror the download slices. One line: *every split keeps the same nine percentiles per metric — only the "one row per what" changes.*
5. **Date coverage caveat** — rewrite to a concrete, checkable statement: *slices are published asynchronously; at any moment the newest month differs per slice (often by 1–2 months). The interactive catalog below derives the example month from the manifest, so it always shows real data. Rule of thumb: for multi-slice joins, use the newest month present in ALL slices you need.* — double-check wording with Simone before landing.
6. **How the notebooks load data** — one short section, one pattern: *every notebook in this set loads data the same way — read the manifest, grab a dataset URL, `pd.read_parquet(url)`. No local cache, no build step; each file is ~1–5 MB, so a fresh download per run is fast and keeps every notebook self-contained.* One line: "if you plan to pull many months repeatedly, a local cache directory makes sense — but for learning, direct reads are the honest default."

### 5.2 Code changes

- `MANIFEST_URL = "https://measurementlab.net/data/stats/manifest.json"`.
- Imports reduced to: `pandas`, `requests`, `ipywidgets`, `IPython.display`. No plotting in 00 (first look = tables) → drop `matplotlib`/`seaborn` entirely.
- **"Look at a sample of the data"** (moved from 01:c7–8): load the *newest* `downloads_by_country` month (derived from the manifest, never hardcoded), show `df.head()` and a one-line note on column naming (`download_p*`, `latency_p*`, `loss_p*`).
- **Pavlos' colab recipes** (ported with attribution): 3 runnable micro-examples —
  - median for one country: `df[df.country_code == "US"]["download_p50"]`,
  - filter by country list: `df[df.country_code.isin([...])][["country_code", "download_p50", "latency_p50"]]`,
  - filter by city on a city slice: `city[city.city == "London"]`.
- **Explore the catalog** — replace the month-list `print` with a second dropdown: `Slice` → `Month` → prints the exact dataset URL (from the manifest) and a one-click `pd.read_parquet(url).head()` preview. This turns the catalog from a readout into the entry point of notebooks 01 and 02.
- **Next Steps** — list only the three surviving notebooks (01, 02, 03) with one-line "what you'll be able to do".

---

## 6. Notebook 01 — Metrics & distributions (country explorer, rewrite detail)

Goal: *load a month in three lines and learn to read a country's quality from the **shape** of its percentile distribution.*

### 6.1 The simplest possible loader (replaces cells 2–6)

```python
import pandas as pd, requests
manifest = requests.get(
    "https://measurementlab.net/data/stats/manifest.json", timeout=30).json()

def month_url(slice_name, start):
    """URL for one month of one slice; start = 'YYYY-MM-DD' (first of month)."""
    for path, meta in manifest["files"].items():
        # cache/v1/{start_ts}/{end_ts}/{slice}/data.parquet
        if start in path and f"/{slice_name}/data.parquet" in path:
            return meta["url"]
    raise ValueError(f"{slice_name} / {start} not in manifest")

df = pd.read_parquet(month_url("downloads_by_country", "2026-06-01"))
```

`start` is passed in by the caller, never hardcoded inside the loader — notebook 00's catalog derives the newest month, and 01/02/03 obtain it the same way. Rationale: no cache dir, no `BytesIO`, no `Path`, no `_mem_cache`. A motivated reader can hold the whole loader in their head — that is the point of this notebook. (Exact form TBD when porting; keep it the shortest thing that works.)

### 6.2 Content: the four metrics, then the shape

Order matters — each section must *demonstrate* something the previous one only claimed:

1. **The four metrics, live.** Interactive country explorer (existing widget, kept): month + metric + top-N, now **sample-count-filtered** (see 6.3). One question per metric, e.g. "who has the fastest typical download?" / "who has the most reliable connection (lowest loss)?" — so each widget run is an answer, not a chore.
2. **The shape: percentile curves.** The core new section. A country multi-select + metric dropdown plots the *percentile curve* (p1→p99) for 4–5 countries on one axis. Teaching points, each visible in the plot:
   - how to read the curve: it is the distribution drawn percentile-by-percentile — the left edge is the slowest ~1%, the middle is the median, the right edge is the fastest ~1%. **Steep means few connections spread over a wide speed range** (the long tail of very fast connections near p90–p99 shows up in almost every country); **flat means many connections packed into a narrow band** (where the bulk of users actually live);
   - **lower on the curve ≠ "worse off".** Where the curve sits low and flat is just where most of the distribution's mass is; the top is a thin minority. Shape is descriptive: a country's curve can be short and tight (most people similar) or stretched at the top (a minority far out front) — neither statement alone says anything about fairness;
   - **median vs mean**: p50 is the robust "typical" number; the mean cannot even be computed from this dataset — the curve *is* the honest summary;
   - **latency/loss curves slope the other way** — the polarity inversion made visible: high percentile = low latency; the label on the axis flips.
3. **Skew at a glance — the p95/p50 shape gauge.** One-cell view: bar chart of `download_p95 / download_p50` per country, top + bottom 10. A ratio near 1 = the distribution's top sits close to its middle (tight shape); > 3–4 = the top stretches 3–4× past the median (long right tail). Immediately surprising, zero new dependencies. Label it clearly as a *shape* gauge, not an index of anything: it summarizes skew, and skew is descriptive — the same ratio can come from very different underlying populations, and it does not by itself say anyone is "better off" or "worse off". (Guards: sample-count filter.)
4. **(Super-power) Percentile sweep.** Metric dropdown + percentile slider (p5→p99); the top-N bar chart re-ranks countries live. Answers "do the rankings hold at p50 vs p95?" — typically they do not, and the user *sees* why via section 2's curves. This is the notebook's demo moment.

### 6.3 Removals / fixes

- `countrylookup.py` import + `sys.path` surgery → delete. Plain ISO codes in dropdowns; one markdown line noting "country codes are ISO 3166-1 alpha-2 (US, DE, ...)".
- "Look at a sample of the data" section → moved to 00 (§5.2).
- "It is the most meaningful single-number summary in this dataset." sentence → deleted.
- **Download vs Upload Scatter** section → deleted (unlabelled points, per feedback).
- **Minimum sample count** — new `IntSlider` (e.g. 100–50 000, default 1000) applied to the country explorer's ranking. `[verify]` that `downloads_by_country` carries a `sample_count` column (the ASN/city slices do; the country schema may differ — check one parquet's columns during porting). Fallback if absent: filter on `downloads_by_country_asn` aggregated sample count per country, or document the caveat and gate on n-largest — decide with Simone during porting.
- Default month = newest month from the manifest (never hardcoded).
- Dead imports (`json`, `mticker`) and unused `sns`/`plt` setup trimmed to what the kept plots use.

---

## 7. Notebook 02 — The splits (new, consolidates old 02–05)

Goal: *one month, four lenses — country, subdivision, city, ASN — and what each lens can and cannot teach you.*

This notebook is the *conceptual* heir of the four deleted notebooks, without their duplication: one loader, one interaction pattern, three sections.

### 7.1 Structure

1. **The splits story (markdown).** Every slice holds the same four metrics and nine percentiles; only "one row per what" changes. Frame the central question the entire notebook answers: **"Where does internet quality vary — between countries, within a country, or between providers?"** Answering it = using the splits, which is exactly what they are for.
   - Reuse 00's learn-table (§5.1.4) so this notebook and the catalog agree verbatim.
2. **Subdivisions: geography within a country.** Interactive section (min-sample slider + metric): pick a country → its states/provinces as a ranked bar chart.
   - What you learn: the *range* within a country (e.g. capital region vs periphery), urban/rural gradient, and that a country's median can hide enormous internal spread.
   - Teaching beat: compare Germany's flat subdivision range next to Brazil's wide one — the same "shape" vocabulary from 01, applied inside one country.
3. **Cities: benchmarking below the country level.** Same interaction at city granularity, min-sample filter prominent (small towns are noise).
   - What you learn: which cities punch above their country's median; useful for "is my city typical?"
4. **ASNs: the provider lens — with a warning.** Same interaction at country×ASN.
   - What you learn: within a country, does provider matter more than region? (Price/plan differences live at this split.)
   - **Standing caution text (from team review):** *these data are not cleaned; small-sample ASN rows can mislead, and we are not in the business of ranking or promoting ISPs. Always set a high sample-count threshold, and treat any provider comparison as indicative, never as a recommendation.* The min-sample slider defaults high here (e.g. 2 000).

### 7.2 Demo / super-power for this notebook

- **"Between or within?"** one-cell view: for a chosen country and metric, plot the *country median* as one vertical line and each subdivision/city's median as points around it. If the points are tighter than the spread across countries on the same axis (from 01), the spread sits *between countries*, not within — or vice versa. This single figure is the payoff of having the splits, and no raw-BigQuery audience could reproduce it as cheaply.

### 7.3 Code notes

- Reuse notebook 01's 3-line loader verbatim (copy the cell; notebooks must stay self-contained for Binder).
- `[verify]` column names per slice (`subdivision1` naming; ASN slices have `asn` + `sample_count`; city slices have `city` + `sample_count`) — detect at porting and normalize in one visible cell, no runtime gymnastics.
- No ASN-name lookup (RIPE) — labels are `AS12345`; the RIPE-name machinery dies with old notebook 02. *(If reviewers want names back, a static in-cell dict, no network.)*

---

## 8. Notebook 03 — Multiple months, the direct way (rework of 06)

Keep the multi-month idea; change the load path. No caching machinery, no IQB-library usage — the notebook does exactly what a reader already knows from 01/02, in a loop.

- **Title/framing**: "Tracking trends over multiple months" — explicit opening text: *this notebook downloads each month's file directly, exactly like notebooks 01–02, and stacks them into a time series. Nothing is cached or pre-built. For a handful of months this is the simplest possible path; if you ever need dozens of months repeatedly, a local cache is the optimization to reach for — not needed here.* Also keep the honesty line: data are **not cleaned** — *treat these charts as exploratory; do not publish claims from these numbers yet*.
- **Mechanism section (the point — one pattern, applied N times)**:
  ```python
  months = ["2025-01-01", "2025-02-01", ...]           # from 00's catalog: pick N most recent

  frames = [pd.read_parquet(month_url("downloads_by_country", m))
            .assign(month=pd.to_datetime(m))
            for m in months]
  ts = pd.concat(frames, ignore_index=True)
  ```
  Then: filter to a few countries, plot the four metrics over time. That is the entire loading story — the same `month_url` from notebook 01, one `concat`, no new concepts. A one-line note that `ts` is ready for any pandas time-series operation reinforces transfer.
- **Keep from old 06**: the 4-panel median view (download/upload/latency/loss over time, multi-country selection optional).
- **Removed**: the p25–p75 band section (misleading on uncleaned data); the dependency-check/`MANIFEST_URL`/cache loader cells (the `month_url` stub replaces them); dead imports.
- **Month-list source**: derive the N most recent months from 00's catalog pattern (descending `start` order), never hardcoded.
- **Review gate**: quick review with Simone that the "most recent N months" derivation is right (e.g. mixed-slice freshness — see 00's date-coverage caveat) and the download-per-month loop is acceptable as the tutorial's default pattern.

---

## 9. "Super-powers" — modern learning theory applied

The rewrite is organized around one principle: **give a user an ability in the first minute, and let them discover the machinery only when they want it.** Concretely:

| Principle (learning science) | How the notebooks apply it |
|------------------------------|----------------------------|
| Immediate feedback loops | Every section is an interactive widget whose state is the answer; no "run analysis, read output" ceremony |
| Worked examples → transfer | 01 opens with one fully worked question ("Is the US median download faster than Germany's?"), then hands over the same controls to the user's own question |
| Reduced extraneous cognitive load | Duplicated setup killed; one job per notebook; no network-dependent name lookups; jargon defined only when used |
| Result-first / progressive disclosure | 00 = see the data, 01 = read distributions, 02 = exploit the splits, 03 = scale across months, same loader all the way |
| Retrieval practice | One 2-line "check yourself" cell per notebook (e.g., "why is latency_p95 the *fastest* 5%?") with a hidden answer — cheap, keeps the polarity caveat from evaporating |
| Authentic tasks | Each notebook frames a real question ("whose distribution stretches furthest past its median?", "is quality spread within or between countries?") rather than "let's plot the columns" |

**The super-power demos** (each = ≤1 notebook cell, defensible with sample-count guards):

1. **Read the shape** (01) — percentile curves for any 5 countries on one axis; the steep-tail / flat / inverted-latency shapes become instantly recognizable, and stay recognizable for a lifetime of reading speed-test charts.
2. **Percentile sweep** (01) — slider p5→p99 re-ranks countries live; immediately shows *which* rankings are robust and why "the median" is the honest headline number.
3. **The p95/p50 shape gauge** (01) — one number that says how far the top of a country's distribution stretches past its median; set it next to *median rank* and watch the two disagree — shape is its own axis, not a proxy for "who's fast".
4. **"Between or within?"** (02) — country median vs its regions vs its cities on one plot; the splits exist precisely to make this decomposition possible.
5. **One month, every lens** (02) — country → city → provider for one country in three ranked views; the catalog table from 00 becomes muscle memory for which slice answers which question.

---

## 10. Rollout & verification

### Porting order
1. 00 rewrite (new manifest URL, typos, interactive month picker, sample section, Pavlos recipes, splits learn-table) — unblocks everything else.
2. 01 rewrite (minimal loader, sample-count filter, remove lookup/scatter/sample; add percentile curves, shape gauge, percentile sweep).
3. 02 new (three lens sections + "between or within" demo; consolidate old 02–05 content).
4. Delete old 02–05 + `countrylookup.py`; update README (new lineup 00–03, `/data/stats/` URL, Binder links) + requirements (drop the `git+…/iqb.git` pin and pycountry mention; align environment.yml / .python-version).
5. 03 rework as direct multi-month loop → quick Simone review of most-recent-N-months derivation.
6. Final imports/URL grep sweep.

### Acceptance checks
- No notebook imports the `iqb` library and `MANIFEST_URL` appears zero times in the surviving files (grep) — all four use the same direct `month_url` + `pd.read_parquet` pattern.
- Each notebook runs end-to-end in a clean env (`python=3.12` + `requirements.txt`), `Restart & Run All`, no errors.
- 01: percentile sweep visibly re-ranks countries between p50 and p95.
- 01/02: min-sample slider demonstrably removes a tiny-sample geography.
- 00: month dropdown prints a URL that resolves (HTTP 200) and loads with `pd.read_parquet`.
- 03: `Restart & Run All` produces a 4-panel trend chart for N months with no writes outside the notebook directory; re-running is clean because nothing persists.
- Unused-import scan script passes (ast per code cell).
- README links point at existing files; catalog link in 00 points at a 200 URL (`https://measurementlab.net/data`).
- **Tutorial dry-run** (§12.5): a non-statistician facilitator can run 00→03 in ≤2 h reading only the notebook text; every interactive chart in 01–03 carries a one-line plain-language caption ("reading it aloud").
- **Low-sample honesty**: any country/month/geography whose sample count is small shows the caveat *in the chart caption*, not only in a warning box far above.

### Open items for the team
- [ ] Confirm `sample_count` exists in `downloads_by_country` (fallback strategy if not — §6.3).
- [ ] Simone: validate 00's "date coverage caveat" rewording and 03's most-recent-N-months derivation.
- [ ] Pavlos: sign off on his colab recipes ported into 00.
- [ ] Simone/Pavlos: approve the standing ISP-caution text in 02 (§7.1.4) and the "between or within" demo (§7.2).
- [ ] Confirm final notebook numbering 00–03 (old `06-time-series` → `03-multiple-months`).

---

## 11. Exploratory — restructuring the data for simpler access

> **Status: exploratory sketch, not a commitment.** Everything in §4–§10 ships without any of this. This section maps the design space of "what if the dataset itself made the tutorial patterns trivial," weighs the options, and ends with a concrete technical proposal. Nothing here changes the current files; it is groundwork for a follow-up discussion with the pipeline team.

### 11.1 Why the current layout fights the tutorial

The tutorial loader in §6.1 works, but it encodes three kinds of friction that live in the data layer, not the teaching:

1. **The manifest is a flat dict keyed by path strings.** The loader is an O(n) substring match over ~2 520 `cache/v1/{ts}/{ts}/{slice}/data.parquet` keys, and the *date* and *slice* are recovered by re-parsing the path convention (`parts[2]`, `parts[4]`). "What months exist for slice X?" is a text-matching exercise, not a query.
2. **One month = one download, every time.** A 12-month trend (notebook 03) is 12 separate ~1–5 MB fetches plus a `pd.concat`. Fine for a handful of files; it does not scale as a *pattern* to "all of 2025" or "since 2019."
3. **There is no logical view.** The dataset is *physically* 2520 files with dates encoded in paths, but *logically* it is one table: `(month × slice × geography) → 9 percentiles × 4 metrics`. Every consumer re-invents the mapping from "I want France's download median in June 2026" to a URL. The `[verify]` schema notes in §6.3/§7.3 are symptoms: consumers must discover per-slice column names at runtime.

One incidental finding from this review: the manifest's `url` fields currently point at a `storage.googleapis.com/mlab-sandbox-iqb-us-central1/…` bucket. For a public tutorial this is fine today, but any "stable endpoint" story should also stabilize that prefix (bucket rename, CDN in front) so a URL you publish keeps working for years.

### 11.2 The good news: the data are small

Before designing anything, size matters, and this dataset is *small*:

- country level: a few hundred rows per month × 210 months ≈ **tens of thousands of rows** in total,
- city level: thousands of rows per month × 210 months ≈ **a few million rows** at most,
- even the whole catalog is ~2 520 files at ≤ ~5 MB each ≈ **low single-digit GB, uncompressed, for everything M-Lab has ever published here**.

A full-history, all-slices merged file is therefore not a Big Data problem — it is a *plumbing* problem. That reframes every option below: the bottleneck is access ergonomics, not storage or query performance.

### 11.3 Restructure / abstraction options (with tradeoffs)

| # | Idea | What gets simpler | What it costs |
|---|------|-------------------|---------------|
| A | **Additive catalog-as-table** — publish the manifest's contents as a queryable `catalog.parquet` (one row per file: slice, start_date, end_date, url, sha256, num_rows, columns, published_at) at a stable URL, regenerated each month | tutorial loader becomes a 2-line filter (`catalog.query("slice == … and start_date == …").url`); DuckDB can join the catalog to `read_parquet(url)` for ad-hoc multi-month queries; versioned by the existing `v` field | One more artifact to generate; catalog must stay schema-stable; does not reduce file count for trends |
| B | **Merged history per slice** — one `history/downloads_by_country.parquet` etc., appended monthly (country: ~50k rows total; city family: a few MB) | Notebook 03 becomes one `pd.read_parquet(url)` + `WHERE month BETWEEN…`; "all history" queries become routine; cache-free tutorial stays cache-free | Pipeline must rebuild monthly (cheap here); storage roughly doubles for derived copies; files are no longer 1:1 with the cache layout consumers rely on; freshness lags one publish cycle; schema must be frozen (which is arguably a *good* forcing function) |
| C | **Wide monthly bundle** — one file per month containing every split in a long format (a `level`/granularity column instead of separate slices) | The catalog quiz disappears; "which split do I want" becomes `WHERE level = 'city'`; one URL per month covers all examples | Files get wider and NULL-heavy (a country row has no `city`); mixed granularity invites users to compare rows that are not comparable; duplicates the existing 12-slice publishing pipeline for marginal teaching gain |
| D | **Hive-partitioned family + DuckDB httpfs globs** — *do nothing*; the path layout is already a hive-ish scheme, and DuckDB's httpfs can fetch `read_parquet('https://…/cache/v1/*/*/downloads_by_country/data.parquet')` with remote globs | Zero new artifacts; ad-hoc cross-month queries in one statement | Every included file costs at least a footer/metadata fetch — across 210 months that is 210+ HTTP requests per query (mitigated by DuckDB's parallel fetch + metadata caching, but the partition dirs are *timestamp-string* named, not month-named, so globs are awkward); great for power users, wrong default for a Binder tutorial |
| E | **Published DuckDB database** — ship a single `.duckdb` file (refreshed monthly) containing the merged tables | The strongest single "logical endpoint": one file, SQL, joins, windows, all history | Binary format ties clients to a DuckDB version; pandas-only users can't read it natively; storage format becomes a contract. Keep as an *optional* accelerator, never the canonical artifact |

### 11.4 Proposed technical solution (stable logical endpoints that grow monthly)

If the team wants the tutorial patterns to be *naturally* simple, the cheapest high-leverage move is **additive, not restructural**:

1. **Keep the per-month parquet files as canonical storage.** They are append-only (a new month is just new files — no rewrites), backward-compatible with every existing consumer (IQB library, curl users, the current notebooks), and they already form a workable partition scheme. Changing them buys nothing we cannot get additively.

2. **Publish the manifest-as-a-table at a stable URL, alongside the JSON, each month:**

   ```
   https://measurementlab.net/data/stats/catalog.parquet
   ```
   | slice | start_date | end_date | url | sha256 | num_rows | columns | published_at |
   |-------|-----------|---------|-----|--------|----------|---------|--------------|

   The pipeline already computes `sha256` and emits a `stats.json` sidecar per file; a tiny aggregation job turns those into this one catalog row-set. Schema frozen from day one; the existing `v` field versions it. The tutorial loader then degrades to:

   ```python
   catalog = pd.read_parquet("https://measurementlab.net/data/stats/catalog.parquet")
   url = catalog.query("slice == 'downloads_by_country' and "
                       "start_date == '2026-06-01'").url.iloc[0]
   df = pd.read_parquet(url)
   ```

   **DuckDB as the logical query layer**: because the catalog is a table, DuckDB can also drive file lists from it —

   ```sql
   SELECT month, download_p50 FROM (
       SELECT * FROM read_parquet(
           (SELECT list(url) FROM read_parquet('…/catalog.parquet')
            WHERE slice = 'downloads_by_country'
              AND start_date >= '2025-01-01'))
   ) WHERE country_code = 'US' ORDER BY month;
   ```

   — i.e. "logical querying across the manifest" without moving a single data file. `httpfs` globbing (option D) can remain the power-user path; nothing forces it on the tutorial.

3. **Optionally, publish a "tutorial tier" of merged history files** (option B) once anecdotes show 03 wants them: `history/{slice}.parquet`, rising 24 months by default, `?full=1` for all history. Country family is ~50k rows; the city family is a few MB — the entire pipeline cost is one monthly rebuild job over small tables. This is the only option that is a true restructure, and only in the derived layer; canonical files stay untouched.

4. **Endpoint stability play**: with the catalog as the only mutable pointer, all *data* URLs can stay immutable and content-addressed (the sha256s already exist). The pattern is: *indexes change, data never does*. As months land, the catalog and (optionally) history files grow in place; every consumer query written against the *names* (`catalog.parquet`, `history/…`) keeps working unchanged. (Also the moment to move the bucket prefix off `mlab-sandbox-…` — the catalog makes a prefix migration a one-line change instead of a link-rot sweep.)

5. **What the tutorial gains** (if 2–3 land):
   - §6.1's string-matching loader becomes a filter (and `[verify]` column probing disappears — `columns` is in the catalog);
   - notebook 03's loop becomes one read (history) or one SQL statement (DuckDB);
   - a new natural super-power: *"ask a question across all 17 years of monthly stats in one statement"* — a legitimate wow-moment for a data-literacy audience, and it is teaching SQL-on-parquet, not a proprietary API.

### 11.5 Risks / open questions (for the pipeline discussion)

- **Schema freeze**: merged/history files force a locked schema across months. This is a feature for the tutorial but a governance decision for the pipeline — does M-Lab commit to a v1 schema for `downloads_by_{…}` columns?
- **Freshness semantics**: derived artifacts (catalog, history) lag the raw files by one publish cycle; the 00 date-coverage caveat (§5.1.5) must describe the *catalog's* freshness, not just the slices'.
- **Egress/cost**: merged rebuilds mean monthly restatements of a few GB — trivial on GCS, but should be measured once.
- **DuckDB version drift**: if option E ever ships, pin the engine; parquet (+ catalog) keeps every other consumer independent of it.
- **Nothing here is required** for the 00–03 rewrite in §§5–8. The right sequencing is: ship the tutorial on today's manifest, prototype the catalog in parallel, and only adopt option B/C if the notebook feedback says the trend examples are still clunky.

---

## 12. Review pass: developing-country audience × statistical literacy × tutorial intent

> Status: **binding guidelines** for the rewrite. This is the audience test of §§5–8: the person most likely to *need* these notebooks is a researcher, regulator, or student in a country with few M-Lab tests and no stats training. Everything here either upgrades how §§5–8 are written or is called out as already good.

### 12.1 What this audience actually wants (and where the plan stands)

People in developing countries bring specific questions. Test each desire against the current plan:

| Desire | Served by | Status |
|---|---|---|
| **"Where does my country stand in the world?"** | 01 explorer + percentile sweep ("does the rank hold at p95?") | Served — but framing must be *position*, not praise (see 12.3: kill "Top N" labelling) |
| **"What is normal / typical for my country?"** | 01 percentile curves (flat vs stretched) | Served — the shape story is exactly this |
| **"Is my region or city different from the rest of my country?"** | 02 splits, "between or within" | Served |
| **"Is my ISP treating me fairly?"** | 02 ASN lens | Partial — ranking/promotion stays off-limits (un-cleaned data); teach *self-checking one provider*, not leaderboards (12.4) |
| **"Are things getting better or worse?"** | 03 trends | Served |
| **"Can I trust these numbers?"** | sample-count filters + caveats | **Gap — today it is a technical guard; must become a taught idea** (12.4) |
| **"Is there any data for MY country at all?"** | 00 catalog + month dropdown | Served — sparse/missing months are visible here; make "is my country even here?" a first-class question |
| **"Can I redo this myself afterwards?"** | notebooks are self-contained, copyable | Served by design — keep it; it is the whole point of the direct loader (§8) |

### 12.2 Statistical-literacy: one plain-language dictionary, frozen in notebook 00

Some participants have no stats background; several readers will translate the material into another language. Fix **exactly one plain-language vocabulary in 00** and never add jargon after it:

| Term | Plain dictionary (00 only) |
|------|----------------------------|
| Percentile | *Line everyone up.* Line up all tests slowest → fastest; p50 = the one in the exact middle; p95 = 95 of every 100, near the front |
| Median | "the middle person's experience" — never call it "average"; there is no average in this dataset |
| Distribution / shape | "how the line spreads": *flat line = most people similar; a line that climbs steeply at the end = a few people far faster (or slower) than the rest* |
| Polarity inversion | *For latency and loss, lower is better — so the data flip the percentiles to keep "higher = better" everywhere.* Show ONE worked pair of countries in 00: same chart, two countries, one plain sentence reading each |
| Sample count | "how many tests went in." *100 tests wiggle; 100 000 are solid. Check the count before believing a rank.* |
| Skew (in §6.2.3) | say "stretched to one side" in all notebook prose; keep "skew" in code comments only |

**Every interactive chart gets a one-line "reading it aloud" caption** — a plain sentence under the plot that states the finding with no jargon ("Sweden's middle user gets about 90 Mbit/s; only 5 of 100 saw more than 200"). Sentence templates live in notebook text so communities can translate them; participants should be able to describe their chart in one breath, in their own language.

### 12.3 Hard data realities for low-sample countries (the tutorial must be true to these)

- **Small countries are exactly where the data are thinnest** — the months, cities, and ISPs they care about are the likeliest to be missing or tiny-sample, and their *rankings* are the likeliest to wiggle. So sample count is not a footnote: it is in 00's primer (§5.1.3), the sliders are prominent in 01/02, **and the caveat appears in the chart caption whenever the count is low** — not only in a distant warning box (§10 acceptance).
- **Labelling**: all "Top N" titles become **"Highest N" / "Where X ranks"**. Ranking a country must read as *position*, not praise — the same chart that flatters one reader stigmatizes another when the numbers are noisy.
- **Latency and loss matter more, proportionally, when bandwidth is scarce.** The polarity inversion therefore deserves the worked pair (12.2), not just a warning block.
- **The ASN lens is the most-requested view for this audience** — regulators and journalists want provider information more than anything else. Our caution is about *public ranking/promotion from un-cleaned data*, which stays. The tutorial response is to teach the safe form: *one provider's numbers over time, with a high sample floor* — self-checking for a regulator's own use, not a leaderboard anyone publishes.
- **Tutorial logistics are part of the design**: a pre-rendered HTML/Colab copy of every notebook so participants who cannot run Jupyter can still follow along; the notebook text carries the lesson either way. The direct-download choice (§8) is load-bearing here — every artifact stays ~1–5 MB, so the tutorial runs on one modest laptop over a shared connection.

### 12.4 Tutorial intent — tighten and simplify around one session

Reframe the four notebooks as ONE station-based tutorial (~2 h):

| Time | Station | Participant leaves able to… |
|------|---------|-----------------------------|
| 15' | 00 — the data, the line-up, the catalog | say what the numbers mean; state which months/slices exist for their country |
| 35' | 01 — their country's shape + median position + percentile sweep | read their country's curve aloud in one plain sentence; say whether its rank holds at p95 |
| 35' | 02 — their country's regions, cities, and one provider self-check | answer "where does the spread sit: between countries or within mine?"; run one ISP self-check |
| 25' | 03 — multi-month trend for their country | produce one trend chart they can describe aloud |

Simplify amendments locked in by this review:
- **One interaction pattern per station.** Loader cell (reused from 00/01) → one widget → one chart → one "reading it aloud" caption. Anything needing a second interaction is a new station or gets cut. §6.2's flow (explorer → curves → shape gauge → sweep) stays — it is one coherent station, not four.
- **Cut nothing conceptual; cut everything ceremonial.** Notebooks have no dependency checks, no unused imports, no helper modules (§2 findings) — ceremony is what makes notebooks intimidating, not the stats.
- **The sweep stays as the demo moment** — it is the single best answer to a developing-country researcher's "which number should I even trust?" because it shows ranks moving live.
- **Sample-count first**: every ranking chart states its test count in the caption; "how many tests went in" is taught in 00 before any plot appears in 01.

### 12.5 Success measures for this review

A participant with **no stats background** can, at the end of the tutorial: (1) describe their country's curve in one plain sentence; (2) state whether its rank holds at p95; (3) name one region/city oddity in their own country; (4) say whether their country is trending up or down. A participant **with data skills** can point at exactly which cells to copy to redo the whole thing for a different country, slice, or month.

Acceptance additions (already in §10): tutorial dry-run by a non-statistician facilitator in ≤2 h with only the notebook text; caption presence low-sample honesty; "Highest N / Where X ranks" phrasing; plain-dictionary freeze in 00 with no new jargon anywhere after it.