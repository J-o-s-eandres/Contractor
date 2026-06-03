from rich.console import Console
from rich.table import Table
from rich import box
from contractor.models import BreakingChange

console = Console()


def print_results(
    changes: list[BreakingChange], base_path: str, candidate_path: str
) -> None:
    console.print()

    if not changes:
        console.print(
            f"[bold green]OK -- No breaking changes detected[/bold green]\n"
            f"  [dim]{base_path}[/dim] -> [dim]{candidate_path}[/dim]"
        )
        console.print()
        return

    console.print(
        f"[bold red]!! {len(changes)} breaking change{'s' if len(changes) != 1 else ''} detected[/bold red]\n"
        f"  [dim]{base_path}[/dim] -> [dim]{candidate_path}[/dim]"
    )
    console.print()

    table = Table(box=box.ASCII, show_header=True, header_style="bold dim")
    table.add_column("Type", style="red", no_wrap=True, min_width=22)
    table.add_column("Location", style="yellow")
    table.add_column("Description", style="white")

    kind_labels = {
        "endpoint_removed": "endpoint removed",
        "required_param_added": "required param added",
        "type_changed": "type changed",
        "required_field_added": "required field added",
    }

    for c in changes:
        table.add_row(kind_labels.get(c.kind, c.kind), c.location, c.description)

    console.print(table)
    console.print()
