"""
PDF helper functions for annotation write-back

This module contains functions for writing annotations to PDF files.
Extracted from main.py to enable lazy loading - these are only needed when saving.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from types_constants import (
        PageNote,
        RectAnnotation,
        HighlightAnnotation,
        InkAnnotation,
    )


def write_annotations_to_pdf(
    source_pdf: Path,
    output_pdf: Path,
    notes: list,
    rect_annotations: list,
    highlight_annotations: list,
    ink_annotations: list,
) -> None:
    """
    Write all annotations back to a PDF file.
    Uses PyMuPDF for annotation manipulation.

    Handles:
    - FreeText/Text notes (PageNote)
    - Square/Rect annotations
    - Highlight/Underline/StrikeOut annotations
    - Ink annotations
    """
    import fitz
    from types_constants import (
        NOTE_COLORS,
        APP_ANNOT_SUBJECT_PREFIXES,
        PDF_ANNOT_NOTE_TYPES,
        PDF_ANNOT_RECT_TYPES,
        PDF_ANNOT_HIGHLIGHT_TYPES,
        PDF_ANNOT_INK_TYPES,
    )

    previous_errors = fitz.TOOLS.mupdf_display_errors(False)
    previous_warnings = fitz.TOOLS.mupdf_display_warnings(False)
    fitz.TOOLS.reset_mupdf_warnings()
    try:
        with fitz.open(str(source_pdf)) as doc:
            # Remove ALL existing managed annotations (notes, rects, highlights, inks)
            for page_index in range(len(doc)):
                page = doc[page_index]
                removable_annots = []
                for annot in page.annots() or []:
                    annot_type = annot.type[1] if len(annot.type) > 1 else ""
                    info = annot.info or {}
                    subject = (info.get("subject", "") or "").strip()
                    is_managed = any(subject.startswith(prefix) for prefix in APP_ANNOT_SUBJECT_PREFIXES)
                    if is_managed:
                        removable_annots.append(annot)
                for annot in removable_annots:
                    page.delete_annot(annot)

            # Group annotations by page
            notes_by_page: dict[int, list] = {}
            rects_by_page: dict[int, list] = {}
            highlights_by_page: dict[int, list] = {}
            inks_by_page: dict[int, list] = {}

            for note in notes:
                notes_by_page.setdefault(note.page_index, []).append(note)
            for rect_annot in rect_annotations:
                rects_by_page.setdefault(rect_annot.page_index, []).append(rect_annot.normalized())
            for highlight_annot in highlight_annotations:
                highlights_by_page.setdefault(highlight_annot.page_index, []).append(highlight_annot)
            for ink_annot in ink_annotations:
                inks_by_page.setdefault(ink_annot.page_index, []).append(ink_annot)

            # Write free text notes (PageNote)
            for page_index, page_notes in notes_by_page.items():
                if not (0 <= page_index < len(doc)):
                    continue
                page = doc[page_index]
                for note in page_notes:
                    _write_note_to_page(page, note)

            # Write rect annotations
            for page_index, page_rects in rects_by_page.items():
                if not (0 <= page_index < len(doc)):
                    continue
                page = doc[page_index]
                for rect_annot in page_rects:
                    rgb = NOTE_COLORS.get(rect_annot.color_name, NOTE_COLORS["Red"])
                    annot = page.add_rect_annot(rect_annot.as_fitz_rect())
                    annot.set_colors(stroke=rgb)
                    annot.set_border(width=2.0)
                    annot.set_opacity(0.95)
                    annot.set_info(
                        title="PDF Compare Viewer",
                        subject=f"Rect Mark - {rect_annot.color_name}",
                        content=rect_annot.text,
                    )
                    annot.update()

            # Write highlight/underline/strikeout annotations
            for page_index, page_highlights in highlights_by_page.items():
                if not (0 <= page_index < len(doc)):
                    continue
                page = doc[page_index]
                for highlight_annot in page_highlights:
                    rects = highlight_annot.as_fitz_rects()
                    if not rects:
                        continue
                    rgb = NOTE_COLORS.get(highlight_annot.color_name, NOTE_COLORS["Yellow"])
                    # PyMuPDF markup annots accept rects directly
                    markup_type = getattr(highlight_annot, "markup_type", "Highlight")
                    if markup_type == "Underline":
                        annot = page.add_underline_annot(rects)
                    elif markup_type == "StrikeOut":
                        annot = page.add_strikeout_annot(rects)
                    else:
                        annot = page.add_highlight_annot(rects)
                    annot.set_colors(stroke=rgb)
                    annot.set_opacity(0.4)
                    annot.set_info(
                        title="PDF Compare Viewer",
                        subject=f"{markup_type} - {highlight_annot.color_name}",
                        content=highlight_annot.text,
                    )
                    annot.update()

            # Write ink annotations
            for page_index, page_inks in inks_by_page.items():
                if not (0 <= page_index < len(doc)):
                    continue
                page = doc[page_index]
                for ink_annot in page_inks:
                    strokes = ink_annot.normalized_strokes()
                    if not strokes:
                        continue
                    rgb = NOTE_COLORS.get(ink_annot.color_name, NOTE_COLORS["Red"])
                    annot = page.add_ink_annot(strokes)
                    annot.set_colors(stroke=rgb)
                    annot.set_border(width=max(1.0, ink_annot.width))
                    annot.set_opacity(0.95)
                    annot.set_info(
                        title="PDF Compare Viewer",
                        subject=f"Ink Mark - {ink_annot.color_name}",
                        content=ink_annot.text,
                    )
                    annot.update()

            # Save the document
            if output_pdf.resolve() == source_pdf.resolve():
                if doc.can_save_incrementally():
                    doc.save(str(output_pdf), incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
                else:
                    with tempfile.NamedTemporaryFile(
                        prefix=f"{output_pdf.stem}_",
                        suffix=output_pdf.suffix,
                        dir=str(output_pdf.parent),
                        delete=False,
                    ) as tmp:
                        tmp_path = Path(tmp.name)
                    try:
                        doc.save(str(tmp_path), garbage=4, deflate=True)
                        os.replace(tmp_path, output_pdf)
                    finally:
                        if tmp_path.exists():
                            tmp_path.unlink(missing_ok=True)
            else:
                doc.save(str(output_pdf), garbage=4, deflate=True)
    finally:
        fitz.TOOLS.mupdf_display_errors(previous_errors)
        fitz.TOOLS.mupdf_display_warnings(previous_warnings)


def _write_note_to_page(page: "fitz.Page", note: "PageNote") -> None:
    """Write a free text note to a PDF page."""
    import fitz
    from types_constants import NOTE_COLORS, FREE_NOTE_MAX_WIDTH

    if _is_quick_symbol(note.text):
        _draw_quick_symbol_on_pdf(page, note)
        return

    rgb = NOTE_COLORS.get(note.color_name, NOTE_COLORS["Yellow"])
    text_rgb = tuple(max(0.0, channel * 0.85) for channel in rgb)
    x0 = max(12.0, min(note.x, page.rect.width - 32.0))
    y0 = max(12.0, min(note.y, page.rect.height - 20.0))
    width = max(100.0, min(FREE_NOTE_MAX_WIDTH, page.rect.width - x0 - 18.0))
    if width <= 0:
        width = FREE_NOTE_MAX_WIDTH
        x0 = max(12.0, page.rect.width - width - 18.0)
    rect = fitz.Rect(x0, y0, x0 + width, min(y0 + 200.0, page.rect.height - 12.0))
    font_name = _ensure_page_font(page, None)
    page.insert_textbox(
        rect,
        note.text,
        fontsize=note.font_size,
        fontname=font_name,
        color=text_rgb,
        align=fitz.TEXT_ALIGN_LEFT,
        overlay=True,
    )


def _is_quick_symbol(text: str) -> bool:
    """Check if text is a quick symbol (checkmark or X)."""
    return text in {"✓", "✗"}


def _ensure_page_font(page: "fitz.Page", font_file: Optional[Path]) -> str:
    """Ensure a font is available on the page, return font name."""
    if font_file is None:
        return "helv"
    font_name = "F0"
    page.insert_font(fontname=font_name, fontfile=str(font_file))
    return font_name


def _draw_quick_symbol_on_pdf(page: "fitz.Page", note: "PageNote") -> None:
    """Draw a checkmark or X symbol on a PDF page."""
    import fitz
    from types_constants import NOTE_COLORS

    rgb = NOTE_COLORS.get(note.color_name, NOTE_COLORS["Green"])
    x0 = max(12.0, min(note.x, page.rect.width - 24.0))
    y0 = max(12.0, min(note.y, page.rect.height - 24.0))
    size = 22.0
    if note.text == "✓":
        page.draw_line(
            fitz.Point(x0 + size * 0.16, y0 + size * 0.60),
            fitz.Point(x0 + size * 0.36, y0 + size * 0.82),
            color=rgb,
            width=2.4,
            overlay=True,
        )
        page.draw_line(
            fitz.Point(x0 + size * 0.36, y0 + size * 0.82),
            fitz.Point(x0 + size * 0.90, y0 + size * 0.14),
            color=rgb,
            width=2.4,
            overlay=True,
        )
    else:
        page.draw_line(
            fitz.Point(x0 + size * 0.14, y0 + size * 0.14),
            fitz.Point(x0 + size * 0.86, y0 + size * 0.86),
            color=rgb,
            width=1.8,
            overlay=True,
        )
        page.draw_line(
            fitz.Point(x0 + size * 0.86, y0 + size * 0.14),
            fitz.Point(x0 + size * 0.14, y0 + size * 0.86),
            color=rgb,
            width=1.8,
            overlay=True,
        )
