import json
from pathlib import Path
from contractor.parser import load_spec
from contractor.detectors import run_all
from contractor.formatters.json_fmt import to_json
from contractor.formatters.markdown import to_markdown

FIXTURES = Path(__file__).parent / "fixtures"


def _get_changes():
    base = load_spec(str(FIXTURES / "base.yaml"))
    candidate = load_spec(str(FIXTURES / "candidate.yaml"))
    return (
        run_all(base, candidate, engine="legacy"),
        str(FIXTURES / "base.yaml"),
        str(FIXTURES / "candidate.yaml"),
    )


def test_json_output_structure():
    changes, base, cand = _get_changes()
    output = to_json(changes, base, cand)
    data = json.loads(output)
    assert data["breaking"] is True
    assert data["count"] == 4
    assert len(data["changes"]) == 4
    assert all("kind" in c for c in data["changes"])


def test_json_no_breaking():
    base = load_spec(str(FIXTURES / "base.yaml"))
    changes = run_all(base, base, engine="legacy")
    output = to_json(changes, "base.yaml", "base.yaml")
    data = json.loads(output)
    assert data["breaking"] is False
    assert data["count"] == 0


def test_markdown_contains_table():
    changes, base, cand = _get_changes()
    output = to_markdown(changes, base, cand)
    assert "Contractor" in output
    assert "| Type |" in output
    assert "endpoint_removed" not in output
    assert "Endpoint removed" in output


def test_markdown_no_breaking():
    base = load_spec(str(FIXTURES / "base.yaml"))
    changes = run_all(base, base, engine="legacy")
    output = to_markdown(changes, "base.yaml", "base.yaml")
    assert "Contractor" in output
    assert "No Breaking Changes" in output
