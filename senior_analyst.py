"""
AMKOR - Senior Analyst  (Agent 07)  --  top-level orchestrator
==============================================================

The Senior Analyst is the main entry point. For your question it:

  1. (optional) ACTIVATES the data agents to refresh data:
        --refresh-market   -> market_agent.py   (Agent 03 + 03b)
        --refresh-edgar T  -> data_agent.py T    (Agent 01 + 01b)
        --refresh-tech "X" -> tech_agent.py "X"  (Agent 02 + 02b)
  2. Runs the DEBATE between the Financial Analyst (04) and the Tech Analyst (05).
  3. Runs the Synthesizer (06) to summarize the debate.
  4. Adds its own SENIOR verdict focused on VALUATION and KPIs.

Usage:
  python senior_analyst.py "Is Amkor fairly valued vs ASE?"
  python senior_analyst.py "Where is Amkor's KPI momentum vs peers?" --rounds 2
  python senior_analyst.py "..." --refresh-market
  python senior_analyst.py "..." --refresh-edgar AMKR --refresh-tech "advanced packaging"
  python senior_analyst.py "..." --dry-run     # build context only, no API calls
"""

import argparse
import subprocess
import sys
import os

import analyst_common as ac
import debate as dbt
import synthesizer as synth
import target_config as tc

HERE = os.path.dirname(os.path.abspath(__file__))

# The senior persona (verdict + valuation + KPI scorecard + the single technical
# sensitivity driver + entry price/IRR + what-would-change-my-mind) is built from
# the ACTIVE TARGET, so it works for any company, long or short. See target_config.


def _run(label, args_list):
    print(f"\n[Senior] activating {label}: {' '.join(args_list)}")
    try:
        subprocess.run([sys.executable] + args_list, cwd=HERE, check=False)
    except Exception as e:
        print(f"[!] {label} failed: {e}")


def refresh(args):
    if args.refresh_market:
        _run("Market Intel Agent (03)", ["market_agent.py", "--news", "4"])
    if args.refresh_edgar:
        _run("Data Agent (01)", ["data_agent.py"] + args.refresh_edgar)
    if args.refresh_tech:
        _run("Tech Agent (02)", ["tech_agent.py", args.refresh_tech])


def senior_verdict(question, transcript_text, synthesis_text, data_brief, effort="high"):
    system = ac.system_with_context(tc.senior_persona(), data_brief)
    user = (f"Question: {question}\n\n"
            "Debate transcript (Financial 04 vs Tech 05):\n"
            f"\"\"\"\n{transcript_text}\n\"\"\"\n\n"
            "Editor's synthesis (06):\n"
            f"\"\"\"\n{synthesis_text}\n\"\"\"\n\n"
            "Now give your SENIOR verdict using the six numbered sections above, "
            "with the valuation view, KPI scorecard, the single technical sensitivity "
            "driver, and the entry-price/IRR thesis front and center.")
    return ac.ask_claude(system, user, max_tokens=4000, effort=effort)


def run(question, rounds, effort, dry_run):
    brief = ac.load_context(*tc.active_scope())

    if dry_run:
        print("=== DRY RUN (no API calls) ===")
        print(f"Data brief length: {len(brief):,} chars\n")
        print(brief[:3000] + ("\n...\n[truncated]" if len(brief) > 3000 else ""))
        return

    print("=" * 70)
    print(f"SENIOR ANALYST (07) - question: {question}")
    print("=" * 70)

    print("\n>>> Stage 1-2: DEBATE (Financial 04 vs Tech 05)")
    transcript = dbt.run_debate(question, brief, rounds=rounds, effort=effort, verbose=True)
    ttext = dbt.transcript_to_text(transcript)

    print("\n>>> Stage 3: SYNTHESIS (06)")
    synthesis = synth.synthesize(question, ttext, brief, effort=effort)
    print(synthesis)

    print("\n>>> Stage 4: SENIOR VERDICT (07)")
    verdict = senior_verdict(question, ttext, synthesis, brief, effort=effort)
    print(verdict)
    return verdict


def main():
    p = argparse.ArgumentParser(description="AMKOR Senior Analyst (07) - orchestrates 01-06.")
    p.add_argument("question", nargs="*")
    p.add_argument("--rounds", type=int, default=1, help="Debate rebuttal rounds (default 1).")
    p.add_argument("--effort", default="high", help="low|medium|high|xhigh|max (default high).")
    p.add_argument("--refresh-market", action="store_true", help="Re-run Market Agent (03) first.")
    p.add_argument("--refresh-edgar", nargs="*", metavar="TICKER",
                   help="Re-run Data Agent (01) for these tickers first.")
    p.add_argument("--refresh-tech", metavar="TOPIC", help="Re-run Tech Agent (02) for this topic first.")
    p.add_argument("--dry-run", action="store_true", help="Build the data brief only; no API calls.")
    args = p.parse_args()

    q = " ".join(args.question).strip() or input("Question for the desk?\n> ").strip()
    if not q:
        return

    if args.refresh_market or args.refresh_edgar or args.refresh_tech:
        refresh(args)

    try:
        run(q, args.rounds, args.effort, args.dry_run)
    except ac.NoApiKey as e:
        print(f"\n[!] {e}")


if __name__ == "__main__":
    main()
