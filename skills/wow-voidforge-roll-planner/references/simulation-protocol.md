# Reproducible Gear Comparisons

Use for actual simulation work. Start from the user's local SimC checkout or
provided results; inspect the supported branch before choosing input syntax.

## Model and Provenance

Keep raw imports unchanged. Save the executable version, source commit, data
build and live/PTR mode, date, talents/Hero tree, race, fight style, length,
targets, iterations, seed, buffs and consumables with the results. Place global
data-mode options before actor creation when required by the tested branch.
New-raid candidates require compatible item data and implemented effects.
An imported item that parses is not proof that its proc works correctly.

Normalize attainable gear ceilings and common comparison settings. Preserve
relevant effect bonuses, sockets and source stats. When comparing player gear,
keep the user's talents/race constant unless those are themselves being tested.
Inspect logs/results for errors, missing effects and modeled proc activation.
Mark unsupported mechanics explicitly; if they materially drive the winner,
treat the recommendation as provisional rather than filling in a DPS estimate.

For retained-effect Catalyst gear, verify eligibility and the branch's modeling
mechanism. Test tier bonuses and precursor effects together. In the pilot's
branch, `redirected_base_stats=<source-id>` with the tier ID and effect bonuses
was used; this is a dated implementation example, not portable syntax by fiat.

## Search Order

1. Build credible complete sets from dated guides, matched player exports and
   attainable old/new content. Vary major weapon, trinket, special-effect and
   tier arrangements before fine-tuning ratings.
2. Check four-piece, weapon legality, unique-equipped restrictions, compatible
   on-use effects, and embellishment count for each set. Two embellishments
   does not restrict ordinary crafted pieces to two.
3. Screen representative single-target and dungeon workloads separately.
   DungeonSlice/fixed-target AoE are models, not measured player routes. New
   target triggers and target-sharing effects need particular scrutiny.
4. Tune leading sets using obtainable crafts/stat pairs, embellishment slots,
   gems, enchants and consumables. Test actual replacement combinations; free
   rating redistribution measures sensitivity, not an obtainable BiS set.
5. Recheck finalists with higher iterations and another seed. Include the
   baseline, report raw DPS and relative change within each workload, and
   carry uncertainty forward. Do not compare absolute raid and dungeon DPS
   to select a mode-independent winner.

Iteration counts scale with runtime and the size of the decision. The pilot
used 3,500-iteration screening and 6,000-iteration independent-seed checks;
those counts are examples, not evidence of sufficient precision for all cases.
Near-ties permit alternate acquisition routes. Overlapping error estimates are
a conservative warning, not a statistical equivalence test. State whether an
error field is a standard error or a confidence-interval half-width.

## Stats and Artifacts

Make consumables explicit in exported recommendations. Verify effective buffs
in output: omitted flask/food settings may enable class defaults. For an
unbuffed snapshot, explicitly disable intended consumables and raid buffs and
describe remaining talent, gear, oil or passive effects. Report ratings and
percentages only when actually computed; do not infer a live panel by
subtracting an assumed flask. Population stat medians are not breakpoints.

Preserve raw `.simc`, result JSON and a short dated interpretation. Export
separate clean raid/dungeon inputs without exploratory profilesets, with the
data mode and complete item modifiers required to reproduce the set. If no
simulation ran, label the conclusion guide-based or untested and omit invented
test results. Publish the best tested attainable candidate with its search
boundary, then derive weekly acquisition routes from the real remaining pools.
