import json
from pathlib import Path
from unittest.mock import ANY

from click.testing import CliRunner
from contractor.cli import cli

FIXTURES = Path(__file__).parent / "fixtures"
BASE = str(FIXTURES / "base.yaml")
CAND = str(FIXTURES / "candidate.yaml")
LEGACY = ["--engine", "legacy"]


def test_diff_exits_1_on_breaking_changes():
    runner = CliRunner()
    result = runner.invoke(cli, ["diff", "--base", BASE, "--candidate", CAND, *LEGACY])
    assert result.exit_code == 1


def test_diff_exits_0_when_no_changes():
    runner = CliRunner()
    result = runner.invoke(cli, ["diff", "--base", BASE, "--candidate", BASE, *LEGACY])
    assert result.exit_code == 0


def test_diff_json_output():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["diff", "--base", BASE, "--candidate", CAND, "--format", "json", *LEGACY]
    )
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["count"] == 4


def test_diff_markdown_writes_file(tmp_path):
    runner = CliRunner()
    out = str(tmp_path / "report.md")
    result = runner.invoke(
        cli, ["diff", "--base", BASE, "--candidate", CAND, "--output", out, *LEGACY]
    )
    assert result.exit_code == 1
    assert Path(out).exists()
    assert "Contractor" in Path(out).read_text(encoding="utf-8")


def test_diff_missing_base_file():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["diff", "--base", "nonexistent.yaml", "--candidate", CAND, *LEGACY]
    )
    assert result.exit_code == 2
    assert "not exist" in result.output.lower() or "Error" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_diff_oasdiff_engine(monkeypatch):
    import subprocess

    fake_json = json.dumps(
        [
            {
                "id": "api-removed-without-deprecation",
                "level": 3,
                "operation": "DELETE",
                "path": "/users/{id}",
                "text": "the API 'DELETE /users/{id}' was removed without deprecation",
                "source": "base.yaml:24:5",
                "fingerprint": "abc123",
            }
        ]
    )

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 1, fake_json, "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")

    runner = CliRunner()
    result = runner.invoke(cli, ["diff", "--base", BASE, "--candidate", CAND])
    assert result.exit_code == 1
    assert "DELETE" in result.output
    assert "endpoint removed" in result.output
