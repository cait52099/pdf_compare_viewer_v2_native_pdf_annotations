# PDF Compare Viewer V2.1.0 for Windows

## Current Folder

`C:\Users\hcai\Downloads\pdf_compare_viewer_v2_native_pdf_annotations_20260412_hand_pan_zoom\pdf_compare_viewer_v2_native_pdf_annotations`

## Recommended Environment

- Windows 10 or Windows 11
- 64-bit Python 3.11

## Setup

```bat
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r starter\requirements.txt
```

## Start

```bat
py -3.11 starter\main.py
```

Or:

```bat
.venv\Scripts\python starter\main.py
```

## Included in V2.1.0

- Hand-pan mode with footer `✋` toggle and mouse middle-button toggle
- `Ctrl + mouse wheel` fine zoom
- `↶` / `↷` rotation buttons
- Per-screen auto layout for multi-monitor setups
- Relative zoom behavior preserved per window in Sync mode
- High-DPI rendering path support

## Notes

- Source build, not a guaranteed final packaged release
- Adobe-compatible annotation write-back is preserved for `Square` and `Ink`
- If high-DPI behavior needs rollback, use environment variable `PDF_COMPARE_DISABLE_HIGH_DPI=1`
