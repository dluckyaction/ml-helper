# Tasks: Repository Baseline (Task 0)

References: specs → `specs/project-baseline/spec.md`, design → `design.md`.
Project Rule: **End every task with a commit**.

## 1. OpenSpec Configuration

- [x] 1.1 Rewrite `openspec/config.yaml` as valid YAML: `context` with tech stack (Python 3.13+, uv, Pandas, Polars, PyArrow, Pydantic, Pytest), domain, hexagonal architecture with strict pure core rule in `src/core`, and artifact language rule (English); `rules` requiring task commits; `operations.apply` instructing to run `uv run pytest` before marking tasks complete · Verify: `openspec doctor` parses without errors · Commit

## 2. Packaging with `uv`

- [x] 2.1 Initialize project with `uv init` setting `requires-python = ">=3.13"`, add runtime dependencies (`pandas`, `polars`, `pyarrow`, `pydantic`), dev optional dependencies (`pytest`), and `[tool.pytest.ini_options] testpaths = ["tests"]` in `pyproject.toml` · Verify: `uv sync` completes without errors · Commit

## 3. Hexagonal Structure

- [x] 3.1 Create `src/core/`, `src/infrastructure/`, `src/entrypoints/`, each with `__init__.py`, and the `tests/` directory · Verify: `uv run python -c "import core, infrastructure, entrypoints"` runs without errors · Commit

## 4. Baseline Tests

- [x] 4.1 Add a smoke test in `tests/` that imports `core`, `infrastructure`, and `entrypoints` · Verify: `uv run pytest` executes green · Commit
- [x] 4.2 Add core purity guard in `tests/`: using `ast` (stdlib), parse all files in `src/core` and fail on any import of `streamlit`, `gradio`, or `fastapi` · Verify: `uv run pytest` passes green; confirm guard catches injected forbidden imports · Commit

## 5. Documentation

- [x] 5.1 Create `README.md` containing: project purpose, tech stack, architecture diagram, repo structure, quickstart guide (`uv sync`, `uv run pytest`), and OpenSpec workflow reference · Verify: manual review confirms all sections exist · Commit

## 6. Integration Verification

- [x] 6.1 Run final baseline verification: `openspec doctor` passes, `uv run pytest` runs green, and `uv sync` is reproducible · Verify: all commands exit OK · Commit