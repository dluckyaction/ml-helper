# Tasks

Every task ends with a commit that leaves `uv run pytest` green.

## 1. Knowledge catalog

- [x] 1.1 In `README.md`, rename `## Technique catalog` to `## Knowledge catalog` and change the table header to `Topic | Kind | Core module | Infrastructure | Notebook | Web`, with `technique` as the kind of the Syntetos-Boylan row. In the same task, update the catalog guard in `tests/test_architecture.py`: new heading constant, the core module read from the column titled `Core module` instead of a fixed position, a failure when that column is missing, and messages naming the Knowledge catalog. Verify: `uv run pytest` passes, and deleting the Syntetos-Boylan row makes `test_every_core_module_is_in_the_catalog` fail and name `syntetos` (restore the row afterwards). Commit.

## 2. Guards and smoke test

- [x] 2.1 Remove the five convention guards from `tests/test_architecture.py` (`test_dependencies_point_inward`, `test_technique_infrastructure_is_isolated`, `test_core_performs_no_computation_over_collections`, `test_ml_helper_is_the_only_package_under_src`, `test_techniques_are_laid_out_consistently`) together with the helpers and constants only they used. Update the module docstring to say the file guards published knowledge and core portability, citing `project-baseline` "Executable Test Suite". Verify: the file defines exactly the standard-library core, knowledge docstring, and Knowledge catalog guards, and `uv run pytest` passes with 57 tests. Commit.
- [x] 2.2 Delete `tests/test_smoke.py`. Verify: `uv run pytest` passes with 56 tests. Commit.

## 3. Documentation and configuration

- [x] 3.1 Update `README.md`: "Every topic answers three questions" in Purpose; the architecture summary describes topics, the three kinds, and the two placement rules (knowledge decides the core module, reuse decides `infrastructure/<topic>/` versus `infrastructure/shared/`), and says the test suite guards the published knowledge while the other rules are enforced by review; the repository structure comments use `<topic>`; the quickstart comment says "open a topic notebook". Keep the link to `openspec/specs/architecture/spec.md`. Verify: `uv run pytest` passes and the README still contains every section required by `project-baseline` "Reference Documentation". Commit.
- [x] 3.2 Update `AGENTS.md`: topics and kinds in "Project" and "Where new code goes", the placement rules as a short table, "a topic package never imports another topic", the README Knowledge catalog, and "one capability per topic". Replace the Testing section with a summary of the testing policy (what to test, what not to test, each test names the scenario or docstring limitation it protects) and drop "Notebook tests run cells against stubbed inputs". Reduce the Guards section to the three guards and state that the other rules are enforced by review. Add the commit rule "every task ends with a commit that leaves `uv run pytest` green". Keep the link to the architecture spec. Verify: the file links to `openspec/specs/architecture/spec.md` and contains no rule that contradicts the delta specs. Commit.
- [ ] 3.3 Update `openspec/config.yaml`: the `context` describes topics, kinds, and the placement rules, and states the testing policy; the `proposal` rule names the topic and its kind; the `specs` rule says one capability per topic; the `tasks` rules become "End every task with a commit that leaves `uv run pytest` green", "Include tasks for the knowledge docstring and the README Knowledge catalog row whenever a core module is added or changed", and "Add a test only for a behavior the testing policy covers, and name the spec scenario or docstring limitation it protects", replacing "Include tests for every task that changes behavior". Verify: `openspec doctor` parses the configuration, `openspec validate --all` passes, and `uv run pytest` passes. Commit.
- [ ] 3.4 Update the package docstrings of `ml_helper`, `ml_helper.core`, `ml_helper.infrastructure`, `ml_helper.infrastructure.shared`, and `ml_helper.entrypoints` to the topic vocabulary; `shared` is described as code reused by several topics, with or without a core module, instead of "technique-agnostic". Verify: `uv run pytest` passes. Commit.
- [ ] 3.5 Update `ROADMAP_Nov2026.md`: in section 1, move the settled open items to Decided (the kind is documentation and not guarded; `entrypoints/shared/` is deferred; a concept may live in core only) and add the testing policy and the reduced guards to its scope; in sections 2 and 3, note that their tests follow the testing policy. Verify: section 1 has no open item this change resolved. Commit.

## 4. Final check

- [ ] 4.1 Search `openspec/specs`, `openspec/changes/core-foundations`, `README.md`, `AGENTS.md`, `openspec/config.yaml`, `tests/`, and `src/` for "technique" (case-insensitive) and confirm each remaining occurrence means the kind, the Syntetos-Boylan technique, the project's description as a portfolio of ML techniques, or one of the six scenario titles kept by design; search the same places for "guard" and confirm each mention refers to one of the three kept guards. Run `uv run pytest` (56 tests), `openspec validate core-foundations --strict`, and `openspec validate --all`; all pass. Commit any fixes.

## Workflow follow-up

- Archive the change on the branch with `openspec archive core-foundations`, so the main specs carry the new requirements, and verify `openspec validate --all` still passes.
- Open a pull request from `core-foundations` to `main` and squash-merge it.
