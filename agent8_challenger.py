"""
AMKOR - Challenger  (Agent 08)
==============================

Agent 08 is a task-driven, document-centric ORCHESTRATOR. For a task you give it
(usually about files you uploaded manually to ./uploads/):

  1. INGEST the uploaded files. PDFs are read NATIVELY by Claude - the real PDF
     is attached to the analysis calls (not just a summary) - and also get a short
     text DIGEST that goes in the brief as a cross-reference/index. docx/html/
     text/csv are extracted to text.
  2. ROUTE: decide which analysis layers the task needs - Financial (04),
     Tech (05), or both - and craft a focused question for each.
  3. Q&A + CHALLENGE each chosen layer: the layer answers, then Agent 08
     CHALLENGES it hard (adversarial review), then the layer DEFENDS / revises.
     The native PDF source is attached so the challenge is grounded in the real
     document, not a summary.
  4. REPORT: hand the whole challenged exchange to the Reporter, which writes the
     final analysis. Saved under data/reports/<task-slug>-<timestamp>/ .

Usage:
  python agent8_challenger.py "Review the uploaded 10-K for margin risks"
  python agent8_challenger.py "Compare uploaded deck vs our data" --files uploads/deck.pdf
  python agent8_challenger.py "..." --layers financial         # force a layer
  python agent8_challenger.py "..." --rounds 2                  # tougher challenge
  python agent8_challenger.py "..." --senior                    # add Senior (07) verdict
  python agent8_challenger.py "..." --allow-no-files            # analyze brief alone
  python agent8_challenger.py "..." --dry-run                   # ingest only, no API
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

import analyst_common as ac
import financial_analyst as fin
import tech_analyst as tech

HERE = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(HERE, "uploads")
REPORTS = os.path.join(HERE, "data", "reports")

MAX_UPLOAD_CHARS = 400000   # 1M-context model; cap per text-like upload (with marker)

LAYERS = {
    "financial": ("Financial Analyst (04)", fin.PERSONA),
    "tech":      ("Tech Analyst (05)", tech.PERSONA),
}

DIGEST_PERSONA = """You are a meticulous document analyst. Produce a FAITHFUL,
detailed text digest of the supplied document: key facts, every important number
and figure, tables (as text), section structure, claims, dates, and named
entities. Do not interpret or opine - just capture the content accurately so it
can serve as an index. (The original document is also attached natively to later
calls, so this digest is a cross-reference, not the only representation.)"""

ROUTER_PERSONA = """You are a routing dispatcher. Given a task and the uploaded
documents, decide which analysis layers to engage and write one focused
sub-question per engaged layer.

Available layers:
- "financial": valuation, margins, growth, cash flow, balance sheet, peer financials.
- "tech": technology, packaging roadmap, technical moat, product mix, R&D, demand.

Respond with ONLY a JSON object, no prose:
{"layers": ["financial","tech"], "financial_q": "...", "tech_q": "..."}
Include a layer only if it is genuinely relevant; include its *_q only if engaged.
If the task clearly spans both, engage both."""

CHALLENGER_PERSONA = """You are THE CHALLENGER - a relentless but fair adversarial
reviewer. You are given an analyst's answer. Your job is to stress-test it, not to
agree.

