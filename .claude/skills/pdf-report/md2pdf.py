# -*- coding: utf-8 -*-
"""Convert a Markdown file to a styled, multi-page PDF (amkr.pdf palette).

Usage:
  python md2pdf.py <input.md> <output.pdf> [--title "..."] [--subtitle "..."]

Renders headings/tables/lists/code with a navy running header + page numbers.
Dependency-light: PyMuPDF (fitz) + markdown — both already in this repo's env.
"""
import sys, os, argparse
import markdown as mdlib
import fitz

NAVY=(31/255, 45/255, 90/255); BLUE=(27/255, 108/255, 181/255)
LBLUE=(0.78, 0.85, 0.94); GRAY=(0.42, 0.42, 0.42); FOOT=(0.96, 0.972, 0.99)

CSS = """
* { font-family: sans-serif; }
body { font-size: 10.5px; color: #222222; }
h1 { color: #1F2D5A; font-size: 18px; margin-top: 6px; margin-bottom: 4px;
     border-bottom: 2px solid #1B6CB5; padding-bottom: 3px; }
h2 { color: #1F2D5A; font-size: 14px; margin-top: 13px; margin-bottom: 4px; }
h3 { color: #1B6CB5; font-size: 12px; margin-top: 10px; margin-bottom: 3px; }
h4 { color: #1B6CB5; font-size: 11px; margin-top: 8px; margin-bottom: 2px; }
p  { margin-top: 4px; margin-bottom: 4px; }
strong { color: #1F2D5A; }
em { color: #444444; }
li { margin-top: 2px; margin-bottom: 2px; }
table { border: 1px solid #cccccc; border-collapse: collapse; margin-top: 6px; margin-bottom: 8px; }
th { background-color: #1F2D5A; color: #ffffff; padding: 4px 6px; font-size: 9px; text-align: left; }
td { border: 1px solid #d6d6d6; padding: 3px 6px; font-size: 9px; }
code { font-family: monospace; background-color: #eef2f9; font-size: 9px; }
pre  { background-color: #f4f8fe; padding: 6px; font-size: 7.5px; }
blockquote { border-left: 3px solid #1B6CB5; color: #555555; padding-left: 8px; }
hr { border: 0; border-top: 1px solid #d5d6ee; }
a { color: #1B6CB5; }
img { width: 92%; }
"""

def md_to_pdf(md_path, out_path, title="Report", subtitle="", assets=None):
    text = open(md_path, encoding="utf-8").read()
    body = mdlib.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    html = f"<html><body>{body}</body></html>"

    MED = fitz.paper_rect("letter")
    WHERE = fitz.Rect(54, 84, MED.width - 54, MED.height - 40)
    # archive lets <img src="relative/path"> resolve (default: the source md's folder)
    root = assets or os.path.dirname(os.path.abspath(md_path)) or "."
    story = fitz.Story(html=html, user_css=CSS, archive=fitz.Archive(root))
    writer = fitz.DocumentWriter(out_path)
    more = 1
    while more:
        dev = writer.begin_page(MED)
        more, _ = story.place(WHERE)
        story.draw(dev)
        writer.end_page()
    writer.close()

    # second pass: stamp navy header band + footer page numbers
    doc = fitz.open(out_path)
    n = doc.page_count
    for i, page in enumerate(doc):
        page.draw_rect(fitz.Rect(0, 0, MED.width, 66), color=NAVY, fill=NAVY)
        page.draw_rect(fitz.Rect(0, 66, MED.width, 69), color=BLUE, fill=BLUE)
        page.insert_textbox(fitz.Rect(54, 14, MED.width - 54, 42), title,
                            fontsize=15, fontname="hebo", color=(1, 1, 1))
        if subtitle:
            page.insert_textbox(fitz.Rect(54, 42, MED.width - 54, 60), subtitle,
                                fontsize=8.5, fontname="helv", color=LBLUE)
        page.draw_rect(fitz.Rect(0, MED.height - 26, MED.width, MED.height), color=FOOT, fill=FOOT)
        page.insert_textbox(fitz.Rect(54, MED.height - 22, MED.width - 54, MED.height - 8),
                            f"{title}   ·   page {i+1} of {n}",
                            fontsize=8, fontname="helv", color=GRAY, align=1)
    doc.saveIncr()
    doc.close()
    return out_path, n

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--title", default="Report"); ap.add_argument("--subtitle", default="")
    ap.add_argument("--assets", default=None, help="image archive root (default: input md's folder)")
    a = ap.parse_args()
    out, pages = md_to_pdf(a.inp, a.out, a.title, a.subtitle, a.assets)
    print(f"wrote {out}  ({pages} pages)")
