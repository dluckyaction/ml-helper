# Proposal

## Why

ML Helper is a portfolio of machine learning techniques, classical and
generative, but its current rules describe a generic hexagonal application and
are duplicated, inconsistently, across `AGENTS.md`, `README.md`, and
`openspec/config.yaml` (the README still allows Pydantic and PyArrow in core).
Before more techniques are added, the intent of each layer — core as the
knowledge base, infrastructure as the computation, entrypoints as the
showcase — must be stated once, normatively, and enforced by tests, so that
future changes and agents follow it without re-deriving it.

## What Changes

- Introduce an `architecture` capability that is the single normative source
  for the layer model:
  - **core** is the knowledge zone: one module per technique or ML concept,
    standard library only, holding vocabulary, thresholds, ports, and
    decisions, documented by a mandatory knowledge docstring (the future
    wiki source).
  - **infrastructure** holds all computation, split into `shared/`
    (technique-agnostic: readers, inference, utilities) and one package per
    technique; technique packages never import each other.
  - **entrypoints** showcase a technique: one package per technique with a
    marimo notebook, and optionally a web delivery that defaults to a static
    WebAssembly export of that notebook. Notebook and web call the same
    technique pipeline, so orchestration is never duplicated.
  - A technique may exist in core only, in core + infrastructure, or in all
    three layers; an entrypoint always implies the other two.
- Replace the blacklist core-purity guard with a standard-library allowlist,
  and replace the "no arithmetic node" guard with a "no computation over
  collections" guard (no loops, comprehensions, or aggregating built-ins in
  core). Scalar comparisons and formulas stay allowed.
- Add guards for knowledge-docstring sections, inter-layer and inter-technique
  imports, technique layout, and the README technique catalog.
- Relax the vocabulary rule: shared infrastructure and generic wording stay
  domain-neutral, while each technique uses its canonical vocabulary inside its
  own core module, infrastructure package, and entrypoint.
- **BREAKING**: move all code under a single `ml_helper` package
  (`ml_helper.core`, `ml_helper.infrastructure`, `ml_helper.entrypoints`), and
  relocate the Syntetos-Boylan code into the new layout:
  `infrastructure/shared/time_series_reader.py`,
  `infrastructure/syntetos/{metrics,pipeline}.py`,
  `entrypoints/syntetos/notebook.py`. The notebook's inline orchestration
  moves, unchanged in behavior, into the Syntetos pipeline.
- Write the Syntetos knowledge docstring describing current behavior; its
  content is revisited in the follow-up Syntetos review change.
- Remove the unused `pydantic` runtime dependency.
- Rewrite `openspec/config.yaml` (portfolio context plus per-artifact rules),
  `AGENTS.md` (short operational checklist pointing at the spec), and
  `README.md` (human overview plus technique catalog).

## Capabilities

### New Capabilities

- `architecture`: layer responsibilities, dependency direction, standard-library
  core, knowledge docstrings, technique layout across layers, entrypoint
  contract (notebook, shared pipeline, WASM-first web delivery), vocabulary,
  language, and the technique catalog.

### Modified Capabilities

- `project-baseline`: the repository structure becomes a single `ml_helper`
  package; the core-purity requirement moves to `architecture`; packaging drops
  Pydantic and lists the actual platform dependencies; documentation and the
  test suite gain the catalog and the architecture guards.

## Impact

- **Code**: every module under `src/` moves; all imports change from
  `core.…` / `infrastructure.…` / `entrypoints.…` to `ml_helper.…`. No
  Syntetos behavior changes (the `syntetos-classification` spec is untouched).
- **Tests**: import paths updated; `test_core_purity.py` and the arithmetic
  guard are replaced by architecture guards; notebook tests target the pipeline.
- **Packaging**: `pyproject.toml` builds `src/ml_helper`; `pydantic` removed.
- **Docs and tooling**: `AGENTS.md`, `README.md`, `openspec/config.yaml`.
- **Out of scope**: reviewing Syntetos semantics, building the WASM export,
  and data-type inference — each is a later change.
