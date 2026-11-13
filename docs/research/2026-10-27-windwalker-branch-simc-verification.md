# Windwalker Branch Samples Verified with Local SimulationCraft

Date: 2026-10-27, Asia/Shanghai.

This study actually ran the local SimulationCraft executable and captured all five
requested first-RSK outcomes using natural seeds: neither hit critical, main-only
critical, Dawn-only critical, both critical, and absent Dawn. These are mechanism
and default-APL examples. They do not establish globally optimal rotations or
counterfactual continuations from an identical combat state.

The machine-readable delivery is
[`simc-branch-evidence.json`](../../apps/windwalker-trainer/tests/fixtures/simc-branch-evidence.json).
Inputs, full logs, JSON reports, bounded sweep results, extraction scripts and
short line-numbered excerpts are under
[`.local/windwalker-v4-simc/`](../../.local/windwalker-v4-simc/).
Only that directory, the evidence fixture and this document were written. No
trainer runtime code or SimC source was changed, and no Git write was performed.

**Pinned executable and source.**

| Item | Verified value |
| --- | --- |
| Source checkout | `E:/github/simc` |
| Source HEAD | `73a372b76188c703e48729caded3258cdc5b726b` |
| Source worktree at collection | Clean |
| Executable | `E:/github/wow-skills/.local/simc-build/Release/simc.exe` |
| Executable SHA-256 | `934cfeb8fe672baee8bd88678bd7dd0788c1755b608c1d25aa30b96f29925633` |
| Report version / engine version | JSON `2.0.0` / SimC `1210-01` |
| Live DBC | WoW `12.1.5.70529`, hotfix `2026-10-22/70529` |
| Base input SHA-256 | `e7339a1b57eb396d19c9bfec29b9da32b78582bdeb671b109e9dbf5700ed4eec` |

Each sample additionally records its wrapper input, full log, report and excerpt
SHA-256. The wrapper includes the shared, hashed `base.simc`; its hash alone is
not the hash of the entire input dependency set.

**Declared simulation conditions.**

Every representative uses the existing fixed talent string, a level-90 Pandaren
Windwalker, two initial chi, the preserved compatible equipment, Patchwerk,
`max_time=300`, `fixed_time=1`, `vary_combat_length=0`, `iterations=1`, `threads=1`
and `optimal_raid=0`. Only events in `[0, 45]` seconds enter the fixture. The
underlying simulations actually finish at 300 seconds; these are not 45-second
fights with end-of-fight cooldown logic.

There is no `actions` override. The engine generates its pinned default APL.
The five principal samples have one target and no Bloodlust, differing only in
seed and output/report destinations. Two additional configurations use three or
five targets and start-of-fight Bloodlust, both with seed 1. They are supplemental
context checks with a different opener, not additional single-target branches.

The inherited default consumables remain enabled: `flask_of_the_magisters_2`,
`harandar_celebration`, `void_touched`, `potion_of_recklessness_2` and
`main_hand:thalassian_phoenix_oil_2/off_hand:thalassian_phoenix_oil_2`. Each selected
JSON report independently confirms baseline haste rating **836** and haste
**0.19**. An initial diagnostic with all consumables disabled produced 820 haste
rating and 18.636%; it was excluded from the sweep and evidence samples.

Baseline crit is 33.8913%. Baseline attack power is 2635 in this unbuffed-raid
context. The trainer calibration report used a different raid-buff context;
matching the 19% haste and talent profile does not imply matching every damage
coefficient or attribute. Equipment/passive procs, potion effects and Momentum
Boost remain active. Actual in-combat haste is therefore not held at a constant
19%, and Jade recovery-rate changes also modify cooldowns.

The engine's lag defaults are retained and recorded from the report: queue lag
0.005 seconds with 0.001 standard deviation, GCD lag 0.150/0.037, channel lag
0.250/0.062, and world lag 0.100/0.010. No roll was forced and the engine was not
patched to produce a branch.

**Equipment compatibility is preserved.**

The equipment lines are inherited verbatim from the existing
[`default-apl.simc`](../../.local/trainer-v3-assessment/default-apl.simc).
Neck `268265`, trinket `270175` and weapon `268215` retain explicit `ilevel=341`.
These overrides address the previously documented discrepancy between the older
DBC bonus resolution and the current character display; they are not new bonus
data or independent measurements of live item stats.

Historical `redirected_base_stats` remain shoulder `251146`, chest `281236`,
hands `272241`, waist `271436`, and legs `251130`; the waist also retains
`crafted_stats=36/49`. These are the existing catalyst/predecessor continuity
assumptions. Their provenance and limits are described in the prior
[`gear-review.md`](../../records/cn-barrens-shaseng/analysis/2026-10-26/gear-review.md).
Removing those fields would change the character and invalidate the intended
comparison.

**Bounded natural sweep and representative outcomes.**

The sweep ran seeds **1 through 64**, once per seed, using `log=1`, `debug=0` and
the same 300-second base input. The outcome totals were:

