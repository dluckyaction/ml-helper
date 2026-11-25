# Proposal

## Why

The architecture treats every core module as a "technique or ML concept",
so knowledge that is not ML — how tabular files are read, what makes a time
series regular — has no place in the knowledge base, even though techniques
rely on it. The rules also tie knowledge to location: `infrastructure/shared/`
is described as "technique-agnostic", which leaves no way to document a
reusable reader. The next two changes in `ROADMAP_Nov2026.md` add such
foundations, so the rules must allow them first.

The test suite has also grown out of proportion to the project: 62 tests for
about 400 lines of source, half of the architecture guards checking
conventions nobody has broken, and still no test for the one case that
crashes (a series with a single nonzero period, a limitation the knowledge
docstring names). The project needs a testing policy before the next two
changes write more tests.

## What Changes

- Rename the unit of the knowledge base from **technique** to **topic** in
  the architecture spec, `README.md`, `AGENTS.md`, `openspec/config.yaml`,
  the architecture guard, and the package docstrings.
- Define three kinds of topic: **technique** (a method that computes or
  decides), **concept** (an ML idea explained and possibly demonstrated), and
  **foundation** (non-ML groundwork that topics rely on). Any kind may exist
  in core only, in core and infrastructure, or in all three layers.
- Separate two placement rules that are currently merged: knowledge decides
  whether code gets a core module; reuse decides whether its infrastructure
  lives in `infrastructure/<topic>/` or in `infrastructure/shared/`. A core
  module may be implemented in `infrastructure/shared/`, and shared code may
  have no core module at all.
- Rename the README **Technique catalog** to **Knowledge catalog** and add a
  `Kind` column. The kind is documentation: the guard checks only that every
  core module has a row.
- Record a topic's kind in the catalog only, never inferred from where its
  code lives: a technique moved to `shared/` because a second topic needs it
  is still a technique.
- Add a **testing policy**: test what a topic teaches and what a user would
  notice if it broke (formulas, decision rules at their edges, documented
  undefined or rejected cases, one pipeline run per showcased topic, and the
  guards that protect published knowledge); do not test third-party
  libraries, constants, enum members, protocol conformance, UI through
  framework internals, behavior already tested in another layer, or
  conventions that review catches.
- **Remove five architecture guards** (inward dependencies, isolated topic
  infrastructure, no computation in core, single package under `src/`,
  layout across layers). Their rules stay in the architecture spec, enforced
  by review. Three guards stay: standard-library core, knowledge docstring,
  and Knowledge catalog.
- **Remove `tests/test_smoke.py`**: every other test module already imports
  the package, so it catches nothing they do not.
- Tighten the commit rule: every task ends with a commit that leaves
  `uv run pytest` green.

No source behavior changes: no module is added, moved, or removed, and the
Syntetos-Boylan topic keeps its current layout and tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `architecture`: introduce topics and their kinds; rename the
  technique-named requirements to topic; allow core modules implemented in
  `infrastructure/shared/`; rename the catalog to the Knowledge catalog with a
  `Kind` column; state the rules no longer guarded by tests as rules enforced
  by review.
- `project-baseline`: add the testing policy as "Test scope" and "Test
  exclusions"; reduce "Executable Test Suite" to the three kept guards; follow
  the new vocabulary in the packaging and README requirements; state the
  commit rule and the testing policy in the configuration requirement.

## Impact

- **Topics affected:** none directly. This change amends the rules that every
  topic follows; Syntetos-Boylan only gains a `Kind` value (technique) in the
  catalog. Trimming the Syntetos, reader, and notebook tests to the policy
  happens in `tabular-data-and-time-series` and
  `simplify-syntetos-classification`, where that code is rewritten.
- **Layers touched:**
  - core: the `core/__init__.py` docstring wording only; no core module is
    added, so no knowledge docstring is written in this change.
  - infrastructure: the `infrastructure/__init__.py` and
    `infrastructure/shared/__init__.py` docstrings, which today call `shared/`
    technique-agnostic.
  - entrypoints: the `entrypoints/__init__.py` docstring wording only.
- **Tests:** `tests/test_architecture.py` keeps three guards and loses five,
  with their helpers; the catalog guard reads the renamed heading and finds
  the core module column by its header. `tests/test_smoke.py` is deleted. The
  suite goes from 62 to 56 tests. Removing guards is deliberate and made
  through this spec amendment, as `AGENTS.md` requires.
- **Documents:** `README.md` (purpose wording, architecture summary,
  catalog, repository structure), `AGENTS.md` (vocabulary, placement,
  testing, guards), `openspec/config.yaml` (context, testing policy, and
  per-artifact rules).
- **Not in this change:** `entrypoints/shared/` for reusable notebook UI (it
  comes with a second notebook); the reader split into `tabular_data` and
  `time_series` (change `tabular-data-and-time-series`); a testing clause for
  nondeterministic (generative) topics, added with the first such topic.
