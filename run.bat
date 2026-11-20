@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=src
poetry run python -m main

PAUSE