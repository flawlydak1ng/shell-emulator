"""Preparation of the emulator at start: debug output and VFS loading."""

from shell_emulator.config import debug_lines
from shell_emulator.session import TAG_DEBUG, TAG_ERROR
from shell_emulator.vfs import Vfs, VfsError


def prepare(config):
    """Load the VFS given in ``config`` and collect the startup messages.

    Returns a pair ``(vfs, messages)`` where ``messages`` is a list of
    ``(text, tag)`` items: the debug output of the parameters, then the
    description of the loaded VFS or the loading error. If the VFS cannot
    be loaded, the default VFS is used instead.
    """
    messages = [(line, TAG_DEBUG) for line in debug_lines(config)]
    vfs = Vfs.default()
    if config.vfs_path is None:
        return vfs, messages
    try:
        vfs = Vfs.from_directory(config.vfs_path)
    except VfsError as exc:
        messages.append(("vfs: {}".format(exc), TAG_ERROR))
        messages.append(("vfs: the default VFS is used instead", TAG_ERROR))
        return vfs, messages
    messages.extend((line, TAG_DEBUG) for line in vfs.summary_lines())
    return vfs, messages
