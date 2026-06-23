"""
AMKOR - Financial Analyst  (Agent 04)
=====================================

Reads ALL data collected by Agents 1/2/3 and answers your question from a
FINANCIAL perspective (valuation, margins, growth, balance sheet, competitive
financial position, risks). It can also rebut the Tech Analyst (Agent 05) in a
debate orchestrated by the Senior Analyst (Agent 07).

Standalone:
  python financial_analyst.py "Is Amkor's valuation justified vs ASE?"
"""

import sys
import analyst_common as ac
import target_config as tc

# The persona is now built from the ACTIVE TARGET (target_config.load_target()),
# so this same agent works for any company, long or short. With no target set it
# falls back to the Amkor default - identical to the original behavior.


def analyze(question, data_brief, opponent_argument=None, effort="medium"):
    system = ac.system_with_context(tc.financial_persona(), data_brief)
    if opponent_argument is None:
        user = (f"Question: {question}\n\n"
                "Give your FINANCIAL analysis and a clear position. "
                "Structure: (1) Financial read of the data, (2) Your position, "
                "(3) Key numbers that support it, (4) Biggest financial risk to your view.")
    else:
        user = (f"Question: {question}\n\n"
                "The TECH analyst argued the following:\n"
                f"\"\"\"\n{opponent_argument}\n\"\"\"\n\n"
                "Respond from the FINANCIAL side. Where does the tech view miss "
                "financial reality (valuation, margins, cash, cyclicality)? Concede "
                "any point that is genuinely valid, then make your strongest financial "
                "counter-points. Stay grounded in the DATA BRIEF.")
    return ac.ask_claude(system, user, max_tokens=3500, effort=effort)


def main():
    q = " ".join(sys.argv[1:]).strip() or input("Financial question?\n> ").strip()
    if not q:
        return
    try:
        brief = ac.load_context()
        print("=== FINANCIAL ANALYST (Agent 04) ===\n")
        print(analyze(q, brief))
    except ac.NoApiKey as e:
        print(f"[!] {e}")


if __name__ == "__main__":
    main()
