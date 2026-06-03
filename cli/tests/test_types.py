from pathlib import Path
from contractor.parser import load_spec
from contractor.detectors.types import detect_type_changes

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_type_change_in_request_body():
    base = load_spec(str(FIXTURES / "base.yaml"))
    candidate = load_spec(str(FIXTURES / "candidate.yaml"))
    changes = detect_type_changes(base, candidate)

    assert len(changes) == 1
    c = changes[0]
    assert c.kind == "type_changed"
    assert c.path == "/orders"
    assert c.method == "POST"
    assert "amount" in c.location
    assert c.base_value == "string"
    assert c.candidate_value == "number"


def test_no_false_positives_when_identical():
    base = load_spec(str(FIXTURES / "base.yaml"))
    changes = detect_type_changes(base, base)
    assert changes == []
