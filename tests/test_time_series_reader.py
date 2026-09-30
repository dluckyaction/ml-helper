"""Tests for the time-series reader adapter."""

import io
from datetime import datetime

import pandas as pd
import pytest
from infrastructure.time_series_reader import (
    TimeSeriesReadError,
    load_time_series,
)

CSV_BODY = "date,value\n2026-01-01,10\n2026-01-02,0\n2026-01-03,12\n"
FRAME = pd.DataFrame(
    {
        "date": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "value": [10, 0, 12],
        "extra": [1, 2, 3],
    }
)


def write_csv(tmp_path) -> str:
    path = tmp_path / "series.csv"
    path.write_text(CSV_BODY, encoding="utf-8")
    return str(path)


def write_parquet(tmp_path) -> str:
    path = tmp_path / "series.parquet"
    FRAME.to_parquet(path)
    return str(path)


def test_load_csv_from_local_path(tmp_path):
    series = load_time_series(write_csv(tmp_path), "date", "value")
    assert series.values.tolist() == [10, 0, 12]
    assert series.dates.iloc[0] == datetime(2026, 1, 1)


def test_load_parquet_from_local_path(tmp_path):
    series = load_time_series(write_parquet(tmp_path), "date", "value")
    assert series.values.tolist() == [10, 0, 12]


def test_only_requested_columns_are_kept(tmp_path):
    series = load_time_series(write_parquet(tmp_path), "date", "value")
    assert list(series.values.index) == [0, 1, 2]


def test_unknown_column_raises(tmp_path):
    with pytest.raises(TimeSeriesReadError, match="not found"):
        load_time_series(write_csv(tmp_path), "when", "value")


def test_invalid_path_raises(tmp_path):
    with pytest.raises(TimeSeriesReadError, match="No such file"):
        load_time_series(str(tmp_path / "missing.csv"), "date", "value")


def test_unsupported_extension_raises(tmp_path):
    path = tmp_path / "series.txt"
    path.write_text("nope", encoding="utf-8")
    with pytest.raises(TimeSeriesReadError, match="Unsupported file type"):
        load_time_series(str(path), "date", "value")


def test_non_numeric_value_column_raises(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("date,value\n2026-01-01,abc\n", encoding="utf-8")
    with pytest.raises(TimeSeriesReadError, match="could not be interpreted as numbers"):
        load_time_series(str(path), "date", "value")


def test_unparseable_date_column_raises(tmp_path):
    path = tmp_path / "bad_dates.csv"
    path.write_text("date,value\nnot-a-date,10\n", encoding="utf-8")
    with pytest.raises(TimeSeriesReadError, match="could not be parsed as dates"):
        load_time_series(str(path), "date", "value")


def test_load_from_file_like_object():
    upload = io.BytesIO(CSV_BODY.encode("utf-8"))
    upload.name = "series.csv"
    series = load_time_series(upload, "date", "value")
    assert series.values.tolist() == [10, 0, 12]


def test_load_from_unsupported_upload_raises():
    upload = io.BytesIO(b"nope")
    upload.name = "series.txt"
    with pytest.raises(TimeSeriesReadError, match="Unsupported upload"):
        load_time_series(upload, "date", "value")


def test_load_from_url(tmp_path, monkeypatch):
    import infrastructure.time_series_reader as reader

    def fake_read_csv(source):
        assert source == "https://example.com/series.csv"
        return FRAME

    monkeypatch.setattr(reader.pd, "read_csv", fake_read_csv)
    series = load_time_series("https://example.com/series.csv", "date", "value")
    assert series.values.tolist() == [10, 0, 12]


def test_load_from_url_with_unsupported_extension_raises():
    with pytest.raises(TimeSeriesReadError, match="Unsupported URL"):
        load_time_series("https://example.com/series.txt", "date", "value")
