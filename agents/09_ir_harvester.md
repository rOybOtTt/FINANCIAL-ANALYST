# Agent 09 — IR Harvester

**Status:** ✅ Built and tested (live)
**Script:** [`../ir_agent.py`](../ir_agent.py)
**Config:** [`../ir_sources.json`](../ir_sources.json)
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

Get reports & investor presentations for companies that **don't file with the
SEC** (so Agent 01/EDGAR can't reach them) by scraping their Investor-Relations
websites with **Playwright** and downloading the document PDFs.

Default targets (in `ir_sources.json`): **JCET, Powertech, Samsung**.
*(SPIL is omitted — it merged into ASE in 2018, so ASE's SEC filings cover it.)*

## How it works

1. Loads each company's `seed_urls` with a real Chromium browser.
2. Collects every link; keeps **document links** (`.pdf/.docx/.pptx/...`) and
   **follows one level** into investor/report sub-pages (e.g. JCET's per-year
   financial-reports pages).
3. **Filters to the last-year window** (current year + previous) — handles
   `YYYYMMDD` filenames, so Samsung's 15-year archive is trimmed to recent only.
4. Downloads the PDFs (browser-grade requests) to `data/ir/<slug>/`.

## Usage

```bash
python ir_agent.py                 # all companies in ir_sources.json
python ir_agent.py samsung jcet    # only these (slug or name)
python ir_agent.py --max 12        # cap docs per company
python ir_agent.py --list          # discover/list candidate links only (no download)
```

## Output

```
data/ir/<slug>/
  <document>.pdf      # downloaded investor docs (annual reports, presentations, earnings releases)
  links.json          # ALL candidate links found (for transparency / fixing seed_urls)
  manifest.json       # what was downloaded
```

## Verified run

- **JCET** → 7 docs (earnings press releases incl. Q4 & Full-Year 2025, Q1 2026).
- **Samsung** → 12 docs (2025 quarterly conference decks in English + interim reports).
- **Powertech** → investor-conference briefing decks (the agent learned its
  `.ashx` download-handler URLs; downloads are verified as real PDFs via magic
  bytes). Note: its annual report is chapter-split and not year-tagged in links,
  so precise last-year-only filtering on annual chapters is imperfect — the
  conference presentations come through cleanly.

## Reality / limitations

IR sites vary wildly — some block bots, some render documents via JS (Powertech),
some are in local languages. This is a **best-effort** harvester:
- If a site yields little, fix its `seed_urls` in `ir_sources.json`, or
- Download the PDFs manually into `uploads/` and let **Agent 08 (Challenger)**
  read them natively.

## Feeding the analysts

The harvested PDFs live in `data/ir/<slug>/`. To analyze them, point **Agent 08**
at them (`--files data/ir/samsung/2025_4Q_conference_eng.pdf ...`) or copy them
into `uploads/`. (A future tweak could fold `data/ir/` into the shared data brief
automatically.)
