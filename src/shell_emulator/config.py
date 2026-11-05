"""Command line parameters of the emulator."""

import argparse
import os
from dataclasses import dataclass
from typing import List, Optional

from shell_emulator.shell import DEFAULT_VFS_NAME

PROGRAM_NAME = "shell_emulator"
NOT_SET = "<not set>"
DEBUG_PREFIX = "[debug]"


@dataclass
class Config:
    """User parameters given to the emulator on the command line."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None

    def vfs_name(self):
        """Return the VFS name: the last component of the VFS path."""
        if self.vfs_path is None:
            return DEFAULT_VFS_NAME
        absolute = os.path.abspath(self.vfs_path)
        return os.path.basename(absolute) or absolute


def build_parser():
    """Create the parser of command line arguments."""
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description="Emulator of a UNIX-like shell with a virtual file "
        "system.",
    )
    parser.add_argument(
        "--vfs-path",
        metavar="PATH",
        help="path to the physical location of the VFS (a directory)",
    )
    parser.add_argument(
        "--script",
        dest="script_path",
        metavar="PATH",
        help="path to the startup script with emulator commands",
    )
    return parser


def parse_args(argv: Optional[List[str]] = None):
    """Parse command line arguments into a Config.

    ``argv`` defaults to ``sys.argv[1:]``. Invalid arguments make
    argparse print a message and raise SystemExit.
    """
    namespace = build_parser().parse_args(argv)
    return Config(
        vfs_path=namespace.vfs_path, script_path=namespace.script_path
    )


def _describe(value):
    """Return a printable form of an optional parameter value."""
    return NOT_SET if value is None else value


def debug_lines(config):
    """Return the debug output listing every parameter of the emulator."""
    return [
        "{} emulator started with parameters:".format(DEBUG_PREFIX),
        "{}   --vfs-path = {}".format(
            DEBUG_PREFIX, _describe(config.vfs_path)
        ),
        "{}   --script   = {}".format(
            DEBUG_PREFIX, _describe(config.script_path)
        ),
        "{}   VFS name   = {}".format(DEBUG_PREFIX, config.vfs_name()),
    ]
