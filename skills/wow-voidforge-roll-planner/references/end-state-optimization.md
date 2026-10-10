# Attainable End-State Optimization

Use this branch for BiS-first planning, not ordinary weekly coin questions.
For execution and reproducibility, use [simulation-protocol.md](simulation-protocol.md).

1. Establish attainable ceilings by source and content, main Hero tree, and
   representative fights. Distinguish this week's accessible content from
   dated future-accessible candidates. Exclude bosses/special caps the player
   cannot attain in either scope; do not discard future candidates merely
   because they cannot be rolled this week.
   Record whether cost, existing crafts or spark time are constraints; do not
   treat owned crafted items as fixed when the player permits replacement.
2. Build full candidate loadouts from current class-author guides, verified
   effect/bonus-aware matched player exports, community references, and new raid
   loot. Retain multiple credible alternatives for contested slots. Community
   rating ranges are hypotheses rather than mandatory breakpoints.
3. Simulate complete sets at attainable levels, with the same chosen talents,
   buffs and consumables. Preserve Catalyst source stats/effects and tier bonuses.
   Check unique-equipped, embellishment count, weapon configuration and on-use
   pairing. Compare single target, multi-target and representative dungeon models;
   state that a toy dungeon model is not the user's actual route.
4. Refine the leading alternatives using obtainable crafted stat pairs, gems,
   enchants, and consumables. Equal-budget redistribution tests measure local
   sensitivity but do not establish a global optimum or an obtainable item set.
   Revalidate finalists after stat tuning; equipment and stat choices interact.
5. Save simulation inputs/commit/data mode, assumptions, outputs, errors, proc
   activation, and implementation limitations. Label conclusions as the best
   tested candidate, not global BiS if the search/effect verification is partial.
6. Derive the source/slot map from these loadouts, then apply actual reward pools
   and exclusion history to coin allocation. A strong item can make a poor roll
   pool; new item availability does not make every old drop worthless. Keep an
   alternative route when finalists are near the simulation's uncertainty.
7. Output attainable target set, viable alternatives, crafts/embellishments,
   stat direction and tested enchant/gem settings, then weekly sequence and stop
   rules. Track acquisitions only after actual reports, never after simulations.
   Recommend [an HTML report](html-report.md) for a substantial study so the
   player can inspect items, compare modes and review the acquisition routes.

For replaceable crafts, test alternate slot placements as full sets, not only
missive pairs on owned slots. Moving a craft out of a tier slot may change which
other source is catalyzed. Compare each new ring against both existing rings;
new-raid overlap alone is not evidence that an old ring's boss is obsolete.

Export a clean single-loadout SimC input without exploratory profilesets when
requested. Include a source/stop-rule map and compatible data mode. Verify
effective consumables and active buffs in the output: omitted input settings
may use class defaults and do not establish an unbuffed stat snapshot. An item
database or reference profile establishes item identity, not its drop boss.

For raid-versus-dungeon requests, optimize and export separate loadouts. Keep
common gear/consumable changes controlled, state encounter length and buffs,
and revalidate shortlisted joint stat/consumable choices with independent seed
and higher iterations. An identical duplicate profile may differ by sampling
noise; do not rank near-ties or call one a breakpoint. Report unbuffed rating
snapshots separately from consumable-buffed/combat snapshots. Do not subtract
an assumed flask amount from a buffed report to invent a live panel.

Use supplied high-ranked exports as real candidate evidence, preserving bonus
effects and provenance. Normalize race, talents and attainable levels for gear
comparisons rather than ranking their raw DPS. Two embellishments do not mean
only two crafts: ordinary crafted rings/chests can rebalance stats. Test gem
families and unique-diamond choices actually present in the exports. A current
player not wearing unreleased loot is not evidence against that future item.
