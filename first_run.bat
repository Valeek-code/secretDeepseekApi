@echo off
setlocal
cd /d "%~dp0"
echo === Installing dependencies ===
poetry lock
if errorlevel 1 goto :error
poetry install
if errorlevel 1 goto :error
echo === Done ===
goto :eof
:error
echo === FAILED ===
exit /b 1
