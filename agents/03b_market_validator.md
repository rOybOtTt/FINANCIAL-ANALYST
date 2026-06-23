# Agent 03b — Market Data Validator

**Status:** ✅ Built and tested (live)
**Script:** [`../market_validator.py`](../market_validator.py)
**Triggered by:** runs **automatically** at the end of every Market Agent (03) run.
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

Confirm the market data pulled by Agent 03 is trustworthy before it is used for
analysis — the financial numbers are corroborated by two independent sources and
the news comes only from reliable outlets.

## Activation

- **Automatic:** Market Agent (03) calls `validate_run()` after pulling all data.
- **Standalone:**
  ```bash
  python market_validator.py
  python market_validator.py --strict   # warnings also cause a non-zero exit
  ```

## Checks (per company snapshot)

1. **Cross-source price** — Yahoo price vs CNBC price agree within **2%**
   (the core check; two independent sources must corroborate the number).
2. **Previous-close agreement** between the two sources.
3. **Field sanity** — price present and > 0; price inside the 52-week range;
   52-week low ≤ high.
4. **News reliability** — every kept news item re-validated through the Source
   Validator (02b); none may be `UNRELIABLE`; list should be non-empty.
5. **Freshness** — snapshot generated within the last 2 days.

## Verdict

| Level | Meaning |
|-------|---------|
| **PASS** | All checks clean. |
| **WARN** | Non-fatal (single-source price, empty news, slightly stale, price just outside 52-wk range). |
| **FAIL** | Price mismatch between sources, missing/invalid price, or an unreliable news item slipped in. |

Writes `data/market/_validation_report.json`. Standalone exit code `0` unless a
`FAIL` (or any `WARN` under `--strict`).

## Verified

Full competitor run → AMKR / ASX / IMOS / JCET / Powertech all **PASS**; Tongfu
(no English reliable news) correctly **WARN**. Tunable via `PRICE_TOLERANCE` and
`FRESH_MAX_DAYS` at the top of the script.
