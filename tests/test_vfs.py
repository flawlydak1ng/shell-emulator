"""Tests of the in-memory VFS."""

import os
import tempfile
import unittest

from shell_emulator.vfs import (
    Vfs,
    VfsDir,
    VfsError,
    VfsFile,
    clear_directory,
    is_protected_path,
    name_from_path,
)

BINARY = bytes(range(256))


class VfsTestCase(unittest.TestCase):
    """Base class that provides a temporary directory."""

    def setUp(self):
        """Create an empty temporary directory."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def make_file(self, relative, data=b""):
        """Create a file (and its parent directories) in the temp dir."""
        path = os.path.join(self.dir, *relative.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as target:
            target.write(data)
        return path

    def snapshot(self):
        """Return the sorted listing of the temp directory with sizes."""
        result = []
        for base, dirs, files in os.walk(self.dir):
            result.extend(os.path.join(base, name) for name in dirs)
            result.extend(
                (os.path.join(base, name),
                 os.path.getsize(os.path.join(base, name)))
                for name in files
            )
        return sorted(result, key=str)


class LoadTest(VfsTestCase):
    """Loading a VFS from a directory."""

    def test_empty_directory(self):
        """An empty directory gives an empty VFS."""
        vfs = Vfs.from_directory(self.dir)
        self.assertEqual(vfs.root.children, {})
        self.assertEqual(vfs.stats().files, 0)

    def test_single_file(self):
        """A minimal VFS with one file."""
        self.make_file("hello.txt", b"Hello")
        vfs = Vfs.from_directory(self.dir)
        expected = VfsFile("hello.txt", b"Hello")
        self.assertEqual(vfs.root.children["hello.txt"], expected)

    def test_nested_levels(self):
        """Files and folders on at least three levels are loaded."""
        self.make_file("a/b/c/deep.txt", b"deep")
        self.make_file("a/b/mid.txt", b"mid")
        self.make_file("top.txt", b"top")
        vfs = Vfs.from_directory(self.dir)
        level_a = vfs.root.children["a"]
        level_b = level_a.children["b"]
        level_c = level_b.children["c"]
        self.assertIsInstance(level_c, VfsDir)
        self.assertEqual(level_c.children["deep.txt"].data, b"deep")
        self.assertEqual(level_b.children["mid.txt"].data, b"mid")
        stats = vfs.stats()
        self.assertEqual((stats.dirs, stats.files), (3, 3))
        self.assertEqual(stats.size, len(b"deep" + b"mid" + b"top"))

    def test_empty_subdirectory_is_loaded(self):
        """Empty directories are part of the VFS."""
        os.makedirs(os.path.join(self.dir, "empty"))
        vfs = Vfs.from_directory(self.dir)
        self.assertEqual(vfs.root.children["empty"].children, {})

    def test_binary_content_is_kept_exactly(self):
        """Binary data is loaded without any conversion."""
        self.make_file("bin.dat", BINARY)
        vfs = Vfs.from_directory(self.dir)
        self.assertEqual(vfs.root.children["bin.dat"].data, BINARY)

    def test_unicode_names(self):
        """Non-ASCII file names are supported."""
        self.make_file("папка/файл.txt", "привет".encode("utf-8"))
        vfs = Vfs.from_directory(self.dir)
        self.assertIn("файл.txt", vfs.root.children["папка"].children)

    def test_loading_does_not_change_the_disk(self):
        """Loading only reads the directory."""
        self.make_file("a/one.txt", b"1")
        self.make_file("two.txt", b"22")
        before = self.snapshot()
        Vfs.from_directory(self.dir)
        self.assertEqual(self.snapshot(), before)

    def test_vfs_lives_in_memory(self):
        """Later changes on the disk do not affect the loaded VFS."""
        path = self.make_file("one.txt", b"1")
        vfs = Vfs.from_directory(self.dir)
        os.remove(path)
        self.assertEqual(vfs.root.children["one.txt"].data, b"1")

    def test_symbolic_links_are_skipped(self):
        """Symbolic links are not followed and not loaded."""
        target = self.make_file("real.txt", b"x")
        link = os.path.join(self.dir, "link.txt")
        try:
            os.symlink(target, link)
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links are not available")
        vfs = Vfs.from_directory(self.dir)
        self.assertNotIn("link.txt", vfs.root.children)
        self.assertEqual(vfs.skipped, 1)

    def test_missing_directory(self):
        """A missing directory is a loading error."""
        with self.assertRaises(VfsError) as ctx:
            Vfs.from_directory(os.path.join(self.dir, "nope"))
        self.assertIn("not found", str(ctx.exception))

    def test_path_is_a_file(self):
        """A path that is a file is a loading error."""
        path = self.make_file("file.txt", b"x")
        with self.assertRaises(VfsError) as ctx:
            Vfs.from_directory(path)
        self.assertIn("not a directory", str(ctx.exception))


class DescriptionTest(VfsTestCase):
    """Name, statistics and tree of a VFS."""

    def test_name_from_path(self):
        """The VFS name is the directory name."""
        self.assertEqual(name_from_path(os.path.join("a", "vfs_x")), "vfs_x")
        self.assertEqual(Vfs.default().name, "default")

    def test_tree_lines(self):
        """The tree lists directories first and shows file sizes."""
        self.make_file("b.txt", b"12")
        self.make_file("d/x.txt", b"1")
        lines = Vfs.from_directory(self.dir).tree_lines()
        self.assertEqual(lines, [
            "/", "|-- d/", "|   `-- x.txt (1 bytes)", "`-- b.txt (2 bytes)",
        ])

    def test_summary_of_default_vfs(self):
        """The default VFS is empty."""
        text = "\n".join(Vfs.default().summary_lines())
        self.assertIn("0 directories, 0 files, 0 bytes", text)


class ClearTest(VfsTestCase):
    """Clearing the physical directory."""

    def test_clear_keeps_the_directory(self):
        """Everything inside is deleted, the directory stays."""
        self.make_file("a/b/c.txt", b"1")
        self.make_file("d.txt", b"2")
        clear_directory(self.dir)
        self.assertTrue(os.path.isdir(self.dir))
        self.assertEqual(os.listdir(self.dir), [])

    def test_clear_missing_directory(self):
        """Clearing a missing directory is an error."""
        with self.assertRaises(VfsError):
            clear_directory(os.path.join(self.dir, "nope"))

    def test_protected_paths(self):
        """The file system root and the home directory are protected."""
        self.assertTrue(is_protected_path(os.path.abspath(os.sep)))
        self.assertTrue(is_protected_path(os.path.expanduser("~")))
        self.assertFalse(is_protected_path(self.dir))


if __name__ == "__main__":
    unittest.main()
