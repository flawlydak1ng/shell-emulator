#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== 1. VFS directory does not exist"
./run.sh --vfs-path examples/vfs/no_such_dir --script examples/startup/vfs_view.txt

echo "== 2. VFS path is a file, not a directory"
./run.sh --vfs-path examples/vfs/minimal/hello.txt \
    --script examples/startup/vfs_view.txt

echo "== 3. vfs-init on a copy of every VFS variant"
TMP=$(mktemp -d)
for name in minimal files deep; do
    cp -r "examples/vfs/$name" "$TMP/$name"
    ./run.sh --vfs-path "$TMP/$name" --script examples/startup/vfs_init.txt
    echo "files left in the directory $name: $(ls -A "$TMP/$name" | wc -l)"
done
rm -rf "$TMP"
