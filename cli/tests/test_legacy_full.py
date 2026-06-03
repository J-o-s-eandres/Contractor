"""Exhaustive tests for legacy detectors — every branch, edge case, boundary."""

import pytest
from pathlib import Path
from contractor.parser import load_spec
from contractor.detectors import run_all
from contractor.detectors.endpoints import detect_removed_endpoints
from contractor.detectors.parameters import detect_required_params_added
from contractor.detectors.types import detect_type_changes
from contractor.detectors.required import detect_required_fields_added

FIXTURES = Path(__file__).parent / "fixtures"

L = ["--engine", "legacy"]


def _legacy_changes(base: dict, cand: dict) -> list:
    return run_all(base, cand, engine="legacy")


# ── Endpoint detector exhaustive ────────────────────────────────────────


def _make_paths(endpoints: dict) -> dict:
    return {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            path: {
                method: {"responses": {"200": {"description": "ok"}}}
                for method in methods
            }
            for path, methods in endpoints.items()
        },
    }


def test_endpoint_removed_delete():
    base = _make_paths({"/users/{id}": ["delete"]})
    cand = _make_paths({})
    changes = detect_removed_endpoints(base, cand)
    assert len(changes) == 1
    assert changes[0].kind == "endpoint_removed"
    assert changes[0].method == "DELETE"


@pytest.mark.parametrize(
    "method", ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
)
def test_endpoint_removed_any_method(method):
    base = _make_paths({"/resource": [method]})
    cand = _make_paths({})
    changes = detect_removed_endpoints(base, cand)
    assert len(changes) == 1
    assert changes[0].method.upper() == method.upper()


def test_multiple_endpoints_removed():
    base = _make_paths({"/a": ["get"], "/b": ["post"], "/c": ["put"]})
    cand = _make_paths({})
    changes = detect_removed_endpoints(base, cand)
    assert len(changes) == 3


def test_some_endpoints_removed():
    base = _make_paths({"/a": ["get"], "/b": ["post"], "/c": ["put"]})
    cand = _make_paths({"/b": ["post"]})
    changes = detect_removed_endpoints(base, cand)
    assert len(changes) == 2
    paths = {c.path for c in changes}
    assert paths == {"/a", "/c"}


def test_no_endpoints_removed():
    base = _make_paths({"/a": ["get"], "/b": ["post"]})
    cand = _make_paths({"/a": ["get"], "/b": ["post"]})
    assert detect_removed_endpoints(base, cand) == []


def test_candidate_has_more_endpoints():
    base = _make_paths({"/a": ["get"]})
    cand = _make_paths({"/a": ["get"], "/b": ["post"]})
    assert detect_removed_endpoints(base, cand) == []


def test_empty_paths():
    assert detect_removed_endpoints({}, {}) == []
    assert detect_removed_endpoints({"paths": {}}, {"paths": {}}) == []


# ── Parameters detector exhaustive ──────────────────────────────────────


def _make_spec_with_params(params: list[dict]) -> dict:
    return {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/test": {
                "get": {
                    "parameters": params,
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }


def test_param_became_required():
    base = _make_spec_with_params(
        [
            {
                "name": "filter",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
            }
        ]
    )
    cand = _make_spec_with_params(
        [
            {
                "name": "filter",
                "in": "query",
                "required": True,
                "schema": {"type": "string"},
            }
        ]
    )
    changes = detect_required_params_added(base, cand)
    assert len(changes) == 1
    assert changes[0].kind == "required_param_added"
    assert changes[0].location == "parameter:filter"


def test_param_stays_optional():
    base = _make_spec_with_params(
        [{"name": "f", "in": "query", "required": False, "schema": {"type": "string"}}]
    )
    cand = _make_spec_with_params(
        [{"name": "f", "in": "query", "required": False, "schema": {"type": "string"}}]
    )
    assert detect_required_params_added(base, cand) == []


def test_param_stays_required():
    base = _make_spec_with_params(
        [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}]
    )
    cand = _make_spec_with_params(
        [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}]
    )
    assert detect_required_params_added(base, cand) == []


@pytest.mark.parametrize("location", ["query", "header", "path", "cookie"])
def test_param_became_required_any_location(location):
    base = _make_spec_with_params(
        [{"name": "x", "in": location, "required": False, "schema": {"type": "string"}}]
    )
    cand = _make_spec_with_params(
        [{"name": "x", "in": location, "required": True, "schema": {"type": "string"}}]
    )
    changes = detect_required_params_added(base, cand)
    assert len(changes) == 1


