"""Tests of the command interpreter and of the session."""

import os
import shutil
import tempfile
import unittest

from shell_emulator.session import TAG_ERROR, TAG_INPUT, TAG_OUTPUT, Session
from shell_emulator.shell import Shell
from shell_emulator.vfs import Vfs


class ShellTest(unittest.TestCase):
    """Execution of commands by the shell."""

    def setUp(self):
        """Create a fresh shell."""
        self.shell = Shell()

    def test_ls_stub_prints_name_and_args(self):
        """The ls stub prints its name and arguments."""
        result = self.shell.execute("ls -l /tmp")
        self.assertEqual(result.output, "ls: args = ['-l', '/tmp']")
        self.assertEqual(result.error, "")

    def test_cd_stub_prints_quoted_args(self):
        """The cd stub receives a quoted argument as a single value."""
        result = self.shell.execute('cd "My Documents"')
        self.assertEqual(result.output, "cd: args = ['My Documents']")

    def test_stub_without_args(self):
        """A stub without arguments prints an empty list."""
        self.assertEqual(self.shell.execute("ls").output, "ls: args = []")

    def test_unknown_command(self):
        """An unknown command is reported as an error."""
        result = self.shell.execute("foo bar")
        self.assertIn("foo: command not found", result.error)
        self.assertEqual(result.output, "")
        self.assertFalse(result.should_exit)

    def test_syntax_error(self):
        """A parse error is reported as a syntax error."""
        result = self.shell.execute('ls "abc')
        self.assertIn("syntax error", result.error)

    def test_blank_line_does_nothing(self):
        """A blank line produces neither output nor error."""
        result = self.shell.execute("   ")
        self.assertEqual((result.output, result.error), ("", ""))

    def test_exit(self):
        """The exit command asks the application to stop."""
        self.assertTrue(self.shell.execute("exit").should_exit)

    def test_exit_with_arguments(self):
        """The exit command rejects arguments."""
        result = self.shell.execute("exit 1")
        self.assertIn("too many arguments", result.error)
        self.assertFalse(result.should_exit)

    def test_prompt_contains_vfs_name(self):
        """The prompt shows the VFS name and the current directory."""
        self.assertEqual(Shell(Vfs.default("/x/demo")).prompt(), "demo:/$ ")


class VfsInitTest(unittest.TestCase):
    """The vfs-init command."""

    def setUp(self):
        """Create a VFS directory with a nested file and load it."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = os.path.join(tmp.name, "my_vfs")
        os.makedirs(os.path.join(self.dir, "sub"))
        with open(os.path.join(self.dir, "sub", "f.txt"), "w") as target:
            target.write("data")
        self.shell = Shell(Vfs.from_directory(self.dir))

    def test_vfs_init_replaces_vfs_and_clears_disk(self):
        """The VFS becomes empty in memory and on the disk."""
        result = self.shell.execute("vfs-init")
        self.assertEqual(result.error, "")
        self.assertIn("physical directory cleared", result.output)
        self.assertIn("0 directories, 0 files", result.output)
        self.assertEqual(self.shell.vfs.root.children, {})
        self.assertTrue(os.path.isdir(self.dir))
        self.assertEqual(os.listdir(self.dir), [])

    def test_vfs_init_keeps_vfs_location(self):
        """After vfs-init the VFS is still bound to its directory."""
        self.shell.execute("vfs-init")
        self.assertEqual(self.shell.vfs.source_path, self.dir)
        self.assertEqual(self.shell.vfs_name, "my_vfs")

    def test_vfs_init_twice(self):
        """Repeating vfs-init is harmless."""
        self.shell.execute("vfs-init")
        self.assertEqual(self.shell.execute("vfs-init").error, "")

    def test_vfs_init_without_directory(self):
        """Without a physical directory only the memory is reset."""
        shell = Shell()
        result = shell.execute("vfs-init")
        self.assertNotIn("cleared", result.output)
        self.assertEqual(result.error, "")

    def test_vfs_init_rejects_arguments(self):
        """Arguments are not accepted and nothing is deleted."""
        result = self.shell.execute("vfs-init now")
        self.assertIn("too many arguments", result.error)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "sub", "f.txt")))

    def test_vfs_init_error_when_directory_vanished(self):
        """If the directory is gone the error is reported."""
        shutil.rmtree(self.dir)
        result = self.shell.execute("vfs-init")
        self.assertIn("vfs-init:", result.error)
        self.assertIn("f.txt", "\n".join(self.shell.vfs.tree_lines()))


class SessionTest(unittest.TestCase):
    """Echo and output of a session."""

    def test_submit_writes_input_output_and_error(self):
        """The session writes the echoed command and its results."""
        written = []
        session = Session(Shell(), lambda *item: written.append(item))
        session.submit("ls a")
        session.submit("nope")
        self.assertEqual(written[0], ("default:/$ ls a", TAG_INPUT))
        self.assertEqual(written[1], ("ls: args = ['a']", TAG_OUTPUT))
        self.assertEqual(written[2][1], TAG_INPUT)
        self.assertEqual(written[3][1], TAG_ERROR)


if __name__ == "__main__":
    unittest.main()
