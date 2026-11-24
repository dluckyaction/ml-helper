# Roadmap — November 2026

Three OpenSpec changes, applied in order. Each one builds on the previous:
the first sets the rules, the second adds the foundations, the third rebuilds
Syntetos-Boylan on top of them.

| # | Change | Goal |
| --- | --- | --- |
| 1 | `core-foundations` | Broaden core from "techniques" to "topics" of three kinds |
| 2 | `tabular-data-and-time-series` | Replace the time series reader with two documented foundations |
| 3 | `simplify-syntetos-classification` | Fix bugs and turn the notebook into a teaching tool |

Each section lists what is already **decided** and what is still **open**.
Open decisions are settled when the change is proposed, before any code is
written.

## Working agreement for all three changes

- Each change is developed on its own branch.
- Every task ends with a commit that leaves `uv run pytest` green. Tasks are
  sized so this holds: steps that only pass together (for example, renaming
  the README catalog and updating its guard) belong to the same task.
- Each change is squash-merged into `main`, so `main` has one commit per
  change while the branch keeps the per-task history.

---

## 1. `core-foundations`

Amends the architecture and project-baseline specs. No Syntetos or reader
code moves.

### Scope

- Rename the unit of the knowledge base from **technique** to **topic** across
  the architecture spec, `README.md`, `AGENTS.md`, and `openspec/config.yaml`.
- Define three kinds of topic:

  | Kind | Meaning | Examples |
  | --- | --- | --- |
  | technique | A method that computes or decides | Syntetos-Boylan, Croston |
  | concept | An ML idea explained and possibly demonstrated | bias-variance, overfitting |
  | foundation | Non-ML groundwork that techniques rely on | tabular data, time series |

- Rename the README **Technique catalog** to **Knowledge catalog**, with a
  `Kind` column.
- State two independent placement rules:

  | Question | Decides | Answer |
  | --- | --- | --- |
  | Does it have knowledge worth a wiki entry? | Whether it gets a core module | Yes → `core/<name>.py` with a knowledge docstring; no → nothing in core |
  | Who uses it? | Where it lives in infrastructure | One topic → `infrastructure/<topic>/`; several → `infrastructure/shared/` |

  All four combinations are valid. For example, readers have knowledge and
  are shared; a chart theme is shared with no knowledge; Syntetos metrics have
  knowledge and belong to one topic.
- Allow a core module's implementation in `infrastructure/<name>/`, in
  `infrastructure/shared/<name>` (module or package), or nowhere when the
  topic is knowledge only.
- Keep the import rules at two levels: topic packages may import `shared/`;
  `shared/` imports only core and third-party libraries, never a topic;
  topics never import each other.
- Add a **testing policy** to the `project-baseline` spec ("Test scope" and
  "Test exclusions"): test what a topic teaches and what a user would notice
  if it broke (formulas, decision rules at their edges, documented undefined
  or rejected cases, one pipeline run per showcased topic); do not test
  third-party libraries, constants, enum members, protocol conformance, UI
  through framework internals, behavior already tested in another layer, or
  conventions that review catches.
- Reduce `tests/test_architecture.py` to three guards: standard-library core,
  knowledge docstring, and Knowledge catalog (which finds the `Core module`
  column by its header). The inward-dependency, isolated-infrastructure,
  no-computation, single-package, and layout guards are removed; their rules
  stay in the architecture spec, enforced by review. `tests/test_smoke.py` is
  removed too.
- Update `AGENTS.md` and `openspec/config.yaml` with the new vocabulary, the
  testing policy, and the commit rule from the working agreement.

Tasks, each ending green:

1. Rename the catalog, add the `Kind` column, and update the catalog guard.
2. Remove the five convention guards and the smoke test.
3. Update `README.md`, `AGENTS.md`, `openspec/config.yaml`, the package
   docstrings, and this roadmap.
4. Search for stray "technique" wording; validate and archive.

### Decided

- The unit is called **topic**, and the catalog is the **Knowledge catalog**.
- The kinds are **technique**, **concept**, and **foundation**.
- Foundations live in core with a full knowledge docstring, like any topic.
- Knowledge decides whether code gets a core module; reuse decides where it
  lives in infrastructure. The two rules are independent.
- `infrastructure/shared/` stays, for reusable code with or without
  knowledge behind it.
- A topic's kind is recorded in the catalog, never inferred from where its
  code lives: a technique may move to `shared/` when a second topic needs it
  (for example, Croston used by a forecaster comparison) and is still a
  technique.
- The amendment is its own change, separate from any code change.
- **The kind is documentation, not a guarded value.** The catalog guard
  checks only that every core module has a row; no test reads the `Kind`
  column.
- **`entrypoints/shared/` is deferred.** Reusable notebook UI (the path / URL
  / upload picker, the error callout) gets the folder when a second notebook
  needs it; the spec does not mention it until then.
- **A concept may live in core only**, like a foundation; a notebook is
  optional for every kind.
- Tests follow the testing policy, and only three architecture guards
  remain; the other rules are enforced by review.
- A testing clause for nondeterministic (generative) topics is written with
  the first such topic.

### Open

None.

---

## 2. `tabular-data-and-time-series`

Splits `infrastructure/shared/time_series_reader.py` (111 lines, reading
and validation mixed, `LoadedSeries` output) into two foundations, one for
reading and one for series preparation. The code stays in `shared/`, because
every topic that takes a table reuses it; what changes is that each module
gets a core counterpart holding its knowledge.

### Scope

- **`core/tabular_data.py`**: knowledge docstring (CSV, Parquet, source
  kinds, references to RFC 4180, the Apache Parquet spec, RFC 3986); the
  `URL_PATTERN` constant; `SourceKind` (path, URL, upload) and `TableFormat`
  (`.csv`, `.parquet`) enums; the decisions `source_kind(source)` and
  `table_format(name)`; and the `TableReader` port.
