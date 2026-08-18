"""
HyperClean Studio - Rich Terminal CLI Runner
Provides interactive terminal scanning and cleanup using Rich tables and progress bars.
"""

import sys
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn
from rich.prompt import Confirm

from core.scanner import SystemScanner
from core.cleaner import SystemCleaner
from core.models import ScanResult, CleanProgressReport
from core.utils import format_size, is_admin, get_disk_info

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(force_terminal=True, legacy_windows=False)



def run_cli_scan() -> ScanResult:
    console.print(
        Panel.fit(
            "[bold cyan]⚡ HyperClean Studio[/bold cyan] - [dim]Master System & Developer Cache Cleaner[/dim]",
            border_style="blue",
        )
    )

    admin_status = "[bold green]ADMINISTRATOR[/bold green]" if is_admin() else "[bold yellow]USER MODE[/bold yellow]"
    console.print(f"Privilege Status: {admin_status}\n")

    scanner = SystemScanner()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Analyzing disk caches...", total=None)

        def _cb(status: str, pct: float):
            progress.update(task, description=f"[cyan]{status}[/cyan]")

        result = scanner.run_scan(progress_callback=_cb)

    # Render Summary Table
    table = Table(title=f"Scan Analysis Complete ({result.elapsed_seconds}s)", header_style="bold magenta")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Targets Count", justify="right", style="yellow")
    table.add_column("Reclaimable Size", justify="right", style="green")

    for cat, group in result.groups.items():
        if group.total_count > 0:
            table.add_row(
                cat.value,
                str(group.total_count),
                format_size(group.total_size_bytes),
            )

    table.add_section()
    table.add_row(
        "[bold]TOTAL RECLAIMABLE[/bold]",
        f"[bold]{result.total_targets}[/bold]",
        f"[bold green]{format_size(result.total_size_bytes)}[/bold green]",
    )

    console.print(table)
    return result


def run_cli_clean(dry_run: bool = False):
    result = run_cli_scan()
    if result.total_targets == 0:
        console.print("[green]No junk caches found. System is clean![/green]")
        return

    if not dry_run:
        confirm = Confirm.ask(
            f"\n[bold red]Are you sure you want to permanently delete {format_size(result.total_size_bytes)} across {result.total_targets} targets?[/bold red]"
        )
        if not confirm:
            console.print("[yellow]Cleanup cancelled by user.[/yellow]")
            return

    cleaner = SystemCleaner()
    all_targets = []
    for g in result.groups.values():
        all_targets.extend(g.targets)

    mode_label = "[bold purple]DRY-RUN SIMULATION[/bold purple]" if dry_run else "[bold green]PERMANENT CLEANUP[/bold green]"
    console.print(f"\nExecuting {mode_label}...")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        clean_task = progress.add_task("Cleaning...", total=len(all_targets))

        def _clean_cb(report: CleanProgressReport):
            progress.update(
                clean_task,
                completed=report.completed_items,
                description=f"[cyan]Processing: {report.current_item[:40]}[/cyan]",
            )

        final_report = cleaner.clean_targets(
            targets=all_targets,
            dry_run=dry_run,
            progress_callback=_clean_cb,
        )

    console.print(
        f"\n[bold green]✅ Clean Finished! Reclaimed {format_size(final_report.freed_bytes)} of disk space.[/bold green]"
    )
