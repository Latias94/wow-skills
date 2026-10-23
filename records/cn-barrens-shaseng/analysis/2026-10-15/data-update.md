# October 15 Live-Data Recheck

The research scope is the existing October 10 attainable Windwalker loadouts,
not a new character snapshot or a complete new-raid eligible reward pool.
No acquisitions, Vault claims, exclusions or coin balances were changed.

## Source Update

Fetched the official SimulationCraft repository and fast-forwarded the clean
`E:/github/simc` checkout from `71a76b73cc` to
`3dcabb94dd32f786786c67541dfd10db9f39e43b` (35 commits). The upstream tip
was dated October 15, 2026, 05:46:01 UTC when fetched. Reconfigured CMake and
rebuilt Release. Final results must identify `3dcabb94dd`, Live
`12.1.5.70391`, hotfix `2026-10-14`; the former study used PTR 70077.

The first incremental build updated the game data but retained a stale
embedded Git label. Its `recheck-*.json/txt` files are preliminary diagnostics.
Reconfiguration corrected the label; `live-*.json/txt` and
`update-summary.json` are the authoritative measurements for this update.
An unsupported `progress=0` CLI display option was ignored with a warning in
the final run; it does not alter the simulation model. Clean exported inputs
do not contain that option.

## Wowhead Item Check

Saved current live Chinese tooltips and previous PTR tooltips together in
`wowhead-live-items.json`. Comparisons normalize item level to 334, which is a
modeled target rather than an assertion about every ordinary drop's level.

| ID | Current Chinese name | Relevant tooltip values at 334 |
| --- | --- | --- |
| 281029 | 虫群召唤者指环 | 110 haste / 295 mastery; 6,884 Nature proc damage |
| 281215 | 扭曲恐兽触须 | 179 primary; 34 crit per stack, 15 seconds; new-target 3-stack trigger once per 5 seconds |
| 281236 | 具象恐惧护胸 | 189 primary; 58 crit / 143 haste; 5,163 Shadow proc, +15% when Venomcursed |

Those major values match the previous cached PTR snapshot. Chinese live
availability and the trinket's displayed upgrade-label wording changed; this
does not establish a mechanical buff or nerf. Displayed ordinary drop rates
are not bonus-roll probabilities.

Source endpoints, retrieved October 15, 2026:

- https://nether.wowhead.com/tooltip/item/281029?locale=4&ilvl=334
- https://nether.wowhead.com/tooltip/item/281215?locale=4&ilvl=334
- https://nether.wowhead.com/tooltip/item/281236?locale=4&ilvl=334
- https://github.com/simulationcraft/simc/commit/3dcabb94dd32f786786c67541dfd10db9f39e43b

## Implementation and Comparison Limits

The new ring and chest implementations in
`engine/player/unique_gear_midnight.cpp` still emit
`UNVERIFIED_IMPLEMENTATION` for the assumption that AoE damage is not split.
The ring also retains a comment questioning five-target diminishing returns.
The trinket implements a new-target callback with three stacks, but a toy
dungeon model is not a real player route. The three relevant implementation
functions did not change in this 35-commit interval. No new Monk module or
Monk APL change appeared in the source diff; generic proc callbacks did change.

Final tests retain the original race, talents, gear ceilings, buffs, oils,
food and model lengths. Each uses 6,000 iterations and seed 15102026, distinct
from the previous 50102026 practical runs. Seven alternatives cover the old
chest/new chest, H7/new trinket, old/crafted ring, craft stat pairs, flask and
another necklace version. The alternative necklace is not the neck the user
reported owning. Proc damage and the trinket buff must appear in output; mere
successful item parsing is insufficient verification.

See `update.html` and `update-summary.json` for final measured deltas and errors.
This is a targeted recheck of the prior candidate family, not a new global BiS
search or a proof of fully verified live mechanics. The previous weekly coin
plan is historical; current spending requires current character/week inputs.
