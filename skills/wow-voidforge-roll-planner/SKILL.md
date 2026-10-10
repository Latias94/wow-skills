---
name: wow-voidforge-roll-planner
description: Optimize attainable WoW BiS loadouts with SimulationCraft, derive weekly raid bonus-roll and crafting routes, compare Great Vault choices, and track results. Use for gear/stat simulations, R-coin allocation, loot-specialization choices, or evidence-backed HTML equipment reports.
---

# WoW Voidforge Roll Planner

Turn current gear, attainable content, and actual reward pools into a weekly plan.
Answer in the user's language. Gear guides and player statistics support roll
decisions; they cannot replace the character's reward preview or sims.

## Modes and Records

- **Plan:** Load the character/week, refresh current rules and relevant pools,
  then recommend an affordable sequence with fallback and stop conditions.
- **Record:** Follow [weekly-records.md](references/weekly-records.md), save the
  reported Vault, roll, drop, or crafting result, and reassess remaining actions.
- **Review:** Compare completed weeks with original plans, retain observed
  results, and explain why next week's priorities changed.
- **End-state optimization:** When the user prioritizes best attainable gear,
  read [end-state-optimization.md](references/end-state-optimization.md). Select
  complete loadouts first, optimize stats/crafts/enchants, then derive roll routes.
  Existing crafts are replaceable unless the user sets a cost constraint.
- **Report:** For a substantial gear study, recommend a standalone HTML report;
  generate it when requested or already within the agreed deliverable. Follow
  [html-report.md](references/html-report.md), including Chinese Wowhead tips,
  accessible row-wide equipment links and measured results.

Read `records/<character-id>/profile.json`, the latest week, and prior confirmed
roll events. Create records when tracking is requested. Keep them in the user's
workspace outside the installed skill. This repository's pilot is
`records/cn-barrens-shaseng/`; its dated conclusions are not class defaults.
For a worked example of the research, simulations and resulting routes, read
[case-shaseng-2026-10.md](references/case-shaseng-2026-10.md). It summarizes
the pilot without requiring access to this repository's character records.

## Planning

1. Establish region/reset date, patch/season, content, combat spec, Hero talents,
   target spec, actual coin balance, and attainable bosses. Preserve the user's
   priorities; distinguish long-term power from an item-level achievement.
2. Preserve raw SimC and inspect item IDs **with all bonus IDs** before assigning
   levels/tracks. Read [simc-intake.md](references/simc-intake.md) for this branch.
3. Verify weekly sources, Vault tradeoffs, roll costs, reward track, lockouts,
   storage limits, and exclusions for this patch. Read
   [source-weighting.md](references/source-weighting.md). Historical costs are
   not defaults; a reported balance is not an income rate. Keep unknowns explicit.
4. Map boss shorthand to raid and boss name. Retain ambiguous shorthand as
   unresolved and ask for its name while analyzing known candidates. Compare old
   and new raids by regional release date, access, value, and overlap. Future
   content is not spendable this week.
5. Build pools using [pool-table-schema.md](references/pool-table-schema.md).
   Inspect full reward pools, not BiS lists or special-effect articles. Compare
   loot specs when they could retain targets and exclude filler.
6. Rank targets using [scoring-model.md](references/scoring-model.md). Match
   guides/player samples to content and Hero talents; record sample date, size,
   scope, and examples. Observed population stats are not required thresholds.
   For simulation work, follow [simulation-protocol.md](references/simulation-protocol.md)
   to separate identity checks, controlled comparisons and uncertainty.
7. Evaluate Vault/crafting with [decision-rules.md](references/decision-rules.md).
   Ownership changes target value; confirmed roll history changes exclusions
   under verified rules. Check four-piece, weapon setup, unique-equipped items,
   catalyst eligibility, and embellishment limits before proposing replacements.
   Compare a whole-loadout slot map across all proposed activities: alternative
   weapon configurations, duplicated cloak/crafted slots, competing on-use
   trinkets, and newly opening raid effects can downgrade otherwise strong pools.
   Mark each slot's planned source and fallback before allocating multiple coins.
8. Give a budgeted allocation, loot spec, targets, fallback, and stop conditions.
   When costs or eligibility remain unknown, give conditional branches rather
   than unsupported exact attempts or guaranteed outcomes.
   Recompute after actual results. Save plans separately from completed events.

## Evidence and Probability

Separate drop source, usable gear, loot-spec eligibility, and the actual remaining
roll pool. A guide establishes value without necessarily establishing eligibility.
An unfiltered or default-level tooltip does not establish this character's reward.

Each pool records completeness, history coverage, source, and verification date.
Missing history means unknown exclusions, not an empty history. Withhold exact
percentages if the eligible remaining pool is unknown. Even with a complete pool,
`k/n` is an equal-weight model unless weights are verified. Simulations are
separate measurements; never invent DPS deltas.

## Output

Lead with sequence and actual budget; use a compact comparison table for pools,
targets, specs, costs, and stop rules. Explain differences that change decisions.
Include next-week branches and assumptions that could change the recommendation.

Persist profile, raw gear snapshot, weekly plan, and reported events following
[weekly-records.md](references/weekly-records.md). JSON stores facts; dated
Markdown stores rationale/sources. Separate offered/claimed Vault rewards and
planned/completed rolls. After an update, report budget and route changes.

For a full report read [analysis-template.md](references/analysis-template.md).
Include clean raid/dungeon SimC exports and measured-result artifacts when
simulations were run. A simulated target is not an acquisition or a ledger event.
For partial inputs read [input-granularity.md](references/input-granularity.md);
the intake checklist is [player-profile-template.md](references/player-profile-template.md).
