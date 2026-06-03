"""Full coverage tests for CLI (cli.py) — all flags, errors, edge cases."""

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner
from contractor.cli import cli

FIXTURES = Path(__file__).parent / "fixtures"
BASE = str(FIXTURES / "base.yaml")
CAND = str(FIXTURES / "candidate.yaml")
LEGACY = ["--engine", "legacy"]


def _invoke(args: list[str]) -> subprocess.CompletedProcess:
    """Helper: run CLI via CliRunner."""
    runner = CliRunner()
    return runner.invoke(cli, args)


# ── Basic execution paths ───────────────────────────────────────────────


def test_diff_help():
    result = _invoke(["diff", "--help"])
    assert result.exit_code == 0
    assert "Detect breaking changes" in result.output


def test_diff_default_engine_oasdiff(monkeypatch):
    """Verificar que el engine por defecto es oasdiff."""

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")
    result = _invoke(["diff", "--base", BASE, "--candidate", BASE])
    assert result.exit_code == 0


def test_diff_engine_oasdiff_explicit(monkeypatch):
    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", BASE, "--engine", "oasdiff"]
    )
    assert result.exit_code == 0


def test_diff_engine_legacy():
    result = _invoke(["diff", "--base", BASE, "--candidate", BASE, *LEGACY])
    assert result.exit_code == 0


def test_diff_engine_legacy_breaking():
    result = _invoke(["diff", "--base", BASE, "--candidate", CAND, *LEGACY])
    assert result.exit_code == 1
    assert "4 breaking change" in result.output


def test_diff_exits_0_on_no_changes():
    result = _invoke(["diff", "--base", BASE, "--candidate", BASE, *LEGACY])
    assert result.exit_code == 0
    assert "No breaking changes" in result.output


# ── Format options ──────────────────────────────────────────────────────


def test_format_console_default():
    result = _invoke(["diff", "--base", BASE, "--candidate", CAND, *LEGACY])
    assert result.exit_code == 1
    assert "breaking" in result.output


def test_format_json():
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", CAND, "--format", "json", *LEGACY]
    )
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["count"] == 4
    assert data["engine"] == "oasdiff"


def test_format_json_no_changes():
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", BASE, "--format", "json", *LEGACY]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["count"] == 0
    assert data["breaking"] is False


def test_format_markdown():
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", CAND, "--format", "markdown", *LEGACY]
    )
    assert result.exit_code == 1
    assert "## Contractor" in result.output
    assert "| Type |" in result.output


def test_format_markdown_no_changes():
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", BASE, "--format", "markdown", *LEGACY]
    )
    assert result.exit_code == 0
    assert "No Breaking Changes" in result.output


def test_format_invalid():
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", CAND, "--format", "xml", *LEGACY]
    )
    assert result.exit_code == 2
    assert "Invalid value" in result.output or "Invalid choice" in result.output


# ── Output file ─────────────────────────────────────────────────────────


def test_output_file_writes_markdown(tmp_path):
    out = str(tmp_path / "report.md")
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", CAND, "--output", out, *LEGACY]
    )
    assert result.exit_code == 1
    assert Path(out).exists()
    content = Path(out).read_text(encoding="utf-8")
    assert "## Contractor" in content
    assert "Endpoint removed" in content


def test_output_file_with_json_format(tmp_path):
    "--output siempre escribe markdown, incluso con --format json"
    out = str(tmp_path / "report.md")
    result = _invoke(
        [
            "diff",
            "--base",
            BASE,
            "--candidate",
            CAND,
            "--format",
            "json",
            "--output",
            out,
            *LEGACY,
        ]
    )
    assert result.exit_code == 1
    assert Path(out).exists()
    content = Path(out).read_text(encoding="utf-8")
    assert "## Contractor" in content
    assert "4 Breaking" in content


def test_output_file_with_markdown_format(tmp_path):
    out = str(tmp_path / "report.md")
    result = _invoke(
        [
            "diff",
            "--base",
            BASE,
            "--candidate",
            CAND,
            "--format",
            "markdown",
            "--output",
            out,
            *LEGACY,
        ]
    )
    assert result.exit_code == 1
    assert Path(out).exists()
    assert "No Breaking Changes" not in Path(out).read_text()


def test_output_file_stdout_still_shows(tmp_path, capsys):
    """Con --output, el mensaje 'Report written to' debe aparecer en stdout."""
    out = str(tmp_path / "report.md")
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", CAND, "--output", out, *LEGACY]
    )
    assert result.exit_code == 1
    assert "Report written to" in result.output


# ── Error handling ──────────────────────────────────────────────────────


def test_missing_base_file():
    result = _invoke(
        ["diff", "--base", "nonexistent.yaml", "--candidate", CAND, *LEGACY]
    )
    assert result.exit_code == 2
    assert "does not exist" in result.output or "not exist" in result.output


def test_missing_candidate_file():
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", "nonexistent.yaml", *LEGACY]
    )
    assert result.exit_code == 2


def test_invalid_yaml_base(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("{{invalid: yaml: here", encoding="utf-8")
    result = _invoke(["diff", "--base", str(bad), "--candidate", CAND, *LEGACY])
    assert result.exit_code == 2
    assert "Error" in result.output or "Failed to parse" in result.output


def test_empty_file(tmp_path):
    empty = tmp_path / "empty.yaml"
    empty.write_text("", encoding="utf-8")
    result = _invoke(["diff", "--base", str(empty), "--candidate", CAND, *LEGACY])
    assert result.exit_code == 2


def test_file_with_only_comments(tmp_path):
    comments = tmp_path / "comments.yaml"
    comments.write_text("# just a comment\n# another\n", encoding="utf-8")
    result = _invoke(["diff", "--base", str(comments), "--candidate", CAND, *LEGACY])
    assert result.exit_code == 2


def test_version():
    result = _invoke(["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


# ── CLI with oasdiff mock ───────────────────────────────────────────────


def test_oasdiff_engine_with_breaking(monkeypatch):
    fake_json = json.dumps(
        [
            {
                "id": "api-path-removed-without-deprecation",
                "level": 3,
                "operation": "DELETE",
                "path": "/users/{id}",
                "text": "api path removed without deprecation",
                "source": "base.yaml:7:5",
                "fingerprint": "abc123",
            }
        ]
    )

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 1, fake_json, "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")

    result = _invoke(["diff", "--base", BASE, "--candidate", CAND])
    assert result.exit_code == 1
    assert "endpoint removed" in result.output.lower()


def test_oasdiff_engine_no_changes(monkeypatch):
    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")

    result = _invoke(["diff", "--base", BASE, "--candidate", BASE])
    assert result.exit_code == 0
    assert "No breaking changes" in result.output


def test_oasdiff_not_installed_gives_clear_error(monkeypatch):
    def fake_find(*args, **kwargs):
        raise FileNotFoundError("oasdiff not found")

    monkeypatch.setattr("contractor.detect._find_binary", fake_find)
    result = _invoke(
        ["diff", "--base", BASE, "--candidate", CAND, "--engine", "oasdiff"]
    )
    assert result.exit_code == 2
    assert "oasdiff not found" in result.output.lower()


def test_oasdiff_error_exit(monkeypatch):
    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 2, "", "invalid spec syntax")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/oasdiff")

    with pytest.raises(SystemExit):
        from contractor.detect import run_oasdiff

        run_oasdiff("x.yaml", "y.yaml")
