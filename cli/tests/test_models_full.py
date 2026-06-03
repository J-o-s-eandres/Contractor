"""Full coverage tests for BreakingChange model — equality, hash, serialization, edge cases."""

from dataclasses import asdict
from contractor.models import BreakingChange, ChangeKind


def _make(kind: ChangeKind = "other", **overrides) -> BreakingChange:
    defaults = dict(
        kind=kind,
        path="/test",
        method="GET",
        location="test:1",
        description="a change",
    )
    defaults.update(overrides)
    return BreakingChange(**defaults)


# ── Construction ─────────────────────────────────────────────────────────


def test_default_fields():
    bc = _make()
    assert bc.rule_id == ""
    assert bc.fingerprint == ""
    assert bc.level == "ERR"
    assert bc.base_value == ""
    assert bc.candidate_value == ""


def test_all_fields_explicit():
    bc = BreakingChange(
        kind="endpoint_removed",
        path="/users/{id}",
        method="DELETE",
        location="base.yaml:24",
        description="endpoint removed without deprecation",
        rule_id="api-path-removed-without-deprecation",
        fingerprint="abc123def456",
        level="ERR",
        base_value="DELETE /users/{id}",
        candidate_value="",
    )
    assert bc.kind == "endpoint_removed"
    assert bc.path == "/users/{id}"
    assert bc.method == "DELETE"
    assert bc.location == "base.yaml:24"
    assert bc.description == "endpoint removed without deprecation"
    assert bc.rule_id == "api-path-removed-without-deprecation"
    assert bc.fingerprint == "abc123def456"
    assert bc.level == "ERR"
    assert bc.base_value == "DELETE /users/{id}"
    assert bc.candidate_value == ""


# ── Equality ─────────────────────────────────────────────────────────────


def test_equality_same_fields():
    assert _make() == _make()


def test_equality_different_kind():
    assert _make(kind="endpoint_removed") != _make(kind="type_changed")


def test_equality_different_path():
    assert _make(path="/a") != _make(path="/b")


def test_equality_different_method():
    assert _make(method="GET") != _make(method="POST")


def test_equality_different_description():
    assert _make(description="x") != _make(description="y")


def test_equality_with_rule_id():
    a = _make(rule_id="api-removed-without-deprecation")
    b = _make(rule_id="api-removed-without-deprecation")
    assert a == b


def test_equality_different_rule_id():
    assert _make(rule_id="a") != _make(rule_id="b")


def test_equality_different_level():
    a = _make(level="ERR")
    b = _make(level="WARN")
    assert a != b


# ── Hash ─────────────────────────────────────────────────────────────────


def test_hashable():
    bc = _make()
    assert hash(bc) is not None


def test_hash_equal_for_equal_objects():
    s = {_make(), _make()}
    assert len(s) == 1


def test_hash_different_for_different_objects():
    s = {_make(path="/a"), _make(path="/b")}
    assert len(s) == 2


def test_hash_different_kind():
    s = {_make(kind="endpoint_removed"), _make(kind="type_changed")}
    assert len(s) == 2


# ── Serialization ────────────────────────────────────────────────────────


def test_asdict_contains_all_fields():
    bc = _make(
        rule_id="x",
        fingerprint="y",
        level="WARN",
        base_value="old",
        candidate_value="new",
    )
    d = asdict(bc)
    assert d["kind"] == "other"
    assert d["path"] == "/test"
    assert d["method"] == "GET"
    assert d["location"] == "test:1"
    assert d["description"] == "a change"
    assert d["rule_id"] == "x"
    assert d["fingerprint"] == "y"
    assert d["level"] == "WARN"
    assert d["base_value"] == "old"
    assert d["candidate_value"] == "new"


def test_asdict_no_missing_keys():
    bc = _make()
    d = asdict(bc)
    expected_keys = {
        "kind",
        "path",
        "method",
        "location",
        "description",
        "rule_id",
        "fingerprint",
        "level",
        "base_value",
        "candidate_value",
    }
    assert set(d.keys()) == expected_keys


# ── is_breaking ──────────────────────────────────────────────────────────


def test_is_breaking_true_for_err():
    assert _make(level="ERR").is_breaking is True


def test_is_breaking_false_for_warn():
    assert _make(level="WARN").is_breaking is False


def test_is_breaking_false_for_info():
    assert _make(level="INFO").is_breaking is False


def test_is_breaking_default_is_err():
    assert _make().is_breaking is True


# ── All kind literals ────────────────────────────────────────────────────


def test_all_kind_literals():
    for kind in [
        "endpoint_removed",
        "required_param_added",
        "type_changed",
        "required_field_added",
        "other",
    ]:
        bc = _make(kind=kind)
        assert bc.kind == kind


# ── String defaults ──────────────────────────────────────────────────────


def test_empty_strings_default():
    bc = BreakingChange(kind="other", path="", method="", location="", description="")
    assert bc.path == ""
    assert bc.method == ""
    assert bc.location == ""
    assert bc.description == ""


# ── Level variants ───────────────────────────────────────────────────────


def test_all_levels():
    for level in ["ERR", "WARN", "INFO"]:
        bc = _make(level=level)
        assert bc.level == level


def test_lowercase_level_stored_as_is():
    """The model doesn't validate level values, it stores what you give."""
    bc = _make(level="err")
    assert bc.level == "err"


# ── Fingerprint handling ─────────────────────────────────────────────────


def test_fingerprint_empty_by_default():
    assert _make().fingerprint == ""


def test_fingerprint_long_value():
    fp = "a" * 64
    bc = _make(fingerprint=fp)
    assert bc.fingerprint == fp
    assert len(bc.fingerprint) == 64


def test_fingerprint_with_special_chars():
    fp = "abc-123_def+ghi/jkl:456"
    bc = _make(fingerprint=fp)
    assert bc.fingerprint == fp


# ── Mutability ───────────────────────────────────────────────────────────


def test_fields_are_mutable():
    """dataclass fields are mutable by default"""
    bc = _make()
    bc.kind = "type_changed"
    assert bc.kind == "type_changed"
    bc.path = "/new-path"
    assert bc.path == "/new-path"
    bc.description = "updated"
    assert bc.description == "updated"
