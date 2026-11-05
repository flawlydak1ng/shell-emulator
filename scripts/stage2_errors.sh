#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

echo "== 1. script with erroneous lines (they are skipped)"
./run.sh --vfs-path examples/vfs/deep --script examples/startup/with_errors.txt

echo "== 2. --help lists all supported parameters"
./run.sh --help

echo "== 3. unknown parameter is rejected (exit code 2)"
./run.sh --vfs-path examples/vfs/minimal --unknown
echo "exit code: $?"

echo "== 4. parameter without a value is rejected (exit code 2)"
./run.sh --script
echo "exit code: $?"
