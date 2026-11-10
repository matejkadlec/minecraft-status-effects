"""CSV, XLSX and JSON exports of the effects table."""

from __future__ import annotations

import csv
import io
import json
import math
import re
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime

from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from . import config
from .data import Effect, strip_html

COLUMNS = ("Mod", "Effect", "Max", "Description", "Tags", "Source")

# Excel column widths (characters), roughly the table's proportions on a 1920px screen.
COLUMN_WIDTHS = (26, 24, 7, 80, 20, 70)

# Colors mirror the CSS variables in public/css/theme.css.
THEME_COLORS = {
    "light": {
        "header_bg": "2366B8",
        "header_text": "FFFFFF",
        "row_odd": "E6EDF5",
        "row_even": "FFFFFF",
        "text": "000000",
        "bold": "2366B8",
        "border": "C8D6E5",
    },
    "dark": {
        "header_bg": "CFA93A",
        "header_text": "000000",
        "row_odd": "2D3035",
        "row_even": "24272B",
        "text": "FFFFFF",
        "bold": "CFA93A",
        "border": "3A3F45",
    },
}

MEDIA_TYPES = {
    "csv": "text/csv; charset=utf-8",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "json": "application/json",
}

_INLINE_TAG_RE = re.compile(r"(</?[bi]>)")


def export_tags(effect: Effect) -> list[str]:
    return effect.tags + (["unreliable"] if effect.unreliable else [])


def filename(version: str, fmt: str, now: datetime | None = None) -> str:
    stamp = (now or datetime.now(UTC)).strftime("%Y%m%d-%H%M%S")
    return f"status-effects-{version}-{stamp}.{fmt}"


def to_json(effects: Sequence[Effect], version: str) -> bytes:
    payload = {
        "version": version,
        "exportedAt": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": config.SITE_URL,
        "license": f"{config.SITE_URL}/license/",
        "effects": [{**effect.public(), "tags": export_tags(effect)} for effect in effects],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def _row(effect: Effect) -> list[str]:
    return [
        effect.mod,
        effect.effect,
        effect.max_level,
        strip_html(effect.description),
        ", ".join(export_tags(effect)),
        strip_html(effect.source),
    ]


def to_csv(effects: Sequence[Effect]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(COLUMNS)
    writer.writerows(_row(effect) for effect in effects)
    # BOM so that Excel opens the file as UTF-8.
    return buffer.getvalue().encode("utf-8-sig")


def _rich_text(html: str, colors: dict[str, str]) -> CellRichText | str:
    """Convert a value with <b>/<i> tags to Excel rich text."""
    if "<" not in html:
        return html
    parts = CellRichText()
    bold = italic = False
    for token in _INLINE_TAG_RE.split(html):
        if token in ("<b>", "</b>"):
            bold = token == "<b>"
        elif token in ("<i>", "</i>"):
            italic = token == "<i>"
        elif token:
            text = strip_html(token)
            if not text:
                continue
            font = InlineFont(
                rFont="Arial",
                sz=10,
                b=bold or None,
                i=italic or None,
                color=colors["bold"] if bold else colors["text"],
            )
            parts.append(TextBlock(font, text))
    return parts


def _line_count(text: str, width: int) -> int:
    return max(1, math.ceil(len(text) / max(1, width - 2)))


def to_xlsx(effects: Sequence[Effect], theme: str, version: str) -> bytes:
    colors = THEME_COLORS.get(theme, THEME_COLORS["light"])
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = f"Status Effects {version}"[:31]

    thin = Side(style="thin", color=colors["border"])
    edge = Side(style="medium", color=colors["header_bg"])
    header_font = Font(name="Arial", size=10.5, bold=True, color=colors["header_text"])
    header_fill = PatternFill("solid", start_color=colors["header_bg"], end_color=colors["header_bg"])
    text_font = Font(name="Arial", size=10, color=colors["text"])

    sheet.append([name.upper() for name in COLUMNS])
    for index, _ in enumerate(COLUMNS, start=1):
        cell = sheet.cell(row=1, column=index)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(left=thin, right=thin, top=edge, bottom=edge)
    sheet.row_dimensions[1].height = 22

    for row_index, effect in enumerate(effects, start=2):
        fill_color = colors["row_odd"] if row_index % 2 == 0 else colors["row_even"]
        fill = PatternFill("solid", start_color=fill_color, end_color=fill_color)
        values: list[object] = [
            effect.mod,
            effect.effect,
            effect.max_level,
            _rich_text(effect.description, colors),
            ", ".join(export_tags(effect)),
            _rich_text(effect.source, colors),
        ]
        plain = _row(effect)
        lines = 1
        for column, value in enumerate(values, start=1):
            cell = sheet.cell(row=row_index, column=column, value=value)
            cell.font = text_font
            cell.fill = fill
            centered = column in (3, 5)
            cell.alignment = Alignment(horizontal="center" if centered else "left", vertical="center", wrap_text=True)
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            lines = max(lines, _line_count(plain[column - 1], COLUMN_WIDTHS[column - 1]))
        sheet.row_dimensions[row_index].height = max(18, 13 * lines + 5)

    for column, width in enumerate(COLUMN_WIDTHS, start=1):
        sheet.column_dimensions[get_column_letter(column)].width = width
    sheet.freeze_panes = "A2"
    if effects:
        sheet.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}{len(effects) + 1}"

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def build(fmt: str, effects: Iterable[Effect], version: str, theme: str = "light") -> tuple[bytes, str]:
    """Return (file content, filename) for an export format."""
    items = list(effects)
    if fmt == "json":
        content = to_json(items, version)
    elif fmt == "csv":
        content = to_csv(items)
    elif fmt == "xlsx":
        content = to_xlsx(items, theme, version)
    else:
        raise ValueError(f"unsupported export format: {fmt}")
    return content, filename(version, fmt)
