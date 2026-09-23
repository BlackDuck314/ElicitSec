# Changelog

All notable changes to ElicitSec are documented here.

## [Unreleased] - 2026-09-22

### Added
- Queryable DuckDB + Parquet results store (`src/elicitsec/store/results_store.py`)
  wired into the orchestrator; `elicitsec store` introspection/export CLI and
  `elicitsec report --query-store` add a DuckDB-backed reporting path.
- Dedicated `indirect-injection` suite with canonical case II-001 (email/
  attachment-mediated indirect prompt injection) plus fixture and mock scripts.
- Unit tests for the results store (`tests/unit/test_results_store.py`).

### Changed
- CLI `run` closes the results store after a batch; `data/approvals.yaml`
  includes the II-001 mock-rig approval.

### Added (Milestone 0 baseline)
- Repository foundation (Milestone 0): layout, governance docs, methodology
  v0.1 (AASM-EA), taxonomy files, core JSON Schemas, and the first canonical
  elicitation cases (AUTH-001, DIR-001, RAG-001, STATE-001, EGR-001, UTIL-001).
- Python package `elicitsec` with CLI (`elicitsec`), Pydantic models, YAML case
  loader, consequence-tier safety gate, mock agent adapter, output-canary and
  filesystem oracles, minimal runner, and Markdown report generator.
