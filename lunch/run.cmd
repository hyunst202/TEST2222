@echo off
setlocal
set "LUNCH_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%LUNCH_PYTHON%" set "LUNCH_PYTHON=%~dp0..\..\DAY7\sync_async_shop\.runtime\python\python.exe"
if not exist "%LUNCH_PYTHON%" (
  echo Please follow README.md to set up Python.
  exit /b 1
)
"%LUNCH_PYTHON%" -m uvicorn main:app --app-dir "%~dp0." --host 127.0.0.1 --port 8010 --workers 1
