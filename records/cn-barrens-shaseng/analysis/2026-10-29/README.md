# Shaseng equipment and talent archive — October 29, 2026

Start with [report.html](report.html), [review.md](review.md),
[tuning-review.md](tuning-review.md) and
[crafting-followup.md](crafting-followup.md).
The original equipped-only input and parsed inventory are
[2026-10-29-equipped.simc](../../snapshots/2026-10-29-equipped.simc) and
[2026-10-29-equipped.items.json](../../snapshots/2026-10-29-equipped.items.json).
Archive preparation makes no acquisition, resource or recommendation changes.

## Retained evidence

- Every existing simulation input, validation record, clean downloadable export,
  report, screenshot, original-source response and generating tool.
- All 154 final/control/static native JSON results, including the 7000-iteration
  equipment finalists, 12000-iteration tuning controls, 10000-iteration talent
  controls, 6000-iteration placement tests and 8000-iteration two-craft tests.
- Full static native JSON, including the current, upgraded and optional tuning
  snapshots required by the report builders. They are intentionally retained
  even though their run length is only 40 requested iterations.
- [screening-summary.md](screening-summary.md) and
  [screening-summary.json](screening-summary.json): all 372 native runs,
  including 218 local-only superseded screens/smokes, their exact measurements,
  warnings, input/result hashes and original acceptance sources.

The dated `.gitignore` excludes only the identified screening raw JSON,
repeated simulation text/progress logs and Python runtime caches. Every
validation record remains included. All retained evidence from October 26
used by the research links is part of the accompanying archive.

## Rebuild the report

From the repository root with Python 3:

```powershell
python records/cn-barrens-shaseng/analysis/2026-10-29/build-tuning-summary.py
python records/cn-barrens-shaseng/analysis/2026-10-29/assemble-report.py
python records/cn-barrens-shaseng/analysis/2026-10-29/build-report.py
```

These tools read retained validations, native static JSON and research data,
and rewrite dated summaries, clean exports and the report. They do not write
the profile or weekly ledger. To render only the already archived report data,
run just `build-report.py`. Archive preparation checked its pure renderer in
memory; the resulting HTML exactly matches the saved report after newline
decoding. No report-writing builder was executed in the shared working tree.

The simulation study tools use one another through local `runpy` imports;
all those modules are retained in this directory. Reproducing simulations
requires the matching source/binary from `simc-manifest-native70575.json`,
`tuning-manifest.json`, `talent-manifest.json` and the crafting manifests.
The original source path was `E:/github/simc`, commit
`710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`, and executable path was
`.local/simc-build/Release/simc.exe`. Engine/build directories are not archived.
The stale embedded revision and native 70575 data distinction remain as
documented in the original review.

## Validation and limits

[archive-validation.json](archive-validation.json) records parsing, syntax,
report/download dependencies and line-ending/provenance checks. Final native
results and the full static JSON remain available independently of local caches.
Run tables preserve requested iterations, engine-reported iterations and
effective samples as separate fields; short runs are not ranking evidence.

The scoped `.gitattributes` retains original dated bytes, including CRLF SimC
inputs, while fixing new archive metadata/tools and the LF equipped snapshot
to LF. Older tracked dates are outside its scope. No original input was
formatted. Existing browser checks/screenshots are historical; no simulations,
new browser checks or source refreshes were run for archive preparation.
