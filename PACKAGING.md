# PDF Compare Viewer V2 - Nuitka Packaging Guide

**Last Updated**: 2026-04-16

## Overview

This document describes the Nuitka packaging configuration for PDF Compare Viewer V2.

## Project Structure

```
pdf_compare_viewer_v2_native_pdf_annotations/
├── starter/
│   └── main.py              # Main application entry point (~4621 lines)
├── types_constants.py       # Dataclasses and constants
├── pdf_helpers.py           # PDF annotation write functions
├── requirements.txt         # Runtime dependencies
├── icon.ico                 # Application icon (required)
├── build_nuitka.bat         # Windows batch build script
├── build_nuitka.ps1         # PowerShell build script
├── test_annotation_save.py  # Verification test for annotation saving
├── SIZE_REPORT.md            # Size analysis and measurements
└── dist/                     # Build output directory
    ├── PDF_Compare_Viewer_V2_Nuitka/          # Original Nuitka build (210MB exe)
    ├── PDF_Compare_Viewer_V2_Nuitka_Light/   # Anti-bloat build (TBD size)
    ├── PDF_Compare_Viewer_V2_Nuitka_UPX/     # UPX compressed (~60MB exe)
    ├── PDF_Compare_Viewer_V2/                # PyInstaller build
    └── *.zip                                  # Distribution packages
```

## Dependencies

### Runtime (required)
- `PySide6>=6.6` — Qt GUI framework (includes QtCore, QtGui, QtWidgets, QtPdf)
- `PyMuPDF>=1.24` — PDF annotation manipulation

### Build (required for compilation)
- `nuitka` — Python to C compiler (install via system Python or venv)

## Build Commands

### Quick Start (Windows)

**Using Batch Script:**
```bat
.\build_nuitka.bat
```

**Using PowerShell:**
```powershell
.\build_nuitka.ps1
```

### Manual Build

```bat
py -3.11 -m venv .venv_nuitka
.venv_nuitka\Scripts\python -m pip install --upgrade pip
.venv_nuitka\Scripts\python -m pip install nuitka PySide6 PyMuPDF

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
```

## Nuitka Options Explained

| Option | Purpose |
|--------|---------|
| `--onefile` | Bundle everything into a single executable |
| `--windows-disable-console` | Hide console window (GUI app) |
| `--windows-icon-from-ico=icon.ico` | Use custom icon |
| `--enable-plugin=pyside6` | Enable PySide6 plugin for better Qt integration |
| `--assume-yes-for-downloads` | Auto-download required files |
| `--show-progress` | Show compilation progress |
| `--report=compilation_report.html` | Generate detailed compilation report |
| `--include-data-file` | Include additional data files |
| `--noinclude-*-mode=nofollow` | Exclude test/unittest/IPython/setuptools/pydoc modules |

## Anti-Bloat Options

These options exclude unused modules from the compilation:

```
--noinclude-pytest-mode=nofollow
--noinclude-unittest-mode=nofollow
--noinclude-IPython-mode=nofollow
--noinclude-setuptools-mode=nofollow
--noinclude-pydoc-mode=nofollow
```

**Note**: These primarily affect stdlib modules. For PySide6-heavy applications, the impact on exe size is modest because PySide6/PyMuPDF/Qt frameworks themselves dominate the size (~140-170MB minimum).

## Prerequisites

- **icon.ico** must exist in the project root directory
- Python 3.11 must be installed
- Windows 10/11 x64
- LLVM MinGW (for C compilation, usually auto-detected)

## Verification

Run the annotation save test:

```bat
py -3.11 test_annotation_save.py
```

Expected output:
```
Type verification:
  Rect (Square):       PASS
  Highlight:           PASS
  Underline:           PASS
  StrikeOut:           PASS
  Ink:                 PASS

TEST PASSED: All PDF annotation types saved successfully
```

## Troubleshooting

### MinGW Not Found
If you see "gcc not found", install LLVM MinGW:
```bat
winget install MartinStorsjo.LLVM-MinGW.MSVCRT
```

### Import Errors
Ensure all dependencies are installed:
```bat
py -3.11 -m pip install PySide6 PyMuPDF
```

### Build Hangs
Try with `--threads=1` to reduce parallel compilation:
```bat
py -3.11 -m nuitka --onefile --threads=1 starter/main.py
```

### Icon Not Found
Ensure `icon.ico` exists in the project root. The scripts check for this and will error clearly if missing.

## Output

- **Executable**: `dist/PDF_Compare_Viewer_V2_Nuitka_Light/PDF_Compare_Viewer_V2.exe`
- **Compilation Report**: `compilation_report.html`

## Size Summary

| Build Type | EXE Size | Status |
|-----------|----------|--------|
| Original Nuitka | ~210MB | Verified |
| Anti-bloat build | TBD | Build in progress |
| UPX compressed | ~60MB | Verified working |
| PyInstaller | ~220MB total | Verified |

## UPX Compression (Optional)

To further compress the exe after building:
```bat
upx -9 dist\PDF_Compare_Viewer_V2_Nuitka_Light\PDF_Compare_Viewer_V2.exe
```

This is verified to work without affecting functionality. The UPX-compressed version is in `dist/PDF_Compare_Viewer_V2_Nuitka_UPX/`.
