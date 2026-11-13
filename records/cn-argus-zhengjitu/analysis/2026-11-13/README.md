# Zhengjitu gearing archive — November 13, 2026

This archive separates the current-week recommendation from the attainable
Farseer end-state study. Neither plan records an in-game purchase or expenditure.

## Read the results

- `report.html`: current gear, Great Vault and Kindo'jan choices, and the one-core plan.
- `endstate-report.html`: complete future loadouts and matched ring comparisons.
- `comparison-results.json`: 66 accepted current-week finalist comparisons.
- `endstate-comparison.json`: 36 accepted end-state finalist comparisons.
- `screening-summary.json`: compact observations for all exploratory, final and
  static runs, including explicit rejected inputs.
- `elite-evidence.json`, `reward-source-evidence.json` and
  `endstate-source-audit.json`: dated sources, acquisition limits and unknowns.

The original full addon export and parsed inventory are in
`../../snapshots/2026-11-13-1320.*`. The current-week ledger is
`../../weeks/2026-11-12.json`.

## Rebuild the reports

From the repository root, using Python 3:

```powershell
python records/cn-argus-zhengjitu/analysis/2026-11-13/build-report.py
python records/cn-argus-zhengjitu/analysis/2026-11-13/build-endstate-report.py
```

The dated renderer is included as `report-renderer.py`; rebuilding does not
depend on another character's uncommitted files. The builders also reconcile
the associated profile and proposed weekly plans. Use a scratch checkout when
only reproducing the reports after newer character results have been recorded.

## Reproduce simulations

The original executable was native SimulationCraft Live 12.1.5.70783, source
commit `de11f57df75dda668bae6ac7043a43b98831fa96`. Source and executable hashes,
talents, model parameters, seeds and acquisition boundaries are preserved in
`simc-manifest.json` and `endstate-manifest.json`.
The character's scoped `.gitattributes` preserves LF endings for these dated
inputs and results so Windows checkouts keep the recorded source hashes.

The study runners expect that source checkout at `.local/simc-source-70783`
and the built executable at `.local/simc-build-70783/Release/simc.exe`.
Alternatively, run the committed `.simc` inputs with an equivalent compatible
executable. The engine and build directory are not archived in Git.

Every run input and validation record is retained. Raw 6000-iteration finalist
JSON and unbuffed snapshot JSON are included. Exploratory raw JSON, duplicate
text reports, progress logs and export-reimport raw JSON remain local under
this directory's `.gitignore`; their compact measurements and validation
outcomes remain reviewable. Runners regenerate missing raw results rather than
treating a validation-only cache as a completed native run.

`export-validation.json` and `endstate-export-validation.json` cover all eight
clean exports. The browser validation files and screenshots record desktop,
mobile, model-tab and download checks. Offline reports include item icons;
Wowhead hover tooltips require a network connection.
