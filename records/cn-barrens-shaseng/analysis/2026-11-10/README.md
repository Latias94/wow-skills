# Shaseng attainable equipment archive — November 10, 2026

Start with [report.html](report.html), [review.md](review.md) and
[comparison-results.json](comparison-results.json). Original conclusions,
current resources and acquisition records remain unchanged.
Both complete original exports are retained:
[21:35](../../snapshots/2026-11-10.simc) and
[22:03](../../snapshots/2026-11-10-2203.simc), together with their parsed
`.items.json` companions. The report links the existing
[weekly ledger](../../weeks/2026-11-05.json).

## Retained evidence

- Every existing simulation input and validation record; all report data,
  clean downloads, original item/player evidence, screenshots and tools.
- All 30 final 6000-iteration native JSON results, all six static snapshots,
  the old-engine identity check and all four native export-reimport results.
  The 41 retained full JSON results preserve the original evidence boundaries.
- [screening-summary.md](screening-summary.md) and
  [screening-summary.json](screening-summary.json): all 91 native runs,
  including the 50 local-only 2000-iteration screens. Measurements, warnings,
  input/result hashes and existing acceptance records are preserved.
- [export-validation.json](export-validation.json), both browser screenshots
  and the existing browser validation receipt.

Only screening raw JSON, repeated native text/progress output, build/reimport
logs and explicit Python runtime caches remain local under `.gitignore`.
No file is deleted. Static and reimport runs are not DPS ranking evidence.

## Rebuild without `.local` report tools

The small assembler formerly present only at
`.local/build-shaseng-report-20261110.py` is preserved as `assemble-report.py`.
Only its root resolution changed so that it works from its dated location.
The compatible October 29 renderer is included as `build-report.py`.

From the repository root with Python 3:

```powershell
python records/cn-barrens-shaseng/analysis/2026-11-10/assemble-report.py
python records/cn-barrens-shaseng/analysis/2026-11-10/build-report.py
```

The assembler reads the preserved validations, inputs, item/player evidence,
22:03 parsed snapshot, and
[October 29 report data](../2026-10-29/report-data.json) for gem names.
It rewrites only dated report data, comparison summaries, Markdown and four
clean SimC exports; it does not write a ledger or profile. To render only the
saved report data, run just `build-report.py`. Its pure in-memory rendering
exactly matches the saved report after newline decoding. The assembler was
syntax/dependency checked but not executed in the shared working tree.

The native engine was Live 12.1.5.70783, source commit
`de11f57df75dda668bae6ac7043a43b98831fa96`. The original runner expects
`.local/simc-source-70783` and `.local/simc-build-70783/Release/simc.exe`;
their hashes and boundaries remain in `simc-manifest.json`. Those runtime
directories are not archived. The original runner accepts a successful
validation as a cache hit even when its raw JSON is missing. To regenerate a
local-only screen in a clean clone, invoke the preserved `.simc` directly with
the matching engine and explicit `json2`/`output` destinations.

## Validation and provenance limits

[archive-validation.json](archive-validation.json) records parsing, syntax,
dependencies, report/download links and byte checks. No simulation, new browser
session or external-source refresh was performed. Historical browser evidence
is retained and is not presented as a new check.

The original full SimC exports use CRLF. `simc-manifest.json` hashes the exact
22:03 CRLF bytes, whereas `intake-update-2203.json` records LF-normalized hashes
for both exports. Both forms are verified without changing either record.
The scoped `.gitattributes` therefore uses `-text` for those exact original
exports and the dated original artifacts. New archive metadata/tools and the
originally LF equipped-only exports use LF. No raw SimC was reformatted and
older tracked dates are unaffected.

The four reimport runs have their base clean exports and full native JSON, but
no separate command-line transcript or `*-reimport.simc` was originally saved.
Their `input_file` and requested iteration fields are deliberately unknown in
the new inventory; `source_export_file` points to the retained base export.
The old-engine identity run has no standalone acceptance receipt, so the
summary leaves acceptance unknown rather than inventing a pass.
