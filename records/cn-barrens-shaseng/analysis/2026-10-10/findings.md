# Celestial Conduit Windwalker: Corrected Gear Analysis

Date: 2026-10-10, CN / Asia-Shanghai. Original character snapshot: 2026-10-09.
This report supersedes prior assumptions that tier display names identify the
precursor or that effect head/chest automatically conflict with four-piece.

## Catalyst Correction

The official 12.1 notes state eligible class-set armor inherits the precursor's
secondary and tertiary stats and certain cantrip effects. This supports effect
head/chest/legs converted into tier. It does not make every item craft, weapon,
or effect universally eligible; inspect the conversion preview and charges.
Source: https://worldofwarcraft.blizzard.com/en-us/news/24293281/curse-of-ulatek-content-update-notes

Murlok tier-head/chest/leg counts cannot distinguish effect precursors. The
previous comparison of 45 tier heads versus five H8 heads is not valid evidence
against using the H8 head. Effect provenance requires bonuses and item effects.

The local SimulationCraft MID2 generator explicitly models converted H8 head:
`id=271519,redirected_base_stats=271875,bonus_id=.../13847/...`.
File: `E:/github/simc/profiles/generators/MID2/MID2_Generate_Monk.simc`.
Commit: `71a76b73cc`, branch `midnight`; snapshot date 2026-10-09.

## Four User-Supplied NGA Images

The current image viewer rejected image input. Text was extracted using local
Windows OCR; keep spelling/numerical ambiguities explicit. Raw extraction is
`references.ocr.json`. Original JPEGs remain untouched at user-provided paths.

1. Equipment list: H8 effect head, necklace, polearm, heart; crafted shoulder
   and shoes with Arcanoweave; Murder Row cloak/wrist/hands/legs/ring and a
   Resonant Bellowstone; tier chest, auction-house belt, crafted ring.
2. Quick-finish plan: Heroic final boss plus Murder Row; take a haste/mastery
   Vault ring if available and buy a haste/mastery BoE belt. Suggested unflasked
   stationary ratings: mastery 1350-1400, haste 950-1000, crit 800-850, minimal
   versatility. Suggested mastery flask for AoE and haste flask for single target.
3. Cropped text repeats the suggested stat ranges; it is not independent evidence.
4. Older dated reply (2026-08-19): H8 converted head, necklace, polearm and heart;
   tier shoulder/chest, H7 cloak/belt/converted legs, crafted crit/mastery wrists
   and shoes, Murder Row hands, H4 crit/mastery ring, PvP haste/mastery ring,
   H2 core. It predates the proposed 12.1.5 route.

These references agree on H8 and a high mastery/haste direction but disagree on
the second trinket, crafted slots, and how many raid pools to pursue. The quick
route optimizes accessible completion; the dated response maps an alternative
end-state. None proves exact stat breakpoints or live future-item superiority.

## Tooltip and Model Caveats

The necklace's dynamic-rating tooltip exposes multiple stat alternatives; raw
tooltip sums are not panel stats. The BoE belt shows random-stat placeholders.
Use SimulationCraft's resolved item stats or a panel screenshot instead of adding
all tooltip alternatives. Talents, racial/passive effects, enchants, gems, oil,
flask and combat procs distinguish stationary ratings from combat percentages.

Current Kith'ix PTR candidates: 281236 leather chest, 281029 ring, 281215 trinket.
Source: https://www.wowhead.com/ptr-2/npc=267861/kithix

Local implementation `unique_gear_midnight.cpp` flags the chest/ring AoE damage
as unverified (assumed not split). The trinket has a new-target trigger; static
five-target damage is not a full dungeon model. Tests include DungeonSlice as
a sensitivity model, not a replica of a real route. Default item IDs omit
bonus-attached effects; include chest bonus 14049, head 13847, polearm 13846.

## Simulation Design

Build local CLI outside SimC source at `.local/simc-build`; leave its dirty
source state untouched. The explicit comparison input is `candidates.simc`:
same original talents/race, 334 candidate items, MID2 four-piece preserved,
source-stat redirection for catalyst candidates, identical oil/no flask/food
settings. Candidate upgrades are conditional possibilities, not acquisitions.

Compare single target, five-target Patchwerk and DungeonSlice. Compare both
individual upgrades and passive-trinket options after a polearm+heart anchor.
Run equal-budget 100-rating swaps separately from obtainable gear; they measure
local sensitivity, not a full build at the NGA recommended ratings.

Record actual outputs, errors, effect activation and confidence before deriving
coin priorities. No simulation result exists until the CLI finishes successfully.

## Superseding Attainable-End-State Request

The user replaced current-equipment upgrade ranking with attainable full-set
optimization and permits replacing all existing crafts. Exclude inaccessible
Mythic raid 7/8 and special 9/6 ceilings. `candidates.simc` and its outputs are
historical current-equipment sensitivity work, not the final recommendation.

`bis.simc` compares a complete 334-loot/331-crafted target with 15 alternatives,
2500 iterations each in single-target, five-target and DungeonSlice models.
`bis-refine.simc` combines the new ring in the second slot, H4 shoulder and new
trinket, then tests real craft pairs, chest/passive alternatives and craft slots.
See `bis-recommendation.md` for decisions and limitations. No run proves a global
optimum across all loot, talents, enchants, gems or dungeon routes.
