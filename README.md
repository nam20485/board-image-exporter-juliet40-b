# PCB Renderer CLI

CLI tool to parse, validate, and render PCB ECAD JSON inputs with visual outputs (SVG/PNG/PDF).

## Features

- Parse and validate ECAD JSON board descriptions
- Geometry and topology validation engine
- Multi-format rendering (SVG, PNG, PDF)
- Property-based testing with Hypothesis
- Snapshot testing for visual regression

## Installation

### From PyPI (when published)

```bash
uv pip install pcb-renderer-cli
```

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/nam20485/board-image-exporter-juliet40-b.git
cd board-image-exporter-juliet40-b

# Install with uv (creates .venv automatically)
uv sync --all-extras

# Activate virtual environment
# On Windows
.venv\Scripts\Activate.ps1
# On Linux/Mac
source .venv/bin/activate
```

## Usage

```bash
# Basic usage
pcb-render input.json --output board.svg

# Specify output format
pcb-render input.json --output board.png --format png

# Run with validation only
pcb-render input.json --validate-only

# Show help
pcb-render --help
```

## Development

### Setup

1. **Install uv** (if not already installed):
   ```bash
   # Windows (PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   
   # Linux/Mac
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and install dependencies**:
   ```bash
   git clone https://github.com/nam20485/board-image-exporter-juliet40-b.git
   cd board-image-exporter-juliet40-b
   uv sync --all-extras
   ```

3. **Run tests**:
   ```bash
   uv run pytest
   ```

4. **Run linting**:
   ```bash
   uv run ruff check src/ tests/
   ```

5. **Format code**:
   ```bash
   uv run ruff format src/ tests/
   ```

### Project Structure

```
board-image-exporter-juliet40-b/
├── src/
│   ├── pcb_render/       # Main package
│   │   ├── cli.py        # CLI entry point
│   │   ├── models.py     # Pydantic models
│   │   ├── geometry.py   # Geometry validation
│   │   └── renderer.py   # Rendering engine
│   └── llm_assistor/     # LLM validation tools
├── tests/
│   ├── fixtures/         # Test data
│   ├── invalid_boards/   # Invalid board scenarios
│   └── snapshots/        # Visual regression snapshots
├── pyproject.toml        # Project configuration
├── README.md             # This file
└── uv.lock              # Dependency lock file (generated)
```

### Running with uv

```bash
# Run CLI directly
uv run pcb-render input.json

# Run tests with coverage
uv run pytest --cov=pcb_render

# Install in editable mode (for active development)
uv pip install -e .

# Add a new dependency
uv add requests

# Add a dev dependency
uv add --dev black
```

### Creating a Release

```bash
# Build package
uv build

# Publish to PyPI (requires PyPI credentials)
uv publish
```

## Testing

The project includes comprehensive test coverage:

- **Unit tests**: Individual component validation
- **Integration tests**: End-to-end rendering pipeline
- **Property-based tests**: Hypothesis for edge cases
- **Snapshot tests**: Visual regression with Syrupy

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=pcb_render --cov-report=html

# Run specific test file
uv run pytest tests/test_geometry.py

# Run with verbose output
uv run pytest -v
```

## Validation Scenarios

The tool validates 14 common PCB design errors:

1. Overlapping traces (same layer)
2. Drill holes outside board boundary
3. Insufficient trace spacing
4. Missing copper on signal layers
5. Invalid unit specifications
6. Topology violations
7. And more...

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Requirements

- Python 3.11 or higher
- uv package manager (recommended) or pip

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Roadmap

- [ ] Implement core validation engine
- [ ] Add SVG rendering
- [ ] Add PNG/PDF export
- [ ] Property-based test suite
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] PyPI publication

## Support

For issues, questions, or contributions:
- Open an issue: https://github.com/nam20485/board-image-exporter-juliet40-b/issues
- Read the docs: https://github.com/nam20485/board-image-exporter-juliet40-b/wiki

## Acknowledgments

- Built with [Pydantic](https://pydantic.dev/) for data validation
- Rendering powered by [Matplotlib](https://matplotlib.org/)
- CLI built with [Typer](https://typer.tiangolo.com/)
- Package management with [uv](https://github.com/astral-sh/uv)
