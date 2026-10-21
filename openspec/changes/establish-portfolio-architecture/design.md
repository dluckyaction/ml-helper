# Design

## Context

See proposal.md for motivation. Current state relevant to the approach:

- Packages `core`, `infrastructure`, `entrypoints` sit directly under `src/`
  and are built as three top-level wheel packages.
- Syntetos-Boylan code: `core/syntetos.py`,
  `infrastructure/syntetos_metrics.py`, `infrastructure/time_series_reader.py`,
  `entrypoints/syntetos_classifier/notebook.py`. The notebook's pipeline cell
  performs the orchestration (resolve source, load, classify) inline.
- Guards: `tests/test_core_purity.py` blacklists three UI frameworks;
  `tests/test_core_syntetos.py::test_core_module_performs_no_arithmetic`
  rejects any arithmetic node in `core/syntetos.py` only.
- `pydantic` is declared but never imported; `pyarrow` is needed by pandas to
  read Parquet.

## Goals / Non-Goals

**Goals:**

- Make the repository conform to the `architecture` spec at the end of the
  change, with every rule backed by a test.
- Keep Syntetos behavior byte-for-byte equivalent: same results, same error
  messages, same notebook UI.

**Non-Goals:**

- Changing Syntetos semantics (thresholds, Not Classifiable rules, batch API).
  That is the follow-up review change, which will also revise the knowledge
  docstring written here.
- Building the WebAssembly export, generating the wiki, or adding data-type
  inference.

## Decisions

### D1. Single `ml_helper` package with a src layout

Code moves to `src/ml_helper/{core,infrastructure,entrypoints}` with `git mv`
to keep history; `pyproject.toml` builds `packages = ["src/ml_helper"]`.
*Alternative*: keep three top-level packages. Rejected because `import core`
collides easily with other installed distributions and hides which project a
module belongs to.

### D2. Target layout for Syntetos

```
src/ml_helper/
  core/syntetos.py
  infrastructure/shared/time_series_reader.py
  infrastructure/syntetos/metrics.py        (was syntetos_metrics.py)
  infrastructure/syntetos/pipeline.py       (new, extracted from the notebook)
  entrypoints/syntetos/notebook.py          (was syntetos_classifier/)
```

Class and function names (`PolarsSyntetosMetrics`, `load_time_series`,
`classify_series`, …) are kept so the move stays mechanical.

### D3. Pipeline boundary

`pipeline.py` exposes one function taking a reader `Source` plus the date and
value column names and returning the loaded series together with its
`SeriesType`; it raises `TimeSeriesReadError` on bad input. It builds the
default `PolarsSyntetosMetrics` engine and accepts an engine override for
tests. Turning form widgets into a `Source` (the "path or upload, not both"
check and wrapping upload bytes in a named stream) stays in the notebook,
because it is input collection specific to that UI; the web export reuses the
same notebook, so nothing is duplicated.
*Alternative*: let the pipeline accept raw form values. Rejected because it
would couple infrastructure to marimo's widget shapes.

### D4. One architecture test module, AST-based

`tests/test_architecture.py` parses every module under `src/ml_helper` with
`ast` (no imports executed) and holds all guards:

- **Standard-library core**: every absolute import root in core must be in
  `sys.stdlib_module_names` or be `ml_helper` (and then `ml_helper.core`);
  relative imports are resolved against the module path.
- **Dependency direction and lateral imports**: resolve each import to a
  layer and, for infrastructure, to a technique (`shared` or the subpackage
  name), then check the allowed edges from the spec.
- **Computation**: in core, reject `For`, `AsyncFor`, `While`, `ListComp`,
  `SetComp`, `DictComp`, `GeneratorExp`, calls to `sum`, `min`, `max`, `len`,
  `sorted`, `map`, `filter`, and imports of `statistics`. Scalar arithmetic is
  allowed, so the Syntetos-only "no arithmetic node" guard is removed.
- **Knowledge docstring**: `ast.get_docstring` of each core module must contain
  the five `## ` headings in order.
- **Layout**: techniques are the subpackages of `infrastructure` other than
  `shared`, and the subpackages of `entrypoints`; check the matching core
  module, `pipeline.py`, and `notebook.py`.
- **Catalog**: parse the README catalog table and check every core module
  name appears in its first column.

Each guard reports all offenders with file paths, not only the first.
*Alternative*: an import-linter tool. Rejected for now: it adds a dependency
and cannot express the docstring, layout, or computation rules, so AST tests
would be needed anyway.

### D5. Knowledge docstrings as Markdown

Headings are Markdown `## ` inside the module docstring so a future
mkdocs + mkdocstrings site renders them unchanged. Formulas are written in
plain text or inline code (`ADI = periods / nonzero_periods`) rather than
LaTeX, so they read well in a terminal and in the rendered wiki.

### D6. Catalog format

A Markdown table in `README.md` under `## Technique catalog` with columns
`Technique | Core module | Infrastructure | Notebook | Web`. The core module
column holds the module name in backticks (`syntetos`), which is what the
guard matches.

### D7. Documentation roles and OpenSpec configuration

- `openspec/specs/architecture/spec.md` is normative.
- `AGENTS.md` becomes a short operational checklist (layer table, where new
  code goes, guard list, test and commit rules) that links to the spec.
- `README.md` is the human overview, catalog, and quickstart, linking to the
  spec.
- `openspec/config.yaml`: `context` rewritten around the portfolio and layer
  roles, kept short and pointing at the spec; per-artifact `rules`:
  - proposal: name the technique and state which layers it touches and why
    the others are not touched;
  - specs: one capability per technique named after the algorithm or concept;
    a technique with web delivery states WebAssembly or server and why;
  - design: when core changes, include the knowledge docstring draft;
  - tasks: include knowledge docstring, README catalog, and test tasks where
    applicable; end every task with a commit.

### D8. Dependencies

Remove `pydantic`. Keep `pandas`, `polars`, `pyarrow`, `marimo`, `altair` as
the platform baseline, because the reader, the notebook contract, and charts
apply to every showcased technique. No optional groups are created yet; the
rule applies from the next technique-exclusive dependency.

## Risks / Trade-offs

- [Every import path changes] → the move is done in one task with the full
  suite run before committing; no external consumers exist yet.
- [The computation guard rejects a legitimate construct in future core code,
  e.g. iterating over an enum] → the guard's message points at the spec; if a
  real need appears, the spec is amended in its own change rather than adding
  silent exceptions.
- [The Syntetos docstring documents behavior that the review may change] →
  the docstring describes current behavior faithfully and the review change
  owns its revision.
- [Markdown catalog parsing is brittle] → the guard only reads the first
  backticked token of each row under the catalog heading and fails with a
  clear message when the table is missing.

## Migration Plan

1. Restructure with `git mv`, update imports and `pyproject.toml`, run
   `uv sync` and the full suite.
2. Extract the pipeline, then add guards, docstring, and documentation.
3. Rollback is reverting the branch; nothing outside the repository depends
   on the old import paths.
