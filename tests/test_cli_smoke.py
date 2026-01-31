"""Smoke tests for CLI.

Modified: 2026-01-30 by GitHub Copilot (nam20485)
Reason: Updated test to work with Typer CLI which uses different internal structure.
"""

import subprocess
import sys
import tempfile
import json
from pathlib import Path


def test_render_command_parses():
    """Test that render command can parse arguments with Typer."""
    # Create a temporary dummy JSON file so Typer doesn't fail on file existence check
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"metadata": {}, "boundary": []}, f)
        dummy_file = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pcb_render.cli", "render", 
             dummy_file, "--format", "svg", "--dpi", "300"],
            capture_output=True,
            text=True,
        )
        
        # Typer outputs "Would render" message for our placeholder implementation
        assert "Would render" in result.stdout or result.returncode == 0
    finally:
        Path(dummy_file).unlink(missing_ok=True)
