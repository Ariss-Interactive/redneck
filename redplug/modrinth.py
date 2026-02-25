from redneck import builder, plugins, config, resolver

import requests
import glob
import json

from zipfile import ZipFile
from pathlib import Path
from pydantic import BaseModel
from requests_cache import CachedSession
from typing import Literal, override

class ModrinthPlugin(plugins.RedneckPlugin):
    def __init__(self):
        super().__init__()
        plugins.register_decl("modrinth", ModrinthModDecl, ModrinthResolver())
        plugins.register_builder("mrpack", ModrinthBuilder(), ModrinthBuilderConfig)

class ModrinthModDecl(config.ModDecl):
    load: Literal["modrinth"]
    project: str
    version: str
    file: int = 0

class ModrinthResolver(resolver.ModResolver[ModrinthModDecl]):
    session: requests.Session

    def __init__(self) -> None:
        super().__init__()

    @override
    def resolve(self, decl: ModrinthModDecl) -> resolver.ResolvedMod:
        try:
            self.session
        except AttributeError:
            self.session = CachedSession(".redneck/rinth_cache", backend="filesystem", cache_control=True)

        info = self.session.get(f"https://api.modrinth.com/v2/project/{decl.project}").json()
        ver = self.session.get(f"https://api.modrinth.com/v2/project/{decl.project}/version/{decl.version}").json()

        file = ver["files"][decl.file]

        return resolver.ResolvedMod(file["url"], {
            "name": info["title"],
            "sha512": file["hashes"]["sha512"],
            "sha1": file["hashes"]["sha1"],
            "filename": file["filename"],
            "size": file["size"],
        })

    def health_check(self, proj: config.RedneckProject, decl: ModrinthModDecl) -> list[str]:
        try:
            self.session
        except AttributeError:
            self.session = CachedSession(".redneck/rinth_cache", backend="filesystem", cache_control=True)
        warnings: list[str] = []

        # info = self.session.get(f"https://api.modrinth.com/v2/project/{decl.project}").json()
        ver = self.session.get(f"https://api.modrinth.com/v2/project/{decl.project}/version/{decl.version}").json()

        if not proj.meta.loader in ver["loaders"]:
            warnings.append(f"Unsupported loader. This mod version supports: {ver["loaders"]}")
        if proj.meta.minecraft not in ver["game_versions"]:
            warnings.append(f"Unsupported game version. This mod version supports: {ver["game_versions"]}")

        return warnings

class ModrinthBuilderConfig(BaseModel):
    include_files: list[str] = []

class ModrinthBuilder(builder.ModpackBuilder[ModrinthBuilderConfig]):
    @override
    def build(self, proj: builder.ResolvedProject, root: Path, options: ModrinthBuilderConfig) -> Path:
        build_path = root / ".redneck" / "build" / f"{proj.meta.pack.id}.mrpack"

        index = {
            "game": "minecraft",
            "name": proj.meta.pack.name,
            "versionId": proj.meta.pack.version,
            "formatVersion": 1,
            "dependencies": {
                "minecraft": proj.meta.minecraft,
            },
            "files": []
        }
        index["dependencies"][proj.meta.loader] = proj.meta.loader_version

        for mod in proj.mods:
            file_decl = {
                "path": f"mods/{mod.extra_info["filename"]}",
                "hashes": {
                    "sha1": mod.extra_info["sha1"],
                    "sha512": mod.extra_info["sha512"]
                },
                "downloads": [mod.url],
                "fileSize": mod.extra_info["size"]
            }

            index["files"].append(file_decl)

        includes: set[str] = set()

        for glop in options.include_files:
            includes.update(glob.glob(glop, root_dir=root, recursive=True, include_hidden=True))

        with ZipFile(build_path, "w") as zip:
            zip.writestr("modrinth.index.json", json.dumps(index, separators=(",", ":")))

            for i in includes:
                if (root / i).is_dir():
                    continue

                zip.write(i, f"overrides/{i}")

        return build_path