import platform
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from rich import box, print
from rich.console import Console
from rich.table import Table


@dataclass
class TestsExeecutionReport:
    total: int
    passed: int
    warnings: int
    errors: int
    skipped: int

    @property
    def passed_percent(self) -> int:
        return int((self.passed / self.total) * 100)

    @property
    def warnings_percent(self) -> int:
        return int((self.warnings / self.total) * 100)

    @property
    def errors_percent(self) -> int:
        return int((self.errors / self.total) * 100)

    @property
    def skipped_percent(self) -> int:
        return int((self.skipped / self.total) * 100)


@dataclass
class TestResult:
    percent: int
    label: str
    status: Optional[str] = "success"
    output: Optional[Any] = None
    postmessage: Optional[str] = ""
    comment: Optional[str] = None


def print_results_table(report: TestsExeecutionReport) -> None:
    table = Table(title="Tests Result", expand=True, box=box.ROUNDED)

    table.add_column("N", style="cyan")
    table.add_column("Tests encountered", style="cyan")
    table.add_column("Percent", style="cyan")

    table.add_row(str(report.total), "Total", "100%")
    table.add_row(
        str(report.passed),
        "Passed",
        f"{report.passed_percent}%",
        style="black bold on green",
    )
    table.add_row(
        str(report.warnings),
        "Warnings",
        f"{report.warnings_percent}%",
        style="black bold on yellow",
    )
    table.add_row(
        str(report.errors),
        "Errors",
        f"{report.errors_percent}%",
        style="black bold on red",
    )
    table.add_row(
        str(report.skipped),
        "Skipped",
        f"{report.skipped_percent}%",
        style="black bold on blue",
    )

    console = Console()
    console.print(table)


def print_header(label: str, plus_len: int = 0, style: str = "bold") -> None:
    width: int = shutil.get_terminal_size().columns - 2 + plus_len

    line: str = f" {label} ".center(width, "=")

    print(f"[{style}]{line}[/{style}]")


def print_platform(items: int) -> None:
    print(f"[white]platform: [reset]{platform.platform()}[/white]")
    print(f"[white]version: [reset]{platform.version()}[/white]")
    print(f"[white]release: [reset]{platform.release()}[/white]")
    print(f"[white]system: [reset]{platform.system()}[/white]")
    print(f"[white]python: [reset]{platform.python_version()}[/white]")
    print(f"[white bold]Collected {items} items[/white bold]\n")


def print_comment(comment: str) -> None:
    print(f"[dim]{comment}[/dim]")


def print_test_result(test_result: TestResult) -> None:
    date: str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    width: int = (
        shutil.get_terminal_size().columns
        - 13
        - len(date)
        - len(test_result.postmessage)
    )

    if test_result.comment is not None:
        label = f"[dim]{test_result.label}[/dim] [white]{test_result.comment}[/white]"
        width += 26

    if test_result.status == "success":
        print(
            f"[black bold on green]PASS[/black bold on green] {date} [green]{label.ljust(width)}[/green][black on blue]{test_result.postmessage}[/black on blue] [dim green][{str(test_result.percent).rjust(3)}%][/dim green]"
        )
    elif test_result.status == "error":
        print(
            f"\n[black bold on red]ERR [/black bold on red] {date} [red]{label.ljust(width)}[/red][black on blue]{test_result.postmessage}[/black on blue] [dim red][{str(test_result.percent).rjust(3)}%][/dim red]"
        )
        print_header(f"ERROR: {label}", style="bold red")
        print(f"[red]{test_result.output}[/red]")
    elif test_result.status == "warning":
        print(
            f"[black bold on yellow]WARN[/black bold on yellow] {date} [yellow]{label.ljust(width)}[/yellow][black on blue]{test_result.postmessage}[/black on blue] [dim yellow][{str(test_result.percent).rjust(3)}%][/dim yellow]"
        )
        print(f"[yellow] > {test_result.output}[/yellow]\n")
    elif test_result.status == "skip":
        print(
            f"[black bold on blue]SKIP[/black bold on blue] {date} [blue]{label.ljust(width)}[/blue][black on blue]{test_result.postmessage}[/black on blue] [dim blue][{str(test_result.percent).rjust(3)}%][/dim blue]"
        )
