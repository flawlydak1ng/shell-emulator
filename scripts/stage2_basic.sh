#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== 1. both parameters: --vfs-path and --script"
./run.sh --vfs-path examples/vfs/minimal --script examples/startup/basic.txt

echo "== 2. only --script (default VFS)"
./run.sh --script examples/startup/basic.txt

echo "== 3. parameters in the opposite order, VFS with several files"
./run.sh --script examples/startup/basic.txt --vfs-path examples/vfs/files
