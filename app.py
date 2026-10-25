"""Run with: streamlit run app.py (after pip install -e '.[dev]')."""
import pandas as pd
import streamlit as st

from equitylens.analytics import format_value, peer_table, previous_year_delta
from equitylens.catalog import COMPANIES, METRICS, YEARS
from equitylens.charts import history_chart, peer_chart
from equitylens.data import load_data

st.set_page_config(page_title="EquityLens AI", page_icon="📊", layout="wide")
st.title("EquityLens AI")
st.caption("Singapore bank research · Annual reports 2023–2025 · Group-level reported figures")
try:
    data, sources = load_data()
except (OSError, ValueError, KeyError, pd.errors.ParserError) as exc:
    st.error(f"Could not load a valid research dataset: {exc}")
    st.stop()

company = st.sidebar.selectbox("Company", COMPANIES)
year = st.sidebar.selectbox("Reporting year", YEARS, index=len(YEARS) - 1)
metric = st.sidebar.selectbox("Chart metric", list(METRICS), format_func=lambda m: METRICS[m][0])
st.sidebar.caption("Blank values are unverified or unavailable. No estimates or imputation are used.")
selected = data[(data.company == company) & (data.year == year)].set_index("metric")
verified = int(data.value.notna().sum())
st.caption(f"Data coverage: {verified}/{len(data)} verified observations. Source notes identify later-report comparatives and differing reporting bases.")
st.subheader(f"{company} · {year}")
columns = st.columns(3)
for i, (key, (label, unit)) in enumerate(METRICS.items()):
    with columns[i % 3]:
        st.metric(f"{label} ({unit})", format_value(selected.loc[key, "value"], unit),
                  previous_year_delta(data, company, year, key), delta_color="off")

st.subheader("Historical performance")
history = data[(data.company == company) & (data.metric == metric)]
if history.value.notna().any():
    st.plotly_chart(history_chart(data, company, metric), width="stretch")
    if history.value.isna().any():
        st.info("Some years are missing. Chart gaps are preserved.")
else:
    st.info("No verified history is available for this metric.")

st.subheader(f"Peer comparison · {year}")
st.caption("Reported definitions and regulatory bases can differ. Review source notes before comparing banks.")
peers = peer_table(data, year, metric)
if peers.value.notna().any():
    st.plotly_chart(peer_chart(peers, metric), width="stretch")
else:
    st.info("No verified peer figures are available for this selection.")
display = peers.copy()
display["value"] = [format_value(v, u) for v, u in zip(peers.value, peers.unit)]
st.dataframe(display.fillna(""), hide_index=True, width="stretch")

with st.expander("Source references and missing data", expanded=False):
    st.caption("Page references are one-based PDF page numbers. Source notes retain report labels and adjustments.")
    evidence = data[(data.company == company)].merge(sources, on=["source_id", "company"], how="left", suffixes=("", "_report"))
    st.dataframe(evidence.astype(object).where(evidence.notna(), ""), hide_index=True, width="stretch")
    st.download_button("Download observations (CSV)", data.to_csv(index=False), "equitylens-metrics.csv", "text/csv")
    st.download_button("Download source registry (CSV)", sources.to_csv(index=False), "equitylens-sources.csv", "text/csv")
