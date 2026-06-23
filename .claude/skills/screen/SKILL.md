---
name: screen
description: Produce a one-page PDF "is this company worth a look?" screen for any company or ticker. A points-only go/no-go with a clear verdict chip (WORTH A LOOK / WATCH / PASS), bull vs bear points, the single driver to watch, a valuation snapshot, an entry note, and what would flip the call. Use this whenever the user names a company and wants a quick worth-a-look read delivered as a PDF — NOT a full deck, model, or long in-chat write-up. The user's standing preference is: deliver the PDF and keep the chat reply terse.
---

# /screen — one-page PDF go/no-go on a company

Goal: a fast, decisive, **points-only** screen answering one question — *is this
company worth a deeper look, yes or no?* — delivered as a **one-page PDF**. This is a
triage screen, not the full `ANALYZE_COMPANY.md` deep dive.

## Steps

1. **Resolve the target.** Get the ticker (and company name) from the user's args.
   If they gave a name, map it to a ticker. If they gave nothing, ask for one.

2. **Get the data (no API key).** Look for `targets/<TICKER>/_brief.txt`.
   - If it exists and is fresh enough, reuse it.
   - Otherwise refresh the deterministic data layer:
     `python run_company.py <TICKER> --side auto --no-llm`
     then read `targets/<TICKER>/_brief.txt`. (Blocked scrapes auto-fall-back to
     Playwright; if a peer is wrong, re-run with `--peers`.)
   - Reuse any existing `targets/<TICKER>/analysis/*.md` if present — don't redo deep work.

3. **Screen it in-session (be decisive).** From the brief's fundamentals + market +
   sell-side + news, form a crisp bull read, a crisp bear read, and a valuation
   snapshot. Identify the **single technical/structural driver** that most decides the
   outcome. Tag every load-bearing number **[FACT]** (in the brief) / **[EST]** /
   **[ATTRIBUTED]**. Then pick ONE verdict:
   - **WORTH A LOOK** — quality + setup justify a deep dive (note the lean: long/short).
   - **WATCH** — interesting but gated on a trigger/price; not now.
   - **PASS** — fails on quality, valuation, or a broken driver.

4. **Assemble the JSON** (this exact schema) and write it to a temp file
   `targets/<TICKER>/_screen.json`:
   ```json
   {
     "ticker": "NVDA",
     "name": "NVIDIA Corporation",
     "asof": "2026-06-22",
     "price": "$209.91",
     "verdict": "WORTH A LOOK",
     "stance": "LONG-biased, two-sided",
     "thesis": "one-line thesis (<=110 chars works best)",
     "bull": ["4-6 crisp points, each tagged", "..."],
     "bear": ["4-6 crisp points, each tagged", "..."],
     "driver": "the single driver to watch (1 sentence)",
     "valuation": "P/E, PEG, cohort rank, etc.",
     "entry": "level / IRR / how to express it",
     "risk": "what would flip the verdict",
     "footnote": "data as-of, source, the key caveat"
   }
   ```
   Keep bullets short (they wrap at ~52 chars/column). 4–6 per side fits one page.

5. **Render the PDF:**
   ```bash
   python .claude/skills/screen/make_screen_pdf.py targets/<TICKER>/_screen.json targets/<TICKER>/<TICKER>_screen.pdf
   ```
   The renderer uses the `amkr.pdf` palette (navy `#1F2D5A`, pale `#F4F8FE`, green/amber/red
   verdict chip) and is dependency-light (matplotlib only).

6. **Reply terse.** In chat, give ONLY: the **verdict + one-line why** and the **PDF
   path** (as a clickable link). The PDF is the deliverable — do not dump the full
   analysis into the chat unless the user explicitly asks. Offer the full deep dive
   (`ANALYZE_COMPANY.md` / deck) as an optional next step.

## Notes
- One page only. If bullets overflow, tighten them — don't spill to page 2.
- Verdict chip color is automatic: PASS/SHORT/AVOID → red, WATCH → amber, else green.
- No `ANTHROPIC_API_KEY` needed — data layer is deterministic Python; the screen
  reasoning is done in-session.
