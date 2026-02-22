import argparse
import logging as log
import inspect
from typing import Any

from pydantic import BaseModel
from redneck import config, resolver, builder
from pkgutil import iter_modules
from importlib import import_module

class RedneckPlugin():
    def __init__(self):
        pass

    def add_subparser(self, parser: argparse.ArgumentParser):
        pass

_instances: list[RedneckPlugin] = []

def plugins():
    log.info(f"{len(_instances)} plugins:")
    for i in _instances:
        log.info(f"- {type(i)}")

def load_plugins():
    """
    Shamelessly stolen from beets, my favorite music database manager.
    """
    if _instances: 
        return

    import redplug
    discovered_plugins: dict[str, RedneckPlugin] = {}

    for module in iter_modules(redplug.__path__, redplug.__name__ + "."):
        try:
            namespace = import_module(module.name)
            for obj in reversed(namespace.__dict__.values()):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, RedneckPlugin)
                    and obj != RedneckPlugin
                    and not inspect.isabstract(obj)
                    # Only consider this plugin's module or submodules to avoid
                    # conflicts when plugins import other plugin classes
                    and (
                        obj.__module__ == namespace.__name__
                        or obj.__module__.startswith(f"{namespace.__name__}.")
                    )
                ):
                    plugin = obj()
                    discovered_plugins[module.name] = plugin
                    _instances.append(plugin)

                    break
        except Exception as e:
            log.error(f"Failed to load plugin {module.name}: {e}");
    log.debug(f"Loaded {len(discovered_plugins)} plugins: {list(discovered_plugins.keys())}")

def register_decl(id: str, decl: type[resolver.T], resl: resolver.ModResolver[resolver.T]):
    config._decls.append(decl) 
    # I am sorry, lord. This simply is the easiest way.
    resolver._resolvers[id] = resl

def register_builder(id: str, bldr: builder.ModpackBuilder[builder.T], conf: type[BaseModel] | None = None):
    builder._builders[id] = bldr
    if conf != None:
        builder._configs[id] = conf