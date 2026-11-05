#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

EMPTY=$(mktemp -d)

echo "== 1. minimal VFS (one file)"
./run.sh --vfs-path examples/vfs/minimal --script examples/startup/vfs_view.txt

echo "== 2. VFS with several files (including UTF-8 content)"
./run.sh --vfs-path examples/vfs/files --script examples/startup/vfs_view.txt

echo "== 3. VFS with 4 levels of files and folders"
./run.sh --vfs-path examples/vfs/deep --script examples/startup/vfs_view.txt

echo "== 4. empty directory as VFS"
./run.sh --vfs-path "$EMPTY" --script examples/startup/vfs_view.txt

echo "== 5. no VFS path: default VFS"
./run.sh --script examples/startup/vfs_view.txt

rmdir "$EMPTY"
