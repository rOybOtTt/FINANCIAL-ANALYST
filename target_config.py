"""
Deep-Tech Analyst - Target Config  (the company-agnostic core)
==============================================================

The original project was hard-wired to Amkor (AMKR). This module makes the whole
analyst pipeline *target-driven* so you can point it at ANY AI / deep-tech name
(NVDA, VRT, ASML, TER, ...) for a LONG or a SHORT idea.

How it works
------------
- `run_company.py` writes the active target to  targets/_current.json .
- Every analyst (04 Financial, 05 Tech, 07 Senior) calls `load_target()` and
  builds its persona from that target instead of a hard-coded "Amkor" string.
- If no target is set, it falls back to the AMKR default, so the original
  AMKR scripts keep working exactly as before (backward compatible).

Target schema (targets/_current.json or targets/<TICKER>.json)
--------------------------------------------------------------
{
  "ticker": "NVDA",
  "name": "NVIDIA Corporation",
  "side": "long",                      # long | short | auto
  "sector": "ai-compute",              # free-form sector slug (see peer_map.py)
  "sector_label": "AI compute / accelerators",
  "one_liner": "Designs the GPUs that train and run modern AI.",
  "thesis_question": "Is NVDA a buy at today's price ...?",   # drives the debate
  "peers": [ {"ticker": "AMD", "name": "Advanced Micro Devices", "role": "competitor"}, ... ],
  "deck_topics": [ "GPU architecture (Blackwell, ...)", ... ]   # optional overrides
}
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS_DIR = os.path.join(HERE, "targets")
CURRENT = os.path.join(TARGETS_DIR, "_current.json")

VALID_SIDES = ("long", "short", "auto")

# --------------------------------------------------------------------------
# AMKR default  (so the legacy scripts still run with no target set)
# --------------------------------------------------------------------------

AMKR_DEFAULT = {
    "ticker": "AMKR",
    "name": "Amkor Technology",
    "side": "auto",
    "sector": "advanced-packaging-osat",
    "sector_label": "semiconductor advanced packaging (OSAT)",
    "one_liner": "The world's largest independent OSAT - it packages and tests "
                 "the chips other companies design and fabricate.",
    "thesis_question": "Is Amkor fairly valued, and is it a long, a short, or a pass?",
    "peers": [
        {"ticker": "ASX", "name": "ASE Technology Holding", "role": "competitor"},
        {"ticker": "IMOS", "name": "ChipMOS Technologies", "role": "competitor"},
        {"ticker": "600584.SS", "name": "JCET Group", "role": "competitor"},
        {"ticker": "6239.TW", "name": "Powertech Technology", "role": "competitor"},
        {"ticker": "002156.SZ", "name": "Tongfu Microelectronics", "role": "competitor"},
        {"ticker": "TSM", "name": "TSMC", "role": "competitor"},
        {"ticker": "INTC", "name": "Intel", "role": "competitor"},
    ],
    "deck_topics": [],
}


# --------------------------------------------------------------------------
# Load / save
# --------------------------------------------------------------------------

def load_target():
    """Return the active target dict. Falls back to the AMKR default if no
    target has been selected yet (keeps the original AMKR scripts working)."""
    if os.path.isfile(CURRENT):
        try:
            with open(CURRENT, encoding="utf-8") as f:
                t = json.load(f)
            return _normalize(t)
        except (OSError, json.JSONDecodeError):
            pass
    return _normalize(dict(AMKR_DEFAULT))


def save_current(target):
    os.makedirs(TARGETS_DIR, exist_ok=True)
    with open(CURRENT, "w", encoding="utf-8") as f:
        json.dump(_normalize(target), f, indent=2)


def load_preset(ticker):
    """Load a saved preset targets/<TICKER>.json, or None."""
    path = os.path.join(TARGETS_DIR, f"{ticker.upper()}.json")
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as f:
                return _normalize(json.load(f))
        except (OSError, json.JSONDecodeError):
            return None
    return None


def _normalize(t):
    t = dict(t)
    t["ticker"] = (t.get("ticker") or "").upper()
    t.setdefault("name", t["ticker"])
    side = (t.get("side") or "auto").lower()
    t["side"] = side if side in VALID_SIDES else "auto"
    t.setdefault("sector", "deep-tech")
    t.setdefault("sector_label", "the deep-tech / semiconductor sector")
    t.setdefault("one_liner", "")
    t.setdefault("thesis_question",
                 f"Is {t['name']} ({t['ticker']}) a long, a short, or a pass at today's price, "
                 f"and what is the single technical driver that most moves the valuation?")
    t.setdefault("peers", [])
    t.setdefault("deck_topics", [])
    return t


def all_tickers(target=None):
    """Target ticker + every peer ticker (used to scope the data brief)."""
    t = target or load_target()
    out = [t["ticker"]] + [p["ticker"] for p in t.get("peers", [])]
    seen, uniq = set(), []
    for tk in out:
        u = (tk or "").upper()
        if u and u not in seen:
            seen.add(u); uniq.append(u)
    return uniq


def active_scope():
    """Return (company_filter, tech_filter) for analyst_common.load_context().

    - If an explicit target has been selected (targets/_current.json exists),
      scope the DATA BRIEF to that target + its peers, and to the tech topics
      researched for it - so a NVDA run doesn't drag in Amkor's 56 dossiers.
    - If NO target is set, return (None, None) so the legacy Amkor scripts keep
      loading everything exactly as before (backward compatible).
    """
    if not os.path.isfile(CURRENT):
        return None, None
    t = load_target()
    company_filter = all_tickers(t)
    tech_filter = t.get("deck_topic_slugs") or None
    return company_filter, tech_filter


# --------------------------------------------------------------------------
# Persona builders  (parameterized by target + long/short side)
# --------------------------------------------------------------------------

def _peer_names(t, n=6):
    names = [p["name"] for p in t.get("peers", []) if p.get("name")]
    return ", ".join(names[:n]) if names else "its closest listed peers"


def _side_mandate(side, name):
    if side == "long":
        return (f"MANDATE: you are pressure-testing a LONG (buy) thesis on {name}. "
                "Build the strongest evidence-based BULL case - but be intellectually "
                "honest: if the data actually argues for a short or a pass, say so plainly.")
    if side == "short":
        return (f"MANDATE: you are pressure-testing a SHORT thesis on {name}. "
                "Build the strongest evidence-based BEAR / short case - the broken "
                "assumptions, the over-earning, the valuation air-pocket, the catalysts "
                "that de-rate it. If the data actually argues for a long or a pass, say so plainly.")
    return (f"MANDATE: decide whether {name} is a LONG, a SHORT, or a PASS based purely "
            "on the evidence. Take a side; do not hedge into mush.")


def financial_persona(target=None):
    t = target or load_target()
    return (
        f"You are a SENIOR FINANCIAL ANALYST covering {t['sector_label']}, "
        f"with {t['name']} ({t['ticker']}) as your focus company.\n\n"
        "Your lens is strictly FINANCIAL:\n"
        "- valuation (P/E, EV/EBITDA, growth vs multiple, peer comparison)\n"
        "- profitability and margins, revenue growth and cyclicality\n"
        "- balance sheet, capex, cash flow, debt, returns on capital (ROIC vs WACC)\n"
        f"- competitive financial positioning vs peers ({_peer_names(t)})\n"
        "- financial risks and catalysts\n\n"
        f"{_side_mandate(t['side'], t['name'])}\n\n"
        "Rules:\n"
        "- Ground EVERY claim in the DATA BRIEF. Cite the specific number or filing/news item.\n"
        "- If the data doesn't support a claim, say so explicitly - do not invent figures.\n"
        "- Be decisive: give a clear financial view, not a hedge.\n"
        "- Keep it tight and structured."
    )


def tech_persona(target=None):
    t = target or load_target()
    return (
        f"You are a SENIOR TECHNOLOGY ANALYST covering {t['sector_label']}, "
        f"with {t['name']} ({t['ticker']}) as your focus company.\n\n"
        "Your lens is strictly TECHNOLOGY:\n"
        "- the core architecture / engineering choice and WHY it is hard to copy (the technical moat)\n"
        "- product/technology roadmap and where the underlying technology is heading\n"
        f"- technical differentiation vs peers ({_peer_names(t)})\n"
        "- product mix, R&D direction, manufacturing / supply capability and capacity\n"
        "- where the end-markets (AI, data center, HPC, automotive, mobile, robotics, quantum) "
        "are heading, and how well-positioned the company is\n\n"
        f"{_side_mandate(t['side'], t['name'])}\n\n"
        "Rules:\n"
        "- Ground EVERY claim in the DATA BRIEF (tech research findings, filings, news). "
        "Cite the specific source or filing.\n"
        "- If the data doesn't support a claim, say so - do not invent technical facts.\n"
        "- Be decisive: give a clear technology view, not a hedge.\n"
        "- Keep it tight and structured."
    )


def senior_persona(target=None):
    """Senior desk head. Outputs the assignment-grade deliverable: a directional
    call + entry price + expected IRR/ROI + the single technical sensitivity driver."""
    t = target or load_target()
    side_note = {
        "long": "The desk is evaluating a LONG. Confirm or reject it.",
        "short": "The desk is evaluating a SHORT. Confirm or reject it.",
        "auto": "Decide the direction yourself.",
    }[t["side"]]
    return (
        f"You are the SENIOR EQUITY ANALYST and head of a deep-tech fund desk. Two of your "
        f"analysts (Financial=04, Technology=05) debated {t['name']} ({t['ticker']}) and an "
        f"editor (06) summarized it. You make the final call, with special authority on "
        f"VALUATION and KPIs. {side_note}\n\n"
        "Deliver, in this order:\n"
        "1. **Verdict** - LONG / SHORT / PASS in one line, with conviction (low/med/high).\n"
        "2. **Valuation view** - cheap / fair / expensive on the actual DATA BRIEF numbers "
        "(P/E vs growth, EV/EBITDA, vs peers, vs its own history).\n"
        "3. **KPI scorecard** - the 3-5 KPIs that matter here, each marked Strong / Neutral / "
        "Weak with the number behind it.\n"
        "4. **The technical sensitivity driver** - name the SINGLE technical variable "
        "(e.g. yield, power efficiency, ASP/mix, capacity ramp, attach rate, latency) that "
        "most moves the valuation, and sketch how the value swings as it moves.\n"
        "5. **Investment thesis** - the PRICE at which you would initiate, your expected "
        "RETURN (IRR / ROI) over a stated holding period, and the logic behind those numbers.\n"
        "6. **What would change my mind** - the single most important data point to watch.\n\n"
        "Be decisive and senior. Ground everything in the DATA BRIEF and the analysts' debate "
        "+ synthesis. Flag clearly if the data is insufficient for a confident call."
    )


# --------------------------------------------------------------------------
# CLI: inspect the current target
# --------------------------------------------------------------------------

if __name__ == "__main__":
    t = load_target()
    print(f"Active target : {t['name']} ({t['ticker']})")
    print(f"Side          : {t['side']}")
    print(f"Sector        : {t['sector']}  ({t['sector_label']})")
    print(f"Peers         : {', '.join(p['ticker'] for p in t['peers']) or '(none)'}")
    print(f"Question      : {t['thesis_question']}")
