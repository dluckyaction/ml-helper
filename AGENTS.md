# AGENTS.md

Operational checklist for AI agents working in this repository. The normative
rules are in
[`openspec/specs/architecture/spec.md`](openspec/specs/architecture/spec.md);
when this file and the spec disagree, the spec wins and this file is fixed.

## Project

ML Helper is a portfolio of machine learning techniques, classical and
generative. The knowledge base is organized in **topics**. Each topic is
documented as knowledge (core), and may be computed efficiently
(infrastructure) and showcased (entrypoints).

Every topic is of exactly one **kind**:

- **technique**: a method that computes or decides (e.g. Syntetos-Boylan);
- **concept**: an ML idea explained and possibly demonstrated;
- **foundation**: non-ML groundwork that topics rely on (e.g. reading tabular
  files).

Any kind may exist in core only, in core and infrastructure, or in all three
layers. The kind is recorded in the README Knowledge catalog, never inferred
from where the code lives.

## Layers

| Layer | Path | Owns | May import |
| --- | --- | --- | --- |
| core | `src/ml_helper/core/` | vocabulary, thresholds, ports, decisions, knowledge docstrings | standard library, `ml_helper.core` |
| infrastructure | `src/ml_helper/infrastructure/` | all computation, I/O, pipelines | core, third-party |
| entrypoints | `src/ml_helper/entrypoints/` | marimo notebooks, web delivery | core, infrastructure, third-party |

## Where new code goes

Two independent rules place a topic's code:

| Question | Decided by | Answer |
| --- | --- | --- |
| Does it get a core module? | knowledge | yes, if it has knowledge worth documenting |
| Where does its infrastructure live? | reuse | `infrastructure/<topic>/` if one topic uses it; `infrastructure/shared/` if several do, with or without a core module |

- **A new topic** → `core/<topic>.py` with a knowledge docstring
  (`## Overview`, `## Definitions`, `## Method`,
  `## Assumptions and limitations`, `## References`, in that order) and a row,
  with its kind, in the README Knowledge catalog.
- **Its computation** → `infrastructure/<topic>/` (or `infrastructure/shared/`
  when reused), behind a port defined in `core/<topic>.py`. Vectorize; never
  loop over data in Python.
- **Code reused by several topics** (readers, inference, utilities) →
  `infrastructure/shared/`. Code needed by two topics moves here; a topic
  package never imports another topic.
- **A showcase** → `entrypoints/<topic>/notebook.py` plus
  `infrastructure/<topic>/pipeline.py`. The notebook collects input, calls the
  pipeline, and presents the result — no orchestration in the notebook.
- **Web delivery** → static WebAssembly export of the notebook by default;
  server-run only for secrets, GPU, or browser-unavailable dependencies, with
  the reason stated in the topic's spec.
- **A dependency used by one topic only** → optional dependency group named
  after the topic.

Use the same snake_case topic name in every layer.

## Core never computes

Core functions take already-computed metrics (scalars or metric objects).
No loops, comprehensions, `sum`/`min`/`max`/`len`/`sorted`/`map`/`filter`,
or `statistics` in core; a core function may receive a collection only to pass
it unchanged to a port. Scalar comparisons and formulas are fine.

## Vocabulary and language

- `infrastructure/shared/` and generic wording are domain-neutral ("series",
  "date column", "value column").
- A topic uses its canonical vocabulary (e.g. "demand" for Syntetos-Boylan)
  only inside its own core module, infrastructure, and entrypoint.
- Name modules and capabilities after the algorithm, concept, or foundation
  they document, never after a product domain.
- Everything — code, docstrings, UI strings, docs, OpenSpec — is in English.

## Guards

`tests/test_architecture.py` guards the published knowledge and core
portability with three guards: standard-library core, knowledge docstring, and
Knowledge catalog. Every other architecture rule (inward and isolated imports,
no computation in core, topic layout) is enforced by review. Do not weaken a
guard to make a change pass; amend the spec in its own change instead.

## Testing

- **Test** what a topic teaches and what a user would notice if it broke:
  formulas against hand-computed values (stated in the test module docstring),
  each decision rule in the knowledge docstring's `Method` on both sides of
  the point where its outcome changes, each undefined or rejected case named
  in `Assumptions and limitations`, and one end-to-end pipeline run per
  showcased topic.
- **Do not test** third-party libraries, constants, enum members, protocol
  conformance, notebooks or other UI through framework internals, behavior
  already tested in another layer, or conventions that review catches.
- Core decisions are tested with a test double for the engine port; do not
  repeat them through infrastructure or a notebook.
- Every test names the spec scenario or docstring limitation it protects.
- `uv run pytest` must pass before a task is marked complete.

## OpenSpec workflow

- Every change lives under `openspec/changes/<name>/` with `proposal.md`,
  `specs/**/spec.md`, `design.md`, and `tasks.md`.
- One capability per topic, named after the algorithm, concept, or
  foundation.
- Every task ends with a commit that leaves `uv run pytest` green.
- Validate with `openspec validate --all`; archive implemented changes so
  `openspec/specs/` stays current.
