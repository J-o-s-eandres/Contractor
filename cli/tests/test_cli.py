from pathlib import Path
from click.testing import CliRunner
from contractor.cli import cli

FIXTURES = Path(__file__).parent / "fixtures"
BASE = str(FIXTURES / "base.yaml")
CAND = str(FIXTURES / "candidate.yaml")


def test_diff_exits_1_on_breaking_changes():
    runner = CliRunner()
    result = runner.invoke(cli, ["diff", "--base", BASE, "--candidate", CAND])
    assert result.exit_code == 1


def test_diff_exits_0_when_no_changes():
    runner = CliRunner()
    result = runner.invoke(cli, ["diff", "--base", BASE, "--candidate", BASE])
    assert result.exit_code == 0


def test_diff_json_output():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["diff", "--base", BASE, "--candidate", CAND, "--format", "json"]
    )
    assert result.exit_code == 1
    import json

    data = json.loads(result.output)
    assert data["count"] == 4


def test_diff_markdown_writes_file(tmp_path):
    runner = CliRunner()
    out = str(tmp_path / "report.md")
    result = runner.invoke(
        cli, ["diff", "--base", BASE, "--candidate", CAND, "--output", out]
    )
    assert result.exit_code == 1
    assert Path(out).exists()
    assert "Contractor" in Path(out).read_text(encoding="utf-8")


def test_diff_missing_base_file():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["diff", "--base", "nonexistent.yaml", "--candidate", CAND]
    )
    assert result.exit_code == 2
    assert "not exist" in result.output.lower() or "Error" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
