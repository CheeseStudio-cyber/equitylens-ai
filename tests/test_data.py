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


def test_ocbc_uses_each_years_report():
    data, sources = load_data()
    for year in YEARS:
        source_id = f"ocbc-ar-{year}"
        source = sources.loc[sources.source_id == source_id]
        assert len(source) == 1
        assert source.iloc[0].company == "OCBC"
        assert source.iloc[0].year == year
        observations = data.loc[(data.company == "OCBC") & (data.year == year)]
        assert observations.value.notna().all()
        assert observations.source_id.eq(source_id).all()
        highlights = observations.loc[observations.metric != "nim"]
        assert highlights.source_page.eq(6 if year == 2024 else 4).all()
        nim = observations.loc[observations.metric == "nim"].iloc[0]
        assert nim.value == {2023: 2.28, 2024: 2.20, 2025: 1.91}[year]
        assert nim.source_page == (96 if year == 2023 else 98)


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
