import sys
from pathlib import Path

import click

from contractor import __version__
from contractor.detectors import run_all
from contractor.formatters.console import print_results
from contractor.formatters.json_fmt import to_json
from contractor.formatters.markdown import to_markdown
from contractor.parser import load_spec


@click.group()
@click.version_option(version=__version__, prog_name="contractor")
def cli() -> None:
    """Contractor -- API contract testing for engineering teams."""


@cli.command()
@click.option(
    "--base",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the base OpenAPI spec (e.g. main branch).",
)
@click.option(
    "--candidate",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the candidate OpenAPI spec (e.g. feature branch).",
)
@click.option(
    "--format",
    "fmt",
    default="console",
    type=click.Choice(["console", "json", "markdown"], case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(dir_okay=False),
    help="Write a Markdown report to this file path (in addition to console output).",
)
def diff(base: str, candidate: str, fmt: str, output: str | None) -> None:
    """Detect breaking changes between two OpenAPI specs.

    Exits with code 0 if no breaking changes are found, 1 otherwise.
    """
    try:
        base_spec = load_spec(base)
        candidate_spec = load_spec(candidate)
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(2)

    changes = run_all(base_spec, candidate_spec)

    if fmt == "json":
        click.echo(to_json(changes, base, candidate))
    elif fmt == "markdown":
        click.echo(to_markdown(changes, base, candidate))
    else:
        print_results(changes, base, candidate)

    if output:
        report = to_markdown(changes, base, candidate)
        Path(output).write_text(report, encoding="utf-8")
        if fmt != "json":
            click.echo(f"Report written to {output}")

    sys.exit(1 if changes else 0)
