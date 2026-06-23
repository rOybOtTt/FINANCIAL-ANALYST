"""
AMKOR - Debate Engine  (Agents 04 vs 05)
========================================

Runs the argument between the Financial Analyst (04) and the Tech Analyst (05)
over your question. Each opens with its own position, then they rebut each other
for a number of rounds. Returns the full transcript (used by the Synthesizer 06
and the Senior Analyst 07).

Standalone:
  python debate.py "Will Amkor outgrow ASE over the next 2 years?" --rounds 1
"""

import argparse
import sys

import analyst_common as ac
import financial_analyst as fin
import tech_analyst as tech


def run_debate(question, data_brief, rounds=1, effort="medium", verbose=True):
    """Return a list of {speaker, role, text} turns."""
    transcript = []

    def add(speaker, role, text):
        transcript.append({"speaker": speaker, "role": role, "text": text})
        if verbose:
            print(f"\n----- {speaker} -----\n{text}\n")

    # Opening positions
    fin_open = fin.analyze(question, data_brief, effort=effort)
    add("Financial Analyst (04)", "financial", fin_open)
    tech_open = tech.analyze(question, data_brief, effort=effort)
    add("Tech Analyst (05)", "tech", tech_open)

    # Rebuttal rounds
    last_fin, last_tech = fin_open, tech_open
    for r in range(rounds):
        fin_reb = fin.analyze(question, data_brief, opponent_argument=last_tech, effort=effort)
        add(f"Financial Analyst (04) - rebuttal {r+1}", "financial", fin_reb)
        tech_reb = tech.analyze(question, data_brief, opponent_argument=last_fin, effort=effort)
        add(f"Tech Analyst (05) - rebuttal {r+1}", "tech", tech_reb)
        last_fin, last_tech = fin_reb, tech_reb

    return transcript


def transcript_to_text(transcript):
    return "\n\n".join(f"[{t['speaker']}]\n{t['text']}" for t in transcript)


def main():
    p = argparse.ArgumentParser(description="Financial vs Tech analyst debate.")
    p.add_argument("question", nargs="*")
    p.add_argument("--rounds", type=int, default=1, help="Rebuttal rounds (default 1).")
    p.add_argument("--effort", default="medium")
    args = p.parse_args()
    q = " ".join(args.question).strip() or input("Question to debate?\n> ").strip()
    if not q:
        return
    try:
        brief = ac.load_context()
        print(f"=== DEBATE: {q} ({args.rounds} rebuttal round(s)) ===")
        run_debate(q, brief, rounds=args.rounds, effort=args.effort)
    except ac.NoApiKey as e:
        print(f"[!] {e}")


if __name__ == "__main__":
    main()