- **`infrastructure/shared/tabular_data.py`**: one reader dict from format to library
  function, passing library options (`**options`) straight through. The
  source kind only decides where the file name comes from; the library call
  is the same for a path, a URL, or bytes.
- **`core/time_series.py`**: knowledge docstring (period, regular and
  irregular series, gaps, duplicate timestamps) and the decision on whether a
  series is usable, taken from already-computed counts.
- **`infrastructure/shared/time_series.py`**: select and rename to a two-column
  `date`/`value` frame, sort by date, and count duplicates and gaps.
- Remove `LoadedSeries` and `time_series_reader.py`; move their tests.
- Uploads are passed as bytes plus a file name, so the notebook no longer
  needs the `BytesIO` and `.name` workaround.
- Tests follow the testing policy from `core-foundations`: the reader tests
  moved from `time_series_reader.py` are trimmed to the behaviors the
  knowledge docstrings state.

### Decided

- Reading and series preparation are separate modules and separate topics.
- Topic names: `tabular_data` and `time_series`, both of kind foundation.
- Their implementations stay in `infrastructure/shared/`, paired with
  `core/tabular_data.py` and `core/time_series.py`.
- Path, URL, and upload sources all stay: notebooks are meant to be
  downloaded and run locally as well as on the web.
- The reader passes library options through unchanged.
- The output is a plain two-column frame, not a custom container.

### Open

- **Library: polars only, or keep pandas.** Passing options through ties the
  reader's API to one library, so one should be chosen. Leaning toward
  polars, pending a check that it runs in the Pyodide runtime used by
  WebAssembly exports.
- **Gap detection.** The user passes the period frequency (daily, weekly, …),
  or the frequency is inferred as the most common step between dates.
  Inferring is friendlier but can be fooled by sparse series.
- **What happens when a check fails.** For duplicates and gaps: reject the
  series, warn, or report counts and let the technique decide. Filling gaps
  with zeros is right for demand but wrong for, say, temperature, so filling
  probably belongs to the technique, not the foundation.
- **Date parsing strictness.** Polars rejects some date formats that pandas
  guesses. Acceptable for a teaching tool, but worth stating in the
  docstring's limitations.
- **Error vocabulary.** One error type defined in core (e.g. `ReadError`), or
  one per foundation.
- **Port return type.** Core cannot name a dataframe type, so the port
  returns `Any` or a generic type; agree on which.

---

## 3. `simplify-syntetos-classification`

Rebuilds the Syntetos-Boylan topic on the new foundations: fixes bugs,
simplifies the engine, returns the metrics, and makes the notebook explain
the classification.

### Scope

- **Bugs:**
  - A series with exactly one nonzero period crashes (`[0, 0, 5, 0]` raises
    `TypeError` because the standard deviation is null).
  - Negative values are accepted silently (`[0, -3, 0, 4, 0, -2]` is
    classified lumpy).
- **Core:** clarify that `ADI = n / k` estimates the mean interval between
  demands; drop the invented "ADI = 1.0 is not classifiable" rule; express
  undefined metrics explicitly instead of through `nonzero_periods`.
- **Infrastructure:** one polars function using `group_by` that handles one
  series or many (replacing `compute` and the unused `compute_batch`),
  returning `n`, `k`, ADI, CV², and the type per series; remove the Python
  loop that converts values; the pipeline returns metrics, not only a label.
- **Notebook:** keep path, URL, and upload input; add bundled samples (one
  per quadrant); show the series chart, a metrics table, and an ADI × CV²
  quadrant map with the 1.32 and 0.49 threshold lines and the series plotted
  on it; name the recommended forecasting method per quadrant.
- **Spec:** rewrite around the technique (metric definitions, decision table,
  undefined cases, how the showcase explains the decision); input handling
  becomes one short requirement. This also resolves the OpenSpec warning
  about an over-long requirement.
- **Tests:** replace the notebook tests that use marimo's private
  `_cell_manager` API, and trim the Syntetos tests to the testing policy from
  `core-foundations` (decision rules at the thresholds, undefined cases, one
  pipeline run).

### Decided

- ADI stays `n / k`, with the docstring explaining why it estimates the mean
  interval between demands.
- All three input kinds stay (path, URL, upload).
- The notebook shows ADI, CV², the thresholds, and where the series falls on
  the quadrant map.

### Open

- **Drop the "ADI = 1.0 is not classifiable" rule.** Proposed: drop it, so
  series with no zeros fall in smooth or erratic as in the original scheme.
  Needs confirmation.
- **Keep the metrics port.** Proposed: keep it, as the architecture spec
  requires. Removing it would be an architecture amendment, not part of this
  change. Needs confirmation.
- **Undefined cases.** Whether one nonzero period (CV² undefined) and no
  demand at all (ADI undefined) are both "not classifiable", and whether the
  notebook shows the reason.
- **Leading zeros.** Zeros before a product exists inflate ADI. Trim them
  automatically, offer a switch, or only document the effect.
- **Calendar gaps.** Whether Syntetos fills gaps with zeros (demand
  semantics) or rejects series with gaps; depends on the time series
  decision in change 2.
- **Forecasting recommendations.** Whether the quadrant-to-method mapping
  (SES, SBA, Croston) lives in core as knowledge or only in the notebook text.
- **Bundled samples.** Synthetic with a fixed seed or hand-written; stored as
  package data or next to the notebook.
- **Web delivery.** Add the WebAssembly export in this change or later; it
  depends on the polars and Pyodide check in change 2.
- **Notebook test strategy.** What replaces the private `_cell_manager`
  approach, and how much of the notebook is worth testing once it is thin.
