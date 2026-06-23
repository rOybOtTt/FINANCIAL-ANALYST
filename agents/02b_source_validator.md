# Agent 02b — Source Validator

**Status:** ✅ Built and tested (live)
**Script:** [`../source_validator.py`](../source_validator.py)
**Triggered by:** the Tech Agent (02) calls it for **every** candidate source.
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

Decide whether a web source is **reliable enough** to use in tech research, so
the Tech Agent never reports findings from low-quality or untrustworthy sites.

## Activation

- **Automatic:** Tech Agent (02) validates each candidate URL before keeping it.
- **Standalone — vet any URL yourself:**
  ```bash
  python source_validator.py https://arxiv.org/abs/2401.12345
  python source_validator.py https://spectrum.ieee.org/advanced-packaging
  python source_validator.py https://some-blog.blogspot.com/post --fetch
  ```
  `--fetch` downloads the page to also check author / date / citations.

## Scoring (0–100)

| Signal | Points |
|--------|--------|
| Discovered via scholarly index (arXiv +60, Crossref/Semantic Scholar +50) | + |
| In registry, **tier 1** (peer-reviewed/academic/standards) | +60 |
| In registry, **tier 2** (reputable analysis/journalism/analyst firm) | +45 |
| Trusted TLD (`.edu` / `.gov`) | +30 |
| HTTPS | +8 |
| Page has an author byline *(needs page HTML)* | +10 |
| Page has a publication date *(needs page HTML)* | +10 |
| Page has citations / DOI / references *(needs page HTML)* | +14 |
| Matches a low-quality signal (blogspot, medium, reddit, quora, …) | −40 |

Score is clamped to 0–100.

## Verdict

| Score | Verdict | Tech Agent action |
|-------|---------|-------------------|
| ≥ 60 | **RELIABLE** | keep |
| 40–59 | **BORDERLINE** | keep |
| < 40 | **UNRELIABLE** | drop |

Standalone exit code: `0` unless the verdict is `UNRELIABLE` (then `1`).

## Registry

Reads [`../reliable_sources.json`](../reliable_sources.json): trusted `sources`
(domain + tier + type), `trusted_tlds`, and `low_quality_signals`. Domain
matching is suffix-aware, so `ieeexplore.ieee.org` matches the `ieee.org` entry.

## Verified

- `spectrum.ieee.org` → **RELIABLE 68** (tier 1 + https).
- `*.blogspot.com` → **UNRELIABLE 0** (low-quality signal −40).
- Crossref DOIs resolved to `link.springer.com` → **RELIABLE 100** (scholarly
  channel + tier 1).

## Tuning knobs (top of the script)

- `RELIABLE_THRESHOLD` / `BORDERLINE_THRESHOLD` — verdict cutoffs.
- `SCHOLARLY_CHANNELS` — discovery-channel bonuses.
- The `_AUTHOR_RE` / `_DATE_RE` / `_CITE_RE` regexes — page-signal detection.
