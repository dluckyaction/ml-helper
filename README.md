# ML Helper

A portfolio of machine learning techniques — classical and generative — each
documented as knowledge, implemented as efficient computation, and showcased
in an interactive notebook.

## Purpose

Every technique in ML Helper answers three questions, one per layer:

- **What is it and why does it work?** A documented core module: definitions,
  formulas, decision rules, assumptions, and references. These docstrings are
  the source of a future wiki.
- **How is it computed efficiently?** Vectorized infrastructure behind the
  ports the core module defines.
- **How does it look in practice?** A marimo notebook for developers and,
  when it makes sense, a web version that runs in the browser.

Not every piece of knowledge needs all three: a concept can live in core
alone, or in core and infrastructure without a showcase.

## Tech Stack

- **Python 3.13+** and **uv** for environments and packaging
- **pandas**, **polars**, **PyArrow** for tabular computation
- **marimo** and **Altair** for notebooks and charts
- **pytest** for tests, **OpenSpec** for change management

## Architecture

The normative rules live in
[`openspec/specs/architecture/spec.md`](openspec/specs/architecture/spec.md).
In short:

```
entrypoints ──▶ infrastructure ──▶ core
 showcase        computation        knowledge
 (notebook,      (shared/ and one   (one documented module per
  web export)     package per        technique or concept,
                  technique)         standard library only)
```

- **core** holds vocabulary, thresholds, ports, and decisions. It imports only
  the standard library and never computes over data. Every module opens with a
  knowledge docstring: Overview, Definitions, Method, Assumptions and
  limitations, References.
- **infrastructure** does the computation. `shared/` is technique-agnostic
  (readers, utilities); every other subpackage implements the core module of
  the same name, exposes a `pipeline.py` when the technique is showcased, and
  never imports another technique.
- **entrypoints** showcase a technique: a marimo `notebook.py` that collects
  input, calls the pipeline, and presents the result. Web delivery defaults to
  a static WebAssembly export of that notebook.

`tests/test_architecture.py` enforces these rules.

## Technique catalog

| Technique | Core module | Infrastructure | Notebook | Web |
| --- | --- | --- | --- | --- |
| Syntetos-Boylan demand classification | `syntetos` | yes | yes | no |

## Repository Structure

```
.
├── openspec/                    # specs (normative) and changes
├── src/ml_helper/
│   ├── core/                    # knowledge: one module per technique/concept
│   ├── infrastructure/
│   │   ├── shared/              # technique-agnostic adapters
│   │   └── <technique>/         # engines and pipeline for one technique
│   └── entrypoints/
│       └── <technique>/         # notebook.py (and web delivery)
├── tests/
├── AGENTS.md                    # checklist for AI agents
└── pyproject.toml
```

## Quickstart

```bash
uv sync                  # create the environment and install dependencies
uv run pytest            # run the test suite

# open a technique notebook (edit mode, or app mode with `run`)
uv run marimo edit src/ml_helper/entrypoints/syntetos/notebook.py
```

## OpenSpec Workflow

Every change goes through [OpenSpec](https://openspec.dev): a change under
`openspec/changes/<name>/` with `proposal.md`, `specs/**/spec.md`,
`design.md`, and `tasks.md`; each task ends with a commit and a green
`uv run pytest`. Validate with `openspec validate --all`, and archive the
change once implemented so `openspec/specs/` stays the source of truth.
