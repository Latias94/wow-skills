"""Compare sourced Celestial-Conduit builds with the same upgraded equipment."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
TOOLS = runpy.run_path(str(HERE / "tuning-study.py"))


def emit(branch, candidate, mode, iterations, seed, tuning="baseline", unbuffed=False):
    talents = json.loads((HERE / "talent-candidates.json").read_text(encoding="utf-8"))[candidate]["talents"]
    source = TOOLS["emit"](branch,tuning,mode,iterations,seed,unbuffed)
    content = ["talents="+talents if line.startswith("talents=") else line
               for line in source.read_text(encoding="utf-8").splitlines()]
    path = HERE / f"talents-{branch}-{'stats' if unbuffed else mode}-{candidate}-{tuning}-{iterations}-{seed}.simc"
    path.write_text("# Fixed gear, race and consumption; only the specified sourced talent build changes.\n"
                    + "\n".join(content)+"\n",encoding="utf-8")
    return path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("stage",choices=["screen","verify","stats"])
    parser.add_argument("--branch",action="append",choices=["zuljin","tendril"])
    parser.add_argument("--candidate",action="append")
    parser.add_argument("--tuning",action="append")
    parser.add_argument("--mode",action="append",choices=["slice","aoe","st"])
    args=parser.parse_args()
    iterations,seed={"screen":(3000,26102961),"verify":(10000,26102971),"stats":(40,26102981)}[args.stage]
    candidates=json.loads((HERE/"talent-candidates.json").read_text(encoding="utf-8"))
    for branch in args.branch or ["zuljin","tendril"]:
        for candidate in args.candidate or list(candidates):
            for tuning in args.tuning or ["baseline"]:
                for mode in args.mode or (["st"] if args.stage=="stats" else ["slice","aoe","st"]):
                    TOOLS["RUN"](emit(branch,candidate,mode,iterations,seed,tuning,args.stage=="stats"))
    (HERE/"talent-manifest.json").write_text(json.dumps({"updated_at":datetime.now().astimezone().isoformat(),
        "engine":"Same native70575 binary and input gear as tuning-manifest.json",
        "candidates":candidates,"scope":"Same Hero tree; current user build vs dated sourced alternatives; no free-form talent search.",
        "comparison_policy":"Each trinket branch compares with its same-stage user build. Tuning interaction compares to the same selected talent baseline, never adds percentages from different runs."},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
