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

# Install

You can install redneck from the PyPI by typing `pip install redneck` (that simple, yes!)

# Usage

You can start with running `redneck init`, and changing the base configuration found in `pack.yml` & the file found in `mods/`. Additional parameters should -- hopefully -- be explained in the docs.