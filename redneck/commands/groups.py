from redneck import config, diag

from rich.tree import Tree

from argparse import Namespace
from pathlib import Path
import logging as log

def groups(args: Namespace):
    proj = config.scan_project(Path("."))
    if proj is None:
        return

    log.debug(f"Enumerated {len(proj.decls)} mods")

    groups: dict[str, list[config.ModDecl]] = {}

    for id, decl in proj.decls.items():
        if decl.group not in groups:
            groups[decl.group] = []

        groups[decl.group].append(decl)

    tree = Tree(f"{proj.meta.pack.id} ({len(groups)} groups)")

    if args.full:
        for group, mods in groups.items():
            count = len(mods)
            group_el = tree.add(f"{group} ({count} {"mod" if count == 1 else "mods"})")
            for mod in mods:
                group_el.add(f"{mod.id} ({mod._from_file}:{mod._line}:{mod._col})")
    else:
        for group, mods in groups.items():
            count = len(mods)
            tree.add(f"{group} ({count} {"mod" if count == 1 else "mods"})")

    diag.console.print(tree)
