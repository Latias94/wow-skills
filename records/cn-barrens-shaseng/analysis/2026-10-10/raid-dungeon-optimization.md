# Raid and Dungeon Joint Equipment Optimization

2026-10-10, Asia/Shanghai. This report supersedes stat choices in the first
target-loadout export. It describes best tested candidate families, not proof
of the unique global optimum across every item, talent, embellishment or route.

Subsequent user-supplied WCL five-player cross-check is in `wcl-top5-review.md`.
Core target profiles remain valid, but dungeon hands/cloak and crafted ring
routes have additional near-equivalent candidates; do not lock their sources.

## Scope and Search

- Keep the user's Pandaren Celestial-Conduit talents fixed. Loot 334, crafts
  331; no inaccessible Mythic raid 7/8 or 9/6 ceilings. All crafts replaceable.
- Local SimC midnight `71a76b73cc`, PTR `12.1.5.70077`, hotfix 2026-10-07.
- `search-*.simc`: 33 variants/model, 1200 iterations, seed 10102026. Nine wrist/
  shoe stat combinations with mastery/haste/crit flasks, plus gem/enchant tests.
- `joint-*.simc`: 23 variants/model, 3000 iterations, independent seed 20102026.
  Joint stat/gem/flask combinations, rings, neck effects, chest, passive trinkets,
  tier shoulders and crafted cloak route. Not an exhaustive Cartesian product.
- `verify-*.simc`: shortlisted joint settings and equipment rechecks, 5000
  iterations, seed 30102026. Controlled 240s single-target / 360s DungeonSlice,
  no external raid buffs or Bloodlust. Food/flask/augmentation/oil are explicit.
- `raid-context.simc`: 4000 iterations, seed 40102026, full generic raid buffs
  and Bloodlust, checking shortlist sensitivity to the raid context.
- `practical-*.simc`: final 4000-iteration confirmation, seed 50102026, keep
  the actually owned neck bonus 13987. Raid enables generic raid buffs/Bloodlust;
  dungeon uses no generic raid buffs/Bloodlust. Actual route buffs differ.
- `unbuffed-recommended-*.json`: 20-iteration stat-only snapshots, consumables,
  generic raid buffs and Bloodlust disabled. Not performance estimates.

The generators are narrow, dated research helpers. Generated SimC and JSON
files are the exact reproducible evidence. `optimization-measurements.json`
collects run options, means, mean standard errors and profile confidence errors.
Identical duplicate profiles have small random differences; do not rank noise.

## Recommended Candidate Family

Clean inputs: `recommended-raid.simc` and `recommended-dungeon.simc`. Both keep
the confirmed owned necklace effect 13987. Necklace 13708 was an alternative
benchmark; it is already excluded from the character's H8 roll pool by item ID.
Do not assume it can be reacquired or freely changed. Its effect conversion or
another obtainable route is unverified and is not required by these profiles.

| Slot | Raid single target | Dungeon |
|---|---|---|
| Head | H8 effect head 271875, converted to 271519 | Same |
| Neck | Owned H8 268265, bonus 13987, upgraded to target level | Same |
| Shoulder | Vashnik 268246, converted to 271517 | Same |
| Cloak | The Coiled Altar 268253 | Same; crafted alternate is near-equivalent |
| Chest | New raid 281236, converted to 271522, bonus 14049 | Ordinary tier 271522; new chest is a near-tie |
| Wrist | Craft 244576, crit/mastery, Arcanoweave Lining | Same candidate; haste/mastery near-equivalent |
| Hands | Murder Row 251124 | Same |
| Waist | The Coiled Altar 268256 | Same |
| Legs | The Coiled Altar 268225, converted to 271518 | Same |
| Shoes | Craft 244569, crit/mastery, Arcanoweave Lining | Same candidate; haste/mastery near-equivalent |
| Ring 1 | Vashnik 268249 | Same |
| Ring 2 | New raid 281029 | Same |
| Trinket 1 | H8 heart 270175 | Same |
| Trinket 2 | H7 passive 270173 | New raid 281215 |
| Weapon | H8 polearm 268215, mastery effect 13846 | Same |
| Flask | Crit 241326 as candidate; haste/other near-ties | Mastery 241322 |

Two embellishments and four tier pieces are retained. Do not interpret a table
entry as guaranteed reward eligibility or automatic coin priority. The new
chest must be confirmed eligible for Catalyst with its effect retained in game.

## What the Higher-Iteration Tests Actually Establish

Controlled verification with neck 13708: raid baseline 178958 DPS. Ordinary
chest -0.51%; new passive -1.21%; replacing the H4 ring rather than the other
ring -0.59%; H2 core -1.71%. The original dungeon-target set -1.63%, equivalent
to approximately +1.65% for this raid candidate against that set in this same
model. This is not an upgrade estimate against the player's current gear.

