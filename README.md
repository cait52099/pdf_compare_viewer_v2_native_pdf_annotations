# PDF Compare Viewer V2

**Version 2.1.0** | Side-by-side PDF comparison with native annotation support

## Features

- **Side-by-side PDF comparison** - Open multiple PDF windows for visual comparison
- **Sync / Solo mode** - Synchronized or independent viewing per window
- **Per-window relative zoom** - Fine-grained zoom control per PDF window
- **Absolute zoom unification** - Set a common zoom level from the footer
- **Page rotation** - Rotate pages with ↶ / ↷ buttons
- **Native PDF annotations** - Rectangle and ink annotations
- **Annotation write-back** - Adobe-compatible standard PDF annotation format
- **Multi-screen aware** - Auto-layout across current screen group
- **Hand-pan mode** - Pan PDFs freely (toggle via footer button or mouse middle button)
- **Ctrl + mouse wheel** - Fine-grained relative zoom

## Quick Start

### Run from source

```bash
# Requires Python 3.11+
py -3.11 starter/main.py
```

Or with virtual environment:

```bash
.venv/Scripts/python starter/main.py
```

### Build from source

**Windows (PowerShell):**

```powershell
./build_nuitka.ps1
```

**Windows (Batch):**

```batch
build_nuitka.bat
```

## Project Structure

```
pdf_compare_viewer_v2_native_pdf_annotations/
├── starter/
│   ├── main.py          # Application entry point
│   └── requirements.txt # Python dependencies
├── build_nuitka.ps1     # Nuitka build script (PowerShell)
├── build_nuitka.bat     # Nuitka build script (Batch)
├── pdf_helpers.py       # PDF annotation helpers
├── types_constants.py   # Type definitions and constants
├── requirements.txt     # Runtime dependencies
└── README.md            # This file
```

## Dependencies

- Python 3.11+
- PyMuPDF (fitz) - PDF rendering
- Nuitka - Python to EXE compilation

## Known Limitations

- Annotation save format is standard PDF annotations for Adobe editing compatibility
- Initial PDF content top alignment may vary in some multi-window startup paths

## License

MIT
