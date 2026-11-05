"""Smoke tests of the graphical interface (skipped without a display)."""

import unittest

try:
    import tkinter as tk
except ImportError:
    tk = None

from shell_emulator.shell import Shell


@unittest.skipIf(tk is None, "tkinter is not installed")
class EmulatorWindowTest(unittest.TestCase):
    """Behaviour of the main window."""

    def setUp(self):
        """Create a window or skip the test if there is no display."""
        from shell_emulator.gui import EmulatorWindow

        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("no display available")
        self.window = EmulatorWindow(self.root, Shell("demo"))

    def tearDown(self):
        """Destroy the window if the test has not closed it already."""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def text(self):
        """Return the whole text shown in the output area."""
        return self.window.output.get("1.0", tk.END)

    def test_title_contains_vfs_name(self):
        """The window title contains the name of the VFS."""
        self.assertIn("VFS: demo", self.root.title())

    def test_command_is_echoed_with_output(self):
        """A submitted command and its output appear in the window."""
        self.window.submit('ls "a b"')
        self.assertIn("demo:/$ ls \"a b\"", self.text())
        self.assertIn("ls: args = ['a b']", self.text())

    def test_error_is_shown(self):
        """An unknown command produces an error line."""
        self.window.submit("foo")
        self.assertIn("foo: command not found", self.text())

    def test_exit_closes_window(self):
        """The exit command destroys the window."""
        self.window.submit("exit")
        with self.assertRaises(tk.TclError):
            self.root.winfo_exists()
            self.root.title()


if __name__ == "__main__":
    unittest.main()
