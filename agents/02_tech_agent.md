# Agent 02 — Tech Agent

**Status:** ✅ Built and tested (live)
**Script:** [`../tech_agent.py`](../tech_agent.py)
**Paired validator:** [Agent 02b — Source Validator](02b_source_validator.md)
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

Answer **technology questions from a tech perspective** and return research /
reports **only from reliable sources**. Use it whenever you want the tech angle
on something (a packaging method, a process node, a material, an architecture).

## When it "activates"

Run it with a topic — that *is* the activation:

```bash
python tech_agent.py "advanced semiconductor packaging 2.5D"
python tech_agent.py "glass core substrates" --max 8
python tech_agent.py "chiplets" --web              # also sweep the open web (Bing)
python tech_agent.py "HBM4 bandwidth" --force-playwright
```

| Flag | Meaning | Default |
|------|---------|---------|
| `--max N` | Max reliable sources to keep | 6 |
| `--web` | Also sweep Bing via the browser (noisy; validator filters it) | off |
| `--force-playwright` | Use the real browser from the start | off |

## How it works (4 stages)

1. **Discover** — through curated, no-key indexes that don't bot-block:
   - **arXiv API** — peer-reviewed-adjacent preprints.
   - **Crossref API** — journal / publisher articles (by DOI).
   - *(optional `--web`)* Bing via Playwright for tier-2 journalism.
   Channels are **interleaved** so no single source crowds out the others.
2. **Scrape** — fetch each candidate page. `urllib` first; **falls back to a
   real Chromium browser (Playwright)** automatically when a site blocks it
   (this is the "scrape with Playwright" requirement). DOI links are followed to
   their real publisher domain (e.g. `doi.org → link.springer.com`).
3. **Validate** — every candidate goes through the **Source Validator (02b)**.
   Only `RELIABLE` / `BORDERLINE` sources survive; `UNRELIABLE` ones are dropped.
4. **Write** — a report under `data/tech/<topic-slug>/`.

## Why not just scrape Google/Bing?

We tried — search engines bot-block and serve junk/CAPTCHA to scripts (Bing even
returned base64-wrapped redirect links and off-topic results). The scholarly
APIs are reliable, return clean metadata, and are themselves a reliability
signal. Bing is kept only as an opt-in (`--web`) sweep, fully filtered by 02b.

## Output

```
data/tech/<topic-slug>/
  report.md        # human-readable: title, source, tier, reliability score, URL, summary
  findings.json    # machine-readable list of kept sources
```

## Reliable-source registry

Both this agent and the validator read [`../reliable_sources.json`](../reliable_sources.json)
— a curated list of trusted domains (arXiv, IEEE, ACM, Nature, MIT Tech Review,
Ars Technica, Gartner, McKinsey, plus semiconductor-specific: SemiEngineering,
SemiAnalysis, EE Times, Yole, TrendForce). **Edit that file to add/remove sources.**

## Verified runs

- `"advanced semiconductor packaging chiplets 2.5D"` → 5 arXiv tier-1 sources (score 100).
- `"semiconductor wafer level packaging fan-out"` → mix of arXiv preprints and
  SpringerLink journal chapters (DOIs resolved + validated), all reliable.

## Future tweaks

- Add Semantic Scholar as a third scholarly channel.
- Pull full-text / PDF for deeper extraction instead of meta-summary only.
- Add a domain-specific channel for SemiEngineering / EE Times article search.
