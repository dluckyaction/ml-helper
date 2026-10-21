"""Tests for the Syntetos-Boylan pipeline.

Expected type is hand-computed for ``[10, 0, 12]``: 3 periods, 2 nonzero, so
ADI = 3/2 = 1.5 (high). Nonzero sizes [10, 12] have mean 11 and sample
variance 2, so CV^2 = 2/121 ≈ 0.017 (low): the series is Intermittent.
"""

import io

import pytest
from ml_helper.core.syntetos import SeriesMetrics, SeriesType
from ml_helper.infrastructure.shared.time_series_reader import TimeSeriesReadError
from ml_helper.infrastructure.syntetos.pipeline import classify_source

CSV_BODY = "date,value\n2026-01-01,10\n2026-01-02,0\n2026-01-03,12\n"


def write_csv(tmp_path) -> str:
    path = tmp_path / "series.csv"
    path.write_text(CSV_BODY, encoding="utf-8")
    return str(path)


def test_csv_path_is_classified(tmp_path):
    result = classify_source(write_csv(tmp_path), "date", "value")
    assert result.series_type is SeriesType.INTERMITTENT
    assert result.series.values.tolist() == [10, 0, 12]


def test_uploaded_stream_is_classified():
    stream = io.BytesIO(CSV_BODY.encode("utf-8"))
    stream.name = "series.csv"
    result = classify_source(stream, "date", "value")
    assert result.series_type is SeriesType.INTERMITTENT


def test_missing_file_raises(tmp_path):
    with pytest.raises(TimeSeriesReadError, match="No such file"):
        classify_source(str(tmp_path / "missing.csv"), "date", "value")


def test_unknown_column_raises(tmp_path):
    with pytest.raises(TimeSeriesReadError, match="not found"):
        classify_source(write_csv(tmp_path), "date", "amount")


def test_engine_can_be_overridden(tmp_path):
    class FakeEngine:
        def compute(self, values) -> SeriesMetrics:
            return SeriesMetrics(adi=2.0, cv2=1.0, nonzero_periods=2)

    result = classify_source(write_csv(tmp_path), "date", "value", engine=FakeEngine())
    assert result.series_type is SeriesType.LUMPY
