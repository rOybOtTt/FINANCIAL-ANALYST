"""
AMKOR - Synthesizer  (Agent 06)
===============================

Takes the full debate between the Financial Analyst (04) and the Tech Analyst
(05) and SUMMARIZES it into a single, balanced answer to your question -
weighing both sides, noting where they agree and disagree, and giving a clear
bottom line.

Standalone (runs the debate first, then summarizes):
  python synthesizer.py "Is Amkor a better buy than ASE right now?"
"""

import argparse

import analyst_common as ac
import debate as dbt

PERSONA = """You are a NEUTRAL RESEARCH EDITOR. Two analysts - a Financial
analyst and a Technology analyst - debated the user's question. Your job is to
SUMMARIZE their debate into one balanced answer.

Produce:
1. **Points of agreement** - where both sides converged.
2. **Key disagreement(s)** - the real crux, stated fairly for each side.
3. **Who had the stronger evidence** - judged only on the DATA BRIEF.
4. **Bottom line** - a clear, balanced answer to the question, with the main
   caveat or what data would change the conclusion.

Be fair to both sides. Ground everything in the DATA BRIEF and the debate. Do
not introduce new facts that neither analyst raised and the brief doesn't support."""


def synthesize(question, transcript_text, data_brief, effort="high"):
    system = ac.system_with_context(PERSONA, data_brief)
    user = (f"Question: {question}\n\n"
            "Here is the full debate transcript between the Financial Analyst (04) "
            "and the Tech Analyst (05):\n"
            f"\"\"\"\n{transcript_text}\n\"\"\"\n\n"
            "Now write your balanced synthesis using the four sections above.")
    return ac.ask_claude(system, user, max_tokens=3500, effort=effort)


def main():
    p = argparse.ArgumentParser(description="Synthesize the 04 vs 05 debate.")
    p.add_argument("question", nargs="*")
    p.add_argument("--rounds", type=int, default=1)
    p.add_argument("--effort", default="high")
    args = p.parse_args()
    q = " ".join(args.question).strip() or input("Question?\n> ").strip()
    if not q:
        return
    try:
        brief = ac.load_context()
        transcript = dbt.run_debate(q, brief, rounds=args.rounds, verbose=True)
        print("\n=== SYNTHESIS (Agent 06) ===\n")
        print(synthesize(q, dbt.transcript_to_text(transcript), brief, effort=args.effort))
    except ac.NoApiKey as e:
        print(f"[!] {e}")


if __name__ == "__main__":
    main()
