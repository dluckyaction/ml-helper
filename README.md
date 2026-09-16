# ML Helper

A platform for machine learning experimentation and analysis, built on a
hexagonal (clean) architecture with a strict pure core.

## Purpose

ML Helper supports machine learning workflows — data processing, model
experimentation, and analysis — while keeping the domain core free of any
UI or framework coupling. Domain logic stays pure and testable; framework
dependencies live behind interfaces in the infrastructure and entrypoint
layers.

## Tech Stack

- **Python 3.13+**
- **uv** — package and environment management
- **Pandas**, **Polars**, **PyArrow** — tabular data processing
- **Pydantic** — data validation and models
- **Pytest** — test runner

## Architecture

Hexagonal architecture with three layers under `src/`:

```
                          ┌───────────────────────┐
                          │      entrypoints      │  UI / API / CLI
                          └───────────┬───────────┘
                                      │
                          ┌───────────▼───────────┐
                          │    infrastructure     │  Adapters: I/O,
                          │   (Pandas, Polars,    │  connectors,
                          │   PyArrow adapters)   │  persistence
                          └───────────┬───────────┘
                                      │
                          ┌───────────▼───────────┐
                          │         core          │  Pure domain: models,
                          │  (stdlib, Pydantic,   │  metrics, ports
                          │   PyArrow only)       │  (Protocol)
                          └───────────────────────┘
```

### Pure Core Rule

`src/core` must remain pure Python: it may only use the standard library,
Pydantic, and PyArrow. It SHALL NOT import **Streamlit**, **Gradio**, or
**FastAPI**. This rule is enforced automatically by the AST-based purity
guard in `tests/test_core_purity.py`, which fails with the offending file
name if the rule is broken.

## Repository Structure

```
.
├── openspec/                # OpenSpec workspace (changes, specs, config)
├── src/
│   ├── core/                # Pure domain: models, metrics, ports
│   ├── infrastructure/      # Adapters: I/O, connectors, persistence
│   └── entrypoints/         # UI/API/CLI entrypoints
├── tests/                   # Pytest suite (smoke + purity guard)
├── pyproject.toml           # Packaging, dependencies, pytest config
└── README.md
```

## Quickstart

```bash
uv sync                 # create the environment and install dependencies
uv run pytest           # run the test suite
```

The project targets Python 3.13+; `uv` will manage the interpreter for you.

## OpenSpec Workflow

This repository uses [OpenSpec](https://openspec.dev) for change management.

- Changes live under `openspec/changes/<name>/` with `proposal.md`,
  `specs/**/spec.md`, `design.md`, and `tasks.md`.
- Every task must end with a commit.
- Before marking a task complete, run `uv run pytest` to confirm the suite
  passes.
- Useful commands:
  - `openspec list` — list active changes
  - `openspec status --change "<name>"` — inspect a change
  - `openspec doctor` — validate the workspace configuration