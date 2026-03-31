from pydantic import ValidationError
from pathlib import Path
import logging

from rich.syntax import Syntax
from rich.console import Console

console = Console()

class RedneckHandler(logging.Handler):
    def emit(self, record):
        match record.levelno:
            case logging.DEBUG:
                console.print(f"[dim]{record.getMessage()}[/]")
            case logging.INFO:
                console.print(f"{record.getMessage()}")
            case logging.WARNING:
                console.print(f"[yellow]{record.getMessage()}[/]")
            case logging.ERROR:
                console.print(f"[red]{record.getMessage()}[/]")

def validation_error(file: Path, line: int, col: int, end_line: int, error: ValidationError):
    source = Path(file).read_text().splitlines()

    console.print(f"[bold cyan]-->[/] {file}:{line}:{col}")

    console.print(Syntax(
        "\n".join(source[line - 1:end_line]),
        "yaml",
        line_numbers=True,
        start_line=line,
        theme="ansi_dark"
    ))

    for e in error.errors():
        loc = "".join(str(l) for l in e["loc"] if l != "modrinth")
        console.print(f"  [bold red]=[/] [bold]error[/]\\[{loc}]: {e["msg"]}")

def error(text: str, error: Exception | None = None):
    console.print(f"[bold red]error[/]: {text}")

    if error is None:
        return

    lines = str(error).splitlines()
    if len(lines) == 1:
        console.print(f" [bold cyan]=[/] {lines[0]}")
        return

    for line in lines:
        if line.strip():
            console.print(f" [bold cyan]|[/] {line}")