| First-RSK category | Count among 64 |
| --- | ---: |
| Both present, neither critical | 5 |
| Main critical, Dawn noncritical | 2 |
| Main noncritical, Dawn critical | 3 |
| Both critical | 12 |
| No Dawn | 42 |

These counts describe this bounded sample, not estimates of branch probabilities.
Fifty-nine seeds shared the core prefix `tiger_palm → invoke_xuen_the_white_tiger
→ zenith → fists_of_fury → rising_sun_kick`. Five inserted an SCK before the
first RSK. All five selected representatives use the common prefix. Auto-attacks,
Touch of Karma, potion and automatic/passive damage still occur around that core.

Selected seeds were replayed with `debug=1`, `log_spell_id=1`, and a JSON report
using `full_states=1`. For all five single-target samples, the actual core casts
and their millisecond log times through 45 seconds matched the original sweep;
first-RSK hit outcomes matched as well. Enabling full-state reporting also
preserved each of the seven representative configurations' actual cast traces
and first-RSK outcomes. No HTML report was requested.

| Category | Seed | First RSK | Main / Dawn | FoF before selection | CDR records at RSK | Directly logged FoF remains after CDR | Chi after pair |
| --- | ---: | ---: | --- | ---: | --- | ---: | ---: |
| Neither critical | 13 | 3.611 | hit / hit | 8.840 | none | not captured | 5 |
| Main only critical | 36 | 3.637 | crit / hit | 8.468 | −2.285 | 6.183 | 5 |
| Dawn only critical | 5 | 3.581 | hit / crit | 8.647 | −2.285 | 6.362 | 5 |
| Both critical | 12 | 3.543 | crit / crit | 8.559 | −2.285, −2.285 | 3.989 | 5 |
| No Dawn | 1 | 3.640 | crit / absent | 8.688 | −2.285 | 6.403 | 4 |

Times and cooldowns are in seconds. “Neither critical” explicitly includes a
present, noncritical Dawn. “No Dawn” is a separate observed absence, not a
noncritical hit. Each selected first-RSK selection snapshot has five chi, consumes
one chi, and a present Dawn returns one chi regardless of its critical result.
Consequently, seed 1 and seed 36 both have one critical hit but end the pair with
different chi. A critical count alone cannot describe the next decision state.

The main and Dawn have separate damage action identities and separately observed
results: `rising_sun_kick_damage` (185099) and
`glory_of_the_dawn_rising_sun_kick_damage` (392959). The two single-critical samples
demonstrate that neither action inherits the other's critical result. In the
source, Dawn executes a separate damage action after a haste-dependent proc roll,
and both use the same base damage impact handler for FoF reduction. This supports
separate outcome handling; the small sweep is not a statistical independence test.

The logged −2.285 seconds is the adjustment actually applied in the active
recovery context. `cooldown_t::adjust` applies the action's recharge-rate multiplier
to the talent reduction. It must not be reinterpreted as four wall-clock seconds,
nor have haste applied to it a second time. WDP/Jade and later buff expiration
then rescale remaining cooldowns dynamically, so that immediate `ready` timestamp
is not a promise of the eventual next FoF cast time.

**Observed continuations through 45 seconds.**

| Category / seed | First WDP + ordinary Jade | Next FoF after first RSK | First Conduit start → cancellation / Great Jade | Second Zenith |
| --- | ---: | ---: | --- | ---: |
| Neither critical / 13 | 4.618 | 10.312 | 12.116 → 12.950 | 22.066 |
| Main only critical / 36 | 4.642 | 8.900 | 10.708 → 11.548 | 22.715 |
| Dawn only critical / 5 | 4.585 | 8.963 | 10.802 → 11.664 | 25.209 |
| Both critical / 12 | 4.548 | 6.884 | 10.676 → 11.462 | 22.115 |
| No Dawn / 1 | 4.645 | 7.891 | 11.778 → 12.618 | 22.169 |

All five samples execute WDP after the first RSK and subsequently gain ordinary
Jade at that WDP timestamp. In seed 12 the early visible continuation is
`RSK 3.543 → WDP 4.548 → SCK 5.552 → FoF 6.884`; seed 13 instead follows
`RSK 3.611 → WDP 4.618 → SCK 5.622 → RSK 6.918 → Blackout 7.924 → SCK 8.927
→ FoF 10.312`. These are observed APL continuations, not prescribed unique routes
for every state with the same first critical category. All core casts through
45 seconds, including filler and Rushing Wind replacements, are retained in the
fixture rather than inferred from phase names.

Ordinary Jade has a first six-second gain/loss pair in each selected sample;
Great Jade similarly lasts six seconds, and each Zenith Jade lasts four seconds.
The buff identities remain separate: ordinary `heart_of_the_jade_serpent`
(443421), Great Jade `heart_of_the_jade_serpent_unity_within` (443616), and Zenith
Jade `heart_of_the_jade_serpent_yulons_avatar` (1238904). Their raw DBC duration
fields alone do not replace the observed effective gain/loss times.

