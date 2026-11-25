# architecture Specification

## Purpose

Defines how ML Helper, a portfolio of machine learning techniques, is organized: core as the documented knowledge base, infrastructure as the computation, and entrypoints as the showcase of each topic, with the rules that keep the three layers consistent as topics are added.

## Requirements

### Requirement: Three-layer package

All source code SHALL live in a single importable package `ml_helper` under `src/`, split into the subpackages `core`, `infrastructure`, and `entrypoints`.

#### Scenario: Layers are importable under the package

- **WHEN** running `uv run python -c "import ml_helper.core, ml_helper.infrastructure, ml_helper.entrypoints"`
- **THEN** the statement completes without import errors

#### Scenario: No top-level layer packages

- **WHEN** listing the directories directly under `src/`
- **THEN** `ml_helper` is the only Python package

### Requirement: Inward dependency direction

Dependencies SHALL point inward only: `entrypoints` MAY import `infrastructure` and `core`; `infrastructure` MAY import `core`; `core` SHALL NOT import `infrastructure` or `entrypoints`, and `infrastructure` SHALL NOT import `entrypoints`.

#### Scenario: Core importing an outer layer is rejected

- **WHEN** a module under `ml_helper/core` imports anything from `ml_helper.infrastructure` or `ml_helper.entrypoints`
- **THEN** review rejects the change and names the offending module

#### Scenario: Infrastructure importing an entrypoint is rejected

- **WHEN** a module under `ml_helper/infrastructure` imports anything from `ml_helper.entrypoints`
- **THEN** review rejects the change and names the offending module

### Requirement: Standard-library core

Modules under `ml_helper/core` SHALL import only the Python standard library and other `ml_helper.core` modules. The test suite SHALL enforce this rule with an allowlist of standard-library modules rather than a blacklist of forbidden packages.

#### Scenario: Third-party import in core is rejected

- **WHEN** a core module imports a package outside the standard library (for example `pydantic`, `pandas`, or `streamlit`)
- **THEN** the architecture guard fails and names the module and the import

#### Scenario: Standard-library imports are accepted

- **WHEN** a core module imports only modules such as `dataclasses`, `enum`, `typing`, or `math`
- **THEN** the architecture guard passes

### Requirement: Core holds knowledge, not computation

Core SHALL contain only vocabulary, thresholds, ports, and decisions for a topic. Core SHALL NOT compute over collections of data: no loops, no comprehensions or generator expressions, and no aggregating built-ins or statistics helpers. Core functions SHALL take already-computed metrics as scalars or metric objects; a core function MAY receive a collection only to hand it unchanged to a port. Scalar comparisons and scalar formulas are allowed. Every computation over data SHALL be implemented in infrastructure behind a port defined in core.

#### Scenario: Aggregation in core is rejected

- **WHEN** a core module contains a `for` loop, a comprehension, or a call to `sum`, `min`, `max`, `len`, or `sorted`, or imports `statistics`
- **THEN** review rejects the change and names the module and the construct

#### Scenario: Scalar decision logic is accepted

- **WHEN** a core function compares scalar metrics against thresholds
- **THEN** the module conforms to this requirement

### Requirement: Knowledge docstring

Every core module other than `__init__.py` SHALL begin with a module docstring that documents its topic as a knowledge entry, written in Markdown with these level-two headings in this order: `## Overview`, `## Definitions`, `## Method`, `## Assumptions and limitations`, `## References`. `Method` SHALL state the formulas and decision rules even when their computation lives in infrastructure. Infrastructure and entrypoint modules SHALL reference the core module they implement instead of repeating its theory.

#### Scenario: Core module with all sections

- **WHEN** the docstring guard inspects a core module whose docstring contains the five headings in order
- **THEN** the guard passes

#### Scenario: Missing or misordered section

- **WHEN** a core module has no docstring, lacks one of the five headings, or has them out of order
- **THEN** the docstring guard fails and names the module and the missing or misplaced heading

### Requirement: Topic layout across layers

A topic SHALL be identified by one snake_case name used identically in every layer it appears in: `core/<topic>.py` (or a `core/<topic>/` package), `infrastructure/<topic>/` or `infrastructure/shared/<topic>` (module or package), and `entrypoints/<topic>/`. Every `infrastructure/<topic>/` package SHALL have a matching core module, and every `entrypoints/<topic>/` package SHALL have a matching core module and infrastructure package.

#### Scenario: Entrypoint without its infrastructure is rejected

- **WHEN** `entrypoints/<topic>/` exists but `infrastructure/<topic>/` or the core module for `<topic>` does not
- **THEN** review rejects the change and names the topic and the missing part

#### Scenario: Core-only concept is accepted

- **WHEN** a core module exists with no matching infrastructure or entrypoint package
- **THEN** the layout conforms to this requirement

#### Scenario: Topic implemented in shared is accepted

- **WHEN** `core/<topic>.py` exists and its implementation is `infrastructure/shared/<topic>.py`
- **THEN** the layout conforms to this requirement

### Requirement: Isolated topic infrastructure

A topic's infrastructure package SHALL NOT import another topic's infrastructure package. `infrastructure/shared/` SHALL NOT import any topic infrastructure package. Code needed by two topics SHALL move to `infrastructure/shared/`.

#### Scenario: Lateral import is rejected

- **WHEN** a module in `infrastructure/<a>/` imports from `ml_helper.infrastructure.<b>` where `<b>` is another topic
- **THEN** review rejects the change and names both topics

#### Scenario: Shared importing a technique is rejected

- **WHEN** a module in `infrastructure/shared/` imports from a topic infrastructure package
- **THEN** review rejects the change and names the module

### Requirement: Topic pipeline

