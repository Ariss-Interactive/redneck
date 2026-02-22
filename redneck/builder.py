from redneck import config, resolver

import logging as log
from traceback import format_exc
from typing import Generic, TypeVar
from pydantic import BaseModel
from pathlib import Path

T = TypeVar("T", bound=BaseModel)

class ResolvedProject():
    meta: config.ModpackMeta
    mods: list[resolver.ResolvedMod]

    def __init__(self, meta: config.ModpackMeta, mods: list[resolver.ResolvedMod]) -> None:
        self.meta = meta
        self.mods = mods

class ModpackBuilder(Generic[T]):
    def build(self, proj: ResolvedProject, root: Path, options: T | None) -> Path:
        raise NotImplementedError

_builders: dict[str, ModpackBuilder] = {}
_configs: dict[str, type[BaseModel]] = {}

def build_project(id: str, proj: ResolvedProject) -> Path | None:
    root = Path(".")
    builds = root / ".redneck" / "build"
    if not builds.exists():
        builds.mkdir(parents=True)

    config = None

    if id in _configs.keys():
        raw = proj.meta.builders.get(id, {})
        try:
            config = _configs[id].model_validate(raw)
        except Exception as e:
            log.error(f"In pack.yml:\n{e}")
            return None

    try:
        return _builders[id].build(proj, root, config)
    except Exception as e:
        log.exception(e)