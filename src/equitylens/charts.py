"""Charts use one metric/unit at a time and retain gaps in time series."""
import plotly.express as px
from equitylens.catalog import METRICS, YEARS


def history_chart(data, company, metric):
    rows = data[(data.company == company) & (data.metric == metric)].sort_values("year")
    fig = px.line(rows, x="year", y="value", markers=True,
                  labels={"value": METRICS[metric][1], "year": "Year"},
                  title=METRICS[metric][0])
    fig.update_traces(connectgaps=False)
    fig.update_xaxes(tickmode="array", tickvals=list(YEARS))
    return fig


def peer_chart(rows, metric):
    return px.bar(rows.dropna(subset=["value"]), x="company", y="value",
                  labels={"value": METRICS[metric][1], "company": "Company"},
                  title=METRICS[metric][0], color="company")
