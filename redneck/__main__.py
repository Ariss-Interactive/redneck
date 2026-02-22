import sys
import coloredlogs
import logging as log
import argparse
from importlib.metadata import version
from pathlib import Path
from redneck.commands import build, groups, check
from redneck import plugins, config, resolver, builder

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Enables debug output for the logger", action="store_true")

    plugins.load_plugins()

    subparser = parser.add_subparsers(dest="action")
    subparser.required = True

    build_command = subparser.add_parser("build", help="Builds the project.")
    build_command.add_argument("-g", "--groups", help="The mod groups to include in the build.")
    build_command.add_argument("builder", help="The builder to use for building the modpack.")

    groups_command = subparser.add_parser("groups", help="Lists the groups defined in the mods.")
    groups_command.add_argument("-f", "--full", help="Lists groups, as well as mod ids and their source files.", action="store_true")

    check_command = subparser.add_parser("check", help="Checks mod decls for validity.")

    plugins_command = subparser.add_parser("plugins", help="Lists the plugins loaded during startup.")

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Change the color because I can't view black on black 
    coloredlogs.DEFAULT_FIELD_STYLES["levelname"]["color"] = "magenta"
    coloredlogs.install(fmt="[%(levelname)-7s] %(message)s", level="DEBUG" if args.verbose else "INFO")
    log.info(f"Redneck v{version("redneck")}")
    
    match args.action:
        case "build":
            build.build(args)
        case "groups":
            groups.groups(args)
        case "check":
            check.check(args)
        case "plugins":
            plugins.plugins()

if __name__ == "__main__":
    main()