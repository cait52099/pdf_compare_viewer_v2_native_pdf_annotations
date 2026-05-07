"""
Minimal verification test for PDF annotation save functionality.

This script tests that all annotation types can be saved:
1. FreeText notes (PageNote) -> drawn as text overlays
2. Rect annotations -> PDF Square annotations
3. Highlight/Underline/StrikeOut -> PDF markup annotations
4. Ink annotations -> PDF Ink annotations

Usage:
    py -3.11 test_annotation_save.py
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import fitz


def create_test_pdf(output_path: Path) -> None:
    """Create a simple test PDF with one page."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size
    page.insert_text((100, 100), "Test PDF for Annotation Save", fontsize=12)
    doc.save(str(output_path))
    doc.close()


def test_annotation_save():
    """Test saving all annotation types."""
    from pdf_helpers import write_annotations_to_pdf
    from types_constants import PageNote, RectAnnotation, HighlightAnnotation, InkAnnotation

    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source PDF
        source_pdf = tmpdir / "source.pdf"
        create_test_pdf(source_pdf)

        # Create output PDF
        output_pdf = tmpdir / "output.pdf"

        # Test data - all annotation types
        notes = [
            PageNote(
                page_index=0,
                x=50.0,
                y=50.0,
                text="Test Free Note",
                color_name="Yellow",
                font_size=11.0,
                width=100.0,
                height=30.0,
            ),
        ]

        rect_annotations = [
            RectAnnotation(
                page_index=0,
                x0=100.0,
                y0=100.0,
                x1=200.0,
                y1=150.0,
                color_name="Red",
                text="Test Rectangle",
            ),
        ]

        highlight_annotations = [
            HighlightAnnotation(
                page_index=0,
                rects=[(100, 300, 300, 320)],
                color_name="Yellow",
                text="Test Highlight",
                markup_type="Highlight",
            ),
            HighlightAnnotation(
                page_index=0,
                rects=[(100, 340, 300, 360)],
                color_name="Green",
                text="Test Underline",
                markup_type="Underline",
            ),
            HighlightAnnotation(
                page_index=0,
                rects=[(100, 380, 300, 400)],
                color_name="Blue",
                text="Test StrikeOut",
                markup_type="StrikeOut",
            ),
        ]

        ink_annotations = [
            InkAnnotation(
                page_index=0,
                strokes=[[(50, 450), (100, 500), (150, 450)]],
                color_name="Red",
                text="Test Ink",
                width=3.0,
            ),
        ]

        # Call the save function
        print("Testing write_annotations_to_pdf...")
        print(f"  Source: {source_pdf}")
        print(f"  Output: {output_pdf}")
        print(f"  Notes: {len(notes)} (text overlay, not PDF annotation)")
        print(f"  Rect annotations: {len(rect_annotations)}")
        print(f"  Highlight annotations: {len(highlight_annotations)} (Highlight/Underline/StrikeOut)")
        print(f"  Ink annotations: {len(ink_annotations)}")

        write_annotations_to_pdf(
            source_pdf,
            output_pdf,
            notes,
            rect_annotations,
            highlight_annotations,
            ink_annotations,
        )

        # Verify output file exists
        if not output_pdf.exists():
            print("ERROR: Output file was not created!")
            return False

        print(f"  Output file size: {output_pdf.stat().st_size} bytes")

        # Open and verify annotations were saved
        doc = fitz.open(str(output_pdf))
        page = doc[0]

        annot_count = 0
        annot_types = []
        expected_types = {"Square", "Highlight", "Underline", "StrikeOut", "Ink"}

        for annot in page.annots() or []:
            annot_count += 1
            annot_type = annot.type[1] if len(annot.type) > 1 else "unknown"
            info = annot.info or {}
            subject = info.get("subject", "") or ""
            annot_types.append((annot_type, subject))
            if annot_type in expected_types:
                expected_types.discard(annot_type)

        doc.close()

        print(f"\nVerification Results:")
        print(f"  Total PDF annotations found: {annot_count}")
        for at_type, subject in annot_types:
            print(f"    - {at_type}: {subject}")

        # Check for missing types
        missing = expected_types - {"Square"}  # Square is expected from rect
        if missing:
            print(f"\nWARNING: Expected annotation types NOT found: {missing}")

        # Verify notes were drawn (check page has text content)
        doc2 = fitz.open(str(output_pdf))
        page2 = doc2[0]
        text = page2.get_text()
        doc2.close()
        if "Test Free Note" in text:
            print(f"  Notes overlay: Found 'Test Free Note' in page text")
        else:
            print(f"  WARNING: Notes overlay text not found in output")

        print(f"\nAnnotation counts by type:")
        type_counts = {}
        for at_type, _ in annot_types:
            type_counts[at_type] = type_counts.get(at_type, 0) + 1
        for t, c in type_counts.items():
            print(f"  {t}: {c}")

        # Summary
        rect_ok = any(at == "Square" for at, _ in annot_types)
        highlight_ok = any(at == "Highlight" for at, _ in annot_types)
        underline_ok = any(at == "Underline" for at, _ in annot_types)
        strikeout_ok = any(at == "StrikeOut" for at, _ in annot_types)
        ink_ok = any(at == "Ink" for at, _ in annot_types)

        print(f"\nType verification:")
        print(f"  Rect (Square):       {'PASS' if rect_ok else 'FAIL'}")
        print(f"  Highlight:           {'PASS' if highlight_ok else 'FAIL'}")
        print(f"  Underline:           {'PASS' if underline_ok else 'FAIL'}")
        print(f"  StrikeOut:           {'PASS' if strikeout_ok else 'FAIL'}")
        print(f"  Ink:                 {'PASS' if ink_ok else 'FAIL'}")

        all_ok = rect_ok and highlight_ok and underline_ok and strikeout_ok and ink_ok
        if all_ok:
            print("\nTEST PASSED: All PDF annotation types saved successfully")
        else:
            print("\nTEST FAILED: Some annotation types missing")

        return all_ok


if __name__ == "__main__":
    print("=" * 60)
    print("PDF Annotation Save Verification Test")
    print("=" * 60)
    print()

    try:
        success = test_annotation_save()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nTEST FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
