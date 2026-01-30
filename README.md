# PCB Renderer CLI (Scaffold)

This repository is being set up to build a PCB Renderer CLI that parses ECAD JSON inputs, validates geometry/topology, and renders outputs (SVG/PNG/PDF). Current state is scaffolding only.

## Getting Started
1. Ensure Python 3.11+ is installed.
2. Install deps (uv or pip):
   - `uv pip install -e .[dev]` **or**
   - `pip install -e .[dev]`
3. Run CLI help: `pcb-render --help`

## Project Structure
- `src/pcb_render/` — CLI, models, geometry, validation, rendering (placeholders)
- `tests/fixtures`, `tests/invalid_boards`, `tests/snapshots` — test data locations
- `pyproject.toml` — project metadata and dependencies

## Planned Work
- Implement Pydantic models and unit normalization
- Validation engine for 14 invalid board scenarios
- Matplotlib rendering with halo text and layer coloring
- Snapshot and property-based tests
- Docker/CI workflows for repeatable builds
