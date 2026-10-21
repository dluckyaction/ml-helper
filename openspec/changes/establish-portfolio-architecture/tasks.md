# Tasks

## 1. Package restructure

- [x] 1.1 Move `src/core`, `src/infrastructure`, `src/entrypoints` under `src/ml_helper/` with `git mv`, add `src/ml_helper/__init__.py`, and set `packages = ["src/ml_helper"]` in `pyproject.toml`; verify `uv sync` succeeds and `uv run python -c "import ml_helper.core, ml_helper.infrastructure, ml_helper.entrypoints"` exits 0; commit
- [x] 1.2 Relocate Syntetos modules per design D2 (`infrastructure/shared/time_series_reader.py`, `infrastructure/syntetos/metrics.py`, `entrypoints/syntetos/notebook.py`), update every import in `src/` and `tests/` to `ml_helper.…`, and update the smoke test; verify `uv run pytest` passes; commit
- [x] 1.3 Remove `pydantic` from the runtime dependencies and refresh `uv.lock`; verify `uv sync` and `uv run pytest` pass; commit

## 2. Syntetos pipeline

- [x] 2.1 Create `infrastructure/syntetos/pipeline.py` per design D3, with tests in `tests/test_syntetos_pipeline.py` covering a classified CSV path, an uploaded stream, a missing file, and an unknown column; verify the new tests pass; commit
- [x] 2.2 Make the notebook's pipeline cell call the pipeline instead of `load_time_series` and `classify_series` directly, keeping messages and outputs unchanged, and update `tests/test_notebook_import.py`; verify `uv run pytest` passes; commit

## 3. Knowledge and catalog content

- [x] 3.1 Rewrite the `core/syntetos.py` module docstring as a knowledge entry with the five headings (Overview, Definitions, Method with ADI and CV² formulas and the quadrant rules, Assumptions and limitations, References to Syntetos, Boylan & Croston 2005), describing current behavior; reference it from the docstrings of `infrastructure/syntetos/metrics.py`, `pipeline.py`, and the notebook; verify `uv run pytest` passes; commit
- [x] 3.2 Give `core/__init__.py`, `infrastructure/__init__.py`, `infrastructure/shared/__init__.py`, and `entrypoints/__init__.py` package docstrings describing each layer's role in one or two sentences; verify `uv run pytest` passes; commit

## 4. Architecture guards

- [ ] 4.1 Create `tests/test_architecture.py` with the standard-library core and dependency-direction/lateral-import guards (design D4); verify they pass on the repository and fail when a temporary `import pandas` or a lateral import is introduced (check manually, then revert); commit
- [ ] 4.2 Add the computation guard to `tests/test_architecture.py`, delete `tests/test_core_purity.py` and `test_core_module_performs_no_arithmetic`; verify it passes and fails on a temporary `for` loop in core (check manually, then revert); commit
- [ ] 4.3 Add the knowledge-docstring guard; verify it passes and fails when a heading is removed from `core/syntetos.py` (check manually, then revert); commit
- [ ] 4.4 Add the layout guard (matching core module, `pipeline.py`, `notebook.py`); verify it passes and fails when `entrypoints/syntetos/notebook.py` is temporarily renamed (check manually, then revert); commit

## 5. Documentation and OpenSpec configuration

- [ ] 5.1 Rewrite `README.md` per design D6–D7 (portfolio purpose, stack, architecture summary linking to `openspec/specs/architecture/spec.md`, structure, technique catalog with the `syntetos` row, quickstart including how to open the notebook); verify the README contains each element; commit
- [ ] 5.2 Add the catalog guard to `tests/test_architecture.py`; verify it passes and fails when the `syntetos` row is temporarily removed (check manually, then revert); commit
- [ ] 5.3 Rewrite `AGENTS.md` as the operational checklist linking to the spec (design D7); verify it links to `openspec/specs/architecture/spec.md` and no longer contradicts it (no Pydantic or PyArrow allowed in core, no blanket "demand" ban); commit
- [ ] 5.4 Rewrite `openspec/config.yaml` `context` and add the per-artifact `rules` from design D7; verify `openspec instructions proposal --change establish-portfolio-architecture --json` shows the new context and rules, and `openspec validate --all` passes; commit

## 6. Verification

- [ ] 6.1 Run `uv run pytest`, `openspec validate --all`, and open the notebook with `uv run marimo run src/ml_helper/entrypoints/syntetos/notebook.py` to confirm it serves and classifies a sample CSV; commit any fixes
