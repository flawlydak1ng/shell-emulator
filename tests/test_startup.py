"""Tests of the start-up preparation (VFS loading and messages)."""

import os
import tempfile
import unittest

from shell_emulator.config import Config
from shell_emulator.session import TAG_DEBUG, TAG_ERROR
from shell_emulator.startup import prepare


class PrepareTest(unittest.TestCase):
    """Messages and VFS produced at start."""

    def test_without_vfs_path(self):
        """Without --vfs-path the default VFS is used silently."""
        vfs, messages = prepare(Config())
        self.assertEqual(vfs.name, "default")
        self.assertTrue(all(tag == TAG_DEBUG for _, tag in messages))

    def test_loaded_vfs_is_described(self):
        """A loaded VFS is described and its tree is shown."""
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "a.txt"), "w") as target:
                target.write("abc")
            vfs, messages = prepare(Config(vfs_path=tmp))
        text = "\n".join(text for text, _ in messages)
        self.assertIn("0 directories, 1 files, 3 bytes", text)
        self.assertIn("a.txt (3 bytes)", text)
        self.assertEqual(vfs.stats().files, 1)

    def test_loading_error_is_reported(self):
        """A missing directory is an error; the default VFS is used."""
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, "missing")
            vfs, messages = prepare(Config(vfs_path=missing))
        errors = [text for text, tag in messages if tag == TAG_ERROR]
        self.assertIn("directory not found", errors[0])
        self.assertEqual(vfs.name, "default")
        self.assertIsNone(vfs.source_path)

    def test_path_to_file_is_an_error(self):
        """A path that is a file cannot be a VFS."""
        with tempfile.NamedTemporaryFile() as tmp:
            _vfs, messages = prepare(Config(vfs_path=tmp.name))
        errors = [text for text, tag in messages if tag == TAG_ERROR]
        self.assertIn("not a directory", errors[0])


if __name__ == "__main__":
    unittest.main()
