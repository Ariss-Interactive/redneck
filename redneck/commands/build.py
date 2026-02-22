from argparse import Namespace
from redneck import config, resolver, builder

import logging as log
from pathlib import Path

def build(args: Namespace):
    groups_split = []
    if args.groups != None:
        groups_split = str(args.groups).split(",")
        log.debug(f"Also using group(s) {groups_split}")

    proj = config.scan_project(Path("."))
    if proj == None:
        return    

    used_mods: list[config.ModDecl] = []

    for id, decl in proj.decls.items():
        if decl.group == "base" or decl.group in groups_split:
            used_mods.append(decl)

    log.info(f"Enumerated {len(proj.decls)} mods, resolving {len(used_mods)} mods")

    mods = resolver.resolve_mods(used_mods)
    final_build = builder.build_project(args.builder, builder.ResolvedProject(proj.meta, mods))

    if final_build == None:
        log.error("Build failed")
        return

    log.info(f"Built {final_build}")