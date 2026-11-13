"""Compare only two talent strings while keeping the user's latest gear fixed."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
run = runpy.run_path(str(HERE / "gear-run.py"))["run"]
elite_talents = next(line for line in (HERE / "wcl-elite-profile.simc").read_text(encoding="utf-8").splitlines() if line.startswith("talents="))
manifest = {"created_at": datetime.now().astimezone().isoformat(), "iterations": 3500, "seed": 2610202641,
            "equipment": "User latest equipment with historical-precursor continuity and sourced ilevel=341 compatibility overrides.",
            "interpretation": "Full talent-string sensitivity only, not a recommendation to switch or a single-talent causal estimate. Actual fight casts and cooldowns also depend on build and encounter length.",
            "runs": {}}
for mode in ("slice", "raid"):
    source = HERE / f"gear-compat341-{mode}-current.simc"
    for variant in ("user", "bisset"):
        content = []
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.startswith("talents=") and variant == "bisset":
                line = elite_talents
            if line.startswith("iterations="):
                line = "iterations=3500"
            if line.startswith("seed="):
                line = "seed=2610202641"
            content.append(line)
        name = f"gear-talents-{mode}-{variant}"
        target = HERE / f"{name}.simc"
        target.write_text("# Talent control only; fixed user gear, race, consumption and workload.\n" + "\n".join(content) + "\n", encoding="utf-8")
        manifest["runs"][name] = {"source": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                                  "talents": next(line.split("=", 1)[1] for line in content if line.startswith("talents=")),
                                  "variant": variant, "mode": mode}
(HERE / "gear-talent-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for name in manifest["runs"]:
    run(HERE / f"{name}.simc")
