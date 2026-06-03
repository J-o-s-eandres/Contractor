import json
import subprocess
from unittest.mock import ANY

import pytest

from contractor.detect import run_oasdiff, _find_binary, OASDIFF_NOT_FOUND_MSG


def test_oasdiff_not_found(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.setattr("os.path.exists", lambda _: False)
    with pytest.raises(FileNotFoundError, match="oasdiff not found"):
        _find_binary()


def test_run_oasdiff_breaking(monkeypatch):
    fake_json = json.dumps(
        [
            {
                "id": "api-removed-without-deprecation",
                "level": 3,
                "operation": "DELETE",
                "path": "/users/{id}",
                "text": "the API 'DELETE /users/{id}' was removed",
                "source": "base.yaml:24:5",
                "fingerprint": "abc123",
            }
        ]
    )

    def fake_run(cmd, **kwargs):
        assert "--format" in cmd
        assert "json" in cmd
        assert cmd[-2] == "base.yaml"
        assert cmd[-1] == "feature.yaml"
        return subprocess.CompletedProcess(cmd, 1, fake_json, "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")

    changes, code = run_oasdiff("base.yaml", "feature.yaml")
    assert code == 1
    assert len(changes) == 1
    assert changes[0].kind == "endpoint_removed"
    assert changes[0].rule_id == "api-removed-without-deprecation"
    assert changes[0].method == "DELETE"
    assert changes[0].path == "/users/{id}"


def test_run_oasdiff_no_changes(monkeypatch):
    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")

    changes, code = run_oasdiff("base.yaml", "feature.yaml")
    assert code == 0
    assert len(changes) == 0


def test_run_oasdiff_returns_warn_and_err(monkeypatch):
    fake_json = json.dumps(
        [
            {
                "id": "api-removed-without-deprecation",
                "level": 3,
                "text": "breaking",
                "path": "/x",
                "operation": "GET",
            },
            {
                "id": "api-deprecated-sunset-missing",
                "level": 2,
                "text": "warning",
                "path": "/y",
                "operation": "POST",
            },
        ]
    )

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 1, fake_json, "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")

    changes, _ = run_oasdiff("base.yaml", "feature.yaml")
    assert len(changes) == 1
    assert changes[0].rule_id == "api-removed-without-deprecation"


def test_run_includes_include_path_params_flag(monkeypatch):
    captured = []

    def fake_run(cmd, **kwargs):
        captured.extend(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")

    run_oasdiff("a.yaml", "b.yaml")
    assert "--include-path-params" in captured
