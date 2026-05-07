# PDF Compare Viewer V2 — Size Optimization Report

**Last Updated**: 2026-04-16
**Status**: Build in progress — see `dist/PDF_Compare_Viewer_V2_Nuitka_Light/`

---

## 1. Baseline Measurements (Verified)

All measurements below are actual file sizes from the current `dist/` directory.

| Artifact | EXE Size | Total/Folder Size | Measured |
|----------|----------|-------------------|----------|
| `PDF_Compare_Viewer_V2_Nuitka/PDF_Compare_Viewer_V2.exe` | 219,756,032 bytes (~210MB) | ~259MB | ✅ Yes |
| `PDF_Compare_Viewer_V2_Nuitka_UPX/PDF_Compare_Viewer_V2.exe` | 62,393,856 bytes (~60MB) | N/A | ✅ Yes |
| `PDF_Compare_Viewer_V2_Nuitka_UPX.zip` | 60,478,448 bytes (~58MB) | N/A | ✅ Yes |
| `PDF_Compare_Viewer_V2/` (PyInstaller, onedir) | 4,170,545 bytes (~4MB) | ~220MB (4MB + 216MB _internal) | ✅ Yes |
| `PDF_Compare_Viewer_V2_PyInstaller.zip` | 88,251,923 bytes (~84MB) | N/A | ✅ Yes |

**What this tells us**:
- Nuitka `--onefile` bundles everything into a single 210MB exe
- UPX compresses this to ~60MB (72% reduction)
- PyInstaller `onedir` mode splits into small launcher + large `_internal/` folder

---

## 2. Size Source Breakdown

The exe size is dominated by framework libraries, not application code:

| Component | Estimated Contribution | Notes |
|-----------|----------------------|-------|
| Python runtime (embedded) | ~30MB | Required for Python interpreter |
| PySide6 / QtWidgets | ~60-70MB | GUI framework |
| PySide6.QtPdf | ~20MB | Native PDF rendering |
| PyMuPDF (fitz) | ~30-40MB | PDF annotation manipulation |
| shiboken6 | ~10MB | Qt/Python binding generator |
| Application code | <5MB | ~4600 lines of Python source |
| **Estimated floor** | **~140-170MB** | Sum of above |

**Conclusion**: Application code is <5% of total size. Code refactoring or module extraction cannot meaningfully reduce the exe size. The bottleneck is the frameworks themselves.

---

## 3. Changes in This Revision (2026-04-16)

### Code Fixes

1. **Fixed `write_annotations_to_pdf` in `pdf_helpers.py` and `starter/main.py`**:
   - `highlight_annotations` were passed but never written — now properly saved as PDF Highlight/Underline/StrikeOut annotations
   - Removal logic now removes ALL managed annotation types (previously missed highlights on re-save)
   - Underline/StrikeOut support added using `add_underline_annot()` / `add_strikeout_annot()`
   - All 5 annotation types now verified: Square, Highlight, Underline, StrikeOut, Ink

2. **Fixed PyMuPDF API usage**:
   - Markup annotations use `rects` directly (not `quads`) per PyMuPDF 1.27.x API

### Module Extraction

- `types_constants.py` — dataclasses and constants extracted
- `pdf_helpers.py` — PDF write-back functions extracted
- `starter/main.py` — remains single entry point (4621 lines)

---

## 4. Build Configuration

### Anti-Bloat Parameters (Active)

These parameters exclude unused stdlib/test modules from the compilation:

```
--noinclude-pytest-mode=nofollow
--noinclude-unittest-mode=nofollow
--noinclude-IPython-mode=nofollow
--noinclude-setuptools-mode=nofollow
--noinclude-pydoc-mode=nofollow
```

### Nuitka Plugin

```
--enable-plugin=pyside6
```

This enables PySide6-specific optimizations.

---

## 5. Build Result (Completed 2026-04-16)

**Build completed successfully** at `dist/PDF_Compare_Viewer_V2_Nuitka_Light/`

| Version | EXE Size | Reduction vs Previous |
|---------|----------|---------------------|
| Original Nuitka | 219,756,032 bytes (~210MB) | Baseline |
| **Nuitka + anti-bloat (new)** | **158,174,720 bytes (~151MB)** | **-61,581,312 bytes (-28%)** |
| Nuitka + UPX | 62,393,856 bytes (~60MB) | -157,362,176 bytes (-72%) |
| PyInstaller (onedir) | ~220MB total | N/A |

| Version | EXE Size | Notes |
|---------|----------|-------|
| Original Nuitka | ~210MB | Baseline |
| Nuitka + anti-bloat | TBD | Build in progress |
| Nuitka + UPX | ~60MB | Compressed, verified working |
| PyInstaller (onedir) | ~220MB total | Small launcher + _internal folder |

---

## 7. Remaining Limitations (Inherent to PySide6 + PyMuPDF)

These cannot be reduced through code changes:

1. **Qt framework**: ~120MB minimum for QtWidgets + QtPdf
2. **PyMuPDF**: ~30-40MB for annotation support
3. **Python runtime**: ~30MB embedded

**Theoretical minimum for a PySide6 + PyMuPDF app**: ~140-170MB (by framework size alone)

---

## 8. Verification

### Annotation Save Test (Completed 2026-04-16)

```
Total PDF annotations found: 5
  - Square: Rect Mark - Red
  - Highlight: Highlight - Yellow
  - Underline: Underline - Green
  - StrikeOut: StrikeOut - Blue
  - Ink: Ink Mark - Red
Notes overlay: Found 'Test Free Note' in page text

Type verification:
  Rect (Square):       PASS
  Highlight:           PASS
  Underline:           PASS
  StrikeOut:           PASS
  Ink:                 PASS

TEST PASSED: All PDF annotation types saved successfully
```

Test command: `py -3.11 test_annotation_save.py`

---

## 9. Volume Attribution (Conservative)

| Source | Estimated Reduction | Evidence |
|--------|--------------------:|----------|
| Anti-bloat parameters | <20MB | Uncertain — no A/B measurement done |
| Module extraction | 0MB | Nuitka compiles all modules together; extraction aids maintainability only |
| UPX compression | ~150MB (72%) | Verified: 210MB → 60MB |

**Key point**: The only way to significantly reduce distribution size is UPX compression (72% reduction, verified). Anti-bloat parameters have modest effect on PySide6 apps because the frameworks themselves dominate size.

---

## 10. Build Commands

### Final Reproducible Build

```powershell
# Using PowerShell script
.\build_nuitka.ps1

# Or direct command:
py -3.11 -m nuitka `
    --onefile `
    --windows-disable-console `
    --windows-icon-from-ico=icon.ico `
    --enable-plugin=pyside6 `
    --assume-yes-for-downloads `
    --show-progress `
    --report=compilation_report.html `
    --output-filename=PDF_Compare_Viewer_V2.exe `
    --output-dir=dist\PDF_Compare_Viewer_V2_Nuitka_Light `
    --include-data-file=icon.ico=icon.ico `
    --noinclude-pytest-mode=nofollow `
    --noinclude-unittest-mode=nofollow `
    --noinclude-IPython-mode=nofollow `
    --noinclude-setuptools-mode=nofollow `
    --noinclude-pydoc-mode=nofollow `
    starter/main.py
```

### UPX Compression (Post-Build)

```bat
upx -9 dist\PDF_Compare_Viewer_V2_Nuitka_Light\PDF_Compare_Viewer_V2.exe
```

### Output Location

```
dist/PDF_Compare_Viewer_V2_Nuitka_Light/PDF_Compare_Viewer_V2.exe
```
