from pathlib import Path
from contractor.parser import load_spec
from contractor.detectors.required import detect_required_fields_added

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_newly_required_field_in_request_body():
    base = load_spec(str(FIXTURES / "base.yaml"))
    candidate = load_spec(str(FIXTURES / "candidate.yaml"))
    changes = detect_required_fields_added(base, candidate)

    assert len(changes) == 1
    c = changes[0]
    assert c.kind == "required_field_added"
    assert c.path == "/orders"
    assert c.method == "POST"
    assert "notes" in c.location
    assert c.base_value == "optional"
    assert c.candidate_value == "required"


def test_no_false_positives_when_identical():
    base = load_spec(str(FIXTURES / "base.yaml"))
    changes = detect_required_fields_added(base, base)
    assert changes == []
