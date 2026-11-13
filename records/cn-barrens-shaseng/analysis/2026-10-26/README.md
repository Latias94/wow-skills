# Shaseng coaching and equipment archive — October 26, 2026

Start with [review.html](review.html), [cast-review.md](cast-review.md),
[gear-review.md](gear-review.md) and [mechanics-review.md](mechanics-review.md).
These are the original dated conclusions. Archiving does not update the
character's equipment, resources, profile or weekly ledger.

The original equipped-only export is
[2026-10-26-equipped.simc](../../snapshots/2026-10-26-equipped.simc).
Historical Catalyst precursor assumptions still refer to the retained
[October 23 export](../../snapshots/2026-10-23.simc).

## Retained evidence

- Every existing simulation input and validation record, all report sources,
  downloads, screenshots and generating tools.
- All WCL JSON, HTML, text responses and exported profiles. In particular,
  `wcl-*.txt` files are original evidence, not repeated simulation text.
- The complete `references/` directory, including the five guide screenshots.
- All 25 final/control/static native JSON results: compatibility comparisons,
  talent controls, verification runs and unbuffed snapshots.
- [screening-summary.md](screening-summary.md) and
  [screening-summary.json](screening-summary.json): measurements and acceptance
  sources for all 51 native runs, including 26 local-only screens/smokes.

The dated `.gitignore` leaves only redundant screening/smoke JSON,
`gear-*.txt`, progress logs and explicit Python caches local. No file is
deleted. Native warnings and exact run/input hashes remain in the summary.
Smoke and static runs are not DPS ranking evidence.

## Rebuild the readable report

From the repository root with Python 3:

```powershell
python records/cn-barrens-shaseng/analysis/2026-10-26/build-review.py
```

The builder reads the retained `cast-analysis.json`, `burst-evidence.json`
and `gear-summary.json`, and rewrites only the dated HTML/Markdown report.
It does not need local-only simulation outputs or another character's files.
The event-analysis tools retain all their WCL input dependencies.

`gear-summarize.py` is the original deeper audit tool. It requires the omitted
screening JSON and simulation text/progress logs; the saved `gear-summary.json`
is sufficient to rebuild the report. Recomputing that audit from a clean clone
requires restoring the local outputs or rerunning the preserved inputs with
the original engine. It was not executed during archiving.

The original engine/source identity is in `gear-manifest.json`: source commit
`73a372b76188c703e48729caded3258cdc5b726b`, with the executable originally at
`.local/simc-build/Release/simc.exe` and source at `E:/github/simc`.
That mutable path alone does not establish the original engine version;
check the recorded executable SHA before reproducing. The 341 compatibility
model and its limitations remain unchanged.

## Validation and byte preservation

[archive-validation.json](archive-validation.json) records JSON parsing,
script syntax, report/download dependency checks and provenance checks.
The original `verification.json` remains unchanged and also indexes local-only
artifacts; it must not be interpreted as a list of committed files.

The character-scoped `.gitattributes` preserves original dated bytes, including
CRLF simulation inputs and evidence covered by existing SHA-256 records.
New archive metadata/tools and the originally LF equipped export use LF.
No original SimC or evidence file was reformatted. Browser screenshots and
browser verification are historical; no new simulation, browser session or
external-source verification was performed for this archive.
