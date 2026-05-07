"""
Type definitions and constants for PDF Compare Viewer V2

This module contains all dataclasses and constants used throughout the application.
Extracted from main.py to improve Nuitka compilation efficiency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# Constants
ZOOM_MULTIPLIER = math.sqrt(2.0)
SCROLL_STEP_PX = 60
WHEEL_SCROLL_STEP_PX = 140
CTRL_WHEEL_ZOOM_STEP = 1.06
WINDOW_MARGIN = 16
WINDOW_GAP = 10
MIN_RECT_SIZE_POINTS = 6.0
RECT_HANDLE_SIZE_PX = 8.0
NOTE_LABEL_FONT_SIZE = 11
NOTE_LABEL_PADDING_X = 8.0
NOTE_LABEL_PADDING_Y = 6.0
NOTE_LABEL_OFFSET_X = 10.0
NOTE_LABEL_OFFSET_Y = 2.0
NOTE_LABEL_MAX_WIDTH = 240.0
NOTE_LABEL_PREVIEW_CHARS = 48
NOTE_LABEL_SELECTED_CHARS = 120
FREE_NOTE_MAX_WIDTH = 220.0
SEARCH_HIGHLIGHT_ALPHA = 70
QUICK_SYMBOL_SIZE_PX = 28.0

NOTE_FONT_FAMILIES = [
    "PingFang SC",
    "Hiragino Sans",
    "Microsoft YaHei UI",
    "Microsoft YaHei",
    "Noto Sans CJK SC",
    "Noto Sans CJK JP",
    "Arial Unicode MS",
    "DejaVu Sans",
]

PDF_EXPORT_FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/YuGothM.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
]

NOTE_COLORS = {
    "Yellow": (1.0, 1.0, 0.0),
    "Red": (1.0, 0.3, 0.3),
    "Green": (0.3, 0.9, 0.3),
    "Blue": (0.3, 0.6, 1.0),
}

PDF_ANNOT_NOTE_TYPES = {"FreeText", "Text"}
PDF_ANNOT_RECT_TYPES = {"Square"}
PDF_ANNOT_HIGHLIGHT_TYPES = {"Highlight", "Underline", "StrikeOut"}
PDF_ANNOT_INK_TYPES = {"Ink"}
APP_ANNOT_SUBJECT_PREFIXES = ("Rect Mark -", "Ink Mark -")
INK_STROKE_WIDTH = 3.0
INK_HIT_TOLERANCE_PX = 10.0
APP_NAME = "PDF Compare Viewer"
APP_VERSION = "V2.1.0"
APP_DISPLAY_NAME = f"{APP_NAME} {APP_VERSION}"


# Dataclasses
@dataclass
class PageNote:
    page_index: int
    x: float
    y: float
    text: str
    color_name: str = "Yellow"
    font_size: float = 11.0
    width: float = 160.0
    height: float = 48.0

    def as_fitz_rect(self) -> "fitz.Rect":
        import fitz
        width = max(self.width, 24.0)
        height = max(self.height, 24.0)
        return fitz.Rect(self.x, self.y, self.x + width, self.y + height)


@dataclass
class RectAnnotation:
    page_index: int
    x0: float
    y0: float
    x1: float
    y1: float
    color_name: str = "Red"
    text: str = ""

    def normalized(self) -> "RectAnnotation":
        return RectAnnotation(
            page_index=self.page_index,
            x0=min(self.x0, self.x1),
            y0=min(self.y0, self.y1),
            x1=max(self.x0, self.x1),
            y1=max(self.y0, self.y1),
            color_name=self.color_name,
            text=self.text,
        )

    def as_fitz_rect(self) -> "fitz.Rect":
        import fitz
        normalized = self.normalized()
        return fitz.Rect(normalized.x0, normalized.y0, normalized.x1, normalized.y1)

    def display_name(self) -> str:
        return "Rectangle"


@dataclass
class HighlightAnnotation:
    page_index: int
    rects: list[tuple[float, float, float, float]] = field(default_factory=list)
    color_name: str = "Yellow"
    text: str = ""
    markup_type: str = "Highlight"

    def as_fitz_rects(self) -> "list[fitz.Rect]":
        import fitz
        output: list[fitz.Rect] = []
        for x0, y0, x1, y1 in self.rects:
            rect = fitz.Rect(x0, y0, x1, y1)
            if not rect.is_empty:
                output.append(rect)
        return output

    def overall_rect(self) -> Optional["fitz.Rect"]:
        import fitz
        rects = self.as_fitz_rects()
        if not rects:
            return None
        combined = fitz.Rect(rects[0])
        for rect in rects[1:]:
            combined.include_rect(rect)
        return combined

    def display_name(self) -> str:
        return self.markup_type


@dataclass
class InkAnnotation:
    page_index: int
    strokes: list[list[tuple[float, float]]] = field(default_factory=list)
    color_name: str = "Red"
    text: str = ""
    width: float = INK_STROKE_WIDTH

    def display_name(self) -> str:
        return "Ink"

    def normalized_strokes(self) -> list[list[tuple[float, float]]]:
        normalized: list[list[tuple[float, float]]] = []
        for stroke in self.strokes:
            cleaned = [(float(x), float(y)) for x, y in stroke]
            if len(cleaned) >= 2:
                normalized.append(cleaned)
        return normalized

    def bounds(self) -> Optional["fitz.Rect"]:
        import fitz
        strokes = self.normalized_strokes()
        if not strokes:
            return None
        first_x, first_y = strokes[0][0]
        rect = fitz.Rect(first_x, first_y, first_x, first_y)
        for stroke in strokes:
            for x, y in stroke:
                rect.include_point((x, y))
        padding = max(self.width, 1.0)
        return fitz.Rect(rect.x0 - padding, rect.y0 - padding, rect.x1 + padding, rect.y1 + padding)


@dataclass
class DocumentSession:
    window_id: str
    file_path: Path
    title: str
    page_count: int = 0
    current_page: int = 0
    zoom_factor: float = 1.0
    initial_zoom_factor: float = 1.0
    initial_zoom_captured: bool = False
    rotation_degrees: int = 0
    page_sizes_points: list = field(default_factory=list)
    display_page_sizes_points: list = field(default_factory=list)
    source_page_rotations: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    rect_annotations: list = field(default_factory=list)
    highlight_annotations: list = field(default_factory=list)
    ink_annotations: list = field(default_factory=list)


@dataclass
class PageRectCache:
    key: tuple
    rects: list


@dataclass
class RectEditState:
    annotation_index: int
    mode: str
    page_index: int
    start_page_point: "QPointF"
    original_annotation: RectAnnotation


@dataclass
class NoteMoveState:
    note_index: int
    page_index: int
    offset_x: float
    offset_y: float


@dataclass
class SearchHit:
    page_index: int
    rect: "fitz.Rect"
    preview: str
