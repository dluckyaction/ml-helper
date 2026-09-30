"""Reader adapter for a single time series."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class LoadedSeries:
    """A single time series as parallel date and value sequences."""

    dates: pd.Series
    values: pd.Series
