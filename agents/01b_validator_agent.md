# Agent 01b — Validator Agent

**Status:** ✅ Built and tested (live against AMKR)
**Script:** [`../validator_agent.py`](../validator_agent.py)
**Triggered by:** runs **automatically** at the end of every Data Agent (01) run.
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

Validate the filings that the Data Agent saved — confirm every report is really
on disk, complete, readable, and not a fake/error page — so we never analyze
broken or missing data.

## Activation

- **Automatic:** the Data Agent calls `validate_run()` at the very end of every
  run. Disable with `python data_agent.py ... --no-validate`.
- **Manual / standalone:**
  ```bash
  python validator_agent.py            # validate the last run
  python validator_agent.py --strict   # warnings also cause a non-zero exit
  ```

## What it checks (per company and per filing)

1. `manifest.json` exists and is readable for each company in the last run.
2. Every filing in the manifest has its folder on disk.
3. The primary document file exists and is **not empty / not suspiciously tiny**
   (< 1 KB → warning).
4. The document is **NOT** an EDGAR rate-limit / "access denied" / error page.
5. The document contains **real filing markers** (HTML / XBRL / SEC text).
6. `_meta.json` exists for the filing.
7. The filing date falls **inside the requested lookback window**.
8. Folder count on disk matches the manifest count (nothing missing/extra).

## Status levels

| Level | Meaning |
|-------|---------|
| **PASS** | Everything checks out. |
| **WARN** | Non-fatal oddity (tiny file, date outside window, disk/manifest count mismatch). |
| **FAIL** | Missing file, empty file, unreadable, or detected error page. |

Exit code: `0` if no FAIL (and, under `--strict`, no WARN); otherwise `1`.

## Output

- Console report: PASS / WARN / FAIL per company and per problem filing.
- `data/_validation_report.json` — full machine-readable results.

## Verified run

After `python data_agent.py AMKR --forms 10-K`, the validator auto-ran and
reported the 10-K document as **PASS** (correct content markers, full size),
with a WARN flagging that more folders existed on disk than the latest manifest
listed — i.e. the count cross-check working as intended.

## Tuning knobs (top of the script)

- `MIN_DOC_BYTES` — size threshold below which a doc is "suspiciously small".
- `ERROR_MARKERS` — strings that identify an EDGAR throttle/error page.
- `CONTENT_MARKERS` — strings expected in a genuine filing.
