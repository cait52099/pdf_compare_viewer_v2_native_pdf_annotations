@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "VENV_PYTHON=%ROOT_DIR%.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
  echo Missing virtual environment: %ROOT_DIR%.venv
  echo.
  echo Run these commands first:
  echo   py -3.11 -m venv .venv
  echo   .venv\Scripts\python -m pip install -r starter\requirements.txt
  exit /b 1
)

"%VENV_PYTHON%" "%ROOT_DIR%starter\main.py"
