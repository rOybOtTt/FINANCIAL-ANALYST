# Agent 06 — Synthesizer

**Status:** ✅ Built (LLM agent — needs `ANTHROPIC_API_KEY` to run)
**Script:** [`../synthesizer.py`](../synthesizer.py)
**Model:** `claude-opus-4-8` (adaptive thinking, streaming) via the Anthropic SDK
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

Take the **full debate** between the Financial Analyst (04) and the Tech Analyst
(05) and summarize it into **one balanced answer** to your question.

## Input

- The debate transcript (from [`debate.py`](../debate.py)).
- The same shared DATA BRIEF.

## Output (four sections)

1. **Points of agreement** — where both analysts converged.
2. **Key disagreement(s)** — the real crux, stated fairly for each side.
3. **Who had the stronger evidence** — judged only on the DATA BRIEF.
4. **Bottom line** — a clear, balanced answer + the main caveat / what data would
   change it.

It is instructed to be fair to both sides and not introduce new facts neither
analyst raised.

## Run it (runs the debate first, then summarizes)

```bash
$env:ANTHROPIC_API_KEY = 'sk-ant-...'
python synthesizer.py "Is Amkor a better buy than ASE right now?"
python synthesizer.py "..." --rounds 2     # deeper debate before summarizing
```

Usually invoked as stage 3 of the **Senior Analyst (07)** pipeline.

## Notes

Runs at `high` effort by default (it's the judging step). Same key/SDK/caching
requirements as the other analysts.
