## Why

The platform scaffold (`core`/`infrastructure`/`entrypoints`) is empty — there are no real entrypoints yet. This change builds the first one, a small marimo notebook, to establish the correct hexagonal design patterns on a deliberately simple example: read a CSV/Parquet of a single time series, chart it, and label it with the Syntetos-Boylan classification. It also fixes the semantic convention for a *generic* ML tool — domain-neutral naming at the app layer, with "demand" reserved for algorithm-inherent math.

## What Changes

- **New marimo notebook entrypoint** under `src/entrypoints/` that exposes a form with three inputs and a "Classify" button:
  - Date/index column name (text field)
  - Value/numeric column name (text field)
  - Data source: path/URL text field *and* an upload button (CSV or Parquet)
- On submit, it loads the file, normalizes it to a single date+value series, renders an interactive Altair time-series chart, and shows a box with the series type: Smooth, Erratic, Intermittent, Lumpy, or Not Classifiable.
- **New time-series reader adapter** in `src/infrastructure/` (`time_series_reader.py`) that reads CSV/Parquet from a local path, a URL, or an uploaded file into a normalized series.
- **New domain decision module** in `src/core/` that holds no calculations: the `SeriesType` enum, the ADI/CV² threshold constants, a `SeriesMetrics` dataclass, a `SeriesMetricsEngine` port (`Protocol`), the `classify(adi, cv2)` quadrant table, and the `classify_series(values, engine)` use case. It contains no arithmetic — every metric is computed by an injected engine. It adds a fifth series type, `NOT_CLASSIFIABLE`, for series outside the intermittent-demand model: no zero-demand periods (continuous) or no demand at all (all zeros). These are treated as labels, not errors.
- **New vectorized metrics engine** in `src/infrastructure/` that computes the Syntetos-Boylan metrics (ADI, CV²) with polars, implementing the core port. It ships a single-series path and a `group_by` path over many series, so scaling up is a supported operation rather than a rewrite.
- **Semantic convention**: reader/notebook vocabulary is domain-neutral ("series", "date column", "value column"); "demand" is confined to algorithm-inherent code, namely the core decision module and the infrastructure metrics engine. Captured in `openspec/config.yaml` context, a new `README.md` "Naming & semantics" note, and a new `AGENTS.md`.
- **New runtime dependencies**: `marimo` and `altair`.
- **BREAKING**: none. The existing purity guard keeps working unchanged (`src/core` gains no third-party imports, so it trivially passes).

## Capabilities

### New Capabilities
- `syntetos-classification`: reading a single time series from CSV/Parquet, selecting its date and value columns, visualizing the series, and labeling its type according to the Syntetos-Boylan classification (including Not Classifiable) through a marimo notebook entrypoint.

### Modified Capabilities
- None.

## Impact

- **Code**: new files under `src/core/`, `src/infrastructure/`, and `src/entrypoints/`; no existing module changes.
- **Documentation**: `openspec/config.yaml` (extend `context` with the naming rule), `README.md` ("Naming & semantics" note), and new `AGENTS.md` (project conventions).
- **Dependencies**: `marimo` and `altair` added to `pyproject.toml` runtime dependencies. `polars` is already present.
- **Tests**: unit tests for the core decision module using a test double for the engine, unit tests for the polars metrics engine including a many-series batch case, and the full suite (`uv run pytest`) staying green, including the core purity guard.
- **Layering**: core holds vocabulary, thresholds, the engine port, and the classification decision, with no arithmetic; all metric computation (counts, means, standard deviations) and dataframe reading live in infrastructure; the notebook stays a thin entrypoint view that wires the reader, the engine, and the core use case together.