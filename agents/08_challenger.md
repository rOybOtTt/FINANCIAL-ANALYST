# Agent 08 — Challenger (document orchestrator)

**Status:** ✅ Built (LLM agent — needs `ANTHROPIC_API_KEY` to run)
**Script:** [`../agent8_challenger.py`](../agent8_challenger.py)
**Model:** `claude-opus-4-8` (adaptive thinking, streaming, native PDF) via the Anthropic SDK
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

A **task-driven, document-centric orchestrator**. You upload files manually and
give it a task; it reads the files, routes them through the analysis layers the
task needs, **challenges** each one adversarially, and hands the result to the
Reporter for a final write-up. Most tasks are expected to be *about the uploaded
files*.

## Upload files

Drop files in [`../uploads/`](../uploads/). Supported:
- **PDF** (`.pdf`) — read **natively by Claude** (no extra dependency)
- **Word** (`.docx`), **HTML** (`.htm/.html`)
- **Text/data** (`.txt`, `.md`, `.csv`, `.tsv`, `.json`, `.yaml`, `.log`)

## The four stages

1. **Ingest** — read every upload (or `--files ...`). PDFs are **read natively by
   Claude** — the real PDF is attached to the analysis/challenge/report calls
   (not just a summary) — and also get a short text **digest** that goes in the
   brief as an index. docx/html/text/csv are extracted to text. Bad/empty/
   oversize/unsupported files are skipped *loudly*, and a missing `--files`
   path aborts rather than silently analyzing nothing.
2. **Route** — an LLM dispatcher decides which layers the task needs
   (**Financial 04**, **Tech 05**, or both) and writes a focused sub-question for
   each. Override with `--layers financial tech`.
3. **Q&A + Challenge** — for each chosen layer: the layer **answers**, the
   **Challenger** stress-tests it (unsupported claims, missing risks, alternative
   readings, toughest questions), the layer **defends/revises**. Repeat
   `--rounds N` times (each round targets the revised answer).
4. **Report** — the **Reporter** writes the final analysis (executive answer, key
   findings, what the challenge changed, open risks, recommendation). With
   `--senior`, the **Senior Analyst (07)** adds a valuation/KPI verdict.

Output is saved to `data/reports/<task-slug>/` (`report.md` + `transcript.json`).

## Usage

```bash
$env:ANTHROPIC_API_KEY = 'sk-ant-...'

python agent8_challenger.py "Review the uploaded 10-K for margin and growth risks"
python agent8_challenger.py "Compare the uploaded deck to our market data" --files uploads/deck.pdf
python agent8_challenger.py "..." --layers financial          # force a layer
python agent8_challenger.py "..." --rounds 2                   # tougher challenge
python agent8_challenger.py "..." --senior                     # add Senior (07) verdict
python agent8_challenger.py "..." --dry-run                    # ingest only, no API
```

| Flag | Effect |
|------|--------|
| `--files ...` | Specific files (default: everything in `uploads/`) |
| `--layers ...` | Force layers (`financial`, `tech`) instead of auto-routing |
| `--rounds N` | Challenge rounds per layer (default 1) |
| `--senior` | Also run the Senior Analyst (07) valuation/KPI verdict |
| `--dry-run` | Ingest + build the brief only; **no API calls** |

## How it "challenges each agent"

The adversarial **answer → challenge → defense** loop is the core. The Challenger
is prompted to refute, not agree — it must cite the document/number/source and
end with the toughest questions, and the layer must defend strictly on the
evidence. This is the same adversarial-verification pattern used to harden the
data agents, applied at question time.

## Verified

`--dry-run` confirmed ingestion + brief assembly; targeted tests confirmed the
hardened helpers (non-UTF-8 reads, corrupt-docx/fake-PDF rejection, robust router
JSON parsing, `--files` resolution, zero-upload guard). The implementation went
through a **multi-agent adversarial review** (24 agents, 5 dimensions, every
finding verified against the code) which surfaced **18 real issues — all fixed**:

- PDFs are now **attached natively** to the analysis/challenge/report calls (was:
  lossy digest only).
- Non-UTF-8 uploads no longer crash the run (lenient decode).
- Corrupt/empty/fake files are detected and skipped loudly (not silently empty).
- docx tables keep cell/row structure; HTML comments handled.
- Text uploads cap raised to 400K chars with an explicit truncation marker.
- Router `max_tokens` raised + balanced-brace JSON parsing + visible fallback.
- Unique timestamped output dirs (no overwriting prior reports).
- Partial work is saved even if a mid-run API call fails.
- Zero-upload runs abort unless `--allow-no-files`.

LLM stages require `ANTHROPIC_API_KEY`.

## Notes

- PDFs use Claude's native document input (base64 block) — no `pypdf` dependency.
  The same PDF is attached to the answer/challenge/defense/report calls so the
  challenge is grounded in the real source (costs more tokens on large PDFs).
- The combined brief (data + uploads) is sent as a **cached** system block, reused
  across routing, every challenge turn, and the report.
