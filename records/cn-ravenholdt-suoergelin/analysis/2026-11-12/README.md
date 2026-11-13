# Suoergelin Arms archive — November 12, 2026

This archive preserves two successive studies of CN/Ravenholdt 索尔葛林.
`report.html`, `report-data.json`, `target-slot-map.json` and `review.md` are
the initial equipped-only WCL/source study. `full-report.html`, its `full-*`
data and `full-review.md` are the later complete 18:29 addon study. The initial
report remains dated history; its weekly-ledger download points to the same
ledger subsequently reconciled by the full study. `../../profile.json` and
`../../weeks/2026-11-12.json` retain that later state. Proposed loadouts and
resource allocations are not recorded acquisitions or expenditures.

## Retained evidence

- `../../snapshots/2026-11-12-wcl.*`: original equipped-only export and intake.
- `../../snapshots/2026-11-12-1829.*`: complete raw addon export and parsed intake,
  including commented inventory, Catalyst predecessors, Omnium and roll history.
- Every `.simc` input and all 83 `full70783-*.validation.json` records: 39 initial
  2000-iteration screenings, 39 final 6000-iteration comparisons across three
  models, and five 20-iteration unbuffed static snapshots.
- All 39 final native JSON results, all five static native JSON results and
  the three short native identity JSON results.
- `full-comparison-results.json`: 13 finalists across three models, plus all
  83 historical run validations. `screening-summary.json` adds compact native
  observations and SHA-256 hashes, including the four export reimports.
- Both HTML/data pairs, their screenshots and browser validations, four clean
  `.simc` downloads, `full-export-validation.json`, and dated source evidence.
- `archive-validation.json`: this archival check, dependency hashes and limits.

Only exploratory 2000-iteration raw JSON, duplicate text reports, progress logs
and export-reimport raw JSON are ignored. They remain on disk. Their input,
native-result and validation hashes and compact measurements are retained in
`screening-summary.json`; the original accepted validations remain authoritative.
Static and identity runs are not evidence for personal DPS rankings.

The scoped `../../.gitattributes` preserves historical bytes, including mixed
LF/CRLF endings. In particular, the complete raw export still has SHA-256
`34e5e588fb1fc2880af4d477272d1998d768d9bde2cdfb8704ca5f2f8312a0c1`.
The three fetched Wowhead HTML captures also retain 11 upstream trailing-space
lines; their scoped whitespace exception preserves these source bytes.

## Report dependencies and rebuilding

`build-report.py` is the archived copy of
`.local/build-arms-report-20261112.py`. `build-full-report.py` copies
`.local/build-arms-full-report-20261112.py` with one dependency-path change:
it reads `full-report-icons.json` here. That JSON is a byte-for-byte snapshot
of `records/cn-barrens-shaseng/analysis/2026-11-10/item-icons.json`, preserving
the original merged icon values without requiring that other study directory.

Both builders use Python 3 standard-library modules and the shared renderer at
`records/cn-barrens-shaseng/analysis/2026-10-29/build-report.py`. Include that
single file in the coordinated main-thread archive; its hash is recorded in
`archive-validation.json`. The source-only builder additionally reads its WCL
snapshot/intake, `elite-evidence.json`, `item-icons.json`, `candidate-tooltips.json`
and `current-tooltips.json`. The full builder reads the initial `report-data.json`,
the complete snapshot/intake, local icon files, final validation/input files and
static validations. All character-specific inputs are retained in this archive.
Report rebuilding requires neither the SimulationCraft executable nor `.local`
copies of the two builders.

These historical builders write reports, validations, exports, profile and weekly
state. The initial builder writes some files before asserting that no profile
exists. Rebuild in a fresh scratch tree, omitting the live profile and ledger;
then run the source-only stage before the full stage. From the repository root:

```powershell
$repo = (Get-Location).Path
$role = 'records/cn-ravenholdt-suoergelin'
$dated = "$role/analysis/2026-11-12"
$renderer = 'records/cn-barrens-shaseng/analysis/2026-10-29'
$scratch = Join-Path ([IO.Path]::GetTempPath()) ('arms-archive-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $scratch "$role/analysis"), (Join-Path $scratch "$role/weeks"), (Join-Path $scratch $renderer) | Out-Null
Copy-Item -LiteralPath (Join-Path $repo "$role/snapshots") -Destination (Join-Path $scratch $role) -Recurse
Copy-Item -LiteralPath (Join-Path $repo $dated) -Destination (Join-Path $scratch "$role/analysis") -Recurse
Copy-Item -LiteralPath (Join-Path $repo "$renderer/build-report.py") -Destination (Join-Path $scratch $renderer)
Push-Location $scratch
try {
    python "$dated/build-report.py"
    if ($LASTEXITCODE -ne 0) { throw 'Source-only report rebuild failed.' }
    python "$dated/build-full-report.py"
    if ($LASTEXITCODE -ne 0) { throw 'Full report rebuild failed.' }
} finally {
    Pop-Location
}
```

The copied scratch outputs may be overwritten by these commands. Generated
timestamps can differ from the historical archive. The archive preparation did
not execute either historical builder or overwrite an existing report or ledger.

## Simulation provenance and reusable checks

`full-simc-manifest.json` records Live 12.1.5.70783, source commit
`de11f57df75dda668bae6ac7043a43b98831fa96` and executable SHA-256
`57c6858151630ea8e70b8f714d18c94a172aaf0e2bad5699d9bf5cf613674160`.
`personal-study.py` expects the source at `.local/simc-source-70783` and executable
at `.local/simc-build-70783/Release/simc.exe`; these build assets are not in Git.
Final inputs request 6000 iterations with seed 26111253; screening inputs request
2000 with seed 26111231; static inputs request 20 with seed 26111255. Native
iteration counters and collected sample counts are preserved separately in the
summary; final DPS distributions contain 5999 samples.

The runner skips an accepted validation even if its native raw JSON is absent.
To regenerate an ignored raw result, run its retained `.simc` directly with the
compatible native executable in a fresh scratch tree, or use a separate runner
scratch tree without the old validation cache. An accepted validation alone does
not establish that a native result was regenerated.

The archival checks parse JSON and Python without running simulations, reconcile
all 83 native results with their validations and the combined results, verify
download targets and file hashes, and preserve all pre-existing character files.
`identity-validation.json`, both browser validations and their four screenshots
are historical evidence. `full-export-validation.json` records four successful
clean-export reimports; their native gear and fight-style evidence can be reused.

The preliminary DungeonSlice identity result has no separate retained `.simc`
or exact invocation. Its native JSON settings and the initial identity input
remain available; the missing invocation is recorded as a provenance limit in
`screening-summary.json`, rather than reconstructed as a historical fact.

No new DPS simulation or browser session was run for this archive. Exact server
reward exclusions/previews and the unverified native item-effect assumptions in
`full-review.md` remain open. Wowhead hover tooltips require network access; item
icons are embedded. Scientific conclusions, balances and proposed resource use
are unchanged by archival preparation.
