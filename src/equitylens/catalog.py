"""Stable identifiers and group-level metric definitions."""
COMPANIES = ("DBS", "OCBC", "UOB")
YEARS = (2023, 2024, 2025)
# Monetary figures are normalized to millions of Singapore dollars.
METRICS = {
    "net_profit": ("Net profit attributable to shareholders", "SGD million"),
    "total_income": ("Total income", "SGD million"),
    "total_assets": ("Total assets", "SGD million"),
    "roe": ("Return on equity", "%"),
    "nim": ("Net interest margin", "%"),
    "cet1_ratio": ("CET1 capital ratio (reported)", "%"),
}
