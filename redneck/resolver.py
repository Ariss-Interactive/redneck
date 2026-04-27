import logging as log

from rich.progress import Progress
from rich.live import Live
from typing import Generic, TypeVar

from redneck import diag
from redneck.config import ModDecl, RedneckProject

T = TypeVar("T", bound=ModDecl)

class ResolvedMod:
    url: str
    extra_info: dict[str, str]

    def __init__(self, url: str, extra_info: dict[str, str]) -> None:
        self.url = url
        self.extra_info = extra_info

class ModResolver(Generic[T]):
    def resolve(self, decl: T) -> ResolvedMod:
        raise NotImplementedError
    def health_check(self, proj: RedneckProject, decl: T) -> list[str]:
        raise NotImplementedError

def resolve_mods(proj: list[ModDecl], prog: Progress) -> list[ResolvedMod] | None:
    mods = []
    failed = False

    task = prog.add_task("Resolving...", total=len(proj))
    for decl in proj:
        try:
            mod = _resolvers[decl.load].resolve(decl)
            mod.extra_info["resolver"] = decl.load
            mods.append(mod)
        except Exception as e:
            diag.error(f"Failed to resolve [cyan]{decl.id}[/]", e)

            failed = True
        prog.advance(task)

    return mods if not failed else None

def health_check(proj: RedneckProject) -> dict[str, list[str]]:
    warnings = {}

    for decl in list(proj.decls.values()):
        warns = _resolvers[decl.load].health_check(proj, decl)

        if len(warns) == 0:
            continue

        warnings[decl.id] = warns

    return warnings

_resolvers: dict[str, ModResolver[ModDecl]] = {}
