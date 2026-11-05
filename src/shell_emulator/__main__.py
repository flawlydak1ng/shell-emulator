"""Entry point: ``python -m shell_emulator``."""

import tkinter as tk

from shell_emulator.config import debug_lines, parse_args
from shell_emulator.gui import EmulatorWindow
from shell_emulator.shell import Shell


def main(argv=None):
    """Parse parameters, start the emulator window and run its loop."""
    config = parse_args(argv)
    lines = debug_lines(config)
    for line in lines:
        print(line)
    root = tk.Tk()
    window = EmulatorWindow(root, Shell(config.vfs_name()))
    root.after(0, window.start, config, lines)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
