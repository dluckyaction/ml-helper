# AGENTS.md

Operational checklist for AI agents working in this repository. The normative
rules are in
[`openspec/specs/architecture/spec.md`](openspec/specs/architecture/spec.md);
when this file and the spec disagree, the spec wins and this file is fixed.

## Project

ML Helper is a portfolio of machine learning techniques, classical and
generative. Each technique is documented as knowledge (core), computed
efficiently (infrastructure), and optionally showcased (entrypoints).

## Layers

| Layer | Path | Owns | May import |
| --- | --- | --- | --- |
| core | `src/ml_helper/core/` | vocabulary, thresholds, ports, decisions, knowledge docstrings | standard library, `ml_helper.core` |
| infrastructure | `src/ml_helper/infrastructure/` | all computation, I/O, pipelines | core, third-party |
| entrypoints | `src/ml_helper/entrypoints/` | marimo notebooks, web delivery | core, infrastructure, third-party |

## Where new code goes

- **A new technique or ML concept** → `core/<name>.py` with a knowledge
  docstring (`## Overview`, `## Definitions`, `## Method`,
  `## Assumptions and limitations`, `## References`, in that order) and a row
  in the README technique catalog.
- **Its computation** → `infrastructure/<name>/`, behind a port defined in
  `core/<name>.py`. Vectorize; never loop over data in Python.
- **Technique-agnostic code** (readers, inference, utilities) →
  `infrastructure/shared/`. Code needed by two techniques moves here; a
  technique package never imports another technique.
- **A showcase** → `entrypoints/<name>/notebook.py` plus
  `infrastructure/<name>/pipeline.py`. The notebook collects input, calls the
  pipeline, and presents the result — no orchestration in the notebook.
- **Web delivery** → static WebAssembly export of the notebook by default;
  server-run only for secrets, GPU, or browser-unavailable dependencies, with
  the reason stated in the technique's spec.
- **A dependency used by one technique only** → optional dependency group
  named after the technique.

Use the same snake_case technique name in every layer.

## Core never computes

Core functions take already-computed metrics (scalars or metric objects).
No loops, comprehensions, `sum`/`min`/`max`/`len`/`sorted`/`map`/`filter`,
or `statistics` in core; a core function may receive a collection only to pass
it unchanged to a port. Scalar comparisons and formulas are fine.

## Vocabulary and language

- `infrastructure/shared/` and generic wording are domain-neutral ("series",
  "date column", "value column").
- A technique uses its canonical vocabulary (e.g. "demand" for
  Syntetos-Boylan) only inside its own core module, infrastructure package,
  and entrypoint.
- Name modules and capabilities after algorithms or ML concepts, never after a
  product domain.
- Everything — code, docstrings, UI strings, docs, OpenSpec — is in English.

## Guards

`tests/test_architecture.py` enforces the standard-library core, inward and
isolated imports, no computation in core, knowledge docstrings, technique
layout, and the README catalog. Do not weaken a guard to make a change pass;
amend the spec in its own change instead.

## Testing

- `uv run pytest` must pass before a task is marked complete.
- Core decisions are tested with a test double for the engine port.
- Infrastructure is tested against hand-computed values, stated in the test
  module docstring.
- Pipelines are tested directly, without a UI.
- Notebook tests run cells against stubbed inputs; keep notebooks thin.

## OpenSpec workflow

- Every change lives under `openspec/changes/<name>/` with `proposal.md`,
  `specs/**/spec.md`, `design.md`, and `tasks.md`.
- One capability per technique, named after the algorithm or concept.
- Every task ends with a commit.
- Validate with `openspec validate --all`; archive implemented changes so
  `openspec/specs/` stays current.
