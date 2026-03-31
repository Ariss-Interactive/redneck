from redneck import config, resolver, diag

from argparse import Namespace
from pathlib import Path
import logging as log

def check(args: Namespace):
    proj = config.scan_project(Path("."))
    if proj is None:
        return

    warns = resolver.health_check(proj)

    for id, warn in warns.items():
        decl = proj.decls[id]

        diag.console.print(f"[bold yellow]warning[/]: [cyan]{decl.id}[/] @ [bold]{decl._from_file}:{decl._line}:{decl._col}[/]")
        for i in warn:
            diag.console.print(f"[bold cyan] =[/] {i}")
