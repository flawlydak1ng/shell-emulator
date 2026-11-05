"""In-memory virtual file system (VFS) loaded from a disk directory."""

import os
import shutil
from dataclasses import dataclass, field
from typing import Dict, Union

DEFAULT_VFS_NAME = "default"
ROOT_NAME = "/"
TREE_BRANCH = "|-- "
TREE_LAST = "`-- "
TREE_PIPE = "|   "
TREE_SPACE = "    "
SUMMARY_PREFIX = "[vfs]"


class VfsError(Exception):
    """Raised when the VFS cannot be loaded or its directory cleared."""


@dataclass
class VfsFile:
    """A file of the VFS; its content is kept in memory as bytes."""

    name: str
    data: bytes = b""

    @property
    def size(self):
        """Return the size of the file in bytes."""
        return len(self.data)


@dataclass
class VfsDir:
    """A directory of the VFS holding files and nested directories."""

    name: str
    children: Dict[str, Union["VfsDir", VfsFile]] = field(
        default_factory=dict
    )

    def sorted_children(self):
        """Return children: directories first, then files, by name."""
        return sorted(
            self.children.values(),
            key=lambda node: (isinstance(node, VfsFile), node.name),
        )


@dataclass
class VfsStats:
    """Number of directories, files and bytes stored in a VFS."""

    dirs: int = 0
    files: int = 0
    size: int = 0


def name_from_path(path):
    """Return the VFS name: the name of its directory on the disk."""
    absolute = os.path.abspath(path)
    return os.path.basename(absolute) or absolute


def _read_directory(path, skipped):
    """Read a directory recursively into a dict of VFS nodes.

    Entries that are neither regular files nor directories (symbolic
    links, sockets, ...) are not loaded; their paths go to ``skipped``.
    """
    children = {}
    with os.scandir(path) as entries:
        for entry in sorted(entries, key=lambda item: item.name):
            if entry.is_symlink():
                skipped.append(entry.path)
            elif entry.is_dir():
                nested = _read_directory(entry.path, skipped)
                children[entry.name] = VfsDir(entry.name, nested)
            elif entry.is_file():
                with open(entry.path, "rb") as source:
                    children[entry.name] = VfsFile(entry.name, source.read())
            else:
                skipped.append(entry.path)
    return children


def _collect(directory, stats):
    """Add the contents of a directory to the statistics, recursively."""
    for node in directory.children.values():
        if isinstance(node, VfsDir):
            stats.dirs += 1
            _collect(node, stats)
        else:
            stats.files += 1
            stats.size += node.size


def _tree(directory, prefix, lines):
    """Append the tree drawing of a directory to ``lines``."""
    nodes = directory.sorted_children()
    for index, node in enumerate(nodes):
        last = index == len(nodes) - 1
        branch = TREE_LAST if last else TREE_BRANCH
        if isinstance(node, VfsDir):
            lines.append("{}{}{}/".format(prefix, branch, node.name))
            _tree(node, prefix + (TREE_SPACE if last else TREE_PIPE), lines)
        else:
            lines.append(
                "{}{}{} ({} bytes)".format(prefix, branch, node.name, node.size)
            )


class Vfs:
    """A virtual file system that lives in memory.

    ``source_path`` is the absolute path of the physical directory the
    VFS was loaded from (``None`` for a VFS without a directory).
    """

    def __init__(self, root=None, source_path=None, skipped=0):
        """Create a VFS from a root directory node."""
        self.root = root if root is not None else VfsDir(ROOT_NAME)
        self.source_path = source_path
        self.skipped = skipped

    @property
    def name(self):
        """Return the VFS name shown in the window title and prompt."""
        if self.source_path is None:
            return DEFAULT_VFS_NAME
        return name_from_path(self.source_path)

    @classmethod
    def default(cls, source_path=None):
        """Return the default VFS: an empty root directory."""
        return cls(source_path=source_path)

    @classmethod
    def from_directory(cls, path):
        """Load the VFS from a directory on the disk into memory.

        Nothing on the disk is changed. Raises VfsError if the path does
        not exist, is not a directory or cannot be read.
        """
        absolute = os.path.abspath(path)
        if not os.path.exists(absolute):
            raise VfsError("directory not found: {}".format(path))
        if not os.path.isdir(absolute):
            raise VfsError("not a directory: {}".format(path))
        skipped = []
        try:
            children = _read_directory(absolute, skipped)
        except (OSError, RecursionError) as exc:
            raise VfsError("cannot read {}: {}".format(path, exc)) from exc
        return cls(VfsDir(ROOT_NAME, children), absolute, len(skipped))

    def stats(self):
        """Count directories (without the root), files and bytes."""
        stats = VfsStats()
        _collect(self.root, stats)
        return stats

    def tree_lines(self):
        """Return the tree drawing of the whole VFS, one string per line."""
        lines = [ROOT_NAME]
        _tree(self.root, "", lines)
        return lines

    def summary_lines(self):
        """Return a description of the VFS followed by its tree."""
        stats = self.stats()
        source = self.source_path or "<none>"
        lines = [
            "{} VFS '{}', physical location: {}".format(
                SUMMARY_PREFIX, self.name, source
            ),
            "{} {} directories, {} files, {} bytes (kept in memory)".format(
                SUMMARY_PREFIX, stats.dirs, stats.files, stats.size
            ),
        ]
        if self.skipped:
            lines.append(
                "{} {} special entries were not loaded".format(
                    SUMMARY_PREFIX, self.skipped
                )
            )
        return lines + self.tree_lines()


def is_protected_path(path):
    """Tell whether a directory must never be cleared by the emulator.

    Protected are the root of a file system and the home directory.
    """
    real = os.path.realpath(path)
    home = os.path.realpath(os.path.expanduser("~"))
    return os.path.dirname(real) == real or real == home


def clear_directory(path):
    """Delete everything inside a directory but keep the directory itself.

    Raises VfsError if the path is not a directory, is protected or
    something cannot be deleted.
    """
    if not os.path.isdir(path):
        raise VfsError("directory not found: {}".format(path))
    if is_protected_path(path):
        raise VfsError("refusing to clear a protected path: {}".format(path))
    try:
        for name in os.listdir(path):
            _remove(os.path.join(path, name))
    except OSError as exc:
        raise VfsError("cannot clear {}: {}".format(path, exc)) from exc


def _remove(path):
    """Delete a file, a link or a directory tree."""
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
