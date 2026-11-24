# Design

## Context

See `proposal.md` for the motivation. The current state that shapes the
approach:

- `tests/test_architecture.py` has eight guards in 318 lines. Three protect
  what the project publishes or how core can be reused: standard-library
  core, knowledge docstring sections, and the README catalog. Five check
  conventions: inward dependencies, isolated technique infrastructure, no
  computation in core, a single package under `src/`, and the same name in
  every layer. None of the five has ever failed on real code.
- If any guard failed, nothing a user runs would break: the package imports,
  the notebook runs, and classifications are unchanged. Guards matter only as
  a stop signal for agents, because `AGENTS.md` makes a green suite the
  condition for finishing a task.
- The catalog guard looks for the heading `## Technique catalog` and reads
  the core module name from the **second** cell of each table row. Inserting
  a `Kind` column before it would break that.
- "Technique" appears 35 times in the architecture spec, in three
  `project-baseline` requirements, in `README.md`, `AGENTS.md`,
  `openspec/config.yaml`, in guard names and messages, and in five package
  docstrings (`ml_helper`, `core`, `infrastructure`,
  `infrastructure/shared`, `entrypoints`).
- The `tasks` rule in `openspec/config.yaml` says "Include tests for every
  task that changes behavior", which turns tests into a per-task quota rather
  than a consequence of what a topic teaches.
- No core module is added or changed, so there is no knowledge docstring to
  draft in this change.

## Goals / Non-Goals

**Goals:**

- One word, **topic**, for the unit of the knowledge base everywhere it
  appears, with **technique** kept only where it means that kind.
- A testing policy precise enough to decide, for any proposed test, whether
  it belongs, and stated where agents read it (`openspec/config.yaml`,
  `AGENTS.md`) as well as in the normative spec.
- A guard file reduced to the three guards that protect published knowledge
  and core portability.
- Every task leaves `uv run pytest` and `openspec validate --all` green.

**Non-Goals:**

- Trimming the Syntetos-Boylan, reader, and notebook tests now; that code is
  rewritten in the next two changes, which apply the policy as they go.
- Checking the `Kind` column in tests.
- Adding `entrypoints/shared/`; the spec does not mention it either, so the
  spec and the code never disagree. It comes with a second notebook.
- Moving or splitting any source module; that is
  `tabular-data-and-time-series`.
- A testing clause for nondeterministic topics (LLM output, sampling); it is
  written with the first generative topic, when there is a real case.

## Decisions

### "Topic" as the unit name

Chosen because it reads naturally in prose, paths (`infrastructure/<topic>/`),
and a wiki. Alternatives considered: *entry* (collides with *entrypoints*),
*concept* (undersells methods such as Syntetos-Boylan, and is now one of the
kinds), *article* (too tied to the wiki to name code).

### Keep three guards, remove five

Kept: **standard-library core** (core is the readable, copyable knowledge;
a third-party import there is the drift agents most often introduce, and the
check is ten lines), **knowledge docstring** (the docstrings are the source of
the wiki), and **Knowledge catalog** (the public index of topics). Removed:
the five convention guards. Their rules stay in the architecture spec as
SHALL statements enforced by review; the scenarios that said "the guard
fails" now say "review rejects the change". Alternatives considered: keep all
eight (the maintenance cost shows already: this change would spend a task
renaming guards that check nothing at today's size); replace the import
guards with `import-linter` contracts (declarative, but a new dev dependency
for rules that have never been broken); remove all guards (loses the cheap
protection of the published knowledge).

### Testing policy in the spec, summarized where agents read it

The normative text is two `project-baseline` requirements: "Test scope"
(what to test) and "Test exclusions" (what not to test), split so each states
one behavior. `openspec/config.yaml` carries the policy in its `context` and
replaces the per-task testing quota with "Add a test only for a behavior the
testing policy covers, and name the spec scenario or docstring limitation it
protects". `AGENTS.md` summarizes it in its Testing section. Tests are tied to
what the knowledge docstring states (`Method` decision rules, `Assumptions and
limitations` cases), so they follow what a topic teaches rather than its code
paths. Alternative considered: the policy only in `config.yaml`; rejected
because `AGENTS.md` makes the spec win over every other document.

### The kind is documentation, not a guarded value

The `Kind` column states technique, concept, or foundation for each row, and
the spec requires it, but no test reads it. This follows the testing policy:
a typo in a table column is caught by review. Alternatives considered: parse
and validate the column against the three kinds; a `KIND = "..."` constant in
each core module.

### The catalog guard finds columns by header name

The guard reads the table header row and takes the column titled
`Core module`, wherever it is, instead of a fixed position, and fails when no
such column exists. Alternative considered: change the fixed index from 1 to
2; simpler, but breaks again on the next column change.

### Delete the smoke test

`tests/test_smoke.py` imports the three layer packages. Every other test
module imports from them already, so an import failure is reported anyway.
Under the new exclusions it tests nothing a user would notice that other tests
miss.

### Old scenario titles kept where OpenSpec cannot rename them

OpenSpec 2.1 rejects a MODIFIED requirement that drops a scenario by name, and
has no syntax for renaming a scenario. Six scenarios therefore keep titles
that say "technique" (for example, "Technique requiring secrets") while their
bodies say "topic". The titles stay true, since a technique is a topic.
Alternative considered: remove and re-add each affected requirement, which
renames the scenarios but loses the requirement's rename history.

### The commit rule lives in the config and the baseline spec

"Every task ends with a commit that leaves `uv run pytest` green" goes into
`openspec/config.yaml` (the `tasks` rule) and `AGENTS.md`, and the
`project-baseline` configuration scenario states it. Squash-merging each
change into `main` is a working agreement recorded in `ROADMAP_Nov2026.md`,
not a spec requirement: nothing in the repository can enforce how a pull
request is merged.

## Risks / Trade-offs

- [An agent breaks a convention that no guard checks any more, such as a
  lateral import between two topics] → The rule is still in the spec and in
  `AGENTS.md`, and every change is reviewed before merge. If a convention is
  broken in practice, a guard for it can be added back by a spec change.
- [The policy is applied loosely and tests grow again] → The `tasks` rule
  requires each test to name the scenario or docstring limitation it
  protects, so a test without one is visible in review.
- [A stray "technique" survives the rename where "topic" is meant] → The last
  task greps the specs, docs, config, tests, and source for "technique" and
  checks each remaining occurrence means the kind, the Syntetos-Boylan
  technique, the project's description, or one of the six kept scenario
  titles.
- [The README table changes format and the catalog guard silently reads
  nothing] → The guard fails when it finds no `Core module` column.
- [The kind column drifts from reality because nothing checks it] → It is one
  word per row in a table reviewed with every change that adds a topic;
  accepted.

## Migration Plan

No data or runtime migration. The change renames, documents, and removes
tests; rolling back is reverting the branch. Archive the change on the branch
before the squash-merge, so `openspec/specs/architecture/spec.md` and
`openspec/specs/project-baseline/spec.md` carry the new requirements before
`tabular-data-and-time-series` is proposed.
