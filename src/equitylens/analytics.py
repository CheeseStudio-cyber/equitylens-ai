"""Pure display calculations with explicit missing-data behavior."""
import pandas as pd


def format_value(value, unit):
    if pd.isna(value):
        return "Not available"
    return f"{value:,.2f}%" if unit == "%" else f"{value:,.0f}"


def previous_year_delta(data, company, year, metric):
    rows = data[(data.company == company) & (data.metric == metric)].set_index("year")
    if year not in rows.index or year - 1 not in rows.index:
        return None
    current, prior = rows.loc[year, "value"], rows.loc[year - 1, "value"]
    if pd.isna(current) or pd.isna(prior):
        return None
    if rows.loc[year, "unit"] == "%":
        return f"{current - prior:+.2f} pp YoY"
    if prior == 0:
        return None
    return f"{(current - prior) / abs(prior) * 100:+.2f}% YoY"


def peer_table(data, year, metric):
    return data[(data.year == year) & (data.metric == metric)][
        ["company", "value", "unit", "missing_reason"]].reset_index(drop=True)
