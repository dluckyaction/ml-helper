"""Syntetos-Boylan use case: load a series from a source and classify it.

Implements the end-to-end flow for ``ml_helper.core.syntetos`` so every
entrypoint (notebook, web export) shares one orchestration. Entrypoints turn
their own input widgets into a reader ``Source`` and present the result.
"""

from dataclasses import dataclass

from ml_helper.core.syntetos import SeriesMetricsEngine, SeriesType, classify_series
from ml_helper.infrastructure.shared.time_series_reader import (
    LoadedSeries,
    Source,
    load_time_series,
)
from ml_helper.infrastructure.syntetos.metrics import PolarsSyntetosMetrics


@dataclass(frozen=True)
class ClassifiedSeries:
    """A loaded series together with its Syntetos-Boylan type."""

    series: LoadedSeries
    series_type: SeriesType


def classify_source(
    source: Source,
    date_column: str,
    value_column: str,
    engine: SeriesMetricsEngine | None = None,
) -> ClassifiedSeries:
    """Load the series in ``source`` and classify its value column.

    Raises ``TimeSeriesReadError`` when the source or columns are unusable.
    """
    series = load_time_series(source, date_column, value_column)
    series_type = classify_series(series.values, engine or PolarsSyntetosMetrics())
    return ClassifiedSeries(series=series, series_type=series_type)
