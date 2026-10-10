# Worked Case: Shaseng, October 10, 2026

Historical example, not a current Windwalker BiS list. Reverify patch rules,
item tuning, source eligibility and player history before reuse. All numbers
below describe saved pilot measurements, not newly run or universal results.

## Scope and Evidence

CN Barrens, Pandaren Windwalker, Celestial Conduit; Mythic+ first, raid second.
The player allowed recrafting any slot, excluded inaccessible Mythic 7/8
special caps, and reported two current coins. H8 neck 268265 had already been
rolled the prior week and was explicitly excluded from later target planning.
New content was scheduled locally for October 15, not spendable October 10.
Candidate comparisons used 334 loot and 331 crafts as attainable targets,
not a claim that ordinary drops arrive at 334.

Evidence combined user-provided guide images, five supplied WCL exports,
bonus-aware item lookups, raid source checks and a local SimC checkout. Player
ranking/time window were user-described, not independently verified. Engine
commit was `71a76b73cc`, with PTR 12.1.5 data for new items. New chest/ring AoE
sharing and new-target trinket behavior had implementation caveats.

All five exports had polearm 268215, heart 270175 and neck 268265. Four had
the head-effect bonus 13847, although all five displayed the same tier head
ID. Four had H7 trinket 270173; one had 270164. Crafted wrists appeared in
five, crafted shoes in four, and crafted rings in three. One player used
four crafted pieces but only two embellishments. These observations supplied
test alternatives, not required slots, stat percentages or future-loot verdicts.

## Best Tested Candidates and Limits

The shared tested core included effect head converted to tier, H8 polearm
and heart, the owned H8 neck, H4 shoulder/ring, H7 waist/converted legs and
crafted wrist/shoe embellishments. Near-tie cloak/hand alternatives remained
viable, as did moving crafts after real loot results.

- Raid: new chest 281236 converted to tier plus H7 trinket 270173.
- Dungeon: ordinary tier chest plus new trinket 281215; ring pair 268249
  and new 281029. This did not establish a single universal loadout.
- A dungeon comparison replacing the new trinket with H7 was about -3.56%;
  a separate raid comparison replacing the new chest was about -1.01%.
  Models differ, so these deltas cannot be added or compared as equal utility.
- Controlled WCL-inspired rechecks found tier hands, alternate raid hands,
  dungeon cloak and alternate embellishment placement around -0.02% to
  +0.12% in the dungeon model. These were near-ties, not strong upgrade orders.
- A crit/haste crafted ring versus the old ring before the new raid was
  effectively tied: raid +0.039%, dungeon -0.015%. Replacing the future new
  ring with a crafted ring screened around -1.07% to -1.44%; crafting was
  therefore a provisional gap-filler, not automatically a permanent BiS ring.

Unbuffed-style rating snapshots, with their remaining talent/gear/oil context,
were raid C780/H811/M1448/V117 and dungeon C722/H730/M1587/V117. These are
reproducible candidate snapshots, not live-panel targets or breakpoints. Tested
craft stat pairs were close; there was no basis to force every existing craft
to change. Gem and enchant comparisons used full sets, not usage-rate voting.

## Acquisition Reasoning

Plan H8 while its valuable core remains, then new-raid ring/trinket (chest for
single target), then compare H4/H7 using actual remaining pools. Keep alternate
dungeon/Vault/craft routes for near-ties. An H8 polearm reduces H7 single-hand
value but does not erase H7 armor/trinket value. A new ring still occupies only
one of two ring slots, so it does not by itself obsolete H4. Stop on useful
targets rather than trying to empty a boss pool. Unknown eligible pool sizes
prevent exact odds. The report proposed plans without inventing spent coins.

## Repository Artifacts

When working inside this repository, resolve these relative to its root:

- `records/cn-barrens-shaseng/profile.json` and `weeks/`: facts and event ledger.
- `records/cn-barrens-shaseng/analysis/2026-10-10/`: dated research/results.
- `recommended-raid.simc`, `recommended-dungeon.simc`: clean final inputs.
- `raid-dungeon-optimization.md`, `wcl-top5-review.md`: reasoning and caveats.
- `practical-*.json`, `wcl-recheck-*.json`, `wcl-verify-*.json`: measurements.
- `dashboard.html`: delivered report; `dashboard.template.html` and
  `build-dashboard.ps1`: data-driven rebuild using those artifacts.

These character files remain outside the skill and may be absent from an
installed copy. Use this summary for methodology; consult raw files only when
available. Do not substitute this historical route for a new character study.
