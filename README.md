<p align="center">
  <img src="https://raw.githubusercontent.com/Ariss-Interactive/redneck/refs/heads/master/docs/assets/logo.png" alt="Redneck">
</p>

<hr>

Redneck is a small, plugin-driven, declarative modpack builder.

Here's an example of how you can declare a mod with a few lines of YAML code:
```yaml
- load: modrinth
  id: fabric-api
  project: "fabric-api"
  version: "0.92.7+1.20.1"
```

## Install

Install from PyPI by typing `pip install redneck` (that simple, yes!)

## Quickstart

Run `redneck init`, and edit `pack.yml` to your needs:
```yaml
pack:
  id: "mypack"
  name: "My Pack"
  version: "0.1.0"
 
versions:
  minecraft: "1.21.1"
  neoforge: "21.1.219"
 
builders:
  mrpack:
    include_files:
      - "config/**"
```

Add mods in `mods/`:
 
```yaml
- load: modrinth
  id: ferrite-core
  project: "ferrite-core"
  version: "7.0.3-neoforge"
  # group: "optimizations"
```

And build with `redneck build mrpack`. Voilà, here's your modpack!

## Goodies

Redneck has a thing called groups. Suppose you have some QoL mods, you put them in the `qol` group, by specifying `group: "qol"` in the mod declaration. Then, when you want to build a modpack for your server, you run `redneck build mrpack -g qol`. Now, imagine that you have a tryhard friend, who prefers running the bare minimum. You can please them too, by running the plain build, leaving them with nothing but the essentials!

You can also check your modpack for warnings, say, if you've overlooked a mod's version. It'd look something like this:
```
$ redneck check
Redneck v0.3.0rc1
warning: fabric-api @ mods/main.yml:1:3
 = Unsupported loader. This mod version supports: ['fabric']
 = Unsupported game version. This mod version supports: ['1.20.1']
warning: sodium @ mods/second.yml:1:3
 = Unsupported loader. This mod version supports: ['fabric', 'quilt']
 = Unsupported game version. This mod version supports: ['1.20.1']
```
