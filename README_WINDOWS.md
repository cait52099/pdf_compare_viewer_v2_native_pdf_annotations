# PDF Compare Viewer V2.1.0 for Windows

## Recommended Environment

- Windows 10 or Windows 11
- 64-bit Python 3.11

## Setup

```bat
py -3.11 starter\main.py
```

Or with virtual environment:

```bat
.venv\Scripts\python starter\main.py
```

## Build EXE

Using PowerShell:

```powershell
.uild_nuitka.ps1
```

Or using Batch:

```batch
build_nuitka.bat
```

The built executable will be in `dist/PDF_Compare_Viewer_V2/`.

## Running the Built EXE

Navigate to the dist folder and run:

```batch
dist\PDF_Compare_Viewer_V2\PDF_Compare_Viewer_V2.exe
```

## Dependencies

- Python 3.11+
- PyMuPDF (fitz)
- Nuitka (for building EXE)

## Features

- Side-by-side PDF comparison
- Sync / Solo mode
- Native PDF annotation support (Adobe-compatible)
- Hand-pan and zoom controls
- Multi-screen aware layout
