from pathlib import Path
import pandas as pd
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_dashboard_selections():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.exception
    assert len(app.metric) == 6
    app.sidebar.selectbox[0].select("OCBC").run()
    app.sidebar.selectbox[1].select(2023).run()
    app.sidebar.selectbox[2].select("nim").run()
    assert not app.exception
    assert len(app.metric) == 6


def test_all_missing_dashboard(monkeypatch):
    from equitylens.data import load_data
    data, sources = load_data()
    data["value"] = float("nan")
    data["missing_reason"] = "Test: not verified"
    monkeypatch.setattr("equitylens.data.load_data", lambda: (data, sources))
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.exception
    assert all(m.value == "Not available" for m in app.metric)
    assert len(app.info) == 2


def test_invalid_dataset_shows_error(monkeypatch):
    from equitylens.data import DataValidationError
    def broken():
        raise DataValidationError("Invalid source")
    monkeypatch.setattr("equitylens.data.load_data", broken)
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.exception
    assert "Invalid source" in app.error[0].value