Do:
- Identify the weakest or least-supported claims.
- Flag anything NOT backed by the DATA BRIEF or the uploaded documents (the real
  documents are attached - check the analyst's numbers against the source).
- Surface missing considerations, alternative interpretations, and overlooked risks.
- Be specific and cite the number / document / source you're referring to.
- End with the 2-3 toughest questions the analyst MUST answer.

Be sharp and concrete. Challenge on the evidence (or the absence of it)."""

REPORTER_PERSONA = """You are the LEAD REPORTER / ANALYST. You receive, for one
task, the challenged analyses from each engaged layer (each as: ANSWER ->
CHALLENGE -> DEFENSE), the DATA BRIEF, and the uploaded documents. Write the
FINAL report.

Structure:
1. **Executive answer** - the direct answer to the task, 2-4 sentences.
2. **Key findings** - grounded in the uploaded documents + the DATA BRIEF, with
   the numbers/sources behind them.
3. **What the challenge changed** - where the adversarial review strengthened,
   weakened, or overturned a conclusion.
4. **Open risks & unknowns** - what the data/documents do NOT settle.
5. **Recommendation** - a clear, decisive call (and what evidence would change it).

Ground everything in the documents and data. Be decisive but mark uncertainty
honestly."""


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "task"


# --------------------------------------------------------------------------
# 1. Ingest uploads
# --------------------------------------------------------------------------

def list_uploads(explicit):
    """Resolve files. --files entries are tried against CWD, then uploads/, then
    the project dir; missing ones warn loudly instead of vanishing."""
    if explicit:
        out = []
        for f in explicit:
            cands = [f, os.path.join(UPLOADS, f), os.path.join(HERE, f)]
            match = next((c for c in cands if os.path.isfile(c)), None)
            if match:
                out.append(os.path.abspath(match))
            else:
                print(f"[!] --files entry not found (tried CWD and uploads/): {f}",
                      file=sys.stderr)
        return out
    if not os.path.isdir(UPLOADS):
        return []
    out = []
    for name in sorted(os.listdir(UPLOADS)):
        p = os.path.join(UPLOADS, name)
        if os.path.isfile(p) and name.lower() != "readme.md":
            out.append(p)
    return out


def ingest(files, dry_run=False):
    """Return (uploads_text, notes, attachments). PDFs are validated, attached
    natively (attachments) AND digested into the brief text; other formats are
    extracted to text. Bad/empty/oversize/unsupported files are skipped loudly."""
    sections, notes, attachments = [], [], []
    for path in files:
        name = os.path.basename(path)

        if ac.is_pdf(path):
            ok, reason = ac.validate_pdf(path)
            if not ok:
                notes.append(f"{name}: PDF skipped ({reason})")
                sections.append(f"### {name} (PDF)\n[NOT INGESTED: {reason} - EXCLUDED from analysis]")
                continue
            if dry_run:
                sections.append(f"### {name} (PDF)\n(valid PDF - read natively by Claude at run time)")
                notes.append(f"{name}: valid PDF (would attach natively)")
                continue
            block = ac.pdf_block(path)
            attachments.append(block)
            try:
                digest = ac.ask_claude(
                    [{"type": "text", "text": DIGEST_PERSONA}],
                    f"Digest this document faithfully and completely. Filename: {name}",
                    max_tokens=4000, effort="medium", attachments=[block])
                notes.append(f"{name}: PDF attached natively + digested ({len(digest)} chars)")
            except Exception as e:
                digest = f"(digest unavailable: {e}; the document is still attached natively)"
                notes.append(f"{name}: digest failed ({e}) - native PDF still attached")
            sections.append(f"### {name} (PDF - native source attached; digest index below)\n{digest}")
            continue

        # text-like formats
        text = ac.read_text_like(path)
        if text is None:
            notes.append(f"{name}: UNSUPPORTED or parse-failed - skipped")
            sections.append(f"### {name}\n[NOT INGESTED: unsupported type or parse failure - EXCLUDED]")
            print(f"[!] {name}: could not ingest (unsupported type / parse failure)", file=sys.stderr)
            continue
        if not text.strip():
            notes.append(f"{name}: read but EMPTY - skipped")
            continue
        orig = len(text)
        if orig > MAX_UPLOAD_CHARS:
            text = (text[:MAX_UPLOAD_CHARS] +
                    f"\n\n...[TRUNCATED: first {MAX_UPLOAD_CHARS:,} of {orig:,} chars of "
                    f"{name}; remainder NOT analyzed]...")
            notes.append(f"{name}: read ({orig:,} chars, TRUNCATED to {MAX_UPLOAD_CHARS:,})")
        else:
            notes.append(f"{name}: read ({orig:,} chars)")
        sections.append(f"### {name}\n{text}")

    uploads_text = "\n\n".join(sections) if sections else "(no readable uploads)"
    return uploads_text, notes, attachments


# --------------------------------------------------------------------------
# 2. Route
# --------------------------------------------------------------------------

def _extract_json_obj(raw):
    """Parse the first balanced {...} object; tolerate leading prose."""
    raw = raw.strip()
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    depth, start = 0, None
    for i, ch in enumerate(raw):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    obj = json.loads(raw[start:i + 1])
                    if isinstance(obj, dict):
                        return obj
                except json.JSONDecodeError:
                    start = None
    return None


def route(task, brief):
    raw = ac.ask_claude(ac.system_with_context(ROUTER_PERSONA, brief),
                        f"Task: {task}\n\nDecide the layers and sub-questions.",
                        max_tokens=1500, effort="low")
    plan = _extract_json_obj(raw)
    if isinstance(plan, dict):
        layers = [l for l in plan.get("layers", []) if l in LAYERS]
        if layers:
            return layers, plan
    print("[!] router: could not parse a routing plan; defaulting to BOTH layers")
    return ["financial", "tech"], {"financial_q": task, "tech_q": task}


# --------------------------------------------------------------------------
# 3. Q&A + Challenge each layer
# --------------------------------------------------------------------------

def challenge_layer(task, layer, sub_q, brief, rounds, attachments):
    label, persona = LAYERS[layer]
    system_layer = ac.system_with_context(persona, brief)
    system_chal = ac.system_with_context(CHALLENGER_PERSONA, brief)

    exchange = {"layer": layer, "label": label, "turns": []}

    answer = ac.ask_claude(
        system_layer,
        f"Task: {task}\nFocused question for you: {sub_q}\n\n"
        "Answer using the DATA BRIEF and the UPLOADED DOCUMENTS (attached). Cite specifics.",
        max_tokens=3500, effort="medium", attachments=attachments)
    exchange["turns"].append({"role": "answer", "text": answer})
    print(f"\n--- {label}: ANSWER ---\n{answer}\n")

    for r in range(rounds):
        challenge = ac.ask_claude(
            system_chal,
            f"Task: {task}\n\nThe {label} answered:\n\"\"\"\n{answer}\n\"\"\"\n\n"
            "Challenge this answer hard, checking it against the attached documents.",
            max_tokens=2500, effort="medium", attachments=attachments)
        exchange["turns"].append({"role": "challenge", "text": challenge})
        print(f"--- CHALLENGER -> {label} (round {r+1}) ---\n{challenge}\n")

        defense = ac.ask_claude(
            system_layer,
            f"Task: {task}\nYour earlier answer:\n\"\"\"\n{answer}\n\"\"\"\n\n"
            f"The Challenger raised:\n\"\"\"\n{challenge}\n\"\"\"\n\n"
            "Defend or revise: concede what is valid, rebut what is not, and answer "
            "their toughest questions - strictly grounded in the DATA BRIEF and the "
            "UPLOADED DOCUMENTS (attached).",
            max_tokens=3000, effort="medium", attachments=attachments)
        exchange["turns"].append({"role": "defense", "text": defense})
        print(f"--- {label}: DEFENSE (round {r+1}) ---\n{defense}\n")
        answer = defense  # next challenge round targets the revised answer

    return exchange


# --------------------------------------------------------------------------
# 4. Report
# --------------------------------------------------------------------------

def report(task, exchanges, brief, attachments):
    blocks = []
    for ex in exchanges:
        lines = [f"### Layer: {ex['label']}"]
        for t in ex["turns"]:
            lines.append(f"[{t['role'].upper()}]\n{t['text']}")
        blocks.append("\n\n".join(lines))
    body = "\n\n=====\n\n".join(blocks)
    return ac.ask_claude(
        ac.system_with_context(REPORTER_PERSONA, brief),
        f"Task: {task}\n\nChallenged analyses per layer:\n\"\"\"\n{body}\n\"\"\"\n\n"
        "Write the final report using the five sections.",
        max_tokens=4000, effort="high", attachments=attachments)


# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------

def _save(out_dir, task, files, layers, final, senior_text, exchanges, stamp):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write(f"# Agent 08 Report: {task}\n\n_Generated {stamp}_\n\n")
        f.write(f"**Files:** {', '.join(os.path.basename(x) for x in files) or 'none'}\n\n")
        f.write(f"**Layers engaged:** {', '.join(layers) or '(none)'}\n\n---\n\n")
        f.write((final or "_(report not produced - run was interrupted; see transcript.json)_") + "\n")
        if senior_text:
            f.write("\n\n---\n\n## Senior Analyst (07) verdict\n\n" + senior_text + "\n")
    with open(os.path.join(out_dir, "transcript.json"), "w", encoding="utf-8") as f:
        json.dump({"task": task, "generated_utc": stamp,
                   "files": [os.path.basename(x) for x in files],
                   "layers": layers, "exchanges": exchanges,
                   "report": final, "senior": senior_text}, f, indent=2)


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def run(task, files, layers_override, rounds, add_senior, dry_run, allow_no_files):
    files = list_uploads(files)
    print(f"Uploaded files: {len(files)}")
    for f in files:
        print(f"  - {os.path.basename(f)}")

    if not files and not allow_no_files:
        print("\n[!] No readable uploaded files found in ./uploads/ (or via --files).")
        print("    Agent 08 is document-centric. Add files to uploads/, pass valid --files,")
        print("    or re-run with --allow-no-files to analyze the background data brief alone.")
        return

    uploads_text, notes, attachments = ingest(files, dry_run=dry_run)
    base_brief = ac.load_context()
    brief = (base_brief +
             "\n\n## UPLOADED DOCUMENTS (provided by the user for this task)\n" + uploads_text)

    if dry_run:
        print("\n=== DRY RUN (no API calls) ===")
        print("Ingestion notes:")
        for n in notes:
            print(f"  - {n}")
        print(f"\nCombined brief length: {len(brief):,} chars "
              f"(base {len(base_brief):,} | uploads {len(uploads_text):,})")
        print(f"PDFs that would be attached natively: "
              f"{sum(1 for f in files if ac.is_pdf(f))}")
        return

    print("\n=== INGESTION ===")
    for n in notes:
        print(f"  - {n}")
    if attachments:
        print(f"  ({len(attachments)} PDF(s) attached natively to the analysis calls)")

    if layers_override:
        layers = [l for l in layers_override if l in LAYERS]
        plan = {"financial_q": task, "tech_q": task}
    else:
        print("\n=== ROUTING ===")
        layers, plan = route(task, brief)
    print(f"Engaging layers: {', '.join(layers)}")

    stamp = datetime.now(timezone.utc).isoformat()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(REPORTS, f"{slugify(task)}-{run_id}")

    exchanges, final, senior_text = [], None, None
    try:
        for layer in layers:
            sub_q = plan.get(f"{layer}_q") or task
            print(f"\n=== CHALLENGE LAYER: {layer} (q: {sub_q}) ===")
            exchanges.append(challenge_layer(task, layer, sub_q, brief, rounds, attachments))

        print("\n=== REPORTER: final report ===")
        final = report(task, exchanges, brief, attachments)
        print(final)

        if add_senior:
            try:
                import senior_analyst as sr
                print("\n=== SENIOR ANALYST (07) verdict ===")
                senior_text = sr.senior_verdict(
                    task,
                    "\n\n".join(t["text"] for ex in exchanges for t in ex["turns"]),
                    final, brief, effort="high")
                print(senior_text)
            except Exception as e:
                print(f"[!] senior verdict skipped: {e}")
    finally:
        if exchanges or final:
            _save(out_dir, task, files, layers, final, senior_text, exchanges, stamp)
            tag = "" if final else "   (PARTIAL - run was interrupted)"
            print(f"\nSaved -> {os.path.join(out_dir, 'report.md')}{tag}")


def main():
    p = argparse.ArgumentParser(description="AMKOR Challenger (Agent 08).")
    p.add_argument("task", nargs="*")
    p.add_argument("--files", nargs="*", help="Specific files (default: all of uploads/).")
    p.add_argument("--layers", nargs="*", choices=list(LAYERS), help="Force layers.")
    p.add_argument("--rounds", type=int, default=1, help="Challenge rounds per layer (default 1).")
    p.add_argument("--senior", action="store_true", help="Also run the Senior Analyst (07) verdict.")
    p.add_argument("--allow-no-files", action="store_true",
                   help="Proceed even with zero uploads (analyze the data brief alone).")
    p.add_argument("--dry-run", action="store_true", help="Ingest only; no API calls.")
    args = p.parse_args()

    task = " ".join(args.task).strip() or input("Task (usually about your uploaded files)?\n> ").strip()
    if not task:
        return
    try:
        run(task, args.files, args.layers, args.rounds, args.senior, args.dry_run,
            args.allow_no_files)
    except ac.NoApiKey as e:
        print(f"\n[!] {e}")
    except Exception as e:
        print(f"\n[!] Run error: {e}\n    Any completed work was saved under data/reports/.")


if __name__ == "__main__":
    main()
