"""Project 2 CLI entry point. Usage: python project2.py {collect|analyze|build|all}

Subcommands are implemented phase by phase (see specs/00-overview.md).
"""
import sys

COMMANDS = ("collect", "analyze", "build", "all")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in COMMANDS:
        print(__doc__.strip())
        return 2
    print(f"'{argv[0]}' is not implemented yet.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
