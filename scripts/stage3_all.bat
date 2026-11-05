@echo off
cd /d "%~dp0.."

echo == all commands of stages 1-3 on a temporary copy of the deep VFS
echo == (the script runs vfs-init, which clears the physical directory)
set TMPV=%TEMP%\vfs_all_%RANDOM%
xcopy /E /I /Q /Y examples\vfs\deep "%TMPV%" >nul
call run.bat --vfs-path "%TMPV%" --script examples\startup\all_commands.txt
rmdir /S /Q "%TMPV%"
