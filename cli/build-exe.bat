@echo off
REM Build the Contractor CLI executable for Windows.
REM Usage:
REM   cd cli
REM   build-exe.bat

cd /d %~dp0

REM Ensure README.md is available for PyPI packaging
if not exist "README.md" if exist "..\README.md" (
    copy "..\README.md" "README.md" > nul
)

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

pyinstaller contractor.spec

if exist dist\contractor.exe (
    echo.
    echo Build complete: %cd%\dist\contractor.exe
    echo To run the executable:
    echo   dist\contractor.exe --help
    exit /b 0
) else (
    echo.
    echo ERROR: No executable found in dist\contractor.exe
    exit /b 1
)
