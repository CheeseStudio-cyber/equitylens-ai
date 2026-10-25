import pandas as pd
from equitylens.analytics import format_value, previous_year_delta, peer_table
from equitylens.charts import history_chart, peer_chart


def observations(values, unit="SGD million"):
    return pd.DataFrame({"company": ["DBS"] * 3, "year": [2023, 2024, 2025],
                         "metric": ["net_profit"] * 3, "value": values,
                         "unit": [unit] * 3, "missing_reason": [None] * 3})


def test_delta_does_not_skip_missing_year_or_divide_by_zero():
    assert previous_year_delta(observations([100, None, 120]), "DBS", 2025, "net_profit") is None
    assert previous_year_delta(observations([100, 0, 120]), "DBS", 2025, "net_profit") is None
    assert previous_year_delta(observations([100, 110, 121]), "DBS", 2025, "net_profit") == "+10.00% YoY"
    assert previous_year_delta(observations([10, 11, 12], "%"), "DBS", 2025, "net_profit") == "+1.00 pp YoY"


def test_format_missing_and_zero():
    assert format_value(float("nan"), "%") == "Not available"
    assert format_value(0, "SGD million") == "0"


def test_chart_retains_gap_and_peer_table_retains_missing():
    data = observations([100, None, 120])
    fig = history_chart(data, "DBS", "net_profit")
    assert fig.data[0].connectgaps is False
    assert pd.isna(fig.data[0].y[1])
    peers = peer_table(data, 2024, "net_profit")
    assert len(peers) == 1 and peers.value.isna().all()
    assert len(peer_chart(peers, "net_profit").data) == 0
