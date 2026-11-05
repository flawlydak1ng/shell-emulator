@echo off
cd /d "%~dp0.."

echo == 1. script with erroneous lines (they are skipped)
call run.bat --vfs-path examples\vfs\deep --script examples\startup\with_errors.txt

echo == 2. --help lists all supported parameters
call run.bat --help

echo == 3. unknown parameter is rejected (exit code 2)
call run.bat --vfs-path examples\vfs\minimal --unknown
echo exit code: %ERRORLEVEL%

echo == 4. parameter without a value is rejected (exit code 2)
call run.bat --script
echo exit code: %ERRORLEVEL%
