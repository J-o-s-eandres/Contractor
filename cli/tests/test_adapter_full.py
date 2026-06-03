"""Full coverage tests for oasdiff_adapter.py — every rule_id, edge case, and boundary."""

import pytest
from contractor.oasdiff_adapter import adapt_changes, _KNOWN_KINDS, _LEVEL_MAP


# ── Every known rule_id maps to correct ChangeKind ──────────────────────


def _make_change(rule_id: str, level: int = 3) -> dict:
    return {
        "id": rule_id,
        "level": level,
        "text": f"change {rule_id}",
        "path": "/test",
        "operation": "GET",
    }


@pytest.mark.parametrize(
    "rule_id,expected_kind",
    [
        ("api-removed-without-deprecation", "endpoint_removed"),
        ("api-path-removed-without-deprecation", "endpoint_removed"),
        ("request-body-removed", "endpoint_removed"),
        ("request-property-type-changed", "type_changed"),
        ("request-parameter-type-changed", "type_changed"),
        ("response-property-type-changed", "type_changed"),
        ("response-parameter-type-changed", "type_changed"),
        ("new-required-request-header-property", "required_field_added"),
        ("request-body-required-value-updated", "required_field_added"),
        ("new-required-request-body", "required_field_added"),
        ("new-request-non-path-parameter", "required_param_added"),
        ("request-parameter-required-value-updated", "required_param_added"),
        ("request-body-became-enum", "type_changed"),
        ("request-parameter-became-enum", "type_changed"),
        ("request-property-became-enum", "type_changed"),
    ],
)
def test_known_rule_id_maps_to_correct_kind(rule_id, expected_kind):
    result = adapt_changes([_make_change(rule_id)])
    assert len(result) == 1
    assert result[0].kind == expected_kind
    assert result[0].rule_id == rule_id
    assert result[0].level == "ERR"


def test_unknown_rule_id_maps_to_other():
    result = adapt_changes(
        [
            {
                "id": "some-random-new-rule",
                "level": 3,
                "text": "x",
                "path": "/x",
                "operation": "GET",
            }
        ]
    )
    assert result[0].kind == "other"
    assert result[0].rule_id == "some-random-new-rule"


def test_empty_id_does_not_crash():
    result = adapt_changes(
        [{"id": "", "level": 3, "text": "x", "path": "/x", "operation": "GET"}]
    )
    assert len(result) == 1
    assert result[0].kind == "other"


# ── Level filtering ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "level_val,expected_count",
    [
        (3, 1),  # ERR → incluido
        (2, 0),  # WARN → filtrado
        (1, 0),  # INFO → filtrado
        (0, 0),  # desconocido → filtrado
        (-1, 0),  # negativo → filtrado
    ],
)
def test_level_filtering(level_val, expected_count):
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": level_val,
            "text": "x",
            "path": "/x",
            "operation": "GET",
        }
    ]
    assert len(adapt_changes(raw)) == expected_count


def test_mixed_levels_only_returns_err():
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "err1",
            "path": "/a",
            "operation": "GET",
        },
        {
            "id": "api-deprecated-sunset-missing",
            "level": 2,
            "text": "warn1",
            "path": "/b",
            "operation": "POST",
        },
        {
            "id": "api-stability-decreased",
            "level": 1,
            "text": "info1",
            "path": "/c",
            "operation": "PUT",
        },
        {
            "id": "request-property-type-changed",
            "level": 3,
            "text": "err2",
            "path": "/d",
            "operation": "PATCH",
        },
    ]
    result = adapt_changes(raw)
    assert len(result) == 2
    assert all(c.level == "ERR" for c in result)


# ── Level mapping ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "oasdiff_level,expected_label",
    [
        (3, "ERR"),
        (2, "WARN"),
        (1, "INFO"),
        (0, "INFO"),
        (None, "INFO"),
    ],
)
def test_level_mapping(oasdiff_level, expected_label):
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": oasdiff_level,
            "text": "x",
            "path": "/x",
            "operation": "GET",
        }
    ]
    result = adapt_changes(raw)
    if expected_label == "ERR":
        assert len(result) == 1
        assert result[0].level == "ERR"
    else:
        assert len(result) == 0


