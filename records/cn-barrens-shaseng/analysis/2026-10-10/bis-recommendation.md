# Shaseng: Attainable Celestial-Conduit Target and Roll Route

Date: 2026-10-10, Asia/Shanghai. Status: best tested candidate family, not a
proven global optimum or a verified live 12.1.5 BiS list.

Superseded for final stat/consumable selection by `raid-dungeon-optimization.md`.
Use `recommended-raid.simc` / `recommended-dungeon.simc` for owned-neck practical
targets. Retain this report as the first equipment-screening evidence.

## Boundaries and Reproducibility

- No inaccessible Mythic raid 7/8 or special 9/6 ceilings. Uniform candidate
  loot level 334 and crafted level 331; this is a normal-cap comparison, not
  a claim that every source drops directly at 334.
- Existing crafts may all be replaced. Keep the supplied Pandaren Conduit
  talent import fixed, original oil, no raid buffs and no Bloodlust. Consumables
  were not explicitly specified, but report inspection confirms default flask,
  food and augmentation buffs were active. These are controlled tests, not a
  replay of a real dungeon route or an unflasked stationary-stat snapshot.
- SimC midnight commit `71a76b73cc`, PTR `12.1.5.70077`, hotfix 2026-10-07.
  Inputs: `bis.simc`, `bis-refine.simc`. Initial/refinement tests: 2500 iterations;
  final slot-placement sensitivity: 1500 iterations. Reported mean errors are
  in the corresponding JSON. Sub-percent differences often cannot be ranked.
- Catalyst candidates preserve source stats via `redirected_base_stats` and
  keep relevant effect bonuses. Moving a craft to shoulders moves the fourth
  tier piece to catalyzed dungeon hands. Never infer original effects from tier
  item names alone. Check conversion eligibility in game before committing.

## Working Full Target

This is the baseline in `bis-refine.simc`; alternatives below are deliberately
retained where results do not distinguish them confidently.

| Slot | Target / source | Simulation item |
|---|---|---|
| Head | H8 effect head, converted | 271519, source 271875, bonus 13847 |
| Neck | H8 necklace, previously rolled; verify effect variant | 268265, bonus 13708 |
| Shoulder | Vaashnik / user H4 shoulder, converted | 271517, source 268246 |
| Cloak | H7 cloak | 268253 |
| Chest | Existing tier source; new effect chest remains alternative | 271522; new source 281236, bonus 14049 |
| Wrist | Crafted, Arcanoweave Lining | 244576, bonus 12384 |
| Hands | Murder Row | 251124 |
| Waist | H7 | 268256 |
| Legs | H7 legs, converted | 271518, source 268225 |
| Feet | Crafted, Arcanoweave Lining | 244569, bonus 12384 |
| Ring 1 | Vaashnik / user H4 | 268249 |
| Ring 2 | New raid Swarmcaller candidate | 281029 |
| Trinket 1 | H8 heart | 270175 |
| Trinket 2 | New raid candidate for dungeon; H7 for single target | 281215 / 270173 |
| Weapon | H8 polearm | 268215, bonus 13846 |

The target contains four tier pieces, two embellishments and one two-handed
weapon. The item-ID map is explicit to avoid ambiguous translated boss/item
names. The new chest is not automatically needed simply because it is new.

## Measured Comparisons

Initial baseline: old H7 passive with H8 anchors and no new chest/ring.
Percentage changes are against that complete set, not against current gear.

| Change | Single target | Five targets | DungeonSlice |
|---|---:|---:|---:|
| New trinket only | -0.56% | +3.39% | +3.79% |
| New ring replaces H4 ring | -0.04% | +0.09% | -0.10% |
| New ring replaces Atroxus ring | +0.58% | +0.86% | +1.24% |
| New chest only | +0.63% | +0.10% | -0.10% |
| H2 core instead of H7 passive | -2.12% | +1.11% | +0.23% |

