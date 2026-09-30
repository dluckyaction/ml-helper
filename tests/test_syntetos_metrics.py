"""Tests for the vectorized metrics engine.

Expected ADI and CV^2 values are hand-computed:

- ``[10, 0, 12, 0, 11, 0, 9, 13]``: 8 periods, 5 nonzero, so ADI = 8/5 = 1.6.
  Nonzero sizes [10, 12, 11, 9, 13] have mean 11 and a sum of squared
  deviations of 10, so sample variance is 10/4 = 2.5 and CV^2 = 2.5/121.
- ``[5, 5, 5, 5]``: ADI = 1.0 and std = 0, so CV^2 = 0.
- ``[0, 0, 100, 0, 0, 5]``: 6 periods, 2 nonzero, so ADI = 3. Sizes [100, 5]
  have mean 52.5 and a sum of squared deviations of 4512.5, so sample variance
  is 4512.5 and CV^2 = 4512.5/2756.25.
"""

import polars as pl
import pytest
from core.syntetos import SeriesMetricsEngine, SeriesType, classify_series
from infrastructure.syntetos_metrics import PolarsSyntetosMetrics

ENGINE = PolarsSyntetosMetrics()

INTERMITTENT = [10, 0, 12, 0, 11, 0, 9, 13]
CONSTANT = [5, 5, 5, 5]
ALL_ZERO = [0, 0, 0, 0]
LUMPY = [0, 0, 100, 0, 0, 5]


def test_engine_satisfies_the_core_port():
    assert isinstance(ENGINE, SeriesMetricsEngine)


def test_adi_and_cv2_for_single_series():
    metrics = ENGINE.compute(INTERMITTENT)
    assert metrics.nonzero_periods == 5
    assert metrics.adi == pytest.approx(1.6)
    assert metrics.cv2 == pytest.approx(2.5 / 121)


def test_constant_series_has_no_variance():
    metrics = ENGINE.compute(CONSTANT)
    assert metrics.nonzero_periods == 4
    assert metrics.adi == pytest.approx(1.0)
    assert metrics.cv2 == pytest.approx(0.0)


def test_all_zero_series_reports_no_nonzero_periods():
    assert ENGINE.compute(ALL_ZERO).nonzero_periods == 0


def test_lumpy_series_metrics():
    metrics = ENGINE.compute(LUMPY)
    assert metrics.nonzero_periods == 2
    assert metrics.adi == pytest.approx(3.0)
    assert metrics.cv2 == pytest.approx(4512.5 / 2756.25)


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (INTERMITTENT, SeriesType.INTERMITTENT),
        (CONSTANT, SeriesType.NOT_CLASSIFIABLE),
        (ALL_ZERO, SeriesType.NOT_CLASSIFIABLE),
        (LUMPY, SeriesType.LUMPY),
    ],
)
def test_classification_through_the_core_use_case(values, expected):
    assert classify_series(values, ENGINE) is expected


def test_batch_matches_single_series_computation():
    groups = {"intermittent": INTERMITTENT, "constant": CONSTANT, "lumpy": LUMPY}
    values = [v for series in groups.values() for v in series]
    series_ids = [name for name, series in groups.items() for _ in series]

    batch = ENGINE.compute_batch(values, series_ids)

    assert batch["series_id"].to_list() == sorted(groups)
    for row in batch.iter_rows(named=True):
        single = ENGINE.compute(groups[row["series_id"]])
        assert row["adi"] == pytest.approx(single.adi)
        assert row["cv2"] == pytest.approx(single.cv2)
        assert row["nonzero_periods"] == single.nonzero_periods


def test_batch_reports_all_zero_series():
    batch = ENGINE.compute_batch(
        ALL_ZERO + CONSTANT, ["empty"] * len(ALL_ZERO) + ["constant"] * len(CONSTANT)
    )
    empty = batch.filter(pl.col("series_id") == "empty")
    assert empty["nonzero_periods"].item() == 0


def test_batch_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        ENGINE.compute_batch([1, 2, 3], ["a", "b"])
