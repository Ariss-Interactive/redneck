from argparse import Namespace
from redneck import config, resolver, builder, diag

import logging as log
from pathlib import Path

def build(args: Namespace):
    if args.builder == "list":
        return

    groups_split: set[str] = set()
    if args.groups != None:
        groups_split = {
            group.strip()
            for group in str(args.groups).split(",")
            if group.strip()
        }
        log.debug(f"Also using group(s) {sorted(groups_split)}")

    proj = config.scan_project(Path("."))
    if proj is None:
        diag.error("build failed")
        return

    used_mods: list[config.ModDecl] = []

    for id, decl in proj.decls.items():
        if decl.group == "base" or decl.group in groups_split:
            used_mods.append(decl)

    log.info(f"Enumerated {len(proj.decls)} mods, resolving {len(used_mods)} mods")

    mods = resolver.resolve_mods(used_mods)
    if mods is None:
        diag.error("build failed")
        return

    project = builder.ResolvedProject(proj.meta, mods)

    failure = False

    def build_w_builder(b):
        nonlocal failure
        final_build = builder.build_project(b, project)

        if final_build is None:
            failure = True
            return

        log.info(f"Built {final_build}")

    if args.builder == "all":
        for b in list(builder._builders.keys()):
            build_w_builder(b)
    else:
        build_w_builder(args.builder)

    if failure:
        diag.error("build failed")
