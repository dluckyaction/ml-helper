"""Syntetos-Boylan demand classification.

## Overview

The Syntetos-Boylan scheme sorts a time series into one of four demand
patterns — smooth, erratic, intermittent, lumpy — from two summary metrics:
how often demand occurs and how variable its size is when it does. The
pattern tells which forecasting method is expected to perform best: smooth
series suit classical methods such as exponential smoothing, while
intermittent and lumpy series call for intermittent-demand methods such as
Croston's method or its Syntetos-Boylan Approximation (SBA).

This module holds the vocabulary, thresholds, metrics-engine port, and
classification decision. The metrics are computed by a ``SeriesMetricsEngine``
in infrastructure (``ml_helper.infrastructure.syntetos.metrics``).

## Definitions

- **Period**: one observation of the series; periods are assumed equally
  spaced.
- **Demand size**: the value of a period with nonzero demand.
- **ADI** (average demand interval): the average number of periods between
  two consecutive nonzero demands.
- **CV²** (squared coefficient of variation): the variability of demand sizes
  relative to their mean, squared.

## Method

Metrics, computed over a series of ``n`` periods with ``k`` nonzero periods:

- ``ADI = n / k``
- ``CV² = (std(sizes) / mean(sizes))²``, where ``sizes`` are the ``k`` nonzero
  values and ``std`` is the sample standard deviation.

Decision, with inclusive cut-offs ``ADI_HIGH = 1.32`` and ``CV2_HIGH = 0.49``:

| | ``CV² < 0.49`` | ``CV² >= 0.49`` |
| --- | --- | --- |
| ``ADI < 1.32`` | smooth | erratic |
| ``ADI >= 1.32`` | intermittent | lumpy |

A series is labeled not classifiable when it has no demand at all
(``k = 0``) or no zero-demand period (``ADI = 1.0``).

## Assumptions and limitations

- Every row is one period: gaps in the calendar must be filled with zeros
  before classification, otherwise ADI is underestimated.
- Values are expected to be non-negative quantities.
- CV² needs at least two demand sizes to be defined.
- The cut-offs come from comparing forecast errors of Croston, SBA, and
  exponential smoothing under the authors' assumptions; they are guidance,
  not hard boundaries.
- Labeling series with ``ADI = 1.0`` as not classifiable is a convention of
  this implementation, not part of the original scheme, which places them in
  the smooth or erratic quadrants.

## References

- Syntetos, A. A., Boylan, J. E., & Croston, J. D. (2005). On the
  categorization of demand patterns. *Journal of the Operational Research
  Society*, 56(5), 495–503.
- Croston, J. D. (1972). Forecasting and stock control for intermittent
  demands. *Operational Research Quarterly*, 23(3), 289–303.
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