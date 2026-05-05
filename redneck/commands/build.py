from argparse import Namespace
from redneck import config, resolver, diag, builder

from rich.tree import Tree
from rich.live import Live
from rich.progress import Progress

import logging as log
from pathlib import Path

def build(args: Namespace):
    if args.builder == "list":
        tree = Tree(f"{len(builder._builders)} builders")
        for bld in builder._builders:
            tree.add(bld)

        diag.console.print(tree)
        return

    used_groups: set[str] = set()

    if args.groups is not None:
        used_groups = {
            group.strip()
            for group in str(args.groups).split(",")
            if group.strip()
        }
        log.debug(f"Using extra group(s) {sorted(used_groups)}")

    proj = config.scan_project(Path("."))
    if proj is None:
        diag.error("build failed")
        return


    sel_profile = args.profile or proj.meta.default_profile
    current = sel_profile

    if current not in proj.meta.profiles:
        diag.error("unkown profile")
        return

    seen = set()
    while True:
        if current in seen:
            diag.error(f"cycle detected in profile chain at '{current}'")
            return
        seen.add(current)
        profile = proj.meta.profiles[current]
        used_groups |= profile.groups
        if current == "base":
            break
        current = profile.depends

    used_mods: list[config.ModDecl] = []

    for id, decl in proj.decls.items():
        if decl.group == "base" or decl.group in used_groups:
            used_mods.append(decl)

    log.info(f"Enumerated {len(proj.decls)} mods, resolving {len(used_mods)} mods")

    def build_w_builder(b):
        nonlocal failure
        final_build = builder.build_project(b, project)

        if final_build is None:
            failure = True
            return

        log.info(f"Built {final_build}")

    progress = Progress(console=diag.console)

    sel_builder = args.builder or proj.meta.profiles[sel_profile].builder

    with Live(progress, console=diag.console, vertical_overflow="visible", transient=True):
        build_task = progress.add_task("Building...", total=None)

        mods = resolver.resolve_mods(used_mods, progress)
        if mods is None:
            diag.error("build failed")
            return

        project = builder.ResolvedProject(proj.meta, mods)

        failure = False

        if sel_builder == "all":
            for b in list(builder._builders.keys()):
                build_w_builder(b)
        else:
            build_w_builder(sel_builder)

        progress.update(build_task, description="[green]Built![/]")

    if failure:
        diag.error("build failed")
