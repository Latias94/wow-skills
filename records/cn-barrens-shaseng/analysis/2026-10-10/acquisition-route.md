# Target Loadout Acquisition Route

Use `target-bis.simc` as the clean full-loadout input without comparison
profilesets. It uses local PTR support and source-stat redirection; not every
online service/importer supports those fields or unreleased items. No claim
of exhaustive BiS, optimized talents or optimized consumables is made.

## Source Coverage

| Source | Target items | Completion / spending rule |
|---|---|---|
| H8 | Head precursor 271875, polearm 268215, heart 270175, necklace 268265 | Neck already rolled and excluded. Stop spending for this target after missing head/weapon/heart are acquired; inspect the full pool. |
| New raid | Ring 281029, dungeon trinket 281215 | Stop after those targets unless an effect-verified chest 281236 or another measured upgrade justifies continuing. Do not automatically clear the pool. |
| Vaashnik (user H4 identity still needs journal confirmation) | Shoulder precursor 268246, ring 268249 | Both remain in this tested set; new ring does not replace this ring. R only if the residual pool beats alternatives. |
| H7 The Coiled Altar | Cloak 268253, waist 268256, leg precursor 268225 | Reconfirmed in the current raid loot guide on 2026-10-10. Boss identity is The Coiled Altar; Zul'jin occurs in the trinket name and is not the boss name. |
| H7 passive | Trinket 270173 | Optional single-target loadout, not required to complete the dungeon target. |
| Murder Row, Kystia Manaheart | Hands 251124 | Item page reconfirms Kystia Manaheart as source. Farm dungeon/Vault route; final track is not guaranteed by ordinary end-of-run drops. |
| Tier/Vault/Catalyst | Chest 271522, four-piece | Choose a Myth-track eligible source; no specific chest roll is required by this input. |
| Crafting | Wrist 244576, shoes 244569 | 331, two Arcanoweave Linings, haste/mastery baseline. Existing crafts can be replaced. |

R coins are not assigned solely because a boss supplies a target. Resolve the
entire eligible residual pool, duplicate outcomes, owned/Vault alternatives,
actual balance, carryover and lockouts. Keep natural drops and Vault options
separate from guaranteed target acquisition. No numeric odds without the pool.

Sources rechecked on 2026-10-10: Wowhead raid loot guide and item 251124 page.
The guide places shoulder/ring under Vashnik the Malignant and cloak/waist/legs
under The Coiled Altar. Item names alone do not establish a reward pool.

## Order After H8 / New-Raid Anchors

1. After every result, remove only confirmed roll exclusions and update actual
   ownership. Preserve the last known two-coin balance until spending is reported.
2. Once H8 anchors and new ring/trinket are obtained, compare Vaashnik's residual
   shoulder/ring pool with the confirmed boss pools for cloak/waist/legs. There
   is no justified fixed H4-before-H7 order while their complete pools are unknown.
3. Use normal drops, Myth-track Vault choices and Catalyst for armor when
   available. A Hero-track item cannot be assumed to reach the modeled cap just
   because this profile sets `ilevel=334`.
4. Fill hands from Murder Row and chest/four-piece from eligible tier or Catalyst
   sources. Newly obtained effect head/legs need conversion resources.
5. Finalize craft slot placement after those drops. The tested wrist/shoes pair
   is a baseline, not a rule. Missing cloak can instead be crafted; then use
   dungeon wrist 251135 and keep shoes as the second embellishment.
6. Do not spend coins on H2/bag/stone merely to fill the second trinket if the
   new-raid dungeon trinket is already obtained. Pursue H7 passive only when a
   single-target alternative matters enough to justify that residual pool.

## Tested Craft Alternatives

- Wrist/shoes haste/mastery: clean input baseline.
- Wrist/shoes crit/mastery: statistically near-equivalent; a legitimate tuning
  alternative, not an instruction to immediately recraft.
- Cloak/shoes: cloak 239656 with bonus 12384 and haste/mastery; remove crafted
  wrist and use dungeon wrist 251135. Around +0.02% DungeonSlice in the 1500-
  iteration comparison, within error. This avoids requiring the raid cloak.
- Shoulder/shoes: shoulder 244572 with bonus 12384, dungeon wrist 251135, and
  hands converted to tier 271520 from 251124 to maintain four-piece.
- Waist/shoes: waist 244573 with bonus 12384, dungeon wrist 251135.

Keep only two embellishments. Slot flexibility compensates for awkward drops
and allows selected stat pairs, but ordinary crafting does not create missing
raid-only effects or the modeled 334 primary-stat budget. Re-simulate the
whole set, not just a naked secondary-stat total, after changing slots.

## Corrected Consumable Interpretation

Previous prose called the tests unflasked because no consumables were specified.
The actual JSON contains `flask_of_the_magisters`, `harandar_celebration` and
`voidtouched` constant buffs. Thus the rating snapshot is buffed and cannot be
compared directly to NGA's unflasked stationary ranges. `target-bis.simc`
explicitly declares the report's effective defaults for reproducibility.
Do not prescribe 592/839/1773/117 as an unbuffed rating target.
