# PCB Renderer Developer Guide

## Architecture Overview

```
User (JSON) → Parser → Units → Models → Validator → Errors
                     ↓
                  Normalized
                  Board
```

### Module Flow

1. **parse.py**: `parse_board()` - Ingests JSON, normalizes coordinates
2. **units.py**: Converts all units to millimeters
3. **models.py**: Pydantic models validate structure
4. **validate.py**: `validate_board()` - Checks board integrity
5. **errors.py**: Structured error reporting

## Adding New Models

1. Define Pydantic model in `models.py`
2. Add validators using `@field_validator` or `@model_validator`
3. Add tests in `tests/test_models.py`

Example:
```python
class NewModel(BaseModel):
    field: float

    @field_validator('field')
    @classmethod
    def check_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('must be positive')
        return v
```

## Adding Validation Rules

1. Add error code to `errors.py`
2. Implement check in `validate.py`
3. Add test in `tests/test_validate.py`

Example:
```python
# In errors.py
E015_NEW_ERROR = "E015_NEW_ERROR"

_ERROR_MESSAGES[E015_NEW_ERROR] = {
    "severity": ErrorSeverity.ERROR,
    "message": "Description",
    "suggestion": "How to fix",
}

# In validate.py
def _validate_new_rule(board: Board) -> list[ValidationError]:
    errors = []
    # Check something
    if invalid_condition:
        errors.append(ValidationError.from_code(E015_NEW_ERROR))
    return errors
```

## Running Tests

```bash
# All tests
uv run pytest

# Specific file
uv run pytest tests/test_models.py

# With coverage
uv run pytest --cov=pcb_render --cov-report=html

# Specific test
uv run pytest tests/test_models.py::TestPoint::test_point_creation
```

## Code Style

- **Line length**: 100 characters
- **Quotes**: Double quotes
- **Indent**: 4 spaces
- **Import order**: stdlib, third-party, local

Check style:
```bash
uv run ruff check .
uv run ruff format .
```

## Type Checking

All code must pass strict type checking:
```bash
uv run pyright
```

## Debugging Tips

### Pydantic Validation Errors

```python
try:
    board = Board(**data)
except ValidationError as e:
    print(e.json())  # Detailed error
```

### Unit Conversion Issues

```python
from pcb_render.units import normalize_value

# Test conversion
result = normalize_value(1000, "MICRON")
print(result)  # Should be 1.0
```

### Parsing Problems

```python
import json
from pcb_render.parse import parse_board

with open("board.json") as f:
    data = json.load(f)

board = parse_board(data)
print(board)  # Debug output
```

## Test Coverage Goals

- **Target**: ≥90% overall
- **Critical modules**: 100% (units, errors)
- **Models**: ≥95%
- **Parsing**: ≥95%

Check coverage:
```bash
uv run pytest --cov=pcb_render --cov-report=term-missing
```

## Contributing Workflow

1. Create feature branch
2. Make changes with tests
3. Ensure all tests pass
4. Check coverage ≥90%
5. Run linting and type checking
6. Commit with descriptive message
7. Create PR

## CI/CD

- **Trigger**: Push to main or feature branches
- **Matrix**: 3 OS × 2 Python versions = 6 jobs
- **Checks**: Lint, format, type check, tests
- **Coverage**: Uploaded to Codecov

All checks must pass before merge.
