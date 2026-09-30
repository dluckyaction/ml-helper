"""Vectorized Syntetos-Boylan metrics engine.

Implements the core ``SeriesMetricsEngine`` port with polars expressions, so
per-period aggregation runs over a column instead of a Python loop and many
series can be classified in a single grouped pass.
"""

from typing import Sequence

import polars as pl
from core.syntetos import SeriesMetrics


class PolarsSyntetosMetrics:
    """Computes ADI and CV^2 for one series or a batch of series."""

    def compute(self, values: Sequence[float]) -> SeriesMetrics:
        """Compute the metrics for a single series."""
        frame = pl.DataFrame({"value": [float(v) for v in values]})
        result = frame.select(
            adi=_adi_expression(),
            cv2=_cv2_expression(),
            nonzero_periods=(pl.col("value") != 0).sum(),
        )

        nonzero = int(result["nonzero_periods"][0])
        return SeriesMetrics(
            adi=float(result["adi"][0]),
            cv2=float(result["cv2"][0]),
            nonzero_periods=nonzero,
        )

    def compute_batch(
        self,
        values: Sequence[float],
        series_ids: Sequence[str],
    ) -> pl.DataFrame:
        """Compute the metrics for many series in one grouped pass."""
        if len(values) != len(series_ids):
            raise ValueError("values and series_ids must have the same length")

        frame = pl.DataFrame(
            {
                "series_id": list(series_ids),
                "value": [float(v) for v in values],
            }
        )

        return (
            frame.group_by("series_id", maintain_order=True)
            .agg(
                adi=_adi_expression(),
                cv2=_cv2_expression(),
                nonzero_periods=(pl.col("value") != 0).sum(),
            )
            .sort("series_id")
        )


def _adi_expression() -> pl.Expr:
    periods = pl.len()
    nonzero = (pl.col("value") != 0).sum()
    return pl.when(nonzero == 0).then(pl.lit(float("inf"))).otherwise(
        periods.cast(pl.Float64) / nonzero.cast(pl.Float64)
    )


def _cv2_expression() -> pl.Expr:
    nonzero = pl.col("value").filter(pl.col("value") != 0)
    return (
        pl.when(nonzero.count() == 0)
        .then(pl.lit(float("nan")))
        .otherwise((nonzero.std() / nonzero.mean()) ** 2)
    )
