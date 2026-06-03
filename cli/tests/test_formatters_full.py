"""Full coverage for formatters — every output format, every change kind, edge cases."""

import json
from pathlib import Path

from contractor.models import BreakingChange
from contractor.formatters.console import print_results
from rich.console import Console
from contractor.formatters.json_fmt import to_json
from contractor.formatters.markdown import to_markdown


def _make_changes() -> list[BreakingChange]:
    return [
        BreakingChange(
            kind="endpoint_removed",
            path="/users/{id}",
            method="DELETE",
            location="base.yaml:24:5",
            description="api removed without deprecation",
            rule_id="api-path-removed-without-deprecation",
            fingerprint="abc123",
            level="ERR",
        ),
        BreakingChange(
            kind="type_changed",
            path="/orders",
            method="POST",
            location="body.amount",
            description="type changed from string to number",
            rule_id="request-property-type-changed",
            fingerprint="def456",
            level="ERR",
        ),
        BreakingChange(
            kind="required_field_added",
            path="/orders",
            method="POST",
            location="body.notes",
            description="new required field notes",
            rule_id="new-required-request-property",
            fingerprint="ghi789",
            level="ERR",
        ),
        BreakingChange(
            kind="required_param_added",
            path="/users",
            method="GET",
            location="parameter:filter",
            description="param filter became required",
            rule_id="request-parameter-became-required",
            fingerprint="jkl012",
            level="ERR",
        ),
        BreakingChange(
            kind="other",
            path="/items",
            method="PATCH",
            location="unknown",
            description="some unknown change",
            rule_id="some-new-rule",
            fingerprint="mno345",
            level="ERR",
        ),
    ]


# ── Console formatter ──────────────────────────────────────────────────


def test_console_no_changes(capsys, monkeypatch):
    monkeypatch.setattr("contractor.formatters.console.console", Console(width=200))
    print_results([], "base.yaml", "candidate.yaml")
    captured = capsys.readouterr()
    assert "No breaking changes" in captured.out


def test_console_with_changes(capsys, monkeypatch):
    monkeypatch.setattr("contractor.formatters.console.console", Console(width=200))
    changes = _make_changes()
    print_results(changes, "base.yaml", "candidate.yaml")
    captured = capsys.readouterr()
    assert "5 breaking changes" in captured.out
    assert "endpoint removed" in captured.out
    assert "api-path-removed-without-deprecation" in captured.out


def test_console_shows_rule_id(capsys, monkeypatch):
    monkeypatch.setattr("contractor.formatters.console.console", Console(width=200))
    print_results(_make_changes()[:1], "x.yaml", "y.yaml")
    captured = capsys.readouterr()
    assert "api-path-removed-without-deprecation" in captured.out


def test_console_single_change_grammar(capsys, monkeypatch):
    monkeypatch.setattr("contractor.formatters.console.console", Console(width=200))
    changes = [
        BreakingChange(
            kind="endpoint_removed",
            path="/x",
            method="DELETE",
            location="x",
            description="removed",
        )
    ]
    print_results(changes, "a", "b")
    captured = capsys.readouterr()
    assert "1 breaking change" in captured.out  # singular, no 's'


def test_console_all_types(capsys, monkeypatch):
    monkeypatch.setattr("contractor.formatters.console.console", Console(width=200))
    kinds = [
        "endpoint_removed",
        "required_param_added",
        "type_changed",
        "required_field_added",
        "other",
    ]
    changes = [
        BreakingChange(kind=k, path="/x", method="GET", location="x", description=k)
        for k in kinds
    ]
    print_results(changes, "a", "b")
    captured = capsys.readouterr()
    for k in kinds:
        assert k in captured.out


# ── JSON formatter ──────────────────────────────────────────────────────


def test_json_structure_with_changes():
    changes = _make_changes()
    output = to_json(changes, "base.yaml", "cand.yaml")
    data = json.loads(output)
    assert data["breaking"] is True
    assert data["count"] == 5
    assert data["base"] == "base.yaml"
    assert data["candidate"] == "cand.yaml"
    assert data["engine"] == "oasdiff"
    assert len(data["changes"]) == 5


