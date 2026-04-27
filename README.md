<p align="center">
  <img src="https://raw.githubusercontent.com/Ariss-Interactive/redneck/refs/heads/master/docs/assets/logo.png" alt="Redneck">
</p>

<hr>

Redneck is a small modpack build tool for people who want to write their pack definition by hand.

You describe the pack in YAML, split mods into groups, and compile the result into a release artifact such as a Modrinth `.mrpack`.

Redneck is currently focused on one thing: **turning a curated YAML recipe into a buildable modpack artifact.**

It is aimed at the authoring side: keeping the pack definition readable, reviewable, and easy to split into variants.

## Why use this?

Use redneck when you want:

- one source tree that can build different pack editions
- simple hand-written mod declarations
- groups such as `base`, `qol`, `performance`, `server`, or `visuals`
- a generated `.mrpack` instead of a hand-assembled archive
- a quick check that declared mods still match your pack loader and Minecraft version

Do **not** use redneck if you want a mature pack deployment workflow, installer support, hosting, automatic updates, or full packwiz feature parity. Redneck is much smaller than that.

## Installation

```sh
pip install redneck
````

Redneck requires Python 3.12 or newer.

## Project layout

A typical redneck project looks like this:

```text
my-pack/
├─ pack.yml
├─ mods/
│  ├─ base.yml
│  ├─ performance.yml
│  └─ qol.yml
└─ config/
   └─ example.toml
```

`pack.yml` describes the pack itself.

Files in `mods/` describe the mods that can be included in the pack.

Folder like `config/` are usually written in the builder config. They are included into the pack, like overrides.

## Quick start

Create a new project:

```sh
redneck init
```

This creates a basic `pack.yml` and project structure.

Then add a mod declaration under `mods/`:

```yaml
- load: modrinth
  id: ferrite-core
  project: ferrite-core
  version: 7.0.3-neoforge
```

Build a Modrinth pack:

```sh
redneck build mrpack
```

The output will be written to the build directory.

## `pack.yml`

Example:

```yaml
pack:
  id: "nedoserver"
  name: "Nedoserver"
  version: "2.0.0"

versions:
  minecraft: "1.21.1"
  neoforge: "21.1.225"

builders:
  mrpack:
    include_files:
      - "./config/**"
```

## Mod declarations

A basic Modrinth declaration looks like this:

```yaml
- load: modrinth   # resolver to use  
  id: ferrite-core # local identifier inside this pack
  project: ferrite-core
  version: 7.0.3-neoforge
```

`id` is the name redneck uses internally. It should be stable and unique inside your pack.

`project` and `version` identify the Modrinth project/version to resolve.

## Groups

Every mod belongs to a group.

If no group is specified, the mod belongs to `base`.

The `base` group is always included.

```yaml
- load: modrinth
  id: create
  project: create
  version: mc1.21.1-6.0.9
  # group: base <- hey, it's default as-is! 

- load: modrinth
  id: jade
  project: jade
  version: 15.10.5+neoforge
  group: qol

- load: modrinth
  id: ferrite-core
  project: ferrite-core
  version: 7.0.3-neoforge
  group: performance
```

Build only the base pack:

```sh
redneck build mrpack
```

Build the base pack plus QoL & performance:

```sh
redneck build mrpack -g qol,performance
```

This lets one source tree produce multiple related packs.

For example:

```sh
# Minimal pack
redneck build mrpack

# Normal client pack
redneck build mrpack -g qol,performance

# Heavier client pack
redneck build mrpack -g qol,performance,visuals

# Server-oriented pack
redneck build mrpack -g server,performance
```

### Example: splitting a pack by intent

Instead of keeping every mod in one large file, you can split declarations by purpose.

`mods/base.yml`:

```yaml
- load: modrinth
  id: create
  project: create
  version: mc1.21.1-6.0.9
```

`mods/performance.yml`:

```yaml
- load: modrinth
  id: ferrite-core
  project: ferrite-core
  version: 7.0.3-neoforge
  group: performance
```

`mods/qol.yml`:

```yaml
- load: modrinth
  id: jade
  project: jade
  version: 15.10.5+neoforge
  group: qol
```

Then build different editions from the same source:

```sh
redneck build mrpack
redneck build mrpack -g performance
redneck build mrpack -g performance,qol
```

## Checking the pack

Run:

```sh
redneck check
```

This checks the pack definition and asks available plugins to validate what they can.

For Modrinth declarations, redneck can warn when a selected version does not appear to match the configured Minecraft version or loader.

Example output may look like:

```text
warning: stupid-platform-dependent-ium may not support loader neoforge
warning: some-mod may not support Minecraft 1.21.1
```

`check` is not a replacement for launching the pack. It is a fast sanity check before building or publishing.

## Plugins

Redneck has an internal plugin system, inspired by [beets](https://pypi.org/project/beets/).

Built-in plugins live in the `redplug` package. They are loaded at startup and register resolvers, builders, and checks with redneck.

Today, the best way to write a plugin is to reference one of the bundled plugins:

- `redplug/modrinth.py` resolves Modrinth declarations and builds `.mrpack` files
- `redplug/modlist.py` generates a simple mod list

A tiny build-target plugin looks like this:

```python
from pathlib import Path
from typing import override
from redneck import plugins, builder

class ModCountPlugin(plugins.RedneckPlugin):
    def __init__(self):
        super().__init__()
        plugins.register_builder("modcount", ModCountBuilder())

class ModCountBuilder(builder.ModpackBuilder):
    @override
    def build(self, proj: builder.ResolvedProject, root: Path, options: None) -> Path:
        out = root / ".redneck" / "build" / "modcount.txt"
        out.write_text(f"{proj.meta.pack.name} includes {len(proj.mods)} mods.\n")
        return out
```

Place the plugin into your packages, into the `redplug` namespace, the target can be built with:

```sh
redneck build modcount
```

## Build targets

Build a Modrinth `.mrpack`:

```sh
redneck build mrpack
```

Build with groups:

```sh
redneck build mrpack -g qol,performance
```

Other build targets may be provided by plugins.

## Current limitations

Redneck is intentionally narrow.

At the moment, expect limitations such as:

* limited dependency handling
* no update workflow
* no installer or hosting story

If you need a complete Minecraft modpack management and deployment workflow today, packwiz is probably the better tool.

If you want a small YAML-first build step for curated pack recipes, redneck may be useful.

## Philosophy

Redneck treats the hand-written YAML files as the source of truth. They require the least amount of information from a user, unless one explicitly specifies or overrides it.

Generated files are build artifacts.

The goal is not to make a prettier copy of another tool’s metadata format, but to make the authoring layer pleasant for curated packs: grouped mods, readable declarations, simple variants, and generated outputs.

## License

GPL-3.0.
