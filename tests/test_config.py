"""Tests of command line parameters and of the debug output."""

import contextlib
import io
import os
import unittest

from shell_emulator.config import Config, debug_lines, parse_args


class ParseArgsTest(unittest.TestCase):
    """Parsing of command line arguments."""

    @staticmethod
    def quiet():
        """Return a context manager that hides argparse error messages."""
        return contextlib.redirect_stderr(io.StringIO())

    def test_no_arguments(self):
        """Without arguments both parameters are not set."""
        self.assertEqual(parse_args([]), Config(None, None))

    def test_both_parameters(self):
        """Both parameters are read in any order."""
        expected = Config("/vfs", "start.txt")
        argv = ["--vfs-path", "/vfs", "--script", "start.txt"]
        self.assertEqual(parse_args(argv), expected)
        self.assertEqual(parse_args(argv[2:] + argv[:2]), expected)

    def test_only_vfs_path(self):
        """The VFS path can be given without a script."""
        self.assertEqual(parse_args(["--vfs-path", "d"]), Config("d", None))

    def test_only_script(self):
        """The script can be given without a VFS path."""
        self.assertEqual(parse_args(["--script", "s"]), Config(None, "s"))

    def test_unknown_parameter(self):
        """An unknown parameter makes argparse exit with code 2."""
        with self.assertRaises(SystemExit) as ctx, self.quiet():
            parse_args(["--unknown"])
        self.assertEqual(ctx.exception.code, 2)

    def test_missing_value(self):
        """A parameter without a value is rejected."""
        with self.assertRaises(SystemExit), self.quiet():
            parse_args(["--script"])


class ConfigTest(unittest.TestCase):
    """VFS name and debug output."""

    def test_default_vfs_name(self):
        """Without a path the VFS is called ``default``."""
        self.assertEqual(Config().vfs_name(), "default")

    def test_vfs_name_is_last_path_component(self):
        """The VFS name is the name of the VFS directory."""
        path = os.path.join("some", "dir", "my_vfs") + os.sep
        self.assertEqual(Config(vfs_path=path).vfs_name(), "my_vfs")

    def test_debug_lists_all_parameters(self):
        """The debug output shows every parameter and its value."""
        text = "\n".join(debug_lines(Config("/vfs", "start.txt")))
        self.assertIn("--vfs-path = /vfs", text)
        self.assertIn("--script   = start.txt", text)

    def test_debug_marks_unset_parameters(self):
        """Parameters that were not given are marked as not set."""
        text = "\n".join(debug_lines(Config()))
        self.assertEqual(text.count("<not set>"), 2)


if __name__ == "__main__":
    unittest.main()
