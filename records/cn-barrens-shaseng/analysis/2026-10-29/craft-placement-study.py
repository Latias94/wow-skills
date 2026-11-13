"""Compare owned double-Arcanoweave placement with an attainable raid cloak route."""

from datetime import datetime
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
TOOLS = runpy.run_path(str(HERE / "personal-study.py"))
UPDATE, FIELDS, RUN = (TOOLS[k] for k in ("update", "fields", "run"))


def main():
    actor, _, current = TOOLS["load"]()
    candidates = TOOLS["candidates"](current)
    belt = candidates["waist_cm"][0]["waist"]
    shoulder = candidates["delve_shoulder334"][0]["shoulder"]
    full = candidates["post_both_shoulder"][0]
    shoe_bonuses = FIELDS(current["feet"])["bonus_id"].split("/") + ["12384"]
    shoe = UPDATE(current["feet"], bonus_id="/".join(shoe_bonuses))
    cloak = "back=,id=268253,bonus_id=13334/12854,ilevel=334"
    setups = {
        "shoulder334_owned": {**current,"shoulder":shoulder},
        "shoulder334_belt331": {**current,"shoulder":shoulder,"waist":belt},
        "shoulder334_raidcloak": {**current,"shoulder":shoulder,"back":cloak,"feet":shoe},
        "armor334_owned": {**current,**full},
        "armor334_raidcloak": {**current,**full,"back":cloak,"feet":shoe},
    }
    manifest = {"created_at":datetime.now().astimezone().isoformat(),
                "scope":"User confirmed shoulder redemption only. Level334, conversion and H7 items are hypothetical comparison conditions.",
                "talents":"User October29 talents, unchanged; no assumed acquisition or talent adoption.",
                "placement":"Owned cloak+wrist vs H7 cloak334 and lining moved to existing331 shoes; wrist lining retained.",
                "limits":"Full raid-cloak reward link unknown; explicit rank12854/level334 without invented proc IDs. All331 craft stats unchanged."}
    for mode,style,length,targets in (("slice","DungeonSlice",360,1),("aoe","Patchwerk",90,5)):
        for key,gear in setups.items():
            path=HERE/f"craft-placement-{mode}-{key}-6000-26102991.simc"
            lines=["# Bounded crafting placement study; acquired shoulder is not assumed upgraded in records.",
                   "ptr=0","item_db_source=local",*actor,*gear.values(),
                   "flask=flask_of_the_magisters_2","food=harandar_celebration","augmentation=void_touched",
                   "potion=potion_of_recklessness_2","temporary_enchant=main_hand:thalassian_phoenix_oil_2",
                   "optimal_raid=0","override.bloodlust=0",f"fight_style={style}",f"max_time={length}",
                   f"desired_targets={targets}","vary_combat_length=0","fixed_time=1","threads=8",
                   "iterations=6000","seed=26102991","confidence=0.95"]
            path.write_text("\n".join(lines)+"\n",encoding="utf-8")
            RUN(path)
    (HERE/"craft-placement-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
