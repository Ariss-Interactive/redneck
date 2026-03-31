import logging as log

from argparse import Namespace
from pathlib import Path


def init(args: Namespace):
    root = Path(".")
    mods = (root / "mods/")

    if not mods.exists():
        mods.mkdir()

    with open(root / "pack.yml", "w") as f:
        f.write("""pack:
  id: "cool-pack"
  name: "Cool pack"
  version: "1.0.0"

versions:
  minecraft: "1.20.1"
  fabric-loader: "0.18.4\"""")

    with open(mods / "hello.yml", "w") as f:
        f.write("""- load: modrinth
  id: fabric-api
  project: "fabric-api"
  version: "0.92.7+1.20.1\"""")

    log.info(f"Initialized empty redneck project in {root.absolute()}")
    log.info("hint: try building the project with \"redneck build mrpack\"")
