# Tasks: Repo Hygiene

References: design → `design.md`.
Project Rule: **End every task with a commit**.

## 1. Ignore Policy

- [x] 1.1 Add a root `.gitignore` covering `.venv/`, `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `build/`, `dist/`, `*.egg-info/`, and `.env`/`.env.*` with `!.env.example` · Verify: `git check-ignore -v .venv .pytest_cache` reports matching patterns, and `git status --porcelain` shows no generated folders 

- [x] 1.2 Untrack the committed bytecode caches with `git rm -r --cached src/core/__pycache__ src/infrastructure/__pycache__ src/entrypoints/__pycache__ tests/__pycache__` · Verify: `git ls-files | grep -E '\.(pyc|pyo)$|__pycache__'` returns nothing, while the cache folders still exist on disk 

- [x] 1.3 Commit the pending `openspec/changes/project-setup/tasks.md` checkbox mark (task 6.1) left uncommitted by the baseline change · Verify: `git status --porcelain` reports a clean tree 

## 2. Verification

- [x] 2.1 Run final hygiene verification: `git status --porcelain` is empty, `uv run pytest` passes green, and `openspec doctor` passes · Verify: all commands exit OK · Commit