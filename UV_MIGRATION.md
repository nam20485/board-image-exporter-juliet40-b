# Migration to UV Package Manager

This project has been migrated from pip to [uv](https://github.com/astral-sh/uv) for faster, more reliable dependency management.

## What Changed

### For End Users

**Before (pip)**:
```bash
pip install pcb-renderer-cli
```

**After (uv)**:
```bash
uv pip install pcb-renderer-cli
```

### For Developers

**Before (pip)**:
```bash
git clone https://github.com/nam20485/board-image-exporter-juliet40-b.git
cd board-image-exporter-juliet40-b
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -e .[dev]
pytest
```

**After (uv)**:
```bash
git clone https://github.com/nam20485/board-image-exporter-juliet40-b.git
cd board-image-exporter-juliet40-b
uv sync --all-extras  # Creates .venv automatically
uv run pytest         # Runs in virtual environment automatically
```

## Benefits of UV

1. **10-100x faster** than pip for dependency resolution and installation
2. **Reproducible builds** via `uv.lock` file (like npm's package-lock.json)
3. **Automatic virtual environment** management
4. **Built-in command runner** with `uv run`
5. **Better caching** and parallel downloads
6. **Drop-in replacement** for most pip commands

## Installation

### Windows (PowerShell)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### Linux/Mac
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Alternative (via pip)
```bash
pip install uv
```

## Key Commands

| Task | Old (pip) | New (uv) |
|------|-----------|----------|
| Install package | `pip install pkg` | `uv pip install pkg` |
| Install from source | `pip install -e .` | `uv sync` or `uv pip install -e .` |
| Install dev deps | `pip install -e .[dev]` | `uv sync --all-extras` |
| Run command in venv | `source .venv/bin/activate && pytest` | `uv run pytest` |
| Add dependency | Edit pyproject.toml, `pip install -e .` | `uv add requests` |
| Add dev dependency | Edit pyproject.toml, `pip install -e .[dev]` | `uv add --dev pytest` |
| Update all deps | `pip install -U -e .[dev]` | `uv sync --upgrade` |
| Lock dependencies | N/A | `uv lock` (automatic with sync) |

## Compatibility

- **uv is backwards compatible** with pip
- Existing `requirements.txt` files still work: `uv pip install -r requirements.txt`
- This project uses `pyproject.toml` (PEP 621 standard)
- The `uv.lock` file ensures everyone gets the same dependency versions

## CI/CD Changes

GitHub Actions workflows now use:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4

- name: Install dependencies
  run: uv sync --all-extras

- name: Run tests
  run: uv run pytest
```

## Lock File

The `uv.lock` file is now tracked in version control. This ensures:
- All developers get identical dependency versions
- CI/CD builds are reproducible
- Prevents "works on my machine" issues

To update dependencies:
```bash
uv sync --upgrade  # Updates within constraints in pyproject.toml
uv lock --upgrade  # Regenerates lock file with latest versions
```

## Troubleshooting

### Issue: "uv: command not found"

**Solution**: Install uv or add to PATH:
```bash
# Check installation
which uv  # Linux/Mac
where.exe uv  # Windows

# Reinstall if needed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Issue: ".venv already exists from pip"

**Solution**: Remove and recreate with uv:
```bash
rm -rf .venv
uv sync --all-extras
```

### Issue: "Package conflicts"

**Solution**: Clear cache and resync:
```bash
uv cache clean
uv sync --all-extras
```

### Issue: "Want to use pip instead"

**Solution**: You can still use pip, but you'll need to manually manage the venv:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -e .[dev]
```

Note: If using pip, ignore the `uv.lock` file.

## Migration Checklist

- [x] Create `pyproject.toml` with project metadata
- [x] Update `.gitignore` to exclude `.egg-info` and include `uv.lock`
- [x] Update README.md with uv installation instructions
- [x] Update CI/CD workflows to use uv
- [x] Generate `uv.lock` file
- [x] Update developer documentation
- [ ] Notify team members to install uv
- [ ] Update project wiki/docs
- [ ] Consider removing old `requirements.txt` (if any)

## Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV GitHub Repository](https://github.com/astral-sh/uv)
- [Python Packaging User Guide (PEP 621)](https://packaging.python.org/en/latest/specifications/declaring-project-metadata/)

## Questions?

Open an issue: https://github.com/nam20485/board-image-exporter-juliet40-b/issues