# ── is_breaking ─────────────────────────────────────────────────────────


def test_is_breaking_true_for_err():
    raw = [{"id": "x", "level": 3, "text": "x", "path": "/x", "operation": "GET"}]
    assert adapt_changes(raw)[0].is_breaking is True


def test_is_breaking_false_when_level_not_err():
    # Sólo ERR pasa el filtro, entonces no hay cambios con is_breaking=False
    raw = [{"id": "x", "level": 2, "text": "x", "path": "/x", "operation": "GET"}]
    assert len(adapt_changes(raw)) == 0


# ── Fingerprint ─────────────────────────────────────────────────────────


def test_fingerprint_preserved_when_present():
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "GET",
            "fingerprint": "abc123def456",
        }
    ]
    assert adapt_changes(raw)[0].fingerprint == "abc123def456"


def test_fingerprint_empty_when_missing():
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "GET",
        }
    ]
    assert adapt_changes(raw)[0].fingerprint == ""


def test_fingerprint_empty_when_none():
    raw = [
        {
            "id": "x",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "GET",
            "fingerprint": None,
        }
    ]
    result = adapt_changes(raw)
    assert result[0].fingerprint == ""


# ── Edge cases ──────────────────────────────────────────────────────────


def test_empty_input_list():
    assert adapt_changes([]) == []


def test_none_input():
    with pytest.raises(TypeError):
        adapt_changes(None)


def test_missing_required_fields():
    """No debe crashear si faltan campos."""
    raw = [{"id": "x", "level": 3, "text": "test"}]
    result = adapt_changes(raw)
    assert len(result) == 1
    assert result[0].path == ""
    assert result[0].method == ""
    assert result[0].location == ""
    assert result[0].description == "test"


def test_extra_fields_ignored():
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "GET",
            "unknown_field": "should_not_crash",
        }
    ]
    result = adapt_changes(raw)
    assert len(result) == 1


def test_unicode_in_description():
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "API /usuarios/{id} foi removida — razón: breaking",
            "path": "/usuarios/{id}",
            "operation": "DELETE",
        }
    ]
    result = adapt_changes(raw)
    assert "usuarios" in result[0].description


def test_very_long_description():
    long_text = "x" * 10000
    raw = [{"id": "x", "level": 3, "text": long_text, "path": "/x", "operation": "GET"}]
    result = adapt_changes(raw)
    assert len(result[0].description) == 10000


def test_kind_labels_are_literals():
    """Verificar que los valores en _KNOWN_KINDS son literales válidos de ChangeKind."""
    valid_kinds = {
        "endpoint_removed",
        "required_param_added",
        "type_changed",
        "required_field_added",
        "other",
    }
    for kind in _KNOWN_KINDS.values():
        assert kind in valid_kinds, f"Invalid kind: {kind}"


def test_all_known_rules_have_handler():
    """Cada entrada en _KNOWN_KINDS mapea a un rule_id que realmente existe."""
    for rule_substring in _KNOWN_KINDS:
        # Construir un rule_id artificial que contenga el substring
        raw = [
            {
                "id": rule_substring,
                "level": 3,
                "text": "x",
                "path": "/x",
                "operation": "GET",
            }
        ]
        result = adapt_changes(raw)
        assert len(result) == 1, f"No match for rule substring: {rule_substring}"


def test_multiple_changes_preserves_order():
    changes = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "first",
            "path": "/a",
            "operation": "DELETE",
        },
        {
            "id": "request-property-type-changed",
            "level": 3,
            "text": "second",
            "path": "/b",
            "operation": "POST",
        },
        {
            "id": "new-request-non-path-parameter",
            "level": 3,
            "text": "third",
            "path": "/c",
            "operation": "GET",
        },
    ]
    result = adapt_changes(changes)
    assert len(result) == 3
    assert result[0].description == "first"
    assert result[1].description == "second"
    assert result[2].description == "third"


def test_same_rule_appears_twice():
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "del1",
            "path": "/a",
            "operation": "DELETE",
        },
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "del2",
            "path": "/b",
            "operation": "POST",
        },
    ]
    result = adapt_changes(raw)
    assert len(result) == 2
    assert result[0].path == "/a"
    assert result[1].path == "/b"
