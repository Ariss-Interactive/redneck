import logging as log

from redneck import diag
from functools import reduce
from pathlib import Path
from typing import Annotated, Any, ClassVar
from yaml import load, SafeLoader, YAMLError
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, TypeAdapter, ValidationError

class ModDeclLoader(SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(ModDeclLoader, self).construct_mapping(node, deep=deep)
        mapping["_line"] = node.start_mark.line + 1
        mapping["_col"] = node.start_mark.column + 1
        mapping["_end_line"] = node.end_mark.line + 1

        return mapping

class ModpackMeta(BaseModel):
    class PackInfo(BaseModel):
        id: str
        name: str
        version: str

    pack: PackInfo
    minecraft: str
    loader: str
    loader_version: str
    builders: dict[str, dict[str, Any]] = {}

class ModDecl(BaseModel):
    id: str
    group: str = "base"

    _line: int = PrivateAttr(default=-1)
    _col: int = PrivateAttr(default=-1)
    _end_line: int = PrivateAttr(default=-1)
    _from_file: str = PrivateAttr(default="unknown")
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

class RedneckProject:
    meta: ModpackMeta
    decls: dict[str, ModDecl]

    def __init__(self, meta: ModpackMeta, decls: dict[str, ModDecl]) -> None:
        self.meta = meta
        self.decls = decls

_decls: list[type[ModDecl]] = []

def scan_project(root: Path) -> RedneckProject | None:
    if not (root / "pack.yml").exists() or len(list((root / "mods/").glob("*.yml"))) == 0:
        log.error("Missing either pack.yml, the \"mods/\" dir, or the yml files in mods dir.")
        return None

    union_type = reduce(lambda a, b: a | b, _decls)
    mod_adapter = TypeAdapter(Annotated[union_type, Field(discriminator="load")]) # ty: ignore[invalid-type-form] - No better way. Sorry, ty.

    mods = {}

    try:
        failed = False

        try:
            with open(root / "pack.yml", "r") as stream:
                log.debug("Loading pack.yml")

                meta = load(stream, Loader=SafeLoader)

                # Bodge to load the loader & loader name from yaml.
                # I couldn't find a better way to do this, sorry.

                versions = meta.pop("versions", {})
                loaders = ["fabric-loader", "forge", "quilt-loader", "neoforge"]
                minecraft = versions.get("minecraft")

                loader = next((i for i in versions if i in loaders), None)

                if not minecraft:
                    raise Exception("Missing \"minecraft\" in the \"versions\" block.", )
                    if not loader:
                        raise Exception(f"Missing a loader in the \"versions\" block. Declare one of: {", ".join(loaders)}.")

                meta["minecraft"] = minecraft
                meta["loader"] = loader
                meta["loader_version"] = versions[loader]
        except YAMLError as e:
            diag.error("Failed to parse pack.yml", e)
            failed = True

        for file in list((root / "mods").glob("*.yml")):
            with open(file, "r") as stream:
                log.debug(f"Loading {file}")
                try:
                    loaded = load(stream, Loader=ModDeclLoader)
                except YAMLError as e:
                    diag.error(f"Failed to parse {file}", e)
                    failed = True
                    continue

                if loaded is None:
                    diag.console.print(f"[bold yellow]warning[/]: [bold]{file}[/] is empty")
                    continue

                for decl in loaded:
                    id = decl["id"]

                    line = decl.pop("_line", None)
                    col = decl.pop("_col", None)
                    end_line = decl.pop("_end_line", None)

                    try:
                        mod = mod_adapter.validate_python(decl)
                    except ValidationError as err:
                        diag.validation_error(file, line, col, end_line, err)
                        failed = True
                        continue

                    mod._from_file = file
                    mod._line = line
                    mod._col = col
                    mod._end_line = end_line

                    if id in mods:
                        diag.console.print(f"[bold yellow]warning[/]: duplicate mod [cyan]{id}[/] @ [bold]{file}:{mod._line}:{mod._col}[/]")
                        diag.console.print(f"[bold cyan] =[/] first seen at {mods[id]._from_file}:{mods[id]._line}:{mods[id]._col}")

                    mods[id] = mod

        return RedneckProject(ModpackMeta(**meta), mods) if not failed else None
    except Exception:
        diag.error("project scan failure")
