"""
AMKOR - Tech Analyst  (Agent 05)
================================

Reads ALL data collected by Agents 1/2/3 and answers your question from a
TECHNOLOGY perspective (process/packaging technology, roadmap, product mix,
technical moat, R&D, where the industry is heading). It can also rebut the
Financial Analyst (Agent 04) in a debate orchestrated by the Senior Analyst (07).

Standalone:
  python tech_analyst.py "Is Amkor's advanced-packaging tech a real moat?"
"""

import sys
import analyst_common as ac
import target_config as tc

# Persona is built from the ACTIVE TARGET (target_config.load_target()), so this
# agent works for any company, long or short. No target set -> Amkor default.


def analyze(question, data_brief, opponent_argument=None, effort="medium"):
    system = ac.system_with_context(tc.tech_persona(), data_brief)
    if opponent_argument is None:
        user = (f"Question: {question}\n\n"
                "Give your TECHNOLOGY analysis and a clear position. "
                "Structure: (1) Technology read of the data, (2) Your position, "
                "(3) Key technical evidence that supports it, (4) Biggest technical "
                "risk to your view.")
    else:
        user = (f"Question: {question}\n\n"
                "The FINANCIAL analyst argued the following:\n"
                f"\"\"\"\n{opponent_argument}\n\"\"\"\n\n"
                "Respond from the TECHNOLOGY side. Where does the financial view miss "
                "the technology reality (roadmap, moat, product mix, where demand is "
                "going)? Concede any point that is genuinely valid, then make your "
                "strongest technical counter-points. Stay grounded in the DATA BRIEF.")
    return ac.ask_claude(system, user, max_tokens=3500, effort=effort)


def main():
    q = " ".join(sys.argv[1:]).strip() or input("Tech question?\n> ").strip()
    if not q:
        return
    try:
        brief = ac.load_context()
        print("=== TECH ANALYST (Agent 05) ===\n")
        print(analyze(q, brief))
    except ac.NoApiKey as e:
        print(f"[!] {e}")


if __name__ == "__main__":
    main()
