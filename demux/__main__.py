"""
demux.__main__
The main entry point for the command line interface.
Invoke as ``demux`` (if installed)
or ``python -m demux`` (no install required).
"""
import sys

from demux.cli.base import demux


def main():
    sys.exit(demux())


if __name__ == "__main__":
    main()
