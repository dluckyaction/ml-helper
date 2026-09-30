# AGENTS.md

Conventions for AI agents working in this repository.

## Project

ML Helper is a **generic** platform for machine learning experimentation and
analysis: data processing, model experimentation, and analysis. It is not tied
to any product domain.

## Architecture

Hexagonal (clean) architecture under `src/` with three layers:

| Layer | Owns | May import |
| --- | --- | --- |
| `src/core` | domain vocabulary, thresholds, ports, decisions | stdlib, Pydantic, PyArrow |
| `src/infrastructure` | adapters: I/O, connectors, persistence, engines | core + third-party |
| `src/entrypoints` | UI, API, CLI | core + infrastructure |

Dependencies point inward only: `entrypoints → infrastructure → core`.
`core` never imports from the layers above it.

## Rule 1 — Pure core

`src/core` SHALL NOT import **streamlit**, **gradio**, or **fastapi**, and
SHALL stay free of third-party dependencies in practice. The AST-based guard
in `tests/test_core_purity.py` enforces the framework ban.

## Rule 2 — Calculations live in infrastructure

This is the rule agents break most often, so it is stated explicitly.

`src/core` contains **vocabulary, thresholds, ports, and decisions only**.
Core modules SHALL NOT perform numeric computation — no `mean`, no `std`, no
sums over per-period data, no division that aggregates a series.

Why: Python loops over per-period values are far too slow for real
workloads. Anything that scales is vectorized and therefore
library-dependent, which makes it an infrastructure concern. Math placed in
core has to be rewritten later to vectorize; math behind a port does not.

The pattern to follow:

```python
# src/core/<domain>.py — decision only
@dataclass(frozen=True)
class SeriesMetrics:
    ...

class MetricsEngine(Protocol):
    def compute(self, values) -> SeriesMetrics: ...

def classify(metrics: SeriesMetrics) -> Type:
    ...  # comparisons only

# src/infrastructure/<domain>_metrics.py — computation
class PolarsMetrics:
    def compute(self, values) -> SeriesMetrics:
        ...  # vectorized expressions
```

Entrypoints inject the concrete engine; core never learns which one it is.

`tests/test_core_syntetos.py::test_core_module_performs_no_arithmetic`
AST-parses `src/core/syntetos.py` and fails on any arithmetic node or metric
helper call. Extend that guard when adding a new core module.

## Rule 3 — Naming & semantics

ML Helper is a generic ML tool, so **application vocabulary is
domain-neutral**. Readers, adapters, and notebooks speak of "series", "date
column", and "value column".

Domain-specific terms — "demand", "SKU", "forecast", "backorder" — are
permitted **only inside algorithm-inherent code**: the core module encoding
that algorithm's vocabulary and the infrastructure module implementing its
math. In this repo that is the Syntetos-Boylan classification, so
`src/core/syntetos.py` and `src/infrastructure/syntetos_metrics.py` may say
"demand" because the algorithm defines it.

They SHALL NOT appear in `src/infrastructure/time_series_reader.py`, in
`src/entrypoints/`, or in any user-visible string.

Name capabilities, modules, and files after algorithms or generic ML
concepts, never after a product domain.

## Testing

- `uv run pytest` before marking any task complete.
- Domain decisions are unit-tested with a **test double** for the engine port,
  since core computes nothing and cannot be tested with real inputs alone.
- Adapters are tested against hand-computed expected values. State the
  hand computation in the test module docstring.
- Notebooks stay thin views; assert they import rather than trying to test
  their cells.

## OpenSpec workflow

- Changes live under `openspec/changes/<name>/` with `proposal.md`,
  `specs/**/spec.md`, `design.md`, and `tasks.md`.
- Every task ends with a commit.
- All OpenSpec artifacts and repository documentation are written in
  **English**.
- Validate with `openspec validate --all` before considering planning done.
