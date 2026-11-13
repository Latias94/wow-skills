"""Run the four requested equipment identities with sourced level-341 overrides."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
TOOLS = runpy.run_path(str(HERE / "gear-run.py"))
SLOTS = TOOLS["SLOTS"]
FIELDS = TOOLS["fields"]
UPDATE = TOOLS["update"]
RUN = TOOLS["run"]


def prepare(source, name, iterations=6000, unbuffed=False):
    output = []
    overrides = {}
    for line in source.read_text(encoding="utf-8").splitlines():
        key = line.split("=", 1)[0]
        if key in SLOTS and "12856" in FIELDS(line).get("bonus_id", "").split("/"):
            before = FIELDS(line)
            line = UPDATE(line, ilevel=341)
            assert FIELDS(line)["bonus_id"] == before["bonus_id"]
            overrides[key] = {"item_id": int(before["id"]), "ilevel": 341, "bonus_id": before["bonus_id"]}
        if key == "iterations":
            line = f"iterations={iterations}"
        if key == "seed":
            line = "seed=2610202631"
        if unbuffed and key in ("flask", "food", "augmentation", "potion", "temporary_enchant"):
            line = f"{key}=disabled"
        if unbuffed and key in ("optimal_raid", "override.bloodlust"):
            line = f"{key}=0"
        output.append(line)
    assert len(overrides) == (4 if "elite_full" in source.stem else 3)
    output.insert(0, "# Compatibility model: level 341 sourced from current WCL display; not new bonus/DBC evidence.")
    path = HERE / f"gear-{name}.simc"
    path.write_text("\n".join(output) + "\n", encoding="utf-8")
    return path, {"source_input": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                  "overrides": overrides, "requested_iterations": iterations,
                  "metadata_family": "literal_export" if "literal" in source.stem or "elite_full" in source.stem else "historical_precursor_continuity"}


def main():
    manifest = {
        "created_at": datetime.now().astimezone().isoformat(),
        "override_source": "October 26 logged-in WCL character pages, supplied by the main agent and preserved in the local page JSON files.",
        "source_evidence": ["wcl-shaseng-page.json", "wcl-elite-page.json"],
        "source_limits": "WCL display evidence for compatibility overrides, not evidence that old DBC or bonus resolution has been updated.",
        "user_wcl_average": 331.75, "elite_wcl_average": 334.81,
        "old_dbc_bonus_level": 340, "compatibility_level": 341,
        "candidate_identities": ["current", "waist_331_cm", "raid_ring_334", "elite_full"],
        "comparison_policy": "Current/waist/ring share the historical-precursor baseline. Elite gear compares only to an extra literal-export current baseline, without mixing precursor families.",
        "runs": {},
    }
    # Save the previous summary as an explicitly superseded audit record.
    audit_path = HERE / "gear-summary-original-bonus.json"
    if not audit_path.exists():
        old = json.loads((HERE / "gear-summary.json").read_text(encoding="utf-8"))
        old["audit_status"] = "Original-bonus 340 model retained for audit. Its item-level conclusions are superseded by current WCL 341 display evidence."
        audit_path.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    smoke = [
        ("unbuffed-current", "gear-verify-raid-current.simc", True),
        ("unbuffed-literal-current", "gear-screen-literal-raid-current.simc", True),
        ("unbuffed-elite_full", "gear-screen-raid-elite_full.simc", True),
        ("smoke-slice-current", "gear-verify-slice-current.simc", False),
        ("smoke-raid-current", "gear-verify-raid-current.simc", False),
    ]
    jobs = []
    for name, filename, unbuffed in smoke:
        path, info = prepare(HERE / filename, f"compat341-{name}", 40, unbuffed)
        manifest["runs"][path.stem] = info
        jobs.append(path)
    for mode in ("slice", "raid"):
        sources = {
            "current": f"gear-verify-{mode}-current.simc",
            "waist_331_cm": f"gear-verify-{mode}-waist_331_cm.simc",
            "raid_ring_334": f"gear-verify-{mode}-raid_ring_334.simc",
            "literal-current": f"gear-screen-literal-{mode}-current.simc",
            "elite_full": f"gear-screen-{mode}-elite_full.simc",
        }
        for key, source in sources.items():
            path, info = prepare(HERE / source, f"compat341-{mode}-{key}")
            manifest["runs"][path.stem] = info
            jobs.append(path)
    (HERE / "gear-compat341-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for path in jobs:
        RUN(path)


if __name__ == "__main__":
    main()
