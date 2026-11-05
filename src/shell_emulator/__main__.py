"""Entry point: ``python -m shell_emulator``."""

import tkinter as tk

from shell_emulator.gui import EmulatorWindow
from shell_emulator.shell import Shell


def main():
    """Start the emulator window and run its event loop."""
    root = tk.Tk()
    EmulatorWindow(root, Shell())
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
