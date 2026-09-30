## 1. Dependencies

- [x] 1.1 Add `marimo` and `altair` to runtime dependencies with `uv add marimo altair` and verify `uv sync` completes and `uv run python -c "import marimo, altair"` succeeds; commit
- [x] 1.2 Create the notebook module skeleton `src/entrypoints/syntetos_classifier/__init__.py` and verify it imports under `uv run pytest tests/test_smoke.py`; commit

## 2. Core decision module (`src/core`)

No calculations in this section: core holds vocabulary, thresholds, the engine port, and the classification decision. Every metric is produced by an injected engine.

- [x] 2.1 Implement `SeriesType` enum (`SMOOTH`, `ERRATIC`, `INTERMITTENT`, `LUMPY`, `NOT_CLASSIFIABLE`) and the threshold constants `ADI_HIGH = 1.32` / `CV2_HIGH = 0.49` in `src/core/syntetos.py` and verify the new test asserting its members and constants passes; commit
- [x] 2.2 Implement the `SeriesMetrics(adi, cv2, nonzero_periods)` dataclass and the `SeriesMetricsEngine` `Protocol` port with `compute(values) -> SeriesMetrics` in `src/core/syntetos.py`, and verify a test double satisfying the protocol type-checks; commit
- [x] 2.3 Implement `classify(adi, cv2)` using only threshold comparisons (ADI >= 1.32 and CV^2 >= 0.49) with ADI == 1.0 returning `NOT_CLASSIFIABLE`, and verify tests cover all four quadrants plus the continuous no-zeros case; commit
- [x] 2.4 Implement `classify_series(values, engine)` delegating to `engine.compute(values)`, mapping `nonzero_periods == 0` to `NOT_CLASSIFIABLE`, and verify tests cover the all-zero case via the test double; commit
- [x] 2.5 Confirm `src/core/syntetos.py` contains no arithmetic (no `avg_demand_interval`, `squared_cv`, `mean`, `std`, or division) and run `uv run pytest tests/test_core_syntetos.py tests/test_core_purity.py` to verify all pass; commit

## 3. Infrastructure adapters (`src/infrastructure`)

- [x] 3.1 Implement `LoadedSeries(dates, values)` dataclass in `src/infrastructure/time_series_reader.py` and verify it imports; commit
- [x] 3.2 Implement `load_time_series(source, date_column, value_column)` reading CSV/Parquet from a local path, URL, or file-like object (dispatch on filename suffix) with pandas, raising domain-friendly errors for unknown columns, unreadable files, and unparseable dates; verify a manual smoke call on a sample CSV; commit
- [x] 3.3 Add `tests/test_time_series_reader.py` with CSV/Parquet fixtures written to `tmp_path` covering happy path, unknown column, and invalid path, and verify it passes; commit
- [x] 3.4 Implement `PolarsSyntetosMetrics` in `src/infrastructure/syntetos_metrics.py` satisfying the core `SeriesMetricsEngine` port, computing ADI and CV^2 with vectorized polars expressions (no per-value Python loop), and verify a manual smoke call on a sample series; commit
- [x] 3.5 Add the batch entry point on `PolarsSyntetosMetrics` that `group_by`s a series id to classify many series in one pass, and verify a manual call over a small multi-series frame; commit
- [x] 3.6 Add `tests/test_syntetos_metrics.py` asserting ADI and CV^2 against hand-computed values for a single series, plus a constant series, an all-zero series (`nonzero_periods == 0`), and a many-series batch; verify it passes; commit

## 4. Marimo entrypoint notebook (`src/entrypoints`)

- [x] 4.1 Create the marimo app `src/entrypoints/syntetos_classifier/notebook.py` with a `mo.ui.form` holding date-column, value-column, and path/URL text fields, a file uploader, and a "Classify" submit button; verify the file opens with `marimo edit` (manual) and imports under pytest; commit
- [x] 4.2 Wire the pipeline cell that, on form submit, calls the reader adapter, passes `PolarsSyntetosMetrics` to the core `classify_series` use case, and reports input errors via `mo.ui.alert`; verify by running the notebook with an invalid path (manual); commit
- [x] 4.3 Add the output cells rendering `mo.ui.altair_chart` (value vs date) and a callout box with the `SeriesType` label, rendered distinctly (e.g. amber) for `NOT_CLASSIFIABLE`; commit
- [x] 4.4 Add a smoke test asserting the notebook module imports without executing cells and verify it passes; commit

## 5. Documentation conventions

- [x] 5.1 Extend the `context` field in `openspec/config.yaml` with the naming/semantics rule (ML Helper is a generic ML tool; app-layer naming is domain-neutral) and verify `openspec validate` still passes; commit
- [x] 5.2 Add a "Naming & semantics" subsection to `README.md` stating the domain-neutral convention and the demand-confined-to-algorithm-code exception; commit
- [x] 5.3 Create `AGENTS.md` capturing project conventions (hexagonal layering, pure-core rule, calculations belong in infrastructure behind a core port, naming/semantics principle) and verify it renders as a readable markdown doc; commit

## 6. Integration verification

- [x] 6.1 Run `uv run pytest` and verify the full suite passes, including the core purity guard; commit
- [ ] 6.2 Run `marimo run src/entrypoints/syntetos_classifier/notebook.py` with a sample series CSV and verify the chart and classification box render, including the Not Classifiable case for a zero-free series (manual); commit