## Context

The platform is a clean-architecture scaffold: `src/core`, `src/infrastructure`, and `src/entrypoints` are empty packages. The core purity guard (tests/test_core_purity.py) forbids `streamlit`, `gradio`, and `fastapi` in `src/core`; the project additionally intends `src/core` to carry no third-party dependencies and, per the agreed convention, no computations either — calculations are infrastructure concerns because they must scale. There is no entrypoint yet — this change is the first one and the pattern it sets shapes the rest of the app. See proposal.md for the motivation.

## Goals / Non-Goals

**Goals:**
- Establish the hexagonal seam on a real example: entrypoint (marimo notebook) → infrastructure (data reader adapter + vectorized metrics engine) → core (decision only, calculations injected through a port).
- Keep every computation out of `src/core`, so per-period aggregation can be vectorized and replaced without touching the domain decision.
- Establish the semantic convention: ML Helper is a *generic* ML tool, so reader and notebook vocabulary is domain-neutral ("series", "date column", "value column"), with "demand" confined to algorithm-inherent code (Syntetos).
- Make that convention durable in project documentation (`openspec/config.yaml`, `README.md`, and a new `AGENTS.md`).
- Keep the example small: one series, two columns, one label.

**Non-Goals:**
- Multi-series UX (per-SKU classification tables, column dropdowns per series). The engine ships a `group_by` batch path, but this example loads one series.
- Column dropdowns auto-populated from the file — the user types column names; worth revisiting later.
- Date resampling or irregular-grid handling — each row is one period.

## Decisions

### 1. Core holds the decision, not the arithmetic

`src/core/syntetos.py` contains data and comparisons only — no metric is computed there:

- `SeriesType` enum: `SMOOTH`, `ERRATIC`, `INTERMITTENT`, `LUMPY`, `NOT_CLASSIFIABLE`.
- Threshold constants: `ADI_HIGH = 1.32`, `CV2_HIGH = 0.49`.
- `SeriesMetrics` dataclass: `adi`, `cv2`, `nonzero_periods` — numbers an engine produced.
- `SeriesMetricsEngine` port: a `Protocol` exposing `compute(values) -> SeriesMetrics`.
- `classify(adi, cv2)` → the four-quadrant table via threshold comparisons, returning `NOT_CLASSIFIABLE` when ADI == 1.0 (a continuous series is outside the intermittent-demand model).
- `classify_series(values, engine)` → the use case: delegates to `engine.compute(values)`, maps `nonzero_periods == 0` to `NOT_CLASSIFIABLE`, and otherwise calls `classify`.

There is no `avg_demand_interval`, no `squared_cv`, no `mean`, no `std`, no division in core. Counting nonzero periods and computing a standard deviation are the operations that must scale, so they are engine concerns.

