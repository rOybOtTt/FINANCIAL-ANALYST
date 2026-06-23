# targets/ — one folder, every company you analyze

Each company you analyze is a **target**. This folder holds the saved presets and
the per-company outputs.

## Files
| Path | What it is |
|---|---|
| `_current.json` | The **active** target. Every analyst (`target_config.load_target()`) reads this. Written by `run_company.py`. |
| `<TICKER>.json` | A **saved preset** — peers, side, sector, one-liner, thesis question, and curated `deck_topics`. Edit this to tune a company, then re-run. |
| `<TICKER>/research_topics.txt` | The deck-headline topics that were deep-researched (by `tech_agent.py --batch`). |
| `<TICKER>/research/*.md` | Your free-form per-headline deep dives. |
| `<TICKER>/analysis/` | `debate.md`, `synthesis.md`, `verdict.md` from the LLM desk. |
| `<TICKER>/ASSIGNMENT_ANSWERS.md`, `model.xlsx` | The final deliverables. |

## How presets work (precedence)
When you run `python run_company.py <TICKER> ...`, each setting is resolved as:

> **explicit CLI flag  >  saved `targets/<TICKER>.json` preset  >  auto (peer_map / templates)**

So you can seed a company once (peers + curated topics), and every later run reuses
it unless you override on the command line.

## Preset schema
```jsonc
{
  "ticker": "NVDA",
  "name": "NVIDIA Corporation",
  "side": "long",                       // long | short | auto
  "sector": "ai-compute",               // a bucket from peer_map.py (python peer_map.py)
  "sector_label": "AI compute / accelerators",
  "one_liner": "...",                   // the title-slide hook
  "thesis_question": "...",             // drives the analyst debate + senior verdict
  "peers": [ { "ticker": "AMD", "name": "...", "role": "competitor" }, ... ],
  "deck_topics": [ "...", ... ]         // optional; overrides the generic headline templates
}
```

## Seeded presets
- **`AMKR.json`** — the original Amkor cohort (auto-archived so the first company is never lost). Re-run with `python run_company.py AMKR`.
- **`NVDA.json`** — the first AI test case (NVIDIA, long), with a curated AI-compute peer set and 10 NVIDIA-specific research topics.

To add a new one: `python run_company.py <TICKER> --side long|short` (auto-builds a
preset), or copy `NVDA.json`, rename it, and edit.
