# SETUP — analyze any AI / deep-tech stock in a fresh project

**Goal:** copy this folder, run two commands once, then just tell Claude a stock
name. No Anthropic API key needed — only Claude Code.

---

## 1. Copy the folder
Copy this project into your new location / new VS Code workspace.

**Must keep** (the engine): all `*.py`, `CLAUDE.md`, `ANALYZE_COMPANY.md`,
`DECK_BLUEPRINT.md`, `README.md`, `requirements.txt`, `competitors.json`,
`reliable_sources.json`, `ir_sources.json`, and the `targets/` folder.

**Can delete to save ~290 MB** (AMKOR's old inputs, not needed): the `data/`
folder and `amkr.pdf`. Fresh data is re-pulled per company, and the deck style is
already written into `DECK_BLUEPRINT.md`.

## 2. One-time install (no API key)
```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 3. Open Claude Code in the folder and name a stock
> "Analyze **NVDA** as a long."
> "Run the workflow on **Vertiv**, I'm thinking short."
> "Pitch **Teradyne** — you decide long or short."

Claude reads `CLAUDE.md`, runs the data layer locally (Playwright, free), and
**plays the analyst desk itself** (Agents 04–08): debate → synthesis → senior
verdict → the 6 assignment answers + sensitivity matrix → Canva deck. Outputs land
in `targets/<TICKER>/`.

---

## What "the agent" is
The workflow is driven by **Claude in your session** — that's the agent. The folder
gives Claude the procedure (`CLAUDE.md` / `ANALYZE_COMPANY.md`), the deterministic
data tools (the `.py` scripts), and the deck blueprint. You supply the stock name;
Claude does the rest. **A Claude Code session must be open** — the folder doesn't run
itself (unless you add an API key for unattended/cron runs; see `CLAUDE.md`).

## Notes
- **No API key** for the normal flow — covered by your Claude subscription.
- Results aren't byte-identical run-to-run (LLM variation + live data move daily), but
  the structure and quality are the same each time.
- Switch/re-run anytime: `python run_company.py <TICKER> --side long|short --no-llm`.
- The original Amkor target is preserved at `targets/AMKR.json` (`python run_company.py AMKR --no-llm`).