def test_multiple_params_became_required():
    params = [
        {"name": "a", "in": "query", "required": False, "schema": {"type": "string"}},
        {"name": "b", "in": "query", "required": False, "schema": {"type": "int"}},
    ]
    base = _make_spec_with_params(params)
    cand_params = [
        {"name": "a", "in": "query", "required": True, "schema": {"type": "string"}},
        {"name": "b", "in": "query", "required": True, "schema": {"type": "int"}},
    ]
    cand = _make_spec_with_params(cand_params)
    assert len(detect_required_params_added(base, cand)) == 2


def test_empty_parameters():
    base = _make_spec_with_params([])
    cand = _make_spec_with_params([])
    assert detect_required_params_added(base, cand) == []


def test_no_parameters_in_spec():
    base = _make_spec_with_params([])
    cand = _make_spec_with_params(
        [{"name": "x", "in": "query", "required": False, "schema": {"type": "string"}}]
    )
    assert detect_required_params_added(base, cand) == []


def test_param_missing_required_field_defaults_false():
    base = _make_spec_with_params(
        [{"name": "x", "in": "query", "schema": {"type": "string"}}]
    )
    cand = _make_spec_with_params(
        [{"name": "x", "in": "query", "required": True, "schema": {"type": "string"}}]
    )
    changes = detect_required_params_added(base, cand)
    assert len(changes) == 1


# ── Type detector exhaustive ────────────────────────────────────────────


def _body_spec(prop_type: str) -> dict:
    return {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"amount": {"type": prop_type}},
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "created"}},
                }
            }
        },
    }


@pytest.mark.parametrize(
    "from_type,to_type",
    [
        ("string", "number"),
        ("number", "string"),
        ("integer", "string"),
        ("string", "boolean"),
        ("integer", "number"),
        ("boolean", "string"),
    ],
)
def test_type_changed(from_type, to_type):
    base = _body_spec(from_type)
    cand = _body_spec(to_type)
    changes = detect_type_changes(base, cand)
    assert len(changes) == 1
    assert changes[0].kind == "type_changed"
    assert from_type in changes[0].description
    assert to_type in changes[0].description


def test_type_unchanged():
    base = _body_spec("string")
    cand = _body_spec("string")
    assert detect_type_changes(base, cand) == []


def test_no_request_body():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {"/x": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    assert detect_type_changes(spec, spec) == []


def test_no_schema():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {"/x": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    assert detect_type_changes(spec, spec) == []


# ── Required field detector exhaustive ──────────────────────────────────


def _required_spec(required_fields: list[str], optional_fields: list[str]) -> dict:
    props = {}
    for f in required_fields + optional_fields:
        props[f] = {"type": "string"}
    return {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": required_fields,
                                    "properties": props,
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "created"}},
                }
            }
        },
    }


def test_field_became_required():
    base = _required_spec(["a"], ["b"])
    cand = _required_spec(["a", "b"], [])
    changes = detect_required_fields_added(base, cand)
    assert len(changes) == 1
    assert changes[0].kind == "required_field_added"
    assert "b" in changes[0].description


def test_multiple_fields_became_required():
    base = _required_spec(["a"], ["b", "c"])
    cand = _required_spec(["a", "b", "c"], [])
    changes = detect_required_fields_added(base, cand)
    assert len(changes) == 2


def test_no_new_required_fields():
    base = _required_spec(["a"], ["b"])
    cand = _required_spec(["a"], ["b"])
    assert detect_required_fields_added(base, cand) == []


def test_field_removed_from_required():
    """Remover campo de required[] no es detectado por este detector."""
    base = _required_spec(["a", "b"], [])
    cand = _required_spec(["a"], ["b"])
    assert detect_required_fields_added(base, cand) == []


def test_no_request_body_required():
    spec = {"openapi": "3.0.0", "info": {"title": "T", "version": "1"}, "paths": {}}
    assert detect_required_fields_added(spec, spec) == []


# ── run_all integration ─────────────────────────────────────────────────


def test_run_all_legacy_finds_4_changes():
    base = load_spec(str(FIXTURES / "base.yaml"))
    cand = load_spec(str(FIXTURES / "candidate.yaml"))
    changes = _legacy_changes(base, cand)
    assert len(changes) == 4


def test_run_all_legacy_identical_specs():
    base = load_spec(str(FIXTURES / "base.yaml"))
    changes = _legacy_changes(base, base)
    assert len(changes) == 0


def test_run_all_legacy_empty_specs():
    changes = _legacy_changes({}, {})
    assert len(changes) == 0


def test_run_all_legacy_missing_paths():
    base = {"openapi": "3.0.0", "info": {"title": "T", "version": "1"}}
    cand = {"openapi": "3.0.0", "info": {"title": "T", "version": "1"}}
    assert _legacy_changes(base, cand) == []
