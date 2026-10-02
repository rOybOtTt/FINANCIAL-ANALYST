# MLCC sector — deliverables (2 Oct 2026)

| Deliverable | File |
|---|---|
| Live cycle dashboard | `mlcc_cycle_watch.html` (published as the MLCC Cycle Watch artifact) |
| Sector note (10 sections) | `MLCC_sector_deep_dive.md` / `.pdf` |
| Competitive deck (7 makers) | `MLCC_competitive_deck_v1_2.10.26.pptx` |
| Murata deep-dive | `murata/6981.T_deep_dive.md` / `.pdf` |
| Murata one-pager | `murata/6981.T_one_pager.pdf` |
| Murata house model | `murata/6981.T_model_v1_2.10.26.xlsx` (EV / 5-yr-mean EBITDA own band; verify with `python build/verify_model.py murata/6981.T_model_v1_2.10.26.xlsx`) |
| Murata pitch deck (Glilot approximation) | `murata/6981.T_pitch_deck_v1_2.10.26.pptx` |
| Peer one-pagers | `peers/<TICKER>/<TICKER>_one_pager.pdf` |
| Peer model | `peers/MLCC_peers_model_v1_2.10.26.xlsx` |
| Research folder | `research/` (memos 01-06, `companies/*.md`), `data/` |
| Working files | `MLCC_working_files.zip` |

Rebuild order: `build/prices.py` → `build/backtest.py` → `build/episodes.py` → `build/episodes2.py` → `build/dashboard_data.py` → `build/build_page.py`;
`build/murata_engine.py` → `build/build_murata_model.py` → `build/verify_model.py` → `build/charts.py` → `build/build_pitch_deck.py`, `build/build_comp_deck.py`, `build/build_peers_model.py`.
