"""Syntetos-Boylan classification decision.

This module holds vocabulary, thresholds, the metrics-engine port, and the
classification decision only. It performs no arithmetic: ADI and CV^2 are
produced by a ``SeriesMetricsEngine`` supplied by the caller, so the
aggregation can be vectorized and replaced without touching this module.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Sequence, runtime_checkable


class SeriesType(Enum):
    """Classification of a single time series."""

    SMOOTH = "smooth"
    ERRATIC = "erratic"
    INTERMITTENT = "intermittent"
    LUMPY = "lumpy"
    NOT_CLASSIFIABLE = "not_classifiable"


ADI_HIGH = 1.32
CV2_HIGH = 0.49


@dataclass(frozen=True)
class SeriesMetrics:
    """Syntetos-Boylan metrics for one series, as computed by an engine."""

    adi: float
    cv2: float
    nonzero_periods: int


@runtime_checkable
class SeriesMetricsEngine(Protocol):
    """Port that computes Syntetos-Boylan metrics for a series."""

    def compute(self, values: Sequence[float]) -> SeriesMetrics: ...


def classify(adi: float, cv2: float) -> SeriesType:
    """Classify a series from its metrics.

    A series with ADI of exactly 1.0 has no zero-demand periods, which is
    outside the intermittent-demand model.
    """
    if adi == 1.0:
        return SeriesType.NOT_CLASSIFIABLE

    adi_high = adi >= ADI_HIGH
    cv2_high = cv2 >= CV2_HIGH

    if adi_high and cv2_high:
        return SeriesType.LUMPY
    if adi_high:
        return SeriesType.INTERMITTENT
    if cv2_high:
        return SeriesType.ERRATIC
    return SeriesType.SMOOTH


def classify_series(values: Sequence[float], engine: SeriesMetricsEngine) -> SeriesType:
    """Classify a series using the metrics produced by ``engine``."""
    metrics = engine.compute(values)
    if metrics.nonzero_periods == 0:
        return SeriesType.NOT_CLASSIFIABLE
    return classify(metrics.adi, metrics.cv2)