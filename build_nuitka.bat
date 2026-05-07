@echo off
REM PDF Compare Viewer V2 - Nuitka Build Script (Windows)
REM This script builds a lightweight single-file exe using Nuitka

echo ================================================
echo PDF Compare Viewer V2 - Nuitka Builder
echo ================================================
echo.

REM Set project root
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

REM Check if icon.ico exists
if not exist "icon.ico" (
    echo ERROR: icon.ico not found in project root!
    echo Please ensure icon.ico exists in: %PROJECT_ROOT%
    exit /b 1
)

REM Check if Python 3.11 is available
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.11 not found. Please install Python 3.11.
    exit /b 1
)

REM Check if Nuitka is available
py -3.11 -m nuitka --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Nuitka not found. Installing...
    py -3.11 -m pip install nuitka
)

REM Clean previous build
if exist "dist\PDF_Compare_Viewer_V2_Nuitka_Light" (
    echo Cleaning previous build...
    rmdir /s /q "dist\PDF_Compare_Viewer_V2_Nuitka_Light"
)

REM Create dist folder
if not exist "dist" mkdir dist

echo.
echo ================================================
echo Building with Nuitka...
echo ================================================
echo.

REM Build command with anti-bloat options
py -3.11 -m nuitka ^
    --onefile ^
    --windows-disable-console ^
    --windows-icon-from-ico=icon.ico ^
    --enable-plugin=pyside6 ^
    --assume-yes-for-downloads ^
    --show-progress ^
    --report=compilation_report.html ^
    --output-filename=PDF_Compare_Viewer_V2.exe ^
    --output-dir=dist\PDF_Compare_Viewer_V2_Nuitka_Light ^
    --include-data-file=icon.ico=icon.ico ^
    --noinclude-pytest-mode=nofollow ^
    --noinclude-unittest-mode=nofollow ^
    --noinclude-IPython-mode=nofollow ^
    --noinclude-setuptools-mode=nofollow ^
    --noinclude-pydoc-mode=nofollow ^
    starter/main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Nuitka build failed!
    exit /b 1
)

echo.
echo ================================================
echo Build completed successfully!
echo ================================================
echo.

REM Get file size
for %%F in ("dist\PDF_Compare_Viewer_V2_Nuitka_Light\PDF_Compare_Viewer_V2.exe") do (
    set SIZE=%%~zF
)
echo Output: dist\PDF_Compare_Viewer_V2_Nuitka_Light\PDF_Compare_Viewer_V2.exe
echo Size: %SIZE% bytes

REM Show comparison if old build exists
if exist "dist\PDF_Compare_Viewer_V2_Nuitka\PDF_Compare_Viewer_V2.exe" (
    echo.
    echo Comparison with previous build:
    for %%F in ("dist\PDF_Compare_Viewer_V2_Nuitka\PDF_Compare_Viewer_V2.exe") do (
        echo Previous: dist\PDF_Compare_Viewer_V2_Nuitka\PDF_Compare_Viewer_V2.exe - %%~zF bytes
    )
)

echo.
echo Compilation report: %PROJECT_ROOT%compilation_report.html
echo.
pause
