# User-Supplied WCL Five-Player Cross-Check

Date: 2026-10-10. The user identifies these as the Mythic+ top five exports.
Treat them as supplied snapshots; rank, scoring period and individual routes
have not been independently verified. Snapshot fields used are recorded in
`wcl-top5-evidence.json`. No current character acquisition is implied.

## Directly Observable Evidence

- H8 polearm 268215, heart 270175 and neck 268265: 5/5. All necks have 13987,
  all polearms have mastery bonus 13846.
- H7 passive 270173: 4/5; explorer bag 270164: 1/5. This does not refute a
  future new-raid trinket candidate: none of these supplied snapshots has it.
- H8 head-effect bonus 13847 is present in 4/5, although all five have tier
  item ID 271519. Bisset's export does not contain that bonus; do not silently
  impute the head effect or assume every tier head has it.
- Crafted wrists 244576: 5/5; crafted shoes 244569: 4/5. Four use wrist/shoe
  Linings; Bisset uses cloak/wrist Linings. Exactly two confirmed embellishments
  in each snapshot.
- Crafted ring 240949: 3/5. Nilenga also uses crafted chest 244570, giving four
  crafted pieces but only two embellishments. A two-embellishment limit does
  not imply a two-crafted-item limit.
- H4 ring 268249: 3/5. Raid cloak 268253: 3/5. Raid waist 268256: 2/5.
- Tier hands 271520: 4/5; the other uses raid hands 268234. None equips the
  previously recommended Murder Row hands 251124 in these exact snapshots.
- Diamond 240983: 5/5; previous candidate used 240967. Confirm tooltip/model
  identity and compare as a real gem replacement, not a stat-weight assertion.

Crafted bonus interpretations confirmed with full tooltip bonuses:
8790 = crit/haste; 8791 = crit/mastery; 8793 = haste/mastery. Their choices vary,
so none establishes a mandatory crit/haste/mastery ratio. Crit/haste rings and
chests can rebalance a set dominated by mastery-bearing raid effects.

## Controlled Tests

`wcl-recheck-raid.simc` and `wcl-recheck-dungeon.simc` use the player's own
Pandaren race/talents, attainable 334 loot/331 crafts, owned neck 13987, same
buffs, consumables and embellishment assumptions as the practical candidates.
Each contains 15 alternatives, 3500 iterations, seed 60102026. Full source
profiles are not imported blindly: their unavailable Mythic 7/8 ceiling,
race/talents, differing gem counts and unknown Catalyst precursor stats would
confound a gear comparison.

Tests cover plain-primary diamond versus crit-effectiveness diamond (same
socket layout and a separate user-like layout); tier hands; crafted crit/haste
and haste/mastery rings replacing the new ring; crafted ring retaining the
new ring; tier hands/crafted chest maintaining four-piece; alternative raid
hands/waist, dungeon cloak/ring and Bisset's alternate embellishment slots.
Clickz/Nilenga-inspired cores are partial normalized candidates, not exact
reproductions or predictions of those players' real DPS.

Random waist 271436 remains unresolved; do not invent its chosen stats. Tier
IDs alone do not identify pre-conversion sources. Crafted chest plus tier
hands preserves four-piece via head/shoulder/hands/legs. The new chest route
instead uses head/shoulder/chest/legs. No candidate exceeds two embellishments.

## Initial Results, 3500 Iterations

Dungeon baseline 319086 DPS. Tier hands -0.02%, raid hands 268234 +0.12%,
dungeon cloak -0.06%, Bisset embellishment placement -0.18%, user-like plain
diamond layout -0.07%: all are near ties, not mandatory changes. Manufactured
ring replacing the future new ring: haste/mastery -1.07%, crit/haste -1.44%.
Crafted chest plus tier hands -0.36% to -0.43%; a viable fallback rather than
evidence that a third/fourth craft must always outperform a 334 loot item.

Raid baseline 217911 DPS. Bisset placement +0.20%, alternative waist +0.17%,
plain diamond layout +0.02%; these overlap sampling uncertainty. Crafted chest
plus tier hands -0.82% to -1.03% against the new effect chest, so they do not
supplant that provisional single-target candidate. Existing core is retained.

`wcl-verify-*.simc` independently rechecks 8 shortlisted alternatives/model at
6000 iterations, seed 70102026. Pre-new-raid comparisons use an old ring/H7
passive/ordinary tier chest before comparing crafted rings. This isolates the
current-season crafted-ring route from future-item assumptions. Final outputs
are `wcl-verify-raid.json` and `wcl-verify-dungeon.json`.

## Independent Verification and Route Revision

6000-iteration dungeon baseline 318700 DPS: tier hands -0.02%, raid hands
268234 +0.12%, dungeon cloak +0.07%, Bisset placement +0.09%, plain diamond
layout -0.12%. Each overlaps uncertainty; maintain them as alternative routes.
Replacing H4 ring with a craft while retaining the new ring -0.29%, also close.
Do not turn these differences into guaranteed personal DPS gains.

6000-iteration raid baseline 217961 DPS: tier hands -0.29%, raid hands -0.26%,
dungeon cloak +0.15%, Bisset placement +0.12%, plain diamond layout -0.08%.
Thus preferred hands depend on content, but no new definitive full BiS emerges.

Before new raid, crafted crit/haste ring versus old Atroxus ring, holding H7
passive/ordinary chest fixed: +0.039% raid and -0.015% dungeon. Both are ties.
Use the craft when it fills an acquisition/stat gap, not because high-ranked
players' ownership proves it is strictly better. Current raw exports reflect
actual available drops, while the future target incorporates provisional new
effects; avoid conflating the two time horizons.

Main recommended profiles remain unchanged. Optional complete inputs:
`alternative-current-crafted-ring.simc` (pre-new-raid obtainable old-item route,
user-like diamond placement and tier hands) and
`alternative-future-tier-hands.simc` (future dungeon target with tier hands).
Both passed CLI parse/smoke runs; short validation runs are not DPS evidence.
The exact combined current-route gem/tier-hand variant was not independently
optimized, so its label is alternative, not new BiS.

Revised acquisition advice: keep H8 anchors and new ring/trinket as provisional
main objectives. H4 ring/shoulder remain useful. Do not require Murder Row hands
when a suitable tier/raid-hand source is already available. Do not pursue H7
cloak as an irreplaceable item when dungeon cloak or a two-Lining craft route
is near-equivalent. Ordinary crafted ring/chest can fill missing sources; do
not add a third embellishment. More crafting is a choice, not a blanket upgrade.
