from pathlib import Path
from typing import override
from redneck import plugins, builder

class ModlistPlugin(plugins.RedneckPlugin):
    def __init__(self):
        super().__init__()
        plugins.register_builder("modlist", ModlistBuilder())

class ModlistBuilder(builder.ModpackBuilder):
    @override
    def build(self, proj: builder.ResolvedProject, root: Path, options: None) -> Path:
        out = root / ".redneck" / "build" / "modlist.html"

        with open(out, "w") as file:
            file.write("<ul>\n")
            for mod in proj.mods:
                file.write(f"<li><a href=\"{mod.url}\">{mod.extra_info["name"] if "name" in mod.extra_info else mod.url}</a></li>\n")
            file.write("</ul>")

        return out