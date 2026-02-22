from redneck import config, resolver, builder

from argparse import Namespace
from pathlib import Path
import logging as log

def groups(args: Namespace):
    proj = config.scan_project(Path("."))
    if proj == None:
        return

    log.info(f"Enumerated {len(proj.decls)} mods")

    groups: dict[str, list[config.ModDecl]] = {}

    for id, decl in proj.decls.items():
        if decl.group not in groups:
            groups[decl.group] = []

        groups[decl.group].append(decl)

    log.info(f"Found {len(groups)} groups:")

    if args.full:
        for group, mods in groups.items():
            log.info(f"- {group}:")
            for mod in mods:
                log.info(f"  * {mod.id} ({mod._from_file}:{mod._line}:{mod._col})")
    else:
        for group, mods in groups.items():
            log.info(f"- {group}")