# Spec Delta

## ADDED Requirements

### Requirement: Test scope

Tests SHALL cover what a topic teaches and what a user would notice if it broke: its formulas against hand-computed values, each decision rule stated in its knowledge docstring's `Method` at the inputs where the outcome changes, each undefined or rejected case named in its `Assumptions and limitations`, and one end-to-end pipeline run per showcased topic.

#### Scenario: Undefined case named in the docstring

- **WHEN** a knowledge docstring names a case where a metric is undefined or an input is rejected
- **THEN** a test exercises that case and checks the documented outcome

#### Scenario: Decision rule at its edge

- **WHEN** a knowledge docstring's `Method` states a decision rule
- **THEN** tests cover inputs on each side of the point where its outcome changes

#### Scenario: Showcased topic

- **WHEN** a topic has an entrypoint
- **THEN** one test runs its pipeline end to end on valid input

### Requirement: Test exclusions

Tests SHALL NOT target the behavior of third-party libraries, constants, enum members, protocol conformance, notebooks or other UI through framework internals, behavior already tested in another layer, or architecture conventions other than the guards required by "Executable Test Suite". Such conventions are enforced by review.

#### Scenario: Constant asserted against its literal

- **WHEN** a proposed test only asserts that a constant equals the value written in the code
- **THEN** the test is not added

#### Scenario: Decision already tested in core

- **WHEN** a decision is tested in core with a test double for its port
- **THEN** no test repeats that decision through infrastructure or a notebook

## MODIFIED Requirements

### Requirement: Project Packaging and Installation

The project SHALL be installable via `uv` from the repository, requiring Python 3.13 or higher, building the single package `ml_helper`, declaring the platform runtime dependencies (`pandas`, `polars`, `pyarrow`, `marimo`, `altair`), and development dependencies (`pytest`). Dependencies used by a single topic SHALL follow the `architecture` capability's rule on topic-exclusive dependencies.

#### Scenario: Editable installation and sync

- **WHEN** running `uv sync`
- **THEN** dependencies are installed cleanly and `pytest` becomes available in the environment

#### Scenario: Minimum Python version requirement

- **WHEN** inspecting `pyproject.toml`
- **THEN** `requires-python` is `>=3.13`

#### Scenario: Unused dependencies are not declared

- **WHEN** inspecting the runtime dependencies in `pyproject.toml`
- **THEN** `pydantic` is not listed

### Requirement: Valid OpenSpec Configuration

`openspec/config.yaml` SHALL be a valid YAML document defining the `context` (tech stack, domain, architecture, and testing policy), `rules` (artifact rules), and `operations` (`apply` and `archive` guidance) sections.

#### Scenario: Configuration is readable by OpenSpec

- **WHEN** running `openspec doctor`
- **THEN** the configuration is parsed as valid YAML without errors

#### Scenario: Rules and operations defined

- **WHEN** reading `openspec/config.yaml`
- **THEN** `context` states the testing policy, `rules` contains the rule to end every task with a commit that leaves `uv run pytest` green and the rule to add a test only for a behavior the testing policy covers, and `operations.apply` contains the guidance to run `uv run pytest` before marking tasks as complete

### Requirement: Reference Documentation

`README.md` SHALL document the project purpose as a portfolio of machine learning techniques, the technical stack, a summary of the architecture linking to the `architecture` specification, the repository structure, the Knowledge catalog, and quickstart steps.

#### Scenario: Essential README content

- **WHEN** reading `README.md`
- **THEN** it contains the purpose, stack, an architecture summary linking to `openspec/specs/architecture/spec.md`, the Knowledge catalog, and a quickstart installation/execution section

### Requirement: Executable Test Suite

Tests SHALL execute via `pytest` (`uv run pytest`) and include the architecture guards that protect published knowledge and core portability: standard-library core, knowledge docstring, and Knowledge catalog. Other architecture rules SHALL be enforced by review, not by tests.

#### Scenario: Green pytest status on baseline

- **WHEN** running `uv run pytest` at the repository root
- **THEN** the entire suite passes without errors

#### Scenario: Architecture guards are part of the suite

- **WHEN** listing the collected tests
- **THEN** the suite contains the standard-library core, knowledge docstring, and Knowledge catalog guards, and no other architecture guard
