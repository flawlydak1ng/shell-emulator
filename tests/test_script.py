"""Tests of the startup script runner."""

import os
import tempfile
import unittest

from shell_emulator.session import TAG_ERROR, TAG_INPUT, Session
from shell_emulator.shell import Shell


class ScriptTest(unittest.TestCase):
    """Running startup scripts."""

    def setUp(self):
        """Create a session that records everything it writes."""
        self.written = []
        self.session = Session(Shell(), lambda *item: self.written.append(item))
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def make_script(self, text):
        """Write a script file and return its path."""
        path = os.path.join(self.dir, "start.txt")
        with open(path, "w", encoding="utf-8") as script:
            script.write(text)
        return path

    def tags(self, tag):
        """Return the texts written with the given tag."""
        return [text for text, item_tag in self.written if item_tag == tag]

    def test_input_and_output_are_shown(self):
        """Every command is echoed and followed by its output."""
        report = self.session.run_script(self.make_script("ls a\ncd b\n"))
        texts = [text for text, _ in self.written]
        self.assertEqual(texts, [
            "default:/$ ls a", "ls: args = ['a']",
            "default:/$ cd b", "cd: args = ['b']",
        ])
        self.assertEqual((report.executed, report.skipped), (2, 0))

    def test_erroneous_lines_are_skipped(self):
        """A bad line is reported and the script goes on."""
        script = 'ls\nfoo\nls "x\nls after\n'
        report = self.session.run_script(self.make_script(script))
        self.assertEqual(len(self.tags(TAG_ERROR)), 2)
        self.assertEqual(len(self.tags(TAG_INPUT)), 4)
        self.assertIn("ls: args = ['after']", [t for t, _ in self.written])
        self.assertEqual((report.executed, report.skipped), (4, 2))

    def test_blank_lines_are_ignored(self):
        """Blank lines are neither shown nor counted."""
        report = self.session.run_script(self.make_script("\nls\n\n  \n"))
        self.assertEqual(report.executed, 1)
        self.assertEqual(len(self.tags(TAG_INPUT)), 1)

    def test_exit_stops_the_script(self):
        """Commands after ``exit`` are not executed."""
        report = self.session.run_script(self.make_script("ls\nexit\nls\n"))
        self.assertTrue(report.exited)
        self.assertEqual(report.executed, 1)
        self.assertEqual(len(self.tags(TAG_INPUT)), 2)

    def test_failed_exit_does_not_stop_the_script(self):
        """``exit`` with arguments is an error and is skipped."""
        report = self.session.run_script(self.make_script("exit 1\nls\n"))
        self.assertFalse(report.exited)
        self.assertEqual((report.executed, report.skipped), (2, 1))

    def test_missing_script(self):
        """A missing script file is reported as an error."""
        path = os.path.join(self.dir, "missing.txt")
        report = self.session.run_script(path)
        self.assertEqual(report.executed, 0)
        self.assertIn("cannot read", self.tags(TAG_ERROR)[0])

    def test_script_with_bom_and_crlf(self):
        """A Windows-style script (BOM, CRLF) is read correctly."""
        path = os.path.join(self.dir, "win.txt")
        with open(path, "wb") as script:
            script.write(b"\xef\xbb\xbfls a\r\ncd b\r\n")
        report = self.session.run_script(path)
        self.assertEqual((report.executed, report.skipped), (2, 0))

    def test_binary_script_is_reported(self):
        """A file that is not valid UTF-8 is reported as an error."""
        path = os.path.join(self.dir, "bin.txt")
        with open(path, "wb") as script:
            script.write(b"\xff\xfe\x00\x80")
        self.session.run_script(path)
        self.assertIn("cannot read", self.tags(TAG_ERROR)[0])


if __name__ == "__main__":
    unittest.main()