Dungeon verification baseline 319765 DPS: H7 passive -3.33%, H2 core -2.61%,
new ring replacing H4 -0.63%. New chest +0.10%, crafted cloak route -0.07%,
haste/mastery crafts +0.18%: these small changes overlap uncertainty and do not
establish a unique winner. The original target set is only +0.02%; its earlier
stat selection was already near-equivalent, not demonstrably badly optimized.

Generic raid-buff context baseline 219024 DPS: haste flask +0.03%, mastery
Garnets +0.05%, haste/mastery crafts +0.01%, mastery flask -0.23%, ordinary
chest -0.69%, new passive -0.51%. Thus the practical equipment differences are
more defensible than claiming a mandatory flask, gem or missive combination.
Practical owned-neck rechecks are stored in `practical-raid.json` and
`practical-dungeon.json`; do not mix their baselines with the above models.

Final practical raid baseline with owned neck: 218214 DPS; old chest -1.01%,
new passive -0.32%, haste flask -0.34%, haste/mastery crafts -0.25%. Final
practical dungeon baseline: 318882 DPS; H7 passive -3.56%, new chest +0.24%,
crit flask -0.22%, haste/mastery crafts -0.07%. Small flask/missive/chest dungeon
differences still overlap sampling uncertainty. The raid and dungeon absolute
DPS are not comparable because fight model, targets and raid buffs differ.

## Attribute Selection and Reproducible Settings

Without consumables, external buffs or Bloodlust, the measured opening snapshots
for the exported crit/mastery-craft candidates are:

| Rating | Raid | Dungeon |
|---|---:|---:|
| Crit | 780 | 722 |
| Haste | 811 | 730 |
| Mastery | 1448 | 1587 |
| Versatility | 117 | 117 |

These are model snapshots with gear/talents/oil, not mandatory live-panel
breakpoints. Combat H8 effects and other procs change ratings over time. NGA's
reference ranges and aggregate player stats are hypotheses, not constraints
to force. Replacing the new ring/chest changes the entire secondary-stat budget.

Craft stat pairs: crit/mastery `32/49`, haste/mastery `36/49`, crit/haste `32/36`.
Both crit/mastery and haste/mastery remain plausible near-equivalent candidates.
The selected crit/mastery pair is one reproducible finalist, not a prescription
to recraft a satisfactory haste/mastery item. No fictitious freely allocated
rating offsets are used in these exports.

Three flexible Garnet sockets use 240906 (crit/haste), compared with 240908
(crit/mastery) and 240904 (pure crit). Other gem families are retained through
neck 240914/240890 and second ring 240900 with unique diamond 240967. These
choices keep color diversity rather than filling every socket with one color.
Garnet 240906 versus 240908 is still a near-tie in the verified finalist sets.

Tested enchant settings: helm 8017, shoulder 8001, chest 7987, legs 8159, shoes
7963, rings 7967, weapon 8689. Swapping both ring enchants to pure mastery 7965
lost approximately 1.82% raid / 2.29% dungeon in the 1200-iteration screen.
Alternative weapon 8039 did not beat 8689 in that screen. Helm utility variants
were too close to rank for damage; utility should decide those.

## Roll and Craft Consequences

1. H8: collect missing effect head, polearm and heart; neck is owned/excluded.
2. New raid: ring and new passive remain dungeon anchors. Add effect chest as
   a conditional single-target objective, not a required dungeon upgrade.
3. Vashnik/H4: shoulder and ring remain useful after new-raid acquisitions.
4. The Coiled Altar/H7: cloak, waist and converted legs remain armor targets;
   the passive becomes relevant if raid single-target performance is a priority.
5. Murder Row: hands and optional dungeon wrist 251135. Complete chest/four-piece
   via eligible tier/Vault/Catalyst sources rather than automatic extra coins.
6. Reserve crafting until source gaps are clearer. Wrist/shoes are a convenient
   two-embellishment pair. Crafted cloak/shoes with dungeon wrist remains close
   and may reduce dependence on one raid armor drop. Recheck the whole set.

Numeric roll odds and a fixed H4-versus-H7 spending order remain unavailable
without complete actual residual pools. No actual coins or Vault results have
been changed by this research; current last-reported balance remains two.

## Limits

New chest/ring AoE implementation explicitly assumes unsplit damage and is
unverified. The trinket's target-acquisition behavior is sensitive to the dungeon
model. Patchwerk is not every raid boss and DungeonSlice is not the actual route.
Talents, all possible embellishments, defensive value, item accessibility,
all socket arrangements and all gear/consumable combinations are not exhaustively
optimized. The result is a measured candidate family with stop rules, not a
universal attribute priority or proof of the sole attainable BiS.
