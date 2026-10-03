I built an MLCC (multilayer ceramic capacitor) sector analysis in a cloud session. Pick it up from here.

WHERE IT LIVES
- GitHub: rOybOtTt/FINANCIAL-ANALYST, branch `claude/blissful-cori-dthz12` (PR #1). Everything is under `targets/MLCC/`.
- Start by reading `targets/MLCC/README.md`. It lists every deliverable and the order to rebuild them in.
- Live dashboard (artifact): MLCC Cycle Watch, https://claude.ai/artifact/Wed4dnNab5Y8UZ85j7wRhS. Its source is `targets/MLCC/mlcc_cycle_watch.html`, built from `build/page_template.html` plus `data/dashboard.json`.
- Get the files with: `git clone --branch claude/blissful-cori-dthz12 https://github.com/rOybOtTt/FINANCIAL-ANALYST` (or `git pull` if you already have it).

SCOPE AND MY DECISIONS (2 Oct 2026)
- Peer set:
  - Murata 6981.T (anchor)
  - Samsung Electro-Mechanics 009150.KS
  - Taiyo Yuden 6976.T
  - TDK 6762.T
  - Yageo 2327.TW
  - Kyocera 6971.T
  - Walsin 2492.TW
  - Fenghua and Three-Circle are tracked only as supply risk.
- Valuation method: EV / 5-yr-mean EBITDA against the company's own p25/median/p75 band, with no regime credit. This is the memory card D-M1 logic. P/B is a timing check only. This is a new layer rule for passives/MLCC; add it to the layer cards.
- Scope: Murata gets the full kit (research folder, deep-dive, one-pager, house model, pitch deck). Peers get the lighter kit (research file, one-pager, a tab in the peer model). All seven share one competitive deck.
- Glilot deck: approximated with `build/deck_kit.py` because the cloud session couldn't see the G: drive. Re-skin it with the real `presentation_blueprint.md`, `deck_kit.py` and house template.

KEY RESULTS
- Cycle score is 18.5/100, "upcycle intact": 7 signals green, 5 amber, 0 red. Fundamentals are mid upcycle; the stocks have already had their late-cycle wobble.
  - Murata MLCC book-to-bill is 1.47, a record (the 2021 peak was 1.32).
  - Lead times are 14-20 weeks, against 8-10 normally.
  - SEMCO raised prices 30% and Yageo 50%. Murata still shows a -¥15bn price headwind.
- The equal-weight basket (Murata, SEMCO, Taiyo Yuden, Yageo, Walsin) is 36% below its Jun-2026 high.
- Backtest: buying the basket 35% below a cycle peak was positive at 24 months in 6 of 6 cycles since 2000 (median +44%). At 12 months it was a coin toss (median +6%, worst -42% in 2007).
- Murata (¥8,467):
  - EV / 5-yr-mean EBITDA is 31.4x, against an own band of 10.4 / 11.6 / 13.5x.
  - Probability-weighted present value is ¥4,140 (Bear 2,937 / Base 4,094 / Bull 5,435). Entry for a 20% IRR is ¥2,844.
  - The price needs a ~21x exit multiple to break even.
  - Verdict WATCH: stage in at ¥6,200 / ¥5,000 / ¥4,100 while book-to-bill stays above 1.0.
- Ranked shortlist:
  1. Walsin: worth a look
  2. Taiyo Yuden: worth a look
  3. Murata: watch
  4. Yageo: watch (decide after the 27 Oct inventory read)
  5. SEMCO: pass (~65x mean EBITDA; short candidate)
  6. TDK: pass, not an MLCC play
  7. Kyocera: pass, not an MLCC play
- Next catalysts:
  - Yageo/Walsin September revenue, ~8-9 Oct
  - Yageo 3Q, 27 Oct
  - SEMCO and Murata 2Q, ~29-30 Oct
  - Japanese 1Q27 price decisions, Nov-Dec

FILES
- `MLCC_sector_deep_dive.md/.pdf` (10 sections)
- `MLCC_competitive_deck_v1_2.10.26.pptx`
- `murata/`:
  - `6981.T_deep_dive.md/.pdf`
  - `6981.T_one_pager.pdf`
  - `6981.T_model_v1_2.10.26.xlsx` (check it with `python build/verify_model.py murata/6981.T_model_v1_2.10.26.xlsx`; it must print PASS)
  - `6981.T_pitch_deck_v1_2.10.26.pptx`
- `peers/<TICKER>/*_one_pager.pdf` and `peers/MLCC_peers_model_v1_2.10.26.xlsx`
- `research/`:
  - 01 demand
  - 02 capacity
  - 03 cycle history
  - 05 financials
  - 06 consensus
  - `companies/*.md`
- `data/clean/`:
  - `murata_history.csv` (FY3/2012-26 from fact books)
  - financials, consensus, prices
  - backtest CSVs

OPEN TASKS FOR YOU (THE LOCAL SESSION)
1. Read every report in `G:\Shared drives\Glilot HF\Roy\Analysts\Semis\mlcc sell-side`. I'm asking you to do this myself; it was blocked earlier only because the request came from the other session.
   - Write `targets/MLCC/research/raw/sellside_extract.md` with one section per report: broker, analyst, date, name covered, rating, target price and method, FY1-FY3 estimates, MLCC market numbers (capacity, share, utilization, prices, lead times, inventory, AI-server content), cycle view, and bull/bear points.
   - Paraphrase only, with no passages over ~15 words, and never copy the PDFs into the repo.
   - Check that the GitHub repo is private before pushing.
2. Reconcile the sell-side numbers against `research/02_capacity_share_supply.md`, `research/03_cycle_history_and_indicators.md` and the Murata model inputs. Where they conflict, show both side by side. Then update §8 (consensus vs variant) of `MLCC_sector_deep_dive.md` and the Murata deep-dive.
3. Re-skin both decks with the real Glilot template and `deck_kit`.
4. Run `financial-forensics` and `management-assessment` on Murata, SEMCO and Taiyo Yuden (§6 of the sector note was not done).
5. Rebuild and republish the dashboard to the SAME artifact URL above (pass it as `url`).
6. Commit and push to branch `claude/blissful-cori-dthz12`.

DATA CAVEATS
- Most 2026 operating figures come from press and aggregators, tagged [A] (TrendForce, passive-components.eu, BigGo). Murata's fact-book and 1Q figures are primary, tagged [F].
- No maker publishes capacity, so June-2026 shipments are the proxy: Murata 140bn, SEMCO 98bn, Taiyo Yuden 40bn pcs/month.
- Peers have only 4 years of history, so their valuation uses Murata's band as a proxy.
- Murata's MLCC price-hike letter is unconfirmed.
