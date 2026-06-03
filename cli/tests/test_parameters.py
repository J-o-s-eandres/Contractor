from pathlib import Path
from contractor.parser import load_spec
from contractor.detectors.parameters import detect_required_params_added

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_param_became_required():
    base = load_spec(str(FIXTURES / "base.yaml"))
    candidate = load_spec(str(FIXTURES / "candidate.yaml"))
    changes = detect_required_params_added(base, candidate)

    assert len(changes) == 1
    c = changes[0]
    assert c.kind == "required_param_added"
    assert c.path == "/users"
    assert c.method == "GET"
    assert "limit" in c.location
    assert c.base_value == "optional"
    assert c.candidate_value == "required"


def test_no_false_positives_when_identical():
    base = load_spec(str(FIXTURES / "base.yaml"))
    changes = detect_required_params_added(base, base)
    assert changes == []


def test_empty_spec_no_crash():
    changes = detect_required_params_added({}, {})
    assert changes == []
