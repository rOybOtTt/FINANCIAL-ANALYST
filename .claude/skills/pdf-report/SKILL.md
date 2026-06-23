---
name: pdf-report
description: Turn any analysis, report, summary, or outcome into a styled multi-page PDF (navy header band, tables, lists, page numbers) using md2pdf.py. Use this to DELIVER ANY SUBSTANTIVE OUTCOME to the user as a PDF instead of a long chat note — the user's standing preference is PDF deliverables, with the chat reply kept terse. Works for any topic, not just company analysis.
---

# /pdf-report — deliver outcomes as a PDF, not a chat note

The user's standing rule: **every substantive outcome is a PDF.** Don't dump long
analyses, reports, or summaries into the chat — write them to a `.md` and convert to a
clean PDF, then reply with a short pointer.

## Steps

1. **Write the outcome as Markdown.** Compose the full result as a `.md` file
   (headings, **bold**, tables, lists, fenced code/diagrams all render). Put it
   somewhere sensible:
   - company work → `targets/<TICKER>/<name>.md`
   - anything else → `reports/<slug>.md` (create `reports/` if needed).

2. **Convert to PDF:**
   ```bash
   python .claude/skills/pdf-report/md2pdf.py <input.md> <output.pdf> \
       --title "Short Title" --subtitle "one-line context · date · key number"
   ```
   - In PowerShell, escape `$` in the subtitle as `` `$ `` (e.g. `` spot `$209.91 ``).
   - Output goes next to the source, named clearly (e.g. `NVDA_full_report.pdf`).

3. **Reply terse.** Give ONLY a one-line summary (the headline / verdict) + the **PDF
   link**. The PDF is the deliverable. Don't paste the body into chat unless asked.

## When to use
- ANY time you'd otherwise write a long markdown answer or a multi-section result.
- For a quick company go/no-go specifically, use the **`screen`** skill (one-page PDF);
  for a full write-up or any other topic, use this one.

## Notes
- Renderer = PyMuPDF (`fitz`) + `markdown` — both already installed; no API key.
- Palette matches `amkr.pdf`: navy `#1F2D5A` header, blue `#1B6CB5` accents, page numbers.
- Multi-page with automatic reflow; tables get a navy header row.
- Tip: to bundle several markdown files into one PDF, concatenate them (with `---`
  separators) into a temp `.md` first, then convert.
