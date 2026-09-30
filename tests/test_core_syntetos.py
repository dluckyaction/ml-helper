"""Decision tests for the core classification module.

Core performs no arithmetic, so these tests drive it with a test double that
implements ``SeriesMetricsEngine`` and returns fixed metrics.
"""

import ast
from pathlib import Path

import pytest
from core.syntetos import (
    ADI_HIGH,
    CV2_HIGH,
    SeriesMetrics,
    SeriesMetricsEngine,
    SeriesType,
    classify,
    classify_series,
)


class FakeEngine:
    """Test double returning preset metrics regardless of the input values."""

    def __init__(self, metrics: SeriesMetrics) -> None:
        self._metrics = metrics
        self.calls = 0

    def compute(self, values) -> SeriesMetrics:
        self.calls += 1
        return self._metrics


def test_series_type_members():
    assert {member.name for member in SeriesType} == {
        "SMOOTH",
        "ERRATIC",
        "INTERMITTENT",
        "LUMPY",
        "NOT_CLASSIFIABLE",
    }


def test_threshold_constants():
    assert ADI_HIGH == 1.32
    assert CV2_HIGH == 0.49


def test_fake_engine_satisfies_the_port():
    engine: SeriesMetricsEngine = FakeEngine(
        SeriesMetrics(adi=1.0, cv2=0.0, nonzero_periods=3)
    )
    assert isinstance(engine, SeriesMetricsEngine)


def test_smooth_when_both_metrics_are_low():
    assert classify(adi=1.2, cv2=0.3) is SeriesType.SMOOTH


def test_erratic_when_cv2_is_high():
    assert classify(adi=1.2, cv2=0.5) is SeriesType.ERRATIC


def test_intermittent_when_adi_is_high():
    assert classify(adi=1.4, cv2=0.3) is SeriesType.INTERMITTENT


def test_lumpy_when_both_metrics_are_high():
    assert classify(adi=1.4, cv2=0.5) is SeriesType.LUMPY


def test_thresholds_are_inclusive():
    assert classify(adi=ADI_HIGH, cv2=CV2_HIGH) is SeriesType.LUMPY
    assert classify(adi=ADI_HIGH - 0.01, cv2=CV2_HIGH - 0.01) is SeriesType.SMOOTH


def test_continuous_series_with_no_zeros_is_not_classifiable():
    assert classify(adi=1.0, cv2=0.0) is SeriesType.NOT_CLASSIFIABLE


def test_classify_series_delegates_to_the_engine():
    engine = FakeEngine(SeriesMetrics(adi=1.4, cv2=0.5, nonzero_periods=5))
    assert classify_series([0, 3, 0, 4], engine) is SeriesType.LUMPY
    assert engine.calls == 1


def test_classify_series_maps_all_zero_series_to_not_classifiable():
    engine = FakeEngine(SeriesMetrics(adi=float("inf"), cv2=0.0, nonzero_periods=0))
    assert classify_series([0, 0, 0, 0], engine) is SeriesType.NOT_CLASSIFIABLE


@pytest.mark.parametrize(
    ("adi", "cv2", "expected"),
    [
        (1.0, 5.0, SeriesType.NOT_CLASSIFIABLE),
        (1.0, 0.0, SeriesType.NOT_CLASSIFIABLE),
        (1.31, 0.48, SeriesType.SMOOTH),
        (1.31, 0.49, SeriesType.ERRATIC),
        (1.32, 0.48, SeriesType.INTERMITTENT),
        (1.32, 0.49, SeriesType.LUMPY),
    ],
)
def test_quadrant_table(adi, cv2, expected):
    assert classify(adi=adi, cv2=cv2) is expected


_ARITHMETIC_NODES = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
)

_METRIC_HELPERS = ("avg_demand_interval", "squared_cv", "mean", "stdev", "std")


def test_core_module_performs_no_arithmetic():
    """Core owns the decision; every calculation belongs to an engine."""
    path = Path(__file__).resolve().parents[1] / "src" / "core" / "syntetos.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    arithmetic = [
        type(node).__name__
        for node in ast.walk(tree)
        if isinstance(node, _ARITHMETIC_NODES)
    ]
    assert not arithmetic, f"Arithmetic found in core: {arithmetic}"

    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    helpers = called & set(_METRIC_HELPERS)
    assert not helpers, f"Metric calculations found in core: {sorted(helpers)}"