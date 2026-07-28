"""Generate EXECUTIVE-DEMO-SPEECH.pdf from EXECUTIVE-DEMO-SPEECH.md."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "EXECUTIVE-DEMO-SPEECH.md"
PDF_PATH = ROOT / "EXECUTIVE-DEMO-SPEECH.pdf"

WINDOWS_FONTS = Path(r"C:\Windows\Fonts")


def strip_md_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2192", "->")
    return text


class DemoSpeechPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-14)
        self.set_font(self.font_family, "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def register_fonts(pdf: DemoSpeechPDF) -> str:
    regular = WINDOWS_FONTS / "arial.ttf"
    bold = WINDOWS_FONTS / "arialbd.ttf"
    italic = WINDOWS_FONTS / "ariali.ttf"
    if regular.is_file() and bold.is_file() and italic.is_file():
        pdf.add_font("ArialUni", "", str(regular))
        pdf.add_font("ArialUni", "B", str(bold))
        pdf.add_font("ArialUni", "I", str(italic))
        return "ArialUni"
    return "Helvetica"


def is_table_separator(line: str) -> bool:
    return line.strip().startswith("|") and re.match(r"^\|[\s\-:|]+\|$", line.strip())


def build_pdf() -> None:
    if not MD_PATH.is_file():
        print(f"Missing {MD_PATH}", file=sys.stderr)
        sys.exit(1)

    lines = MD_PATH.read_text(encoding="utf-8").splitlines()
    pdf = DemoSpeechPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(18, 18, 18)
    pdf.add_page()

    family = register_fonts(pdf)
    pdf.font_family = family
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    def write_block(style: str, size: int, text: str, lh: float = 5.5) -> None:
        pdf.set_font(family, style, size)
        pdf.set_text_color(30, 35, 50)
        pdf.multi_cell(page_width, lh, text)

    for raw in lines:
        line = raw.rstrip()
        if line == "---":
            pdf.ln(2)
            y = pdf.get_y()
            pdf.set_draw_color(210, 218, 228)
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(4)
            continue
        if is_table_separator(line):
            continue
        if line.startswith("# "):
            pdf.ln(2)
            write_block("B", 17, strip_md_inline(line[2:]), 8)
            pdf.ln(2)
            continue
        if line.startswith("## "):
            pdf.ln(3)
            write_block("B", 13, strip_md_inline(line[3:]), 7)
            pdf.ln(1)
            continue
        if line.startswith("### "):
            pdf.ln(2)
            write_block("B", 11, strip_md_inline(line[4:]), 6)
            pdf.ln(1)
            continue
        if line.startswith("|"):
            cells = [strip_md_inline(c.strip()) for c in line.split("|") if c.strip()]
            write_block("", 9, "  |  ".join(cells), 5)
            continue
        if line.startswith("- ") or line.startswith("* "):
            write_block("", 10, "  • " + strip_md_inline(line[2:]))
            continue
        if re.match(r"^\d+\.\s", line):
            write_block("", 10, "  " + strip_md_inline(line))
            continue
        if line.startswith(">"):
            quote = strip_md_inline(line.lstrip("> ").strip().strip('"'))
            pdf.set_text_color(60, 70, 90)
            write_block("I", 10, "    " + quote)
            pdf.set_text_color(30, 35, 50)
            continue
        if not line.strip():
            pdf.ln(2)
            continue
        write_block("", 10, strip_md_inline(line))

    pdf.output(str(PDF_PATH))
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