**Why**: Python loops over per-period values are far too slow for real workloads, and any math placed in core has to be rewritten later to vectorize. Keeping core to a decision table means the arithmetic is swappable from the start and the entrypoint depends on a port rather than an engine class. **Alternative considered**: stdlib `math`/`statistics` in core — rejected; pure-python aggregation is the exact bottleneck this project will hit first. **Alternative considered**: PyArrow compute in core (the README's letter permits it) — rejected; the README's allowance is not the reason to put computations in the domain layer.

### 2. The metrics engine lives in `src/infrastructure`, vectorized

`src/infrastructure/syntetos_metrics.py` provides `PolarsSyntetosMetrics`, which implements the core port:

- ADI = number of periods / number of periods with nonzero demand.
- CV² = (std / mean)² over nonzero demand sizes.
- `compute(values)` for a single series, and a batch entry point that `group_by`s a series id so many series are classified in one pass.

Core's contract never changes when the engine is replaced — a NumPy or Rust engine satisfies the same `Protocol`. Scaling is a supported path from day one, not a deferred rewrite.

**Why**: polars expresses both ADI and CV² as vectorized expressions over a column, which is what makes the many-series case cheap.

### 3. Time-series reader adapter in `src/infrastructure`

`src/infrastructure/time_series_reader.py` exposes a single function that reads CSV or Parquet from one of three sources (local path, URL, uploaded file) into a `LoadedSeries` dataclass `(dates, values)`, selecting only the two requested columns by name.

- Local/URL: `pandas.read_csv` / `pandas.read_parquet`; pandas is already a runtime dependency.
- Uploaded file: marimo provides a file-like object — the reader takes any file-like object and dispatches on the filename suffix.
- Validation: missing/unknown columns, unreadable file, or unparseable dates raise a domain-friendly error the notebook translates into a message.

**Why pandas over polars for reading**: polars is already a dependency, but pandas reads both CSV and Parquet with the least friction here, and the reader is the natural place to swap engines later. **Alternative**: polars — equivalent; not chosen for this example.

### 4. Naming and semantics across layers

ML Helper assists general ML work, so names carry no demand/forecasting connotation:

- Reader and notebook vocabulary is neutral: `time_series_reader`, `LoadedSeries`, "date column", "value column".
- "Demand" is confined to algorithm-inherent code, meaning the core decision module and the infrastructure metrics engine where the Syntetos math lives. It must not leak into the reader, the notebook, or any user-visible wording.
- Capabilities and files are named after algorithms or generic ML concepts, never after a product domain.

**Why**: semantics leak into UX and code; a "demand" naming would steer the whole app toward forecasting. **Alternative considered**: brand the reader as demand-specific — rejected.

### 5. Marimo notebook is the entrypoint

One marimo app file under `src/entrypoints/`, e.g. `src/entrypoints/syntetos_classifier/notebook.py`. Marimo apps are plain Python (`import marimo` + `@app.cell` blocks), so they install as part of the `src/entrypoints` package and run with `marimo edit|run <file>`.

The notebook layout keeps the form and the "show after submit" cells separate:

1. **Form cell**: `mo.ui.form` containing a date-column `text_field`, a value-column `text_field`, a source `text_field` (path/URL), a `file_uploader`, and a submit button labeled "Classify".
2. **Pipeline cell**: runs only when the form returns a value (marimo forms do not re-run downstream cells until submit) → call the reader adapter → on error, render `mo.ui.alert`; on success, call `classify_series(values, PolarsSyntetosMetrics())`. The notebook names the engine, not a function: it depends on the core port, and the concrete adapter is chosen here.
3. **Output cell**: `mo.ui.altair_chart` plotting value vs date, plus a `mo.ui.callout`/banner box with the `SeriesType` label.

**Why the text field + uploader coexist**: the user asked for both; the notebook uses whichever is provided and errors if both are empty. **Alternative**: an exclusive toggle — rejected as extra complexity for this example.

### 6. Altair for the chart

`mo.ui.altair_chart` gives interactive time-series charts (tooltip, brush/zoom). Altair becomes a new runtime dependency alongside marimo.

### 7. Edge behavior

- Series with **no zero-demand periods** (ADI == 1.0): continuous, outside the intermittent-demand model → `NOT_CLASSIFIABLE`.
- **All-zero series**: no demand at all, so CV² is undefined. The engine does not raise; it reports `nonzero_periods == 0`, and `classify_series` maps that to `NOT_CLASSIFIABLE` (symmetric to the no-zeros case; reserved for valid data outside the model).
- Constant nonzero series: std = 0 → CV² = 0 → `SMOOTH`.
- `NOT_CLASSIFIABLE` is a *label*, not an error: the notebook renders it in a distinct box (e.g. amber callout) rather than an alert. Real errors are reserved for bad input (unknown column, unreadable file, non-numeric values).
- Both columns empty / no source: form submit is blocked or surfaces an error message.

### 8. Documentation conventions

The semantic convention is made durable in three places during apply:

- `openspec/config.yaml` → extend the `context` field so every future planning session inherits the naming rule.
- `README.md` → add a short "Naming & semantics" subsection stating ML Helper is a generic ML tool and domain-neutral naming is required.
- `AGENTS.md` (new) → project-wide conventions for AI agents: hexagonal layering, pure-core rule, calculations belong in infrastructure behind a core port, and the naming/semantics principle.

**Why** : conventions that live only in one design doc evaporate. **Alternative considered**: leaving docs unchanged — rejected, the user explicitly wants this context written down.

### 9. Testing

- `tests/test_core_syntetos.py`: unit tests of the decision module driven by a test double implementing `SeriesMetricsEngine` — all four quadrants, the ADI == 1.0 edge, and the all-zero edge. No arithmetic is exercised because core performs none; the double supplies metrics directly.
- `tests/test_syntetos_metrics.py`: unit tests of `PolarsSyntetosMetrics` against hand-computed ADI/CV², covering a single series, a constant series, an all-zero series, and a many-series `group_by` batch.
- `tests/test_time_series_reader.py`: write small CSV/Parquet fixtures to `tmp_path`; assert normalized output, unknown-column error, invalid-path error. The marimo upload type is emulated with a plain file-like object.
- A smoke test asserts the notebook module imports (marimo apps import cleanly under pytest).
- `uv run pytest` must stay green, including the existing purity guard.

## Risks / Trade-offs

- [Pandas in the reader makes infra slightly heavier] → Reader is a single adapter; the switch to polars or a streaming engine is contained there.
- [Marimo notebooks are awkward to unit-test] → All real logic sits in core/infra and is pytest-covered; the notebook stays a thin view.
- [The engine is polars-bound, so a future NumPy or Rust engine means a second adapter] → Accepted: that is what the `SeriesMetricsEngine` port is for, and the notebook depends on the port so only infra changes.
- [URL sources can be slow or fail] → Reader handles HTTP errors and reports them as a message, never a crash.
- [`NOT_CLASSIFIABLE` may puzzle a user expecting four labels] → Rendered distinctly (amber callout) and documented next to the box.

## Migration Plan

Additive only: new runtime dependencies (`marimo`, `altair`) via `uv add`, new modules under each `src/` package, four new test files, plus the `config.yaml` context, `README.md` note, and new `AGENTS.md`. No existing behavior changes, so the rollback is simply removing the new files and dependencies and reverting the docs. No data migrations involved.

## Open Questions

None — the deferrable unknowns (dropdown column selectors, multi-series UX) are recorded as non-goals rather than blockers.