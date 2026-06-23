"""
Deep-Tech Analyst - One-Command Orchestrator
============================================

Point the WHOLE pipeline at any AI / deep-tech company, LONG or SHORT, with one
command. This is the generalized version of senior_analyst.py: it auto-builds a
peer set, refreshes the no-API-key data layer, deep-researches the deck headlines,
and (with an API key) runs the analyst debate -> synthesis -> senior verdict.

USAGE
-----
  python run_company.py NVDA --side long
  python run_company.py VRT  --side long  --sector data-center-infra
  python run_company.py AMD  --side short --peers NVDA INTC AVGO TSM
  python run_company.py NVDA --no-llm           # data + research only (no API key needed)
  python run_company.py NVDA --dry-run          # just write config + research plan, no network
  python run_company.py AMKR                    # re-run the original Amkor target

WHAT IT PRODUCES
----------------
  targets/<TICKER>.json              the saved target (peers, sector, side, topics)
  targets/_current.json              the active target (read by every analyst)
  competitors.json                   regenerated cohort for the market/news agents
  data/<TICKER>/, data/market/...    refreshed filings, fundamentals, market, news
  data/tech/<slug>/                  scholarly deep-research per deck headline
  targets/<TICKER>/research_topics.txt   the headline topic list that was researched
  targets/<TICKER>/analysis/         debate.md, synthesis.md, verdict.md (LLM stage)

After it runs, follow ANALYZE_COMPANY.md to answer the assignment questions and
build the Canva deck from DECK_BLUEPRINT.md.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

import peer_map
import target_config as tc

HERE = os.path.dirname(os.path.abspath(__file__))
COMPETITORS = os.path.join(HERE, "competitors.json")
TARGETS_DIR = os.path.join(HERE, "targets")


def _slugify(text):
    # must match tech_agent.slugify so tech_filter lines up with data/tech/<slug>
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


# --------------------------------------------------------------------------
# Deck-headline research topics (parameterized from amkr.pdf's structure)
# --------------------------------------------------------------------------

TOPIC_TEMPLATES = [
    "{name} core product architecture and the key engineering choice that creates a technical moat",
    "{sector} value chain: upstream suppliers and downstream customers",
    "{name} end markets total addressable market size and growth CAGR forecast",
    "{name} competitive landscape and main competitors technology comparison",
    "{name} technology roadmap and next-generation products",
    "{sector} pricing trends average selling price and unit volume (PxQ economics)",
    "{name} manufacturing supply chain capacity and geographic footprint",
    "{name} gross margin and cost structure drivers",
    "{sector} demand drivers AI data center capital expenditure",
    "bear case and key technical risks for {name}",
]


def build_topics(target):
    if target.get("deck_topics"):
        topics = list(target["deck_topics"])
    else:
        topics = [t.format(name=target["name"], sector=target["sector_label"])
                  for t in TOPIC_TEMPLATES]
    return topics


# --------------------------------------------------------------------------
# Config writing
# --------------------------------------------------------------------------

def archive_amkr_once():
    """Preserve the original Amkor competitors.json as targets/AMKR.json so the
    Amkor target is never lost when competitors.json gets regenerated."""
    amkr_preset = os.path.join(TARGETS_DIR, "AMKR.json")
    if os.path.isfile(amkr_preset) or not os.path.isfile(COMPETITORS):
        return
    try:
        with open(COMPETITORS, encoding="utf-8") as f:
            cfg = json.load(f)
        if (cfg.get("our_company") or "").upper() != "AMKR":
            return
        peers = [c for c in cfg.get("companies", []) if c.get("role") != "us"]
        preset = dict(tc.AMKR_DEFAULT)
        preset["peers"] = [{"ticker": c["ticker"], "name": c.get("name", c["ticker"]),
                            "role": "competitor"} for c in peers]
        os.makedirs(TARGETS_DIR, exist_ok=True)
        with open(amkr_preset, "w", encoding="utf-8") as f:
            json.dump(preset, f, indent=2)
        print(f"[setup] archived original Amkor cohort -> targets/AMKR.json")
    except (OSError, json.JSONDecodeError, KeyError):
        pass


def write_competitors(target):
    """Regenerate competitors.json = the active target + its peers, so the
    Market (03) and News (03c) agents pick up the right cohort with no edits."""
    companies = [{"ticker": target["ticker"], "name": target["name"], "role": "us"}]
    companies += [{"ticker": p["ticker"], "name": p["name"], "role": "competitor"}
                  for p in target["peers"]]
    cfg = {
        "_comment": f"AUTO-GENERATED by run_company.py for target {target['ticker']}. "
                    "Re-run run_company.py to switch targets. Saved presets live in targets/.",
        "our_company": target["ticker"],
        "companies": companies,
    }
    with open(COMPETITORS, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


# --------------------------------------------------------------------------
# Subprocess helpers
# --------------------------------------------------------------------------

def run_step(label, argv):
    print(f"\n{'='*70}\n[run] {label}\n  $ python {' '.join(argv)}\n{'='*70}")
    try:
        subprocess.run([sys.executable] + argv, cwd=HERE, check=False)
        return True
    except Exception as e:
        print(f"[!] {label} failed: {e}")
        return False


# --------------------------------------------------------------------------
# Main flow
# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Deep-Tech Analyst - analyze any AI/deep-tech company.")
    p.add_argument("company", help="Ticker or company name (e.g. NVDA, 'NVIDIA').")
    p.add_argument("--side", default=None, choices=tc.VALID_SIDES, help="long | short | auto (default: preset or auto).")
    p.add_argument("--sector", default=None, help="Force a sector bucket (see: python peer_map.py).")
    p.add_argument("--peers", nargs="*", default=None, help="Override peer tickers.")
    p.add_argument("--name", default=None, help="Override the company display name.")
    p.add_argument("--question", default=None, help="Override the thesis question driving the debate.")
    p.add_argument("--news", type=int, default=6, help="News items per company (default 6).")
    p.add_argument("--max-tech", type=int, default=6, help="Reliable sources per tech topic (default 6).")
    p.add_argument("--rounds", type=int, default=1, help="Debate rebuttal rounds (default 1).")
    p.add_argument("--effort", default="high", help="LLM effort low|medium|high|xhigh|max (default high).")
    p.add_argument("--no-llm", action="store_true", help="Data + research only; skip the analyst LLM stage.")
    p.add_argument("--skip-tech", action="store_true", help="Skip the per-headline scholarly research.")
    p.add_argument("--skip-data", action="store_true", help="Skip EDGAR/market/news refresh (use existing data).")
    p.add_argument("--dry-run", action="store_true", help="Write config + research plan only; no network, no API.")
    args = p.parse_args()

    ticker = args.company.strip().upper()

    # precedence everywhere: explicit CLI flag  >  saved preset  >  auto default
    preset = tc.load_preset(ticker) or {}
    conf = "high"

    # 1) build the peer set ------------------------------------------------
    if args.peers:
        peers = [{"ticker": tk.upper(), "name": peer_map.name_for(tk) or tk.upper(),
                  "role": "competitor"} for tk in args.peers]
        _, slug, label, _ = peer_map.peers_for(ticker, args.sector)
    elif preset.get("peers"):
        peers = preset["peers"]
        slug = preset.get("sector")
        label = preset.get("sector_label")
    else:
        peers, slug, label, conf = peer_map.peers_for(ticker, args.sector)

    sector = args.sector or preset.get("sector") or slug
    sector_label = (peer_map.list_sectors().get(args.sector) if args.sector else None) \
        or label or preset.get("sector_label") or "the deep-tech / semiconductor sector"
    side = args.side or preset.get("side") or "auto"
    name = args.name or preset.get("name") or peer_map.name_for(ticker) or ticker

    # 2) assemble + save the target ---------------------------------------
    target = tc._normalize({
        "ticker": ticker,
        "name": name,
        "side": side,
        "sector": sector,
        "sector_label": sector_label,
        "one_liner": preset.get("one_liner", ""),
        "thesis_question": args.question or preset.get("thesis_question") or (
            f"Is {name} ({ticker}) a {('long' if side=='long' else 'short' if side=='short' else 'long, short, or pass')} "
            f"at today's price? Identify the single technical driver that most moves the valuation, "
            f"and state an entry price and expected IRR/ROI."),
        "peers": peers,
        "deck_topics": preset.get("deck_topics", []),
    })

    topics = build_topics(target)
    target["deck_topic_slugs"] = [_slugify(t) for t in topics]

    archive_amkr_once()
    os.makedirs(os.path.join(TARGETS_DIR, ticker), exist_ok=True)
    tc.save_current(target)
    with open(os.path.join(TARGETS_DIR, f"{ticker}.json"), "w", encoding="utf-8") as f:
        json.dump(target, f, indent=2)
    write_competitors(target)

    topics_path = os.path.join(TARGETS_DIR, ticker, "research_topics.txt")
    with open(topics_path, "w", encoding="utf-8") as f:
        f.write(f"# Deck-headline research topics for {name} ({ticker})\n")
        f.write("# one topic per line; researched by tech_agent.py --batch\n\n")
        f.write("\n".join(topics) + "\n")

    print(f"\nTARGET   : {name} ({ticker})")
    print(f"SIDE     : {target['side']}")
    print(f"SECTOR   : {target['sector']}  ({target['sector_label']})"
          + ("   [low-confidence peer match - consider --peers]" if conf == "low" else ""))
    print(f"PEERS    : {', '.join(p['ticker'] for p in peers) or '(none)'}")
    print(f"TOPICS   : {len(topics)} headline topics -> {os.path.relpath(topics_path, HERE)}")
    print(f"QUESTION : {target['thesis_question']}")

    if args.dry_run:
        print("\n[dry-run] config + research plan written. No network/API calls made.")
        print("Next: drop --dry-run to collect data, then follow ANALYZE_COMPANY.md.")
        return

    # 3) data layer (no API key) ------------------------------------------
    if not args.skip_data:
        all_tk = [ticker] + [p["ticker"] for p in peers]
        run_step("Data Agent 01 (EDGAR filings + fundamentals)",
                 ["data_agent.py", ticker] + [p["ticker"] for p in peers]
                 + ["--exhibits", "--smart-current"])
        run_step("Market Intel 03 (Yahoo+CNBC, cross-checked)",
                 ["market_agent.py", "--news", str(args.news)])
        run_step("News & Analyst Harvester 03c",
                 ["news_agent.py", "--news", str(max(args.news * 5, 20))])

    # 4) per-headline scholarly research ----------------------------------
    if not args.skip_tech:
        run_step("Tech Agent 02 (deep research on each deck headline)",
                 ["tech_agent.py", "--batch", topics_path, "--max", str(args.max_tech)])

    # 5) analyst LLM stage (needs ANTHROPIC_API_KEY) ----------------------
    if args.no_llm:
        print("\n[--no-llm] Skipping the analyst debate/synthesis/verdict stage.")
        _print_next_steps(target)
        return

    try:
        import analyst_common as ac
        import debate as dbt
        import synthesizer as synth
        import senior_analyst as senior

        q = target["thesis_question"]
        brief = ac.load_context(*tc.active_scope())
        print(f"\n{'='*70}\nANALYST DESK on {name} ({ticker})  -  brief {len(brief):,} chars\n{'='*70}")

        print("\n>>> Stage 1-2: DEBATE (Financial 04 vs Tech 05)")
        transcript = dbt.run_debate(q, brief, rounds=args.rounds, effort=args.effort, verbose=True)
        ttext = dbt.transcript_to_text(transcript)

        print("\n>>> Stage 3: SYNTHESIS (06)")
        synthesis = synth.synthesize(q, ttext, brief, effort=args.effort)
        print(synthesis)

        print("\n>>> Stage 4: SENIOR VERDICT (07)")
        verdict = senior.senior_verdict(q, ttext, synthesis, brief, effort=args.effort)
        print(verdict)

        adir = os.path.join(TARGETS_DIR, ticker, "analysis")
        os.makedirs(adir, exist_ok=True)
        _save(os.path.join(adir, "debate.md"), f"# Debate - {name} ({ticker})\n\n{ttext}")
        _save(os.path.join(adir, "synthesis.md"), f"# Synthesis - {name} ({ticker})\n\n{synthesis}")
        _save(os.path.join(adir, "verdict.md"), f"# Senior Verdict - {name} ({ticker})\n\n{verdict}")
        print(f"\nSaved analyst outputs -> {os.path.relpath(adir, HERE)}")
    except ac.NoApiKey as e:
        print(f"\n[!] {e}\n[i] Data + research are still saved. Set the key and re-run, "
              "or use --no-llm to skip this stage.")
    finally:
        _print_next_steps(target)


def _save(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _print_next_steps(target):
    print(f"\n{'-'*70}\nNEXT STEPS  ({target['name']} {target['ticker']})\n{'-'*70}")
    print("1. Review the analyst outputs in targets/%s/analysis/." % target["ticker"])
    print("2. Open ANALYZE_COMPANY.md and answer the 6 assignment questions.")
    print("3. Build the Canva deck from DECK_BLUEPRINT.md (same style as amkr.pdf).")


if __name__ == "__main__":
    main()
