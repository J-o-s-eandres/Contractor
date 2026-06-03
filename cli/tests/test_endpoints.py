from pathlib import Path
from contractor.parser import load_spec
from contractor.detectors.endpoints import detect_removed_endpoints

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_removed_delete_endpoint():
    base = load_spec(str(FIXTURES / "base.yaml"))
    candidate = load_spec(str(FIXTURES / "candidate.yaml"))
    changes = detect_removed_endpoints(base, candidate)

    assert len(changes) == 1
    c = changes[0]
    assert c.kind == "endpoint_removed"
    assert c.path == "/users/{id}"
    assert c.method == "DELETE"


def test_no_false_positives_when_identical():
    base = load_spec(str(FIXTURES / "base.yaml"))
    changes = detect_removed_endpoints(base, base)
    assert changes == []


def test_empty_paths_no_crash():
    changes = detect_removed_endpoints({}, {})
    assert changes == []
