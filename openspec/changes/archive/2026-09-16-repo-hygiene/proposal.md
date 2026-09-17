## Why

The baseline commits polluted the repository with generated artifacts: the repo has no root `.gitignore`, so `__pycache__/*.pyc` bytecode files (6 files) were committed during setup, and `.venv/` and `.pytest_cache/` only stay untracked because uv and pytest drop a hidden `*` gitignore inside each folder — fragile and invisible. Without an explicit ignore policy, generated folders and secrets can be committed by accident.

## What Changes

- Adds a root `.gitignore` declaring the project's ignore policy explicitly:
  - `.venv/` virtual environment
  - `__pycache__/` and compiled Python (`*.py[cod]`)
  - `.pytest_cache/` pytest cache
  - build artifacts (`build/`, `dist/`, `*.egg-info/`)
  - local secrets (`.env`, `.env.*`) while keeping `.env.example` committable
- Untracks the already-committed `__pycache__` files with `git rm -r --cached` (files stay on disk; only the git index is cleared).
- Commits the pending `project-setup/tasks.md` checkbox mark left dangling from that change.
- **BREAKING**: None — version-control hygiene only, no runtime impact.

## Capabilities

### New Capabilities

None — this is pure tooling/repo-hygiene with no spec-level behavior change.
The change declares `skip_specs: true` in `.openspec.yaml`.

### Modified Capabilities

None.

## Impact

- **Code**: None. No source, test, or configuration changes to `src/`, `tests/`, or `pyproject.toml`.
- **Version control**: `.gitignore` added; 6 generated `.pyc` files removed from the index (remain on disk); one pending task file mark committed.
- **Dependencies**: None.
- **Out of Scope**: CI configuration, linting/formatting/type-check tooling (deferred by the baseline design), and any change to `.opencode/` tracking except documenting its intent.