"""Load and validate source-backed observations; never impute financial figures."""
from pathlib import Path
import re

import pandas as pd

from equitylens.catalog import COMPANIES, METRICS, YEARS

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
METRIC_COLUMNS = ["company", "year", "metric", "value", "unit", "source_id",
                  "source_page", "source_note", "missing_reason"]
SOURCE_COLUMNS = ["source_id", "company", "year", "title", "local_path", "url",
                  "sha256", "verified_on"]


class DataValidationError(ValueError):
    """The dataset violates its provenance or financial schema."""


def _require(condition, message):
    if not condition:
        raise DataValidationError(message)


def validate(metrics: pd.DataFrame, sources: pd.DataFrame) -> None:
    _require(set(METRIC_COLUMNS) <= set(metrics.columns), "Missing metric columns")
    _require(set(SOURCE_COLUMNS) <= set(sources.columns), "Missing source columns")
    _require(not metrics.duplicated(["company", "year", "metric"]).any(), "Duplicate observations")
    _require(not sources.source_id.duplicated().any(), "Duplicate source IDs")
    for _, source in sources.iterrows():
        _require(source.company in COMPANIES and source.year in YEARS, "Invalid source company/year")
        _require(all(pd.notna(source[c]) and str(source[c]).strip() for c in
                     ["source_id", "title", "sha256", "verified_on"]), "Incomplete source metadata")
        _require(pd.notna(source.local_path) or pd.notna(source.url), "Source needs a path or URL")
        _require(bool(re.fullmatch(r"[a-f0-9]{64}", str(source.sha256))), "Invalid SHA256")
        _require(not pd.isna(pd.to_datetime(source.verified_on, errors="coerce")), "Invalid verification date")
    registry = sources.set_index("source_id")
    for _, row in metrics.iterrows():
        _require(row.company in COMPANIES and row.year in YEARS, "Invalid observation company/year")
        _require(row.metric in METRICS, "Unknown metric")
        _require(row.unit == METRICS[row.metric][1], "Incorrect metric unit")
        if pd.isna(row.value):
            _require(pd.notna(row.missing_reason) and bool(str(row.missing_reason).strip()),
                     "Missing value requires missing_reason")
        else:
            _require(pd.api.types.is_number(row.value) and float('-inf') < row.value < float('inf'),
                     "Value must be a finite number")
            _require(pd.isna(row.missing_reason), "Populated value cannot have missing_reason")
            _require(row.source_id in registry.index, "Value requires a registered source")
            page = pd.to_numeric(row.source_page, errors="coerce")
            _require(pd.notna(page) and float(page).is_integer() and page >= 1,
                     "Value requires a positive one-based PDF page")
            _require(pd.notna(row.source_note) and str(row.source_note).strip(), "Value requires source note")
        if pd.notna(row.source_id):
            _require(row.source_id in registry.index, "Unknown source ID")
            source = registry.loc[row.source_id]
            _require(source.company == row.company and source.year >= row.year,
                     "Source company/year mismatch")


def load_data(data_dir: Path = DATA_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    metrics = pd.read_csv(data_dir / "metrics.csv")
    sources = pd.read_csv(data_dir / "sources.csv")
    validate(metrics, sources)
    # Reindex the entire research scope: absent rows become explicit gaps, never zeros.
    index = pd.MultiIndex.from_product([COMPANIES, YEARS, METRICS], names=["company", "year", "metric"])
    metrics = metrics.set_index(["company", "year", "metric"]).reindex(index).reset_index()
    metrics["unit"] = metrics.metric.map(lambda m: METRICS[m][1])
    metrics.loc[metrics.value.isna() & metrics.missing_reason.isna(), "missing_reason"] = "Not yet verified"
    return metrics, sources
