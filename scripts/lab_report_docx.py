"""Render a NUIST laboratory report from Markdown to DOCX."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Mm, Pt, RGBColor


BODY_FONT = "Times New Roman"
HEAD_FONT = "Arial"
CODE_FONT = "Consolas"
BLACK = "000000"
NAVY = "1F4E79"
LIGHT_BLUE = "DCE9F7"
LIGHT_GRAY = "F2F2F2"
BORDER_GRAY = "D9D9D9"
MID_GRAY = "666666"
PENDING_PATTERN = re.compile(r"\[PENDING:")
IMAGE_PATTERN = re.compile(
    r"^!\[(?P<caption>.*?)\]\((?P<path>[^)]+)\)"
    r"(?:\{(?P<attrs>[^}]*)\})?\s*$"
)
TABLE_SEPARATOR = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*$")
HEADING_PATTERN = re.compile(r"^(#{1,3})\s+(.+?)\s*$")


@dataclass(frozen=True)
class Block:
    kind: str
    value: str = ""
    attrs: dict[str, str] | None = None
    rows: tuple[tuple[str, ...], ...] = ()
    items: tuple[str, ...] = ()


def set_run_font(
    run,
    name: str,
    size: float | None = None,
    *,
    bold: bool | None = None,
    italic: bool | None = None,
    color: str | None = None,
) -> None:
    run.font.name = name
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for key in ("w:ascii", "w:hAnsi", "w:eastAsia"):
        rfonts.set(qn(key), name)


def set_style_font(
    style,
    name: str,
    size: float,
    *,
    bold: bool = False,
    italic: bool = False,
    color: str = BLACK,
) -> None:
    style.font.name = name
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    style.font.color.rgb = RGBColor.from_string(color)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for key in ("w:ascii", "w:hAnsi", "w:eastAsia"):
        rfonts.set(qn(key), name)


def set_picture_alt(picture, title: str, description: str) -> None:
    doc_pr = picture._inline.docPr
    doc_pr.set("title", title)
    doc_pr.set("descr", description)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def set_cell_border(
    cell,
    edge: str,
    *,
    color: str = BORDER_GRAY,
    size: int = 6,
) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    element = borders.find(qn(f"w:{edge}"))
    if element is None:
        element = OxmlElement(f"w:{edge}")
        borders.append(element)
    element.set(qn("w:val"), "single")
    element.set(qn("w:sz"), str(size))
    element.set(qn("w:space"), "0")
    element.set(qn("w:color"), color)


def set_table_borders(table, *, visible: bool = True) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single" if visible else "nil")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), BORDER_GRAY)


def set_cell_margins(cell, top: int = 70, start: int = 90, bottom: int = 70, end: int = 90) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        element = margins.find(qn(f"w:{side}"))
        if element is None:
            element = OxmlElement(f"w:{side}")
            margins.append(element)
        element.set(qn("w:w"), str(value))
        element.set(qn("w:type"), "dxa")


def prevent_row_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:cantSplit"))


def repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def set_paragraph_bottom_border(paragraph, color: str = BORDER_GRAY, size: int = 4) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    bottom = borders.find(qn("w:bottom"))
    if bottom is None:
        bottom = OxmlElement("w:bottom")
        borders.append(bottom)
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)


def add_page_field(paragraph) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = "PAGE"
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, text, end])


def configure_styles(doc: Document) -> None:
    styles = doc.styles
    normal = styles["Normal"]
    set_style_font(normal, BODY_FONT, 10.5)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.line_spacing = 1.16
    normal.paragraph_format.first_line_indent = Cm(0.55)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.widow_control = True

    for name, size, before, after, color in (
        ("Heading 1", 14, 13, 6, NAVY),
        ("Heading 2", 11.5, 10, 4, NAVY),
        ("Heading 3", 10.5, 8, 3, BLACK),
    ):
        style = styles[name]
        set_style_font(style, HEAD_FONT, size, bold=True, color=color)
        style.paragraph_format.first_line_indent = Pt(0)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.keep_together = True
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    title = styles["Title"]
    p_pr = title.element.find(qn("w:pPr"))
    if p_pr is not None:
        border = p_pr.find(qn("w:pBdr"))
        if border is not None:
            p_pr.remove(border)
    set_style_font(title, HEAD_FONT, 24, color=BLACK)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.first_line_indent = Pt(0)
    title.paragraph_format.space_before = Pt(0)
    title.paragraph_format.space_after = Pt(0)

    if "Abstract Title" not in [style.name for style in styles]:
        styles.add_style("Abstract Title", WD_STYLE_TYPE.PARAGRAPH)
    abstract = styles["Abstract Title"]
    set_style_font(abstract, HEAD_FONT, 12, bold=True, color=BLACK)
    abstract.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    abstract.paragraph_format.first_line_indent = Pt(0)
    abstract.paragraph_format.space_before = Pt(4)
    abstract.paragraph_format.space_after = Pt(7)

    if "Source Code" not in [style.name for style in styles]:
        styles.add_style("Source Code", WD_STYLE_TYPE.PARAGRAPH)
    code = styles["Source Code"]
    set_style_font(code, CODE_FONT, 7.4, color=BLACK)
    code.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    code.paragraph_format.first_line_indent = Pt(0)
    code.paragraph_format.line_spacing = 1.0
    code.paragraph_format.space_before = Pt(0)
    code.paragraph_format.space_after = Pt(0)
    code.paragraph_format.left_indent = Inches(0.18)
    code.paragraph_format.right_indent = Inches(0.10)

    caption = styles["Caption"]
    set_style_font(caption, BODY_FONT, 8.5, color=BLACK)
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    caption.paragraph_format.first_line_indent = Pt(0)
    caption.paragraph_format.line_spacing = 1.0
    caption.paragraph_format.space_before = Pt(3)
    caption.paragraph_format.space_after = Pt(7)


def set_page_geometry(section, *, cover: bool = False) -> None:
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    if cover:
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.25)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
    else:
        section.left_margin = Mm(25)
        section.right_margin = Mm(25)
        section.top_margin = Mm(25)
        section.bottom_margin = Mm(25)
        section.header_distance = Mm(12)
        section.footer_distance = Mm(12)


def add_cover(doc: Document, config: dict[str, Any], cover_assets: tuple[Path, Path]) -> None:
    section = doc.sections[0]
    set_page_geometry(section, cover=True)
    section.different_first_page_header_footer = True
    wordmark, seal = cover_assets

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture = paragraph.add_run().add_picture(str(wordmark), width=Inches(3.35))
    set_picture_alt(picture, "University wordmark", "University wordmark")
    paragraph.paragraph_format.space_before = Cm(0.05)
    paragraph.paragraph_format.space_after = Cm(0.45)

    title = doc.add_paragraph(str(config.get("report_type", "Experimental Report")), style="Title")
    for run in title.runs:
        set_run_font(run, HEAD_FONT, 24, color=BLACK)
    title.paragraph_format.space_after = Cm(1.05)

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture = paragraph.add_run().add_picture(str(seal), width=Inches(1.10))
    set_picture_alt(picture, "University seal", "University seal")
    paragraph.paragraph_format.space_after = Cm(3.0)

    fields = (
        ("Course Name", str(config.get("course", ""))),
        ("Project Name", str(config.get("title", ""))),
        ("Student Name", str(config.get("student", ""))),
        ("Student ID", str(config.get("student_id", ""))),
        ("Major", str(config.get("major", ""))),
        ("College", str(config.get("college", ""))),
    )
    table = doc.add_table(rows=len(fields), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table, visible=False)
    widths = (Inches(1.80), Inches(3.95))
    table.columns[0].width = widths[0]
    table.columns[1].width = widths[1]
    repeat_header(table.rows[0])
    for row_index, (label, value) in enumerate(fields):
        row = table.rows[row_index]
        row.height = Cm(1.0)
        prevent_row_split(row)
        label_cell, value_cell = row.cells
        label_cell.width, value_cell.width = widths
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell, top=35, start=80, bottom=35, end=80)
        label_p = label_cell.paragraphs[0]
        label_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        label_p.paragraph_format.first_line_indent = Pt(0)
        label_p.paragraph_format.space_after = Pt(0)
        set_run_font(label_p.add_run(label), HEAD_FONT, 18, bold=True)
        value_p = value_cell.paragraphs[0]
        value_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        value_p.paragraph_format.first_line_indent = Pt(0)
        value_p.paragraph_format.space_after = Pt(0)
        set_run_font(value_p.add_run(value), HEAD_FONT, 18)
        set_cell_border(value_cell, "bottom", color=BLACK, size=8)

    for _ in range(8):
        spacer = doc.add_paragraph()
        spacer.paragraph_format.first_line_indent = Pt(0)
        spacer.paragraph_format.line_spacing = Pt(18)
        spacer.paragraph_format.space_after = Pt(0)
    date = doc.add_paragraph()
    date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date.paragraph_format.first_line_indent = Pt(0)
    set_run_font(date.add_run(f"Date: {config.get('date', '')}"), HEAD_FONT, 18, bold=True)


def add_body_section(doc: Document, config: dict[str, Any]):
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    set_page_geometry(section, cover=False)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    section.different_first_page_header_footer = False

    header = section.header.paragraphs[0]
    header.paragraph_format.first_line_indent = Pt(0)
    header.paragraph_format.tab_stops.add_tab_stop(Inches(6.27), WD_TAB_ALIGNMENT.RIGHT)
    set_run_font(header.add_run(str(config.get("course_short", config.get("course", "")))), HEAD_FONT, 8.5, color=MID_GRAY)
    set_run_font(header.add_run("\t"), HEAD_FONT, 8.5, color=MID_GRAY)
    right_text = str(
        config.get(
            "header_right",
            f"Lab {config.get('lab_number', '')} | {config.get('report_type', 'Experimental Report')}",
        )
    ).strip()
    set_run_font(header.add_run(right_text), HEAD_FONT, 8.5, color=MID_GRAY)
    set_paragraph_bottom_border(header)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.first_line_indent = Pt(0)
    add_page_field(footer)
    for run in footer.runs:
        set_run_font(run, HEAD_FONT, 8.5, color=MID_GRAY)
    return section


def _is_block_start(line: str, next_line: str = "") -> bool:
    stripped = line.strip()
    return bool(
        not stripped
        or HEADING_PATTERN.match(stripped)
        or stripped.startswith(("```", "$$", "::pagebreak", "<!-- pagebreak -->"))
        or IMAGE_PATTERN.match(stripped)
        or stripped.startswith(("- ", "* ", "+ "))
        or re.match(r"^\d+\.\s+", stripped)
        or stripped.startswith("|")
        or stripped.startswith("Table: ")
    )


def _split_table_row(line: str) -> tuple[str, ...]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return tuple(cell.strip() for cell in stripped.split("|"))


def parse_markdown(text: str) -> list[Block]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: list[Block] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        if stripped in {"::pagebreak", "<!-- pagebreak -->"}:
            blocks.append(Block("pagebreak"))
            index += 1
            continue
        heading = HEADING_PATTERN.match(stripped)
        if heading:
            blocks.append(Block("heading", heading.group(2), {"level": str(len(heading.group(1)))}))
            index += 1
            continue
        if stripped.startswith("```"):
            language = stripped[3:].strip()
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            index += 1
            blocks.append(Block("code", "\n".join(code_lines), {"language": language}))
            continue
        image = IMAGE_PATTERN.match(stripped)
        if image:
            blocks.append(
                Block(
                    "image",
                    image.group("path"),
                    {
                        "caption": image.group("caption").strip(),
                        "attrs": image.group("attrs") or "",
                    },
                )
            )
            index += 1
            continue
        if stripped.startswith("$$"):
            formula = stripped[2:]
            if formula.endswith("$$"):
                formula = formula[:-2]
                index += 1
            else:
                formula_lines = [formula] if formula else []
                index += 1
                while index < len(lines) and lines[index].strip() != "$$":
                    formula_lines.append(lines[index].strip())
                    index += 1
                index += 1
                formula = " ".join(formula_lines)
            blocks.append(Block("equation", formula.strip()))
            continue
        if stripped.startswith("Table: "):
            blocks.append(Block("table_caption", stripped[7:].strip()))
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines) and TABLE_SEPARATOR.match(lines[index + 1]):
            rows = [_split_table_row(stripped)]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(_split_table_row(lines[index]))
                index += 1
            width = len(rows[0])
            normalized = tuple(
                tuple((row + ("",) * width)[:width])
                for row in rows
            )
            blocks.append(Block("table", rows=normalized))
            continue
        if stripped.startswith(("- ", "* ", "+ ")):
            items = []
            while index < len(lines) and lines[index].strip().startswith(("- ", "* ", "+ ")):
                items.append(lines[index].strip()[2:].strip())
                index += 1
            blocks.append(Block("bullets", items=tuple(items)))
            continue
        numbered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if numbered:
            items = []
            while index < len(lines):
                match = re.match(r"^\d+\.\s+(.+)$", lines[index].strip())
                if not match:
                    break
                items.append(match.group(1).strip())
                index += 1
            blocks.append(Block("numbers", items=tuple(items)))
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            next_line = lines[index]
            if _is_block_start(next_line, lines[index + 1] if index + 1 < len(lines) else ""):
                break
            paragraph_lines.append(next_line.strip())
            index += 1
        blocks.append(Block("paragraph", " ".join(paragraph_lines)))
    return blocks


INLINE_PATTERN = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*]+\*|\[[^\]]+\]\([^)]+\))")


def add_inline_runs(
    paragraph,
    text: str,
    *,
    font: str = BODY_FONT,
    size: float = 10.5,
    color: str = BLACK,
) -> None:
    for token in INLINE_PATTERN.split(text):
        if not token:
            continue
        bold = italic = False
        code = False
        value = token
        if token.startswith("**") and token.endswith("**"):
            value, bold = token[2:-2], True
        elif token.startswith("`") and token.endswith("`"):
            value, code = token[1:-1], True
        elif token.startswith("*") and token.endswith("*"):
            value, italic = token[1:-1], True
        elif token.startswith("[") and "](" in token:
            value = token[1 : token.index("]")]
        run = paragraph.add_run(value)
        set_run_font(
            run,
            CODE_FONT if code else font,
            size - 0.5 if code else size,
            bold=bold,
            italic=italic,
            color=color,
        )


def add_caption(doc: Document, label: str, text: str, *, keep_with_next: bool = False) -> None:
    paragraph = doc.add_paragraph(style="Caption")
    paragraph.paragraph_format.keep_with_next = keep_with_next
    set_run_font(paragraph.add_run(f"{label}. "), BODY_FONT, 8.5, bold=True)
    add_inline_runs(paragraph, text, size=8.5)


def parse_width(value: str, content_width) -> Any:
    value = value.strip().lower()
    if not value:
        return int(content_width * 0.92)
    if value.endswith("%"):
        return int(content_width * float(value[:-1]) / 100.0)
    if value.endswith("in"):
        return Inches(float(value[:-2]))
    if value.endswith("cm"):
        return Cm(float(value[:-2]))
    if value.endswith("mm"):
        return Mm(float(value[:-2]))
    return Inches(float(value))


def add_figure(
    doc: Document,
    report_dir: Path,
    block: Block,
    figure_number: int,
) -> None:
    attrs = block.attrs or {}
    image_path = Path(os.path.abspath(report_dir / block.value))
    if not image_path.is_file():
        raise FileNotFoundError(f"Figure not found: {image_path}")
    caption = attrs.get("caption") or image_path.stem.replace("_", " ")
    width_text = ""
    for item in attrs.get("attrs", "").split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            if key.strip() == "width":
                width_text = value.strip()
    section = doc.sections[-1]
    content_width = section.page_width - section.left_margin - section.right_margin
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Pt(0)
    paragraph.paragraph_format.keep_with_next = True
    picture = paragraph.add_run().add_picture(str(image_path), width=parse_width(width_text, content_width))
    set_picture_alt(picture, f"Figure {figure_number}", caption)
    add_caption(doc, f"Figure {figure_number}", caption)


def add_data_table(
    doc: Document,
    rows: Sequence[Sequence[str]],
    table_number: int,
    caption: str,
) -> None:
    if not rows:
        return
    if caption:
        add_caption(doc, f"Table {table_number}", caption, keep_with_next=True)
    column_count = len(rows[0])
    table = doc.add_table(rows=len(rows), cols=column_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table, visible=True)
    section = doc.sections[-1]
    content_width = section.page_width - section.left_margin - section.right_margin
    column_width = int(content_width / max(column_count, 1))
    for column in table.columns:
        column.width = column_width
    for row_index, values in enumerate(rows):
        row = table.rows[row_index]
        prevent_row_split(row)
        if row_index == 0:
            repeat_header(row)
        for column_index, value in enumerate(values):
            cell = row.cells[column_index]
            cell.width = column_width
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            if row_index == 0:
                set_cell_shading(cell, NAVY)
            elif row_index % 2 == 0:
                set_cell_shading(cell, LIGHT_GRAY)
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = Pt(0)
            paragraph.paragraph_format.space_after = Pt(0)
            add_inline_runs(
                paragraph,
                value,
                font=HEAD_FONT if row_index == 0 else BODY_FONT,
                size=8.2,
                color="FFFFFF" if row_index == 0 else BLACK,
            )
    spacer = doc.add_paragraph()
    spacer.paragraph_format.first_line_indent = Pt(0)
    spacer.paragraph_format.space_after = Pt(0)


def render_blocks(doc: Document, report_dir: Path, blocks: Iterable[Block], *, allow_pending: bool) -> None:
    table_number = 0
    figure_number = 0
    pending_table_caption = ""
    for block in blocks:
        if block.kind == "pagebreak":
            doc.add_page_break()
        elif block.kind == "heading":
            level = int((block.attrs or {}).get("level", "1"))
            if level == 1 and block.value.strip().lower() in {"abstract", "摘要"}:
                paragraph = doc.add_paragraph(block.value, style="Abstract Title")
            else:
                paragraph = doc.add_heading(block.value, level=level)
                for run in paragraph.runs:
                    set_run_font(run, HEAD_FONT, {1: 14, 2: 11.5, 3: 10.5}[level], bold=True, color=NAVY if level < 3 else BLACK)
        elif block.kind == "paragraph":
            if PENDING_PATTERN.search(block.value) and not allow_pending:
                raise ValueError(f"Unresolved pending marker: {block.value}")
            paragraph = doc.add_paragraph()
            add_inline_runs(paragraph, block.value)
        elif block.kind == "bullets":
            for item in block.items:
                paragraph = doc.add_paragraph(style="List Bullet")
                paragraph.paragraph_format.first_line_indent = Pt(0)
                add_inline_runs(paragraph, item)
        elif block.kind == "numbers":
            for item in block.items:
                paragraph = doc.add_paragraph(style="List Number")
                paragraph.paragraph_format.first_line_indent = Pt(0)
                add_inline_runs(paragraph, item)
        elif block.kind == "code":
            for line in block.value.splitlines() or [""]:
                paragraph = doc.add_paragraph(style="Source Code")
                set_run_font(paragraph.add_run(line or " "), CODE_FONT, 7.4)
                paragraph.paragraph_format.keep_together = True
        elif block.kind == "equation":
            paragraph = doc.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = Pt(0)
            paragraph.paragraph_format.space_before = Pt(3)
            paragraph.paragraph_format.space_after = Pt(5)
            set_run_font(paragraph.add_run(block.value), BODY_FONT, 10.5, italic=True)
        elif block.kind == "table_caption":
            pending_table_caption = block.value
        elif block.kind == "table":
            table_number += 1
            add_data_table(doc, block.rows, table_number, pending_table_caption)
            pending_table_caption = ""
        elif block.kind == "image":
            figure_number += 1
            add_figure(doc, report_dir, block, figure_number)
        else:
            raise ValueError(f"Unsupported Markdown block: {block.kind}")


def validate_docx(path: Path, *, allow_pending: bool = False) -> dict[str, int]:
    findings: list[str] = []
    image_count = 0
    table_count = 0
    with ZipFile(path) as archive:
        document_xml = archive.read("word/document.xml").decode("utf-8")
        if "[PENDING:" in document_xml and not allow_pending:
            findings.append("DOCX still contains a pending marker.")
        image_count = document_xml.count("<w:drawing>")
        table_count = document_xml.count("<w:tbl>")
        doctree = ET.fromstring(document_xml.encode("utf-8"))
        namespace = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        }
        for doc_pr in doctree.findall(".//wp:docPr", namespace):
            if not (doc_pr.get("descr") or doc_pr.get("title")):
                findings.append("A DOCX image is missing alternative text.")
                break
        for table in doctree.findall(".//w:tbl", namespace):
            if table.find(".//w:tblHeader", namespace) is None:
                findings.append("A DOCX table is missing a repeating header row.")
                break
    if findings:
        raise ValueError(" ".join(findings))
    return {"images": image_count, "tables": table_count}


def build_docx(
    report_dir: Path,
    config: dict[str, Any],
    content_path: Path,
    output_path: Path,
    cover_assets: tuple[Path, Path],
    *,
    allow_pending: bool = False,
) -> dict[str, int]:
    markdown = content_path.read_text(encoding="utf-8")
    if PENDING_PATTERN.search(markdown) and not allow_pending:
        raise ValueError("Report content still contains [PENDING: ...] markers.")
    blocks = parse_markdown(markdown)
    if not blocks:
        raise ValueError("Report content is empty.")

    doc = Document()
    configure_styles(doc)
    properties = doc.core_properties
    properties.title = str(config.get("title", "Laboratory Report"))
    properties.subject = str(config.get("course", "Laboratory Report"))
    properties.author = str(config.get("student", ""))
    properties.category = f"Lab {config.get('lab_number', '')}".strip()
    properties.keywords = "laboratory report; experiment; results; analysis"
    properties.comments = "Created with the NUIST lab-report skill."

    add_cover(doc, config, cover_assets)
    add_body_section(doc, config)
    render_blocks(doc, report_dir, blocks, allow_pending=allow_pending)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return validate_docx(output_path, allow_pending=allow_pending)