def test_json_structure_no_changes():
    output = to_json([], "base.yaml", "cand.yaml")
    data = json.loads(output)
    assert data["breaking"] is False
    assert data["count"] == 0
    assert data["changes"] == []


def json_change_fields():
    c = _make_changes()[0]
    output = to_json([c], "b.yaml", "c.yaml")
    data = json.loads(output)
    change = data["changes"][0]
    assert change["kind"] == "endpoint_removed"
    assert change["path"] == "/users/{id}"
    assert change["method"] == "DELETE"
    assert change["description"] == "api removed without deprecation"
    assert change["rule_id"] == "api-path-removed-without-deprecation"
    assert change["fingerprint"] == "abc123"
    assert change["level"] == "ERR"


def test_json_change_fields():
    json_change_fields()


def test_json_all_fields_present():
    changes = _make_changes()
    output = to_json(changes, "b.yaml", "c.yaml")
    data = json.loads(output)
    for c in data["changes"]:
        assert "kind" in c
        assert "path" in c
        assert "method" in c
        assert "description" in c
        assert "rule_id" in c
        assert "fingerprint" in c
        assert "level" in c


# ── Markdown formatter ─────────────────────────────────────────────────


def test_markdown_no_changes():
    output = to_markdown([], "base.yaml", "cand.yaml")
    assert "No Breaking Changes" in output
    assert "base.yaml" in output
    assert "cand.yaml" in output


def test_markdown_with_changes():
    output = to_markdown(_make_changes(), "base.yaml", "cand.yaml")
    assert "5 Breaking Changes" in output
    assert "| Type" in output
    assert "| Location" in output
    assert "| Description" in output


def test_markdown_contains_all_types():
    kinds = [
        "endpoint_removed",
        "required_param_added",
        "type_changed",
        "required_field_added",
        "other",
    ]
    changes = [
        BreakingChange(kind=k, path="/x", method="GET", location="x", description=k)
        for k in kinds
    ]
    output = to_markdown(changes, "a", "b")
    for k in kinds:
        label_map = {
            "endpoint_removed": "Endpoint removed",
            "required_param_added": "Required param added",
            "type_changed": "Type changed",
            "required_field_added": "Required field added",
            "other": "Other",
        }
        assert label_map[k] in output


def test_markdown_shows_rule_id():
    c = [
        BreakingChange(
            kind="endpoint_removed",
            path="/x",
            method="DELETE",
            location="x:1",
            description="removed",
            rule_id="api-path-removed-without-deprecation",
        )
    ]
    output = to_markdown(c, "a", "b")
    assert "api-path-removed-without-deprecation" in output


def test_markdown_no_rule_id():
    c = [
        BreakingChange(
            kind="endpoint_removed",
            path="/x",
            method="DELETE",
            location="x:1",
            description="removed",
        )
    ]
    output = to_markdown(c, "a", "b")
    assert "removed" in output


def test_markdown_timestamp():
    import re

    output = to_markdown([], "a", "b")
    assert re.search(r"\d{4}-\d{2}-\d{2}", output)


def test_markdown_generated_by_footer():
    output = to_markdown(_make_changes(), "a", "b")
    assert "Generated by" in output
    assert "Contractor" in output


# ── Edge cases ──────────────────────────────────────────────────────────


def test_json_accepts_empty_rule_id():
    c = [
        BreakingChange(
            kind="endpoint_removed",
            path="/x",
            method="GET",
            location="x",
            description="x",
        )
    ]
    output = json.loads(to_json(c, "a", "b"))
    assert output["changes"][0]["rule_id"] == ""


def test_json_accepts_empty_fingerprint():
    c = [
        BreakingChange(
            kind="endpoint_removed",
            path="/x",
            method="GET",
            location="x",
            description="x",
        )
    ]
    output = json.loads(to_json(c, "a", "b"))
    assert output["changes"][0]["fingerprint"] == ""


def test_json_with_warn_level():
    c = BreakingChange(
        kind="other",
        path="/x",
        method="GET",
        location="x",
        description="warn",
        rule_id="some-warn",
        level="WARN",
    )
    output = json.loads(to_json([c], "a", "b"))
    assert output["changes"][0]["level"] == "WARN"
    assert output["changes"][0]["base_value"] == ""
    assert output["changes"][0]["candidate_value"] == ""
