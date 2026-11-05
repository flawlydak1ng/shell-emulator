"""Entry point: ``python -m shell_emulator``."""

import tkinter as tk

from shell_emulator.config import parse_args
from shell_emulator.gui import EmulatorWindow
from shell_emulator.shell import Shell
from shell_emulator.startup import prepare


def echo(text):
    """Print a line to the console even if it cannot encode the text."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def main(argv=None):
    """Parse parameters, load the VFS, show the window, run the loop."""
    config = parse_args(argv)
    vfs, messages = prepare(config)
    for text, _tag in messages:
        echo(text)
    root = tk.Tk()
    window = EmulatorWindow(root, Shell(vfs))
    root.after(0, window.start, config, messages)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
