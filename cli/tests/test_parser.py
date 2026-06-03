import pytest
from pathlib import Path
from contractor.parser import load_spec

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_yaml():
    spec = load_spec(str(FIXTURES / "base.yaml"))
    assert isinstance(spec, dict)
    assert "paths" in spec
    assert "/users" in spec["paths"]


def test_load_nonexistent_raises():
    with pytest.raises(FileNotFoundError):
        load_spec("nonexistent.yaml")


def test_load_invalid_raises():
    import tempfile, os

    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
        f.write(": invalid: yaml: {{{")
        name = f.name
    try:
        with pytest.raises(ValueError, match="Failed to parse"):
            load_spec(name)
    finally:
        os.unlink(name)
