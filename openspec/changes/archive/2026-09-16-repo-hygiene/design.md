## Context

See proposal.md — Why. The repo is a fresh `uv`-managed Python project (Python 3.13+) whose baseline commits accidentally included `__pycache__/*.pyc` bytecode files. There is no root `.gitignore`; `.venv/` and `.pytest_cache/` are currently kept untracked only because uv and pytest each write their own hidden `gitignore` (containing `*`) inside those folders.

## Goals / Non-Goals

**Goals:**
- Make the repo's ignore policy explicit and robust via a single root `.gitignore`.
- Remove generated artifacts already committed to the index without deleting them from disk.
- Leave `git status` clean after the change lands.

**Non-Goals:**
- No changes to `src/`, `tests/`, `pyproject.toml`, or instrumentation behavior.
- No tooling beyond the current stack (ruff/mypy/CI remain deferred per the baseline design).
- No change to whether `.opencode/` is tracked — only documenting its intent.

## Decisions

### 1. Add a root `.gitignore` — single source of truth

A root `.gitignore` is the standard, discoverable place for the project's ignore policy. Alternatives considered:
- Rely on the existing nested self-ignores (`.venv/.gitignore`, `.pytest_cache/.gitignore`): rejected — they are tool-generated, invisible, and give no protection against committing other generated files or secrets.
- Ignore via `~/.config/git/ignore`: rejected — machine-local, not shared with the repo.

Entry set: `.venv/`, `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `build/`, `dist/`, `*.egg-info/`, and `.env`/`.env.*` with `!.env.example` (see Decision 3).

### 2. Untrack committed caches with `git rm -r --cached`

`git rm -r --cached` removes files from the git index while leaving them on disk — exactly what is needed for the 6 tracked `.pyc` files. Files removed only from the index stop appearing in `git status` once covered by the ignore rules. Alternatives considered: no other practical option preserves the working tree.

### 3. Ignore secrets but allow an example env file

`.env*` is ignored except `.env.example`, so a tracked starter template remains possible while real credentials stay out of the repo. The `!.env.example` negation keeps the pattern useful if an env-file convention is adopted later.

### 4. `.opencode/` stays tracked

`.opencode/` (agent skills/commands) is deliberate team tooling and remains committed; `.opencode/node_modules` is already covered by `.opencode/.gitignore`. Recorded for clarity, not changed.

## Risks / Trade-offs

- **[Future tooling introduces new cache dirs (e.g., `.ruff_cache`, `.mypy_cache`)]** → Add their ignore lines in the tooling change when those tools are adopted, rather than speculatively now; the root `.gitignore` makes that a one-line change.
- **[`git rm --cached` looks like deletion at a glance]** → The change commit message and this design record that files remain on disk; `uv run pytest` still runs from a working tree with the caches present.
- **[Negation rules ordering bugs (e.g., `!.env.example` not matching)]** → Git applies the last matching pattern; the explicit `!.env.example` line after `.env*` ensures the exception wins.

## Migration Plan

Rollback is trivial: `git revert` the hygiene commit restores the tracked `.pyc` files and removes `.gitignore` — harmless either way; nothing depends on the new ignore policy at runtime.