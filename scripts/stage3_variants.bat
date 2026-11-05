@echo off
cd /d "%~dp0.."
set EMPTY=%TEMP%\vfs_empty_%RANDOM%
mkdir "%EMPTY%"

echo == 1. minimal VFS (one file)
call run.bat --vfs-path examples\vfs\minimal --script examples\startup\vfs_view.txt

echo == 2. VFS with several files (including UTF-8 content)
call run.bat --vfs-path examples\vfs\files --script examples\startup\vfs_view.txt

echo == 3. VFS with 4 levels of files and folders
call run.bat --vfs-path examples\vfs\deep --script examples\startup\vfs_view.txt

echo == 4. empty directory as VFS
call run.bat --vfs-path "%EMPTY%" --script examples\startup\vfs_view.txt

echo == 5. no VFS path: default VFS
call run.bat --script examples\startup\vfs_view.txt

rmdir "%EMPTY%"