Refinement baseline already includes H4 shoulder, retained H4 ring, new ring in
the other slot and new trinket: 174815 single-target / 320571 DungeonSlice DPS.
H7 passive instead of the new trinket: +0.54% single / -3.77% DungeonSlice.
New chest plus H7 passive: +1.23% single / -3.41% DungeonSlice. Keep a
single-target passive rather than declaring the new trinket universally best.

## Crafts, Stats and Enchant Settings

Use wrist/shoes as a convenient baseline, not a proven mandatory slot pair.
Both haste/mastery and crit/mastery missives were tested. Crit/mastery on both
gave +0.01% single / +0.16% DungeonSlice, within uncertainty. Both crit/haste
gave +0.17% single / -0.38% DungeonSlice, not a persuasive dungeon improvement.
Do not reforge solely on these small differences.

1500-iteration slot tests against wrist/shoes: shoulder/shoes -0.38% dungeon,
belt/shoes -0.38%, cloak/shoes +0.02%. Errors approximately 770-790 DPS around
320k; these small differences do not establish a reliable winner. Crafting a
cloak to avoid pursuing H7 is therefore a viable near-equivalent route in the
tested model, but actual remaining pools and other missing H7 items decide
whether that saves coins.

Baseline buffed simulation snapshot: crit 592, haste 839, mastery 1773,
versatility 117. This is not a prescribed breakpoint or a prediction of the
player's unbuffed live panel. NGA's 800-850 / 950-1000 / 1350-1400 reference is a hypothesis,
not something to force at the cost of stronger effects. No exhaustive stat,
gem, enchant or flask search has been completed.

Tested enchant IDs: head 8017, shoulders 8001, chest 7987, legs 8159, feet 7963,
rings 7967, weapon 8689. Gem IDs: head 240967; neck 240914/240890; wrists, belt,
first ring 240908; second ring 240900. These are reproducible baseline settings,
not a claim that all alternatives were individually optimized. Neck bonus
13708 differs from the user's current 13987; verify acquisition/upgrades retain
the intended neck effect before using this profile to predict live stats.

## This Week and Stop Rules

1. Current balance is two coins, not a simulated acquisition. Roll H8 once if
   the in-game chosen-spec preview contains the missing polearm/heart/head.
   The guide's Brewmaster suggestion is not a substitute for that preview.
2. Reserve the second coin for the planned 2026-10-15 new raid if carryover/cap
   allow. If it would overflow, choose the actual best remaining old-raid pool
   after H8's result, rather than spending automatically on H4.
3. New-raid priority is the dungeon trinket and complementary ring. Inspect the
   complete live eligible pool first. Do not state a 1/3 or other success rate
   from the three known target items alone.
4. H4 is not obsolete: its ring remains in the tested target alongside the new
   ring, and the shoulder is a viable tier precursor. Pursue it when its complete
   residual pool gives better target acquisition than H8/new raid.
5. H7 is optional rather than forbidden. It offers a single-target trinket and
   several target armor slots. A duplicate one-hander lowers pool value after
   the H8 polearm is acquired; crafting cloak can reduce dependence on H7.
6. H2/core, explorers/bag and Murder Row stone are backup passive choices,
   not automatic extra raid rolls for this dungeon-first target.

Upper limits, complete current pools and general exclusion scope remain unresolved.
The user confirmed on 2026-10-10 that last week's H8 necklace 268265 is already
excluded from the relevant H8 pool. Do not count it as a possible repeat or infer
a universal cross-spec rule from this confirmation. No current-week result or
Vault choice has been reported. Recompute the
route after each actual roll/Vault result. Mythic Delve legs are not assumed.

## Confidence Limits

SimC explicitly flags new chest/ring AoE effects as unverified and assumes no
damage splitting. The new trinket has target-acquisition behavior; DungeonSlice
is a sensitivity model, not a replay of a real route. Consequently new-item
rankings are provisional. Real 12.1.5 effect measurements may change them.
Full reward probabilities require the live preview plus complete relevant
history. These files demonstrate controlled comparisons, not proof of the
single strongest attainable loadout across every option.
