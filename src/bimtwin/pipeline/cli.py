"""Command line entry point (`bimtwin`)."""

import argparse

from bimtwin import __version__


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="bimtwin", description="4D BIM digital twin and progress monitor"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path")
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