Every topic that has an entrypoint SHALL expose its end-to-end use case (load input, compute, decide) as a pipeline module `infrastructure/<topic>/pipeline.py`. Entrypoints SHALL call the pipeline for orchestration and SHALL limit themselves to collecting input, calling the pipeline, and presenting its result.

#### Scenario: Pipeline exists for a showcased technique

- **WHEN** `entrypoints/<topic>/` exists
- **THEN** `infrastructure/<topic>/pipeline.py` exists

#### Scenario: Pipeline is usable without a UI

- **WHEN** the pipeline is called directly from a test with valid input
- **THEN** it returns the same result the notebook presents for that input

### Requirement: Notebook entrypoint

Every `entrypoints/<topic>/` package SHALL contain a marimo notebook `notebook.py` that presents the topic to developers.

#### Scenario: Notebook present

- **WHEN** `entrypoints/<topic>/` exists
- **THEN** it contains `notebook.py` defining a marimo app

### Requirement: WebAssembly-first web delivery

A topic MAY offer a web delivery. When it does, the default delivery SHALL be a static WebAssembly export of its marimo notebook that runs entirely in the visitor's browser. A topic SHALL use a server-run delivery instead only when it needs secrets, a GPU, or dependencies unavailable in the browser runtime, and its capability spec SHALL state which delivery it uses and why.

#### Scenario: Technique without special needs

- **WHEN** a topic adds a web delivery and needs no secrets, GPU, or browser-unavailable dependency
- **THEN** its delivery is a static WebAssembly export and its spec records that choice

#### Scenario: Technique requiring secrets

- **WHEN** a topic calls an external service that needs an API key
- **THEN** its web delivery is server-run and its spec states the reason

### Requirement: Topic-exclusive dependencies

A third-party dependency used by exactly one topic and not part of the platform baseline SHALL be declared as an optional dependency group named after that topic, so installing one topic does not pull in another topic's dependencies.

#### Scenario: New heavy dependency for one technique

- **WHEN** a change adds a dependency used only by one topic
- **THEN** `pyproject.toml` declares it under an optional group named after that topic

### Requirement: Vocabulary

Shared infrastructure and generic wording SHALL be domain-neutral ("series", "date column", "value column"). A topic SHALL use its canonical vocabulary (for example, "demand" in Syntetos-Boylan) only inside its own core module, infrastructure, and entrypoint. Modules, packages, and capabilities SHALL be named after the algorithm, concept, or foundation they document, never after a product domain.

#### Scenario: Domain term in shared infrastructure

- **WHEN** reviewing a module in `infrastructure/shared/`
- **THEN** it uses no product-domain vocabulary and no other topic's canonical vocabulary

#### Scenario: Canonical vocabulary inside a technique

- **WHEN** the Syntetos-Boylan notebook explains the average demand interval
- **THEN** the term "demand" is permitted

### Requirement: English documentation

Code, docstrings, user-visible strings, repository documentation, and OpenSpec artifacts SHALL be written in English.

#### Scenario: New knowledge docstring

- **WHEN** a change adds a core module
- **THEN** its knowledge docstring is written in English

### Requirement: Knowledge catalog

`README.md` SHALL contain a Knowledge catalog table with one row per core module, stating its kind (technique, concept, or foundation) and whether it has infrastructure, a notebook, and a web delivery. The test suite SHALL check that every core module appears in the catalog; the kind is documentation and is not checked by the suite.

#### Scenario: New core module without a catalog row

- **WHEN** a core module exists that has no row in the README Knowledge catalog
- **THEN** the catalog guard fails and names the module

#### Scenario: Catalog row states the kind

- **WHEN** reading a row of the Knowledge catalog
- **THEN** its `Kind` column is technique, concept, or foundation

### Requirement: Single normative source

This specification SHALL be the normative source for the architecture. `AGENTS.md` and `README.md` SHALL summarize the rules and link to `openspec/specs/architecture/spec.md` rather than restating them with different wording.

#### Scenario: Documents point at the spec

- **WHEN** reading `AGENTS.md` and `README.md`
- **THEN** each links to `openspec/specs/architecture/spec.md`

### Requirement: Topics and kinds

The knowledge base SHALL be organized in topics, each documented by one core module. Every topic SHALL be of exactly one kind: technique (a method that computes or decides), concept (an ML idea explained and possibly demonstrated), or foundation (non-ML groundwork that topics rely on). A topic of any kind MAY exist in core only, in core and infrastructure, or in all three layers.

#### Scenario: Foundation in core only

- **WHEN** a core module documents a foundation and has no infrastructure or entrypoint
- **THEN** the layout conforms to this specification

#### Scenario: Concept without a notebook

- **WHEN** a core module documents a concept and has no `entrypoints/<topic>/` package
- **THEN** the layout conforms to this specification

### Requirement: Placement by knowledge and reuse

Whether code has a core module and where its infrastructure lives SHALL be decided independently. Code with knowledge worth documenting SHALL have a core module. Infrastructure used by one topic SHALL live in `infrastructure/<topic>/`; infrastructure used by several topics SHALL live in `infrastructure/shared/`, with or without a core module. A topic's kind SHALL NOT be inferred from where its infrastructure lives.

#### Scenario: Reusable code with knowledge

- **WHEN** a reader used by several topics is documented by `core/<topic>.py` and implemented in `infrastructure/shared/<topic>.py`
- **THEN** the layout conforms to this specification

#### Scenario: Reusable code without knowledge

- **WHEN** a module in `infrastructure/shared/` has no matching core module
- **THEN** the layout conforms to this specification

#### Scenario: Technique moved to shared

- **WHEN** a technique's infrastructure moves to `infrastructure/shared/` because a second topic needs it
- **THEN** its catalog row still states the kind technique
