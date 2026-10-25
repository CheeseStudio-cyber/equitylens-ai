# EquityLens AI

A Python, Pandas, Plotly and Streamlit research dashboard for DBS, OCBC and UOB, covering financial years 2023–2025. Milestone 1 provides company selection, six KPI cards, historical charts, peer comparisons and downloadable source references. No RAG or investment recommendation engine is implemented.

## Run locally

Requires Python 3.11+ (tested with Python 3.14.2).

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).

```bash
python -m pytest -q
python scripts/verify_sources.py
```

The first command tests the data contract, missing-data calculations, charts and Streamlit interactions. The second optionally audits the supplied local PDFs against stored hashes and checks page bounds; it requires the ignored `data/raw/` PDFs. Tests and the dashboard work without PDFs or network access after installation. `requirements-lock.txt` records the exact development environment versions tested on Python 3.14; for that environment install it before installing the editable project.

## Repository structure

```text
app.py                       Streamlit controls and presentation
src/equitylens/
  catalog.py                 Company/year scope, metric definitions, units
  data.py                    CSV loading, schema/provenance validation, gap expansion
  analytics.py               Pure KPI formatting and comparison calculations
  charts.py                  Plotly chart construction
scripts/verify_sources.py    Optional local PDF identity and page audit
data/
  metrics.csv                Long-form observations; checked into Git
  sources.csv                Source document registry; checked into Git
  raw/                       Original supplied annual reports; PDFs ignored by Git
tests/                       Contract, analytics, chart and UI tests
pyproject.toml               Package metadata and dependency ranges
requirements-lock.txt        Tested development dependency snapshot
```

## Data schema

`metrics.csv` has one row per `(company, year, metric)`. Empty numeric fields mean missing; zero always means a verified zero.

| Field | Meaning |
| --- | --- |
| company | Stable identifier: DBS, OCBC or UOB |
| year | Financial observation year: 2023, 2024 or 2025 |
| metric | Identifier from `catalog.py` |
| value | Finite numeric value, or empty when not verified |
| unit | `SGD million` or `%`, fixed for each metric |
| source_id | Reference to `sources.csv`; required for populated values |
| source_page | One-based PDF page number, required for populated values; not the printed page number |
| source_note | Original label, reporting basis, rounding or comparative explanation |
| missing_reason | Required when value is empty; empty when populated |

`sources.csv` has `source_id`, `company`, `year` (the **report** year), `title`, `local_path`, `url`, `sha256` and `verified_on` (ISO date). Local file paths point to the supplied PDFs, whose contents were inspected on 2026-10-25. URLs are blank because the supplied files were used directly; public download locations have not been independently established. File hashes preserve document identity without distributing the reports. Verification here means checking figures against the supplied report text; it is not an independent audit or authentication of publisher origin.

A later report can supply an earlier year's comparative. A source must match the company and its report year must be at least the observation year. Notes identify those comparatives. Do not silently mix original and restated figures: document any replacement and its reporting basis. The present schema stores one chosen value per metric/year; a future version can add explicit revisions if multiple vintages need to coexist.

### Metrics and current coverage

- Net profit attributable to shareholders: statutory/reported profit, including one-off expenses. DBS adjusted headline profit is deliberately excluded.
- Total income: consolidated income statement total.
- Total assets: consolidated year-end balance sheet total. UOB values currently come from rounded financial highlights, converted from SGD billion to million; notes retain that reduced precision.
- ROE and NIM: reported full-year percentages (e.g. `2.15` means 2.15%, not 0.0215). DBS ROE is a reported headline ratio on an adjusted basis; it is not recomputed from statutory profit. DBS NIM uses the Group basis including markets trading.
- CET1 ratio: reported ratio. Transitional and fully phased-in capital ratios differ; these observations use reported ratios and note changes following final Basel III reforms.

There are **51 verified observations out of 54**. UOB total income for all three years remains explicitly missing pending further table verification. All OCBC observations use their respective year’s annual report: financial highlights on PDF page 4 (2023 and 2025) or 6 (2024), and full-year NIM from the Management Discussion and Analysis overview on PDF page 96 (2023) or 98 (2024 and 2025). UOB 2023 reported profit and ROE use its 2024 comparative table rather than its 2023 core-performance highlights.

Reported definitions, rounding and regulatory bases limit peer comparability. Source notes are part of the dataset, not optional commentary. Monetary charts display SGD million; ratio changes are percentage points. Monetary YoY changes require the immediately preceding year and a nonzero denominator. Missing observations never become zero, interpolate or fall back to a different year. Historical charts retain gaps; peer tables retain missing companies and bar charts omit their unavailable bars.

## Architecture and incremental milestone

1. **Data contract:** define stable metric identifiers and normalized units; keep observations separate from document metadata. Long-form CSV is reviewable in Git and supports new metrics without changing table columns.
2. **Validation and calculations:** isolate Pandas loading and pure functions from Streamlit. Reject duplicate observations, invalid units, non-finite values and missing/mismatched provenance. Reindex the research scope so omitted rows appear as explicit missing observations.
3. **Dashboard:** use shared metric definitions for KPI cards and single-unit charts. Keep company selection separate from the fixed three-bank peer universe. Show errors for invalid files and informative empty states for valid missing data. No data caching at this scale, so edits appear on rerun.
4. **Verification:** automated contract and UI tests plus an optional PDF hash/page audit. Synthetic values used in calculation tests never enter production CSVs.

To add a verified figure, inspect the original table and footnotes, check its company/year, group basis and units, register the document and hash, and enter the value with page and source note. Clear `missing_reason` only after verification. Run the tests and optional PDF audit. Never populate a figure from memory, an unreviewed extraction, or a generated answer. The loader enforces required provenance fields; human review establishes whether the cited table actually supports the number.

Stable source IDs, file hashes and page references provide a seam for future document ingestion and retrieval. A later RAG module can link chunks to those IDs and pages without changing the dashboard's calculation layer. Embeddings, vector stores, chat and generated financial claims are outside this milestone.