The logs explicitly record Conduit's `cancel_if returns 1, cancelling channel`,
followed at the same timestamp by Great Jade. The second Zenith is an actual
`performs Action` event, with its own Jade gain, not a milestone inferred from
elapsed time. In the double-critical sample, WDP at 4.548 changes FoF's ready time
from 7.532 to 6.098; Zenith Jade expiring at 5.831 changes it again to 6.344.
Further SCK reductions and other state changes are visible in the excerpts.

**Supplemental three/five-target Bloodlust checks.**

| Targets / seed | Conduit start → cancel / Great Jade | First Zenith / FoF | First RSK | Main / Dawn | FoF before RSK selection | Next FoF | First WDP | Second Zenith |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 3 / 1 | 1.762 → 2.408 | 2.758 | 5.274 | crit / crit | 0.414 | 6.278 | 9.761 | 23.633 |
| 5 / 1 | 1.762 → 2.408 | 2.813 | 5.304 | crit / crit | 0.439 | 6.309 | 10.729 | 22.364 |

These configurations naturally prioritize Conduit earlier, as allowed by the
target-count/Bloodlust APL condition. Their first RSK has both critical hits, but
the main hit's logged −0.914-second adjustment already resets FoF. The logger then
prints raw `ready=-3600.000` and a negative `remains`. Those values are internal
reset sentinels, not physical cooldown durations. The later Dawn hit is critical,
but `cooldown_t::adjust` returns immediately for an already-ready cooldown and
does not emit another adjustment line. Both hits were observed; a second measured
CDR amount was not. The fixture preserves the raw sentinel record and leaves the
post-hit cooldown point unmeasured.

SCK also contributes delayed FoF reduction at ground-effect expiration, using
distinct targets hit subject to the source cap. Its reduction records and the
actual dynamic FoF recovery changes are retained in each local excerpt. The
supplemental cases do not hold buffs or opener state equal to the single-target
samples and cannot serve as counterfactual replacements for them.

**Evidence interpretation and reproduction.**

Line numbers in the fixture always refer to the original full log, starting at
one. Each `.evidence.txt` line repeats that original number alongside the exact
source text. Hit and first-RSK cooldown records additionally embed the exact log
line in the fixture, so the central mechanism observations remain readable even
without the larger local files.

JSON `action_sequence` records selection/queue snapshots; they are not universally
execution-time snapshots. For example, seed 1 reports a later RSK selection at
6.840 but logs the actual execution at 6.887. The fixture's `coreCasts` always use
the latter `performs Action` records. Each selected first-RSK selection time
matches execution to displayed log precision, and its report JSON pointer is
recorded explicitly. Active buff stacks/remains and reported cooldowns are copied
from that snapshot, not reconstructed from a trainer state.

Full-state JSON reports only list cooldowns that are down. An omitted cooldown is
stored as `null`, not an invented measured zero or an inferred charge count. In
the neither-critical sample no immediate post-hit FoF point was logged, so that
value remains `null` even though the preselection value and absence of a same-time
adjustment are known. The AoE reset-sentinel cases also have no numeric measured
post-hit cooldown in the fixture.

Use PowerShell from `E:/github/wow-skills` to reproduce a selected sample:

```powershell
& ./.local/simc-build/Release/simc.exe `
  ./.local/windwalker-v4-simc/st-double-crit-seed-012-debug.simc
```

The wrapper selects seed 12, the shared base input, `debug=1`, and the full-state
JSON report destination. The other six wrappers are listed with full executable
commands and hashes in the fixture. To repeat the bounded sweep and rebuild the
evidence from the selected reports:

```powershell
python ./.local/windwalker-v4-simc/verify.py
python ./.local/windwalker-v4-simc/build_evidence.py
```

The sweep script has a fixed 64-seed range and a per-process timeout. It neither
changes engine RNG nor searches without a bound. Source RNG initialization,
`deterministic` reseeding, debug/log behavior, cooldown adjustment, JSON snapshot
collection and APL references are recorded with local source paths and line
numbers in `provenance.sourceRefs`. `deterministic=0` with an explicit nonzero seed
uses that seed without the extra per-iteration reseed performed by
`deterministic=1`.

The final local audit checked all referenced artifact hashes, all 64 sweep
classifications, all seven completed 300-second representative runs, 380 event
references, the five selected sweep/replay traces, first-window Jade durations,
the preserved equipment lines, and null/reset-sentinel handling. Its result is
[`audit.json`](../../.local/windwalker-v4-simc/audit.json). Trainer runtime tests
were not needed for this evidence-only change.

The engine reports implementation-not-yet-verified damage-splitting assumptions
for Battle Gi of the Monkey King and Band of the Swarmcaller. Those notices,
historical equipment assumptions, different raid-buff context, and omitted trainer
pet/item/passive contributions limit damage comparisons. This delivery validates
observed hit identities, CDR records and APL continuations in the pinned SimC
model; it makes no measured DPS-loss, global-optimality or live-client-parity claim.
