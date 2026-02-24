# Matchmaking

An application that lets people connect to potential matches based on assortative mating.

## Newcomer Guide

This repository is currently at an early stage and mostly captures product intent.

### Current structure

- `README.md`: project description and onboarding notes.

As the project grows, expect a structure similar to:

- `docs/`: product and architecture decision records.
- `src/` (or `backend/` + `frontend/`): implementation code.
- `tests/`: automated unit and integration tests.
- Tooling and automation files such as `pyproject.toml`/`package.json`, lint configuration, and CI workflows.

## What to learn next

If you are onboarding and want to move the project forward, follow this sequence.

### 1) Define core domain concepts

Create a short design document that clarifies:

- what “assortative mating” means in this product context,
- which inputs are used (traits, preferences, constraints),
- what matching output should include (score, explanation, confidence),
- which fairness and safety constraints apply.

### 2) Create baseline architecture

Set up the repository with clear boundaries:

- `docs/` for design decisions,
- `src/` (or `backend/`, `frontend/`) for implementation,
- `tests/` for unit and integration tests,
- baseline tooling (formatter, linter, test runner, CI).

### 3) Implement the smallest end-to-end slice

Build one complete vertical flow:

- user profile creation,
- compatibility scoring function/endpoint,
- simple match listing via CLI or minimal UI.

### 4) Add observability and quality early

Prioritize confidence and measurement from day one:

- automated tests for matching logic,
- representative fixtures for user data,
- basic metrics around match quality and potential bias.
