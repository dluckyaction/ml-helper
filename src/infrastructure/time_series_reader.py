"""Reader adapter for a single time series.

Reads CSV or Parquet from a local path, a URL, or an uploaded file-like object
into a normalized ``LoadedSeries`` of parallel date and value sequences.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import IO, Union

import pandas as pd


class TimeSeriesReadError(Exception):
    """Raised when the source cannot be read or the requested columns are unusable."""


@dataclass(frozen=True)
class LoadedSeries:
    """A single time series as parallel date and value sequences."""

    dates: pd.Series
    values: pd.Series


Source = Union[str, Path, IO[bytes]]


def _suffix_of(name: str) -> str:
    return Path(name.split("?")[0]).suffix.lower()


def _read_csv(source) -> pd.DataFrame:
    try:
        return pd.read_csv(source)
    except Exception as exc:
        raise TimeSeriesReadError(f"Could not read the CSV source: {exc}") from exc


def _read_parquet(source) -> pd.DataFrame:
    try:
        return pd.read_parquet(source)
    except Exception as exc:
        raise TimeSeriesReadError(f"Could not read the Parquet source: {exc}") from exc


def _read_frame(source: Source) -> pd.DataFrame:
    if isinstance(source, str) and source.startswith(("http://", "https://")):
        suffix = _suffix_of(source)
        if suffix == ".csv":
            return _read_csv(source)
        if suffix == ".parquet":
            return _read_parquet(source)
        raise TimeSeriesReadError(
            f"Unsupported URL '{source}': expected a .csv or .parquet file."
        )

    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.is_file():
            raise TimeSeriesReadError(f"No such file: {path}")
        suffix = path.suffix.lower()
        if suffix == ".csv":
            return _read_csv(path)
        if suffix == ".parquet":
            return _read_parquet(path)
        raise TimeSeriesReadError(
            f"Unsupported file type '{suffix}': expected .csv or .parquet."
        )

    name = getattr(source, "name", "") or ""
    suffix = Path(str(name)).suffix.lower()
    if suffix == ".csv":
        return _read_csv(source)
    if suffix == ".parquet":
        return _read_parquet(source)
    raise TimeSeriesReadError(
        f"Unsupported upload '{name}': expected a .csv or .parquet file."
    )


def load_time_series(
    source: Source,
    date_column: str,
    value_column: str,
) -> LoadedSeries:
    """Load a single series, keeping only the requested date and value columns."""
    frame = _read_frame(source)

    missing = [
        name for name in (date_column, value_column) if name not in frame.columns
    ]
    if missing:
        raise TimeSeriesReadError(f"Column(s) not found: {', '.join(missing)}.")

    dates = pd.to_datetime(frame[date_column], errors="coerce")
    if dates.isna().any():
        raise TimeSeriesReadError(
            f"Column '{date_column}' could not be parsed as dates."
        )

    values = pd.to_numeric(frame[value_column], errors="coerce")
    if values.isna().any():
        raise TimeSeriesReadError(
            f"Column '{value_column}' could not be interpreted as numbers."
        )

    return LoadedSeries(
        dates=dates.reset_index(drop=True),
        values=values.reset_index(drop=True),
    )
