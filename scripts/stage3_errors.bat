@echo off
cd /d "%~dp0.."

echo == 1. VFS directory does not exist
call run.bat --vfs-path examples\vfs\no_such_dir --script examples\startup\vfs_view.txt

echo == 2. VFS path is a file, not a directory
call run.bat --vfs-path examples\vfs\minimal\hello.txt --script examples\startup\vfs_view.txt

echo == 3. vfs-init on a copy of every VFS variant
set TMPV=%TEMP%\vfs_copy_%RANDOM%
for %%N in (minimal files deep) do (
    xcopy /E /I /Q /Y examples\vfs\%%N "%TMPV%\%%N" >nul
    call run.bat --vfs-path "%TMPV%\%%N" --script examples\startup\vfs_init.txt
    echo files left in the directory %%N:
    dir /b "%TMPV%\%%N"
)
rmdir /S /Q "%TMPV%"
