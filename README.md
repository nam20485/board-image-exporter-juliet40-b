# PCB Renderer CLI

A lightweight, high-performance Command Line Interface tool for parsing ECAD JSON files and rendering them into accurate visual representations (SVG, PNG, PDF).

## Overview

The PCB Renderer serves as a bridge between raw ECAD data and visual verification. It ingests JSON board definitions, performs rigorous validation, and produces layered visual outputs. The tool focuses on geometric correctness, handling complex coordinate transformations, and validating board integrity against strict rules.

**Current Status**: Phase 1 Foundation Complete ✅

### Phase 1 Features
- ✅ Parse ECAD JSON board definitions
- ✅ Normalize coordinates from multiple units (MICRON, MILLIMETER, MILS, INCH) to millimeters
- ✅ Validate boards against 14 error classes
- ✅ Support for components, traces, vias, layers, and keepouts
- ✅ Comprehensive test coverage (93%)

### Planned Features (Phases 2-5)
- ⏳ Geometric transformations (rotation, translation, mirroring)
- ⏳ Rendering to SVG, PNG, PDF
- ⏳ Visual regression testing
- ⏳ CLI commands (render, validate, info)

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/nam20485/board-image-exporter-juliet40-b.git
cd board-image-exporter-juliet40-b

# Install dependencies
uv sync --all-extras

# Verify installation
uv run pytest --version
```

## Quick Start

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=pcb_render --cov-report=html

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type check
uv run pyright
```

## Project Structure

```
.
├── src/
│   └── pcb_render/
│       ├── __init__.py       # Package metadata
│       ├── models.py         # Pydantic models (Point, Polygon, Board, etc.)
│       ├── units.py          # Unit conversion utilities
│       ├── parse.py          # JSON parsing and normalization
│       ├── validate.py       # Validation engine
│       └── errors.py         # Error definitions
├── tests/
│   ├── fixtures/             # Valid board JSON files
│   │   ├── minimal_board.json
│   │   └── complex_board.json
│   ├── invalid_boards/       # Invalid boards for testing (14 files)
│   ├── test_models.py        # Model tests
│   ├── test_units.py         # Unit conversion tests
│   ├── test_parse.py         # Parsing tests
│   └── test_validate.py      # Validation tests
├── docs/
│   ├── error_reference.md    # All 14 error codes documented
│   └── developer_guide.md    # Architecture and contribution guide
├── pyproject.toml            # Project configuration
├── uv.lock                   # Locked dependencies
└── README.md
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_models.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=pcb_render --cov-report=term-missing
```

### Code Quality

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run pyright
```

## Phase 1 Status

### Completed ✅
- [x] Project structure and configuration
- [x] Geometric primitive models (Point, Polygon, Polyline, Circle)
- [x] Domain models (Board, Component, Trace, Via, Layer, Stackup)
- [x] Unit normalization (4 unit types → millimeters)
- [x] JSON parsing with coordinate normalization
- [x] Validation framework (14 error classes)
- [x] Comprehensive test suite (98 tests, 93% coverage)
- [x] Test fixtures (2 valid + 14 invalid boards)
- [x] CI/CD pipeline (GitHub Actions)

### Test Coverage
- **Overall**: 93% (exceeds 90% target)
- **models.py**: 93%
- **units.py**: 100%
- **parse.py**: 96%
- **validate.py**: 85%
- **errors.py**: 95%

### Error Classes Supported
1. E001: Missing boundary
2. E002: Malformed coordinates (NaN/Infinity)
3. E003: Invalid rotation
4. E004: Negative width
5. E005: Invalid via geometry
6. E006: Nonexistent layer
7. E007: Nonexistent net
8. E008: Self-intersecting boundary
9. E009: Component outside boundary
10. E010: Duplicate layer hash
11. E011: Non-sequential layer indices
12. E012: Empty stackup
13. E013: Invalid design units
14. E014: Negative diameter

See [docs/error_reference.md](docs/error_reference.md) for detailed descriptions.

## Contributing

See [docs/developer_guide.md](docs/developer_guide.md) for:
- Architecture overview
- Adding new models
- Adding validation rules
- Running tests
- Code style guidelines

## License

See [LICENSE.md](LICENSE.md) for details.

## Acknowledgments

Built with:
- [Pydantic](https://docs.pydantic.dev/) for data modeling
- [pytest](https://docs.pytest.org/) for testing
- [uv](https://github.com/astral-sh/uv) for package management
- [ruff](https://docs.astral.sh/ruff/) for linting and formatting
