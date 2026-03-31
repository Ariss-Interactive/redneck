import argparse
import logging as log
import sys

from rich.markup import escape
from importlib.metadata import version

from redneck import plugins, diag
from redneck.commands import build, check, groups, init


def main():
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("-v", "--verbose", action="store_true")
    pre_args, _ = pre_parser.parse_known_args()

    log.basicConfig(
        handlers=[diag.RedneckHandler()],
        level="DEBUG" if pre_args.verbose else "INFO",
        format="%(message)s",
        datefmt="[%X]"
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Enables debug output for the logger", action="store_true")

    plugins.load_plugins()

    subparser = parser.add_subparsers(dest="action")
    subparser.required = True

    build_command = subparser.add_parser("build", help="Builds the project. \"all\" builds w/ all builders. \"list\" lists all builders.")
    build_command.add_argument("-g", "--groups", help="The mod groups to include in the build.")
    build_command.add_argument("builder", help="The builder to use for building the modpack.")
    build_command.set_defaults(func=build.build)

    groups_command = subparser.add_parser("groups", help="Lists the groups defined in the mods.")
    groups_command.add_argument("-f", "--full", help="Lists groups, as well as mod ids and their source files.", action="store_true")
    groups_command.set_defaults(func=groups.groups)

    check_command = subparser.add_parser("check", help="Checks mod decls for validity.", )
    check_command.set_defaults(func=check.check)

    plugins_command = subparser.add_parser("plugins", help="Lists the plugins loaded during startup.")
    plugins_command.set_defaults(func=plugins.plugins)

    init_command = subparser.add_parser("init", help="Creates a bare-bones project.")
    init_command.set_defaults(func=init.init)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    log.info(f"[bold]Redneck [cyan]v{escape(version("redneck"))}[/]")

    args.func(args)

if __name__ == "__main__":
    main()
