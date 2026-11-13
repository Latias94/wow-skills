"""Compare two new crafted purchases against the post-redemption equipped set."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
TOOLS = runpy.run_path(str(HERE / "personal-study.py"))
UPDATE, FIELDS, RUN = (TOOLS[k] for k in ("update", "fields", "run"))


def sets():
    actor, _, current = TOOLS["load"]()
    existing = TOOLS["candidates"](current)
    base = {**current, **existing["delve_shoulder334"][0]}
    belt_cm = existing["waist_cm"][0]["waist"]
    belt_hm = existing["waist_hm"][0]["waist"]
    leg_template = current["feet"].replace("feet=", "legs=", 1)
    legs_cm = UPDATE(leg_template, id=244574, enchant_id=8159)
    legs_hm = UPDATE(legs_cm, bonus_id=FIELDS(legs_cm)["bonus_id"].replace("8791", "8793"))
    old = (HERE.parents[1]/"snapshots/2026-10-26-equipped.simc").read_text(encoding="utf-8")
    old_hands = UPDATE(next(x for x in old.splitlines() if x.startswith("hands=")),redirected_base_stats=272241)
    no_lining = UPDATE(base["back"],bonus_id="/".join(x for x in FIELDS(base["back"])["bonus_id"].split("/") if x!="12384"))
    loa = "finger2=,id=251513,ilevel=331,bonus_id=12214/13667/12497/13751/14001/13836,enchant_id=7967,gem_id=240908"
    cases = {
        "baseline": (base, "Redeemed shoulder modeled as Catalyst334; H7 legs and belt not assumed acquired."),
        "belt_cm": ({**base,"waist":belt_cm}, "One new331 CM ordinary belt."),
        "belt_hm": ({**base,"waist":belt_hm}, "One new331 HM ordinary belt."),
        "belt_legs_cm_oldhands": ({**base,"waist":belt_cm,"legs":legs_cm,"hands":old_hands}, "Two new331 CM crafts. Requires still owning the old321 tier gloves; no current bag claim."),
        "belt_legs_hm_oldhands": ({**base,"waist":belt_cm,"legs":legs_hm,"hands":old_hands}, "New331 CM belt and HM legs. Requires old321 tier gloves for four-piece."),
        "belt_loa": ({**base,"waist":belt_cm,"back":no_lining,"finger2":loa}, "Two new331 crafts: CM belt+Loa ring. Remove cloak lining, retain wrist lining, so exactly two embellishments."),
        "belt_legs_hm_gloves334": ({**base,"waist":belt_cm,"legs":legs_hm,"hands":UPDATE(old_hands,ilevel=334)}, "Conditional future334 tier gloves with same precursor272241. Not an owned item."),
    }
    return actor,cases


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("stage",choices=["screen","verify"])
    parser.add_argument("--candidate",action="append")
    parser.add_argument("--talents",choices=["user","short_martial"],default="user")
    args=parser.parse_args()
    actor,cases=sets()
    if args.talents=="short_martial":
        data=json.loads((HERE/"talent-candidates.json").read_text(encoding="utf-8"))
        actor=["talents="+data["user_short_cd_martial"]["talents"] if x.startswith("talents=") else x for x in actor]
    iterations,seed=(3500,261029101) if args.stage=="screen" else (8000,261029111)
    for key in args.candidate or cases:
        gear,note=cases[key]
        for mode,style,length,targets in (("slice","DungeonSlice",360,1),("aoe","Patchwerk",90,5)):
            path=HERE/f"two-crafts-{args.talents}-{mode}-{key}-{iterations}-{seed}.simc"
            lines=["# "+note,"ptr=0","item_db_source=local",*actor,*gear.values(),
                   "flask=flask_of_the_magisters_2","food=harandar_celebration","augmentation=void_touched",
                   "potion=potion_of_recklessness_2","temporary_enchant=main_hand:thalassian_phoenix_oil_2",
                   "optimal_raid=0","override.bloodlust=0",f"fight_style={style}",f"max_time={length}",
                   f"desired_targets={targets}","vary_combat_length=0","fixed_time=1","threads=8",
                   f"iterations={iterations}",f"seed={seed}","confidence=0.95"]
            path.write_text("\n".join(lines)+"\n",encoding="utf-8")
            RUN(path)
    (HERE/"two-crafts-manifest.json").write_text(json.dumps({"updated_at":datetime.now().astimezone().isoformat(),
        "scope":"Two additional crafted gear purchases allowed; no assumed current H7 loot, new bags or talent adoption.",
        "confirmed_resources":"User says sufficient sparks; exact count, crests, current crafted level changes not provided.",
        "cases":{k:n for k,(_,n) in cases.items()},"engine":"Same Live70575 binary and controls as personal-study.py"},indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
