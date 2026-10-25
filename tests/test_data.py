"""Data contract tests; fixtures are synthetic and never enter the dashboard."""
import pandas as pd
import pytest

from equitylens.catalog import COMPANIES, METRICS, YEARS
from equitylens.data import DataValidationError, load_data, validate


def test_repository_dataset():
    data, sources = load_data()
    validate(data, sources)
    assert len(data) == len(COMPANIES) * len(YEARS) * len(METRICS)
    assert data.value.notna().any()


@pytest.mark.parametrize("column,value,message", [
    ("source_id", "unknown", "registered source"),
    ("source_page", None, "PDF page"),
    ("source_note", None, "source note"),
    ("unit", "USD", "unit"),
    ("value", float("inf"), "finite"),
    ("company", "Unknown", "company/year"),
])
def test_reject_invalid_observations(column, value, message):
    data, sources = load_data()
    row = data[data.value.notna()].head(1).copy()
    row.loc[row.index[0], column] = value
    with pytest.raises(DataValidationError, match=message):
        validate(row, sources)


def test_missing_requires_reason():
    data, sources = load_data()
    row = data.head(1).copy()
    row["value"] = float("nan")
    row["missing_reason"] = None
    with pytest.raises(DataValidationError, match="missing_reason"):
        validate(row, sources)


def test_duplicate_rejected():
    data, sources = load_data()
    with pytest.raises(DataValidationError, match="Duplicate observations"):
        validate(pd.concat([data, data.head(1)]), sources)


def test_absent_observations_expand_to_missing(tmp_path):
    data, sources = load_data()
    data.iloc[:0].to_csv(tmp_path / "metrics.csv", index=False)
    sources.to_csv(tmp_path / "sources.csv", index=False)
    loaded, _ = load_data(tmp_path)
    assert len(loaded) == 54
    assert loaded.value.isna().all()
    assert loaded.missing_reason.notna().all()
