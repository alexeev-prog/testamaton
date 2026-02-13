import re
import platform
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from rich import box, print
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.measure import measure_renderables

console = Console()


@dataclass
class TestsExeecutionReport:
    total: int
    passed: int
    warnings: int
    errors: int
    skipped: int

    @property
    def passed_percent(self) -> int:
        return int((self.passed / self.total) * 100) if self.total > 0 else 0

    @property
    def warnings_percent(self) -> int:
        return int((self.warnings / self.total) * 100) if self.total > 0 else 0

    @property
    def errors_percent(self) -> int:
        return int((self.errors / self.total) * 100) if self.total > 0 else 0

    @property
    def skipped_percent(self) -> int:
        return int((self.skipped / self.total) * 100) if self.total > 0 else 0


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

    table.add_column("N", style="cyan", justify="right")
    table.add_column("Tests encountered", style="cyan")
    table.add_column("Percent", style="cyan", justify="right")

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


def strip_rich(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\[/?[a-z0-9_]+(?:=[^\]]+)?\]", "", text)
    text = re.sub(r"\\\[", "[", text)
    text = re.sub(r"\\\]", "]", text)
    return text


def print_header(label: str, plus_len: int = 0, style: str = "bold") -> None:
    width: int = shutil.get_terminal_size().columns - 2 + plus_len
    line: str = f" {label} ".center(width, "=")
    console.print(f"[{style}]{line}[/{style}]")


def print_platform(items: int) -> None:
    print(f"[white]platform: [reset]{platform.platform()}[/white]")
    print(f"[white]version: [reset]{platform.version()}[/white]")
    print(f"[white]release: [reset]{platform.release()}[/white]")
    print(f"[white]system: [reset]{platform.system()}[/white]")
    print(f"[white]python: [reset]{platform.python_version()}[/white]")
    print(f"[white bold]Collected {items} items[/white bold]\n")


def print_comment(comment: str) -> None:
    print(f"[dim]{comment}[/dim]")


def get_render_width(renderable) -> int:
    """Получить реальную ширину отображения Rich renderable"""
    measurement = measure_renderables(console, console.options, renderable)
    return measurement.maximum


def print_test_result(test_result: TestResult) -> None:
    date: str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    term_width = shutil.get_terminal_size().columns

    # Статус тег с Rich разметкой
    status_tag = {
        "success": "[black bold on green]PASS[/black bold on green]",
        "error": "[black bold on red]ERR [/black bold on red]",
        "warning": "[black bold on yellow]WARN[/black bold on yellow]",
        "skip": "[black bold on blue]SKIP[/black bold on blue]",
    }.get(test_result.status, "[black bold on white]????[/black bold on white]")

    # Процент с Rich разметкой
    percent_color = "green" if test_result.status == "success" else test_result.status
    percent_str = f"[dim][{percent_color}][{str(test_result.percent).rjust(3)}%][/{percent_color}][/dim]"

    # Измеряем ширину процента
    percent_renderable = console.render_str(percent_str)
    percent_width = get_render_width(percent_renderable)

    # Формируем лейбл
    if test_result.comment:
        label = f"[dim]{test_result.label}[/dim] [white]{test_result.comment}[/white]"
    else:
        label = test_result.label

    # Постсообщение
    postmessage = test_result.postmessage or ""
    if postmessage:
        postmessage = f" {postmessage}"

    # Определяем цвет лейбла
    label_color = {
        "success": "green",
        "error": "red",
        "warning": "yellow",
        "skip": "blue",
    }.get(test_result.status, "white")

    # Собираем базовую строку
    base = f"{status_tag} {date} [{label_color}]{label}[/{label_color}]{postmessage}"

    # Измеряем базовую строку
    base_renderable = console.render_str(base)
    base_width = get_render_width(base_renderable)

    # Вычисляем количество пробелов до правого края
    # Нужно учесть, что пробелы тоже имеют ширину
    space_width = get_render_width(console.render_str(" "))
    needed_spaces = (term_width - base_width - percent_width) // space_width

    if needed_spaces < 1:
        # Если не влезает, обрезаем лейбл
        if test_result.comment:
            # Обрезаем название функции
            max_label_width = (
                term_width
                - get_render_width(
                    console.render_str(f"{status_tag} {date} []{postmessage}")
                )
                - percent_width
                - 10
            )
            max_func_len = max(10, max_label_width // 2)
            truncated_func = test_result.label[:max_func_len] + "..."
            label = f"[dim]{truncated_func}[/dim] [white]{test_result.comment}[/white]"
        else:
            # Обрезаем весь лейбл
            max_label_width = (
                term_width
                - get_render_width(
                    console.render_str(f"{status_tag} {date} []{postmessage}")
                )
                - percent_width
                - 5
            )
            truncated = test_result.label[:max_label_width] + "..."
            label = f"[dim]{truncated}[/dim]"

        # Пересобираем и перемеряем
        base = (
            f"{status_tag} {date} [{label_color}]{label}[/{label_color}]{postmessage}"
        )
        base_renderable = console.render_str(base)
        base_width = get_render_width(base_renderable)
        needed_spaces = (term_width - base_width - percent_width) // space_width

    # Создаём строку с правильным количеством пробелов
    spaces = " " * (max(1, needed_spaces) - 4)
    final_line = f"{base}{spaces}{percent_str}"

    # Печатаем
    if test_result.status == "success":
        console.print(final_line)

    elif test_result.status == "error":
        console.print(f"\n{final_line}")
        console.print(
            f"[bold red]=================================== ERROR: {label} ====================================[/bold red]"
        )
        if test_result.output:
            console.print(Text(test_result.output, style="red"))

    elif test_result.status == "warning":
        console.print(final_line)
        if test_result.output:
            console.print(f"[yellow] > {test_result.output}[/yellow]\n")

    elif test_result.status == "skip":
        console.print(final_line)
