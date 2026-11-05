"""Graphical interface of the emulator built with tkinter."""

import tkinter as tk
from tkinter import font as tkfont

from shell_emulator.session import (
    TAG_DEBUG,
    TAG_ERROR,
    TAG_INPUT,
    TAG_OUTPUT,
    Session,
)

APP_TITLE = "Shell Emulator"
WINDOW_SIZE = "820x520"
BACKGROUND = "#1e1e1e"
TAG_COLORS = {
    TAG_INPUT: "#9cdcfe",
    TAG_OUTPUT: "#d4d4d4",
    TAG_ERROR: "#f48771",
    TAG_DEBUG: "#8a8a8a",
}
FONT_SIZE = 11
PADDING = 6


class EmulatorWindow:
    """Main window: scrolling terminal output and a command input line."""

    def __init__(self, root, shell):
        """Build the window widgets for the given shell."""
        self.root = root
        self.shell = shell
        self.session = Session(shell, self.write, self._after)
        self.history = []
        self.history_pos = 0
        self._build_widgets()
        self.refresh()

    def _build_widgets(self):
        """Create the output area, the prompt label and the input line."""
        self.root.geometry(WINDOW_SIZE)
        mono = tkfont.nametofont("TkFixedFont").copy()
        mono.configure(size=FONT_SIZE)
        self.output = tk.Text(
            self.root, state=tk.DISABLED, wrap=tk.WORD, font=mono,
            bg=BACKGROUND, fg=TAG_COLORS[TAG_OUTPUT], padx=PADDING,
            pady=PADDING, borderwidth=0, highlightthickness=0,
        )
        for tag, color in TAG_COLORS.items():
            self.output.tag_configure(tag, foreground=color)
        scroll = tk.Scrollbar(self.root, command=self.output.yview)
        self.output.configure(yscrollcommand=scroll.set)
        bottom = tk.Frame(self.root, bg=BACKGROUND)
        self.prompt = tk.Label(
            bottom, font=mono, bg=BACKGROUND, fg=TAG_COLORS[TAG_INPUT]
        )
        self.entry = tk.Entry(
            bottom, font=mono, bg=BACKGROUND, fg=TAG_COLORS[TAG_OUTPUT],
            insertbackground=TAG_COLORS[TAG_OUTPUT], borderwidth=0,
            highlightthickness=0,
        )
        self.prompt.pack(side=tk.LEFT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=PADDING, pady=PADDING)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Up>", self._on_history_up)
        self.entry.bind("<Down>", self._on_history_down)
        self.entry.focus_set()

    def refresh(self):
        """Update the window title and the prompt from the shell state."""
        self.root.title(
            "{} - VFS: {}".format(APP_TITLE, self.shell.vfs_name)
        )
        self.prompt.configure(text=self.shell.prompt())

    def write(self, text, tag=TAG_OUTPUT):
        """Append a line of text to the output area."""
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", tag)
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)

    def _after(self, result):
        """Refresh the window after a command; close it on ``exit``."""
        if result.should_exit:
            self.root.destroy()
        else:
            self.refresh()

    def start(self, config, debug_lines):
        """Show the debug output of the parameters, run the startup script.

        The window stays open for interactive work after the script.
        """
        for line in debug_lines:
            self.write(line, TAG_DEBUG)
        if config.script_path is not None:
            self.session.run_script(config.script_path)

    def _on_enter(self, _event):
        """Handle the Enter key in the input line."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        if line.strip():
            self.history.append(line)
        self.history_pos = len(self.history)
        self.session.submit(line)

    def _show_history(self):
        """Put the history item at the current position into the entry."""
        self.entry.delete(0, tk.END)
        if self.history_pos < len(self.history):
            self.entry.insert(0, self.history[self.history_pos])

    def _on_history_up(self, _event):
        """Show the previous command from the history."""
        if self.history_pos:
            self.history_pos -= 1
        self._show_history()

    def _on_history_down(self, _event):
        """Show the next command from the history."""
        if self.history_pos < len(self.history):
            self.history_pos += 1
        self._show_history()
