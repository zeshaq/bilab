# Changelog

All notable changes to bilab are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/) and
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Phase 2 viz MVP: FastAPI backend (/api/cubes, /api/query, audit log) and a
  React + TypeScript + ECharts frontend (KPI cards, bar charts, Explore) over the
  semantic layer; verified end to end in a browser against live lab data.
- Phase 1 semantic core: bilab's own Cube + Cubestore (semantic/), metric model
  (transactions, branches) on the lab's Trino/Iceberg, and "same numbers
  everywhere" acceptance tests (SQL/REST/GraphQL, 5/5 green).
- ADR-0006 (clean-room semantic layer + Phase 1 service identity).
- Repository initialized (private, later public).
- Documentation: product vision, architecture, ADRs (0001-0005), roadmap,
  engineering principles, contribution guide.
- Issue templates, PR template, CI scaffold, repo hygiene (.gitignore,
  .editorconfig, license).
