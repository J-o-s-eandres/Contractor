from contractor.oasdiff_adapter import adapt_changes


def test_empty_changes():
    assert adapt_changes([]) == []


def test_filters_warn_level():
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "removed",
            "path": "/x",
            "operation": "GET",
        },
        {
            "id": "api-deprecated-sunset-missing",
            "level": 2,
            "text": "missing sunset",
            "path": "/y",
            "operation": "POST",
        },
        {
            "id": "info-level",
            "level": 1,
            "text": "info",
            "path": "/z",
            "operation": "GET",
        },
    ]
    result = adapt_changes(raw)
    assert len(result) == 1
    assert result[0].rule_id == "api-removed-without-deprecation"


def test_classify_endpoint_removed():
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "DELETE",
        }
    ]
    assert adapt_changes(raw)[0].kind == "endpoint_removed"


def test_classify_type_changed():
    raw = [
        {
            "id": "request-property-type-changed",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "POST",
        }
    ]
    assert adapt_changes(raw)[0].kind == "type_changed"


def test_classify_required_field():
    raw = [
        {
            "id": "new-required-request-header-property",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "GET",
        }
    ]
    assert adapt_changes(raw)[0].kind == "required_field_added"


def test_classify_required_param():
    raw = [
        {
            "id": "new-request-non-path-parameter",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "GET",
        }
    ]
    assert adapt_changes(raw)[0].kind == "required_param_added"


def test_classify_unknown_rule():
    raw = [
        {
            "id": "some-unknown-rule",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "GET",
        }
    ]
    assert adapt_changes(raw)[0].kind == "other"


def test_fingerprint_preserved():
    raw = [
        {
            "id": "api-removed-without-deprecation",
            "level": 3,
            "text": "x",
            "path": "/x",
            "operation": "GET",
            "fingerprint": "abc123",
        }
    ]
    assert adapt_changes(raw)[0].fingerprint == "abc123"


def test_level_mapped_correctly():
    raw = [{"id": "x", "level": 3, "text": "x", "path": "/x", "operation": "GET"}]
    assert adapt_changes(raw)[0].level == "ERR"
    assert adapt_changes(raw)[0].is_breaking is True


def test_missing_fields_dont_crash():
    raw = [{}]
    result = adapt_changes(raw)
    assert len(result) == 0


def test_partial_fields():
    raw = [{"id": "api-removed-without-deprecation", "level": 3, "text": "gone"}]
    result = adapt_changes(raw)
    assert len(result) == 1
    assert result[0].path == ""
    assert result[0].method == ""
