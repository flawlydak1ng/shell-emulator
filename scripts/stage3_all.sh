#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== all commands of stages 1-3 on a temporary copy of the deep VFS"
echo "== (the script runs vfs-init, which clears the physical directory)"
TMP=$(mktemp -d)
cp -r examples/vfs/deep "$TMP/deep"
./run.sh --vfs-path "$TMP/deep" --script examples/startup/all_commands.txt
rm -rf "$TMP"
