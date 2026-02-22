from redneck import config, resolver, builder

from argparse import Namespace
from pathlib import Path
import logging as log

def check(args: Namespace):
    proj = config.scan_project(Path("."))
    if proj == None:
        return

    warns = resolver.health_check(proj)
    log.warning(f"{len(warns)} mods have warnings.")

    for id, warn in warns.items():
        decl = proj.decls[id]

        log.warning(f"{id} ({decl._from_file}:{decl._line}:{decl._col}):")
        for i in warn:
            log.warning(f" * {i}")