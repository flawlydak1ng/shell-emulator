@echo off
cd /d "%~dp0.."

echo == 1. both parameters: --vfs-path and --script
call run.bat --vfs-path examples\vfs\minimal --script examples\startup\basic.txt

echo == 2. only --script (default VFS)
call run.bat --script examples\startup\basic.txt

echo == 3. parameters in the opposite order, VFS with several files
call run.bat --script examples\startup\basic.txt --vfs-path examples\vfs\files
