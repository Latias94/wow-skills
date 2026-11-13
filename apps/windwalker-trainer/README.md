# Windwalker Dojo

A buildless, browser-local burst trainer for Shaseng's Celestial Conduit Windwalker build. Version 04 turns the supplied burst diagrams into a stable conditional routine map, with channel bars, resources, critical-branch feedback and eight action slots in the same viewport. It includes generated Pandaren action sprites, protected/raw input, six scenario presets, local candidate comparison, checkpoint retry and restorable JSON export.

Private hosted app: https://shaseng-windwalker-dojo.frostyfir65.chatgpt.site

## Run

Requires Node.js for tests and Python 3 for the local server. No npm dependencies or install step.

```powershell
cd E:\github\wow-skills\apps\windwalker-trainer
npm test
npm start
```

Open `http://127.0.0.1:8766`. Serve over HTTP; opening `index.html` directly does not reliably load JavaScript modules. The server binds to loopback only.

Default keys: `1` Rising Sun Kick / Rushing Wind Kick, `2` Tiger Palm, `3` Blackout Kick, `4` Xuen / Celestial Conduit, `5` Zenith / Zenith Stomp, `E` Spinning Crane Kick, `F` Fists of Fury, `G` Whirling Dragon Punch. There are eight dynamic action buttons. The Blackout Kick icon only highlights; it does not transform into Rushing Wind Kick. Ordinary valid spells can interrupt Conduit to obtain Great Jade; Zenith Stomp can coexist with that channel. `Esc` / `X` explicitly cancel a channel, Space pauses, and Enter starts a round. Bindings are editable and saved in local browser storage. Opening any inspection dialog or hiding the browser tab pauses active training; closing a dialog leaves it paused for deliberate continuation.

The UI defaults to protected input. Other skills cannot clip FoF, and the optional SCK guard prevents FoF from replacing an active SCK channel. Valid ordinary RSK, Palm and Blackout inputs can coexist with SCK. Rushing Wind has different coexistence rules despite sharing the RSK slot. Explicit cancellation remains possible. Raw mode disables those input guards. These are input policies on the same combat model, not a claim to reproduce every in-game macro. The engine class defaults to raw for standalone compatibility; the UI passes its protected setting explicitly.

## Model Contract

- Pinned source: SimulationCraft `73a372b76188c703e48729caded3258cdc5b726b`, Live `12.1.5.70529`, personal research dated 2026-10-26.
- Profile: Shaseng's current four-piece / Celestial Conduit / 20-second Zenith talent string, in `dist/calibration.js`.
- Fixed one-second melee GCD; spell-specific Xuen/Conduit GCDs. Two Zenith charges recharge serially; manual stomp uses gate reactivation. Although Zenith itself is off-GCD, this reference scheduler waits for Xuen's GCD before Zenith, matching the default pinned APL probe.
- Current talent-adjusted costs: Tiger Palm 55 energy; FoF 2 chi / 1 during Zenith; RSK and SCK 2 / 1. Energy regen 11/s before haste. Defaults are 2 chi and 10 Tigereye stacks, not a claim about every live pull's starting resources.
- RSK, independent Rushing Wind and FoF cooldown work is hasted; WDP is not. All three receive appropriate Jade recovery multipliers. A four-second discrete reduction advances the wall-clock completion by `4 / recovery`, without dividing by haste again.
- Small/large Jade lasts approximately six seconds; Zenith Jade lasts four. Large replaces small; Zenith Jade remains independent. FoF normally has five normal pulses and one immediate half-strength tier hit. It snapshots haste, fixes the end event at channel start and reads the current Jade multiplier when scheduling each next pulse; a mid-channel Jade expiration can reduce normal pulse count without a player clip.
- Implemented proc paths include haste-scaled Dawn chance, the RSK-family crit modifiers, chi from Dawn, 8% Tiger Palm highlight, 60% highlighted Blackout-to-Rushing-Wind, 1 RPPM haste-scaled Dance with bounded bad-luck protection, guaranteed Dance from WDP and highlighted Blackout from Dance-SCK. The missing Echo/Obsidian talents are not granted.
- Forced branches distinguish no crit, main-only crit, Dawn-only crit, double crit and no Dawn. They are drills, not probability predictions. A fixed RNG seed requires the same input timing/order to reproduce a run.

### Damage Is Approximate

`scripts/extract-calibration.py` exports named non-critical observed minimum hits from the existing personal raid SimC report, with a SHA-256 provenance record. These are not isolated naked coefficients; residual report buffs can remain. Dynamic tier multipliers and critical results provide training feedback, not a complete calibrated character simulation.

Not modeled fully: auto attacks, Xuen pet/Empowered Tiger Lightning, trinkets, enchants, embellishments, several hero-passive damage components, Teachings extra damage, Jadefire/Chi Explosion, Momentum Boost's full damage ramp, all live-client cancellation latency and every APL condition. Five-target scaling is approximate; it is not a DungeonSlice simulation. Do not compare its damage/DPS with WCL or Raidbots, rank gear by it, or claim measured DPS-loss percentages from its feedback.

The coach uses `dist/policy.js`, an explicit ordered projection of the pinned APL for this fixed build and the implemented core buttons. It returns the first executable rule, source line, action identity and explanation without consuming RNG or probing future rolls. Strict time-threshold decisions use a consistent next-millisecond boundary; state expiration and actual cooldown readiness retain engine event boundaries. It is not complete SimC parity or a proof of globally optimal damage. Trinket/potion/racial/external-buff, Touch of Death and Slicing Winds decisions are excluded, rather than assumed to be untalented.

The reference scenario is homogeneous Patchwerk targets with a 300-second lifetime. A 45/60/120-second round is a prefix, not a target scheduled to die at the training bell. End-of-fight dumping is therefore not applied. In source line 248, the pinned `cooldown.whirling_dragon` name resolves to an initially ready placeholder, not the real WDP cooldown; the projection preserves this condition instead of silently correcting upstream text.

### Timing Evidence

Timing was checked against six short local SimC debug probes, not just tooltip arithmetic. Source locations in the pinned revision:

- SCK channel / independent ground driver: `sc_monk.cpp:1591`, `:1596`, `:1619`, `:1649`; ground expiration in `ground_aoe.cpp:287`. Channel lasts `3 * round(500 / haste) ms`; four ground pulses start immediately at `(1.5 / haste / 4 - 0.1)` intervals. The talent CDR callback occurs at fixed cast +1.500 seconds, even after canceling the channel.
- FoF dynamic tick scheduling and fixed end: `action.cpp:2792`, `dot.cpp:815`, `:919`, `:1144`, `parse_effects.hpp:1123`. Pure haste changes do not alter its snapshot. Already scheduled ticks are not moved by Jade expiration.
- Dawn executes synchronously after the main hit: `sc_monk.cpp:987`. The previous artificial 0.36-second delay has been removed.
- Rushing Wind is a distinct action/CD: `sc_monk.cpp:1179`, generated DBC row `sc_spell_data.inc:26282`; base cooldown is 10 seconds. The same physical Sun key resolves its actual spell before cooldown validation. Rushing Wind does not start Sun cooldown, trigger WDP availability, or inherit Sun's SCK coexistence permission.
- WDP availability: `sc_monk.cpp:4552`. Sun/FoF execution can establish a nonrefreshing ready buff lasting `min(SunCD,FoFCD) + 1.5 / haste`; subsequent Sun resets do not erase it.
- Conduit APL cancellation: `dot.cpp:825`, `:1112`; only nonzero timed ticks evaluate `cancel_if`. Manual X/spell cancellation remains distinct. The simulated cancellation grants Great Jade immediately; live input latency is not reproduced.

`tests/timing.test.mjs` locks these boundaries. `tests/reference.test.mjs` covers legal recommendations, determinism, channel protection, target-specific priorities and GCD-excluded FoF opportunities.

### Branch Routine, Session And Review

`routine-graph.js` builds a serializable routine with a shared prefix through the next RSK-family input and six exact outcome branches: critical/noncritical main hit, crossed with absent/noncritical/critical Dawn. The view groups these as no/single/double crit while keeping each exact result individually selectable. It preserves the full burst phase outline, physical slot and resolved spell, channel duration and window-instance identity. Common skill order is the layout axis; simulation time determines legality, cooldowns and channel completion.

`routine-runner.js` owns the route cursor, observed branch selection, completed nodes, adaptations and deviations. Ordinary clock ticks do not replace a route. Successful execution advances it once; queued and rejected inputs do not count as completed skills. An actual RSK result selects the exact edge by cast ID, and that selection remains visible through its segment. A later unresolved RSK receives its own fork. Past routes remain available through the map's archive selector and review records.

Previews replace the fork's hidden RNG with a fixed display seed. They enumerate the next Sun outcome and stop at the next meaningful unresolved Sun/Blackout decision, with later proc-dependent actions marked conditional. They do not read the live future RNG. Immediately before a matching Sun executes, its unresolved fork is rebased on the actual physical state while retaining the graph/prefix identities. The selected summary then comes from the observed result. Similar-looking paths can share presentation without merging their underlying combat states.

The ordered APL projection remains the reproducible reference. The optional candidate dialog separately compares a few legal first actions with paired sample rollouts over 8-12 seconds plus four seconds of continuation. Close/noisy comparisons retain the baseline. It never silently replaces the stable visible teaching route and is not a globally optimal rotation solver. The diagrams' historical 6-7 / 5-6 / 7 FoF totals are not pass thresholds.

`session.js` owns Combat, the routine runner, session lifecycle, input records, accepted queues, asynchronous candidate jobs and atomic retry checkpoints. Queue execution is observed at its actual boundary using the original attempt identity. Old job generations/revisions cannot alter a new or restored session. The DOM entry point composes these modules; it no longer owns competing battle flags and checkpoint arrays. The former history-inferred live milestone implementation and single sampled continuation display were removed.

Each different legal action retains the original reference in an archive and records the actual deviation before attaching recovery from the new physical state. It is a choice needing inspection, not an automatic measured DPS loss. Review uses the same graph/node/action IDs as practice. Physical clips, overflow and repeated attacks remain factual evidence. A timer adaptation is distinguished from a player's different input.

The latest 100 accepted-input checkpoints store Combat, the complete teaching state and input-record contents. Retry restores all three, including pending channel ticks, queued attempts, live RNG, same-timestamp execution order and branch selection, then pauses for inspection. Later queue replacements/executions cannot leak their mutated record status into the restored history. Checkpoints remain in memory and are lost on reload.

Schema 4 JSON export includes the final restorable physical and teaching state, route history/archives, original input evidence, calibration/policy provenance, the demonstration flag and the latest candidate comparison with its timestamp/staleness. It does not contain an exact live DPS-loss assessment.

Critical feedback retains separate main/Dawn labels, no/single/double crit, measured FoF wall-time reduction and the distinction between cooldown-ready and legally castable. Each hit has its own number and explicit critical label. Optional audio starts after a user gesture; reduced motion retains the text and route selection.

Optional Bloodlust lasts 40 simulation seconds and multiplies haste by 1.3. It affects hasted recovery, regeneration, Dawn probability and channel timing, not the fixed melee GCD. Buff bars and all route/channel playback pause with simulation time.

### Actual SimC Sample Evidence

The local pinned SimC executable was run for seeds 1-64, each with the default APL, a 300-second fixed lifetime and one iteration. Five natural first-RSK categories were selected and replayed with debug logs and full-state JSON, plus three/five-target Bloodlust contexts. Runtime source was not patched to force their results. The complete audited fixture is `tests/fixtures/simc-branch-evidence.json`; the small presentation snapshot is `dist/simc-samples.js`, shown in **拳谱依据 -> 查看实际跑过的 SimC 分支样例**.

The samples independently demonstrate main/Dawn results, recovery-scaled FoF reductions, WDP/Jade, Conduit cancellation/Great Jade and later Zenith casts. During the selected single-target Zenith-Jade context, each crit logs an approximately 2.285-second reduction rather than four wall seconds. No Dawn and a noncritical Dawn remain distinct because only the latter returns chi. Tests compare directly measured cooldown/chi transitions with isolated core mechanics; they do not claim full damage/APL timing parity.

Different natural seeds are not identical-state counterfactuals. SimC includes lag, equipment/passive/potion effects and missing damage components. The fixture preserves item-compatibility assumptions and marks omitted cooldown readouts as null; a cooldown reset sentinel is not a negative duration. These examples establish possible observed reference paths, not branch probabilities or global optimality. The research report is `docs/research/2026-10-27-windwalker-branch-simc-verification.md` in the parent repository.

### Scenarios And Artwork

Six presets cover single-target burst, five-target burst, a declared RSK crit branch, a low-chi checkpoint with active SCK, a 120-second sustained loop, and a public synthetic wave sequence. Checkpoints are established by legal cast replay, preserving pending events rather than inventing disconnected cooldown values. The wave example is five targets at 0s, one at 18s, untargetable at 25s and five again at 30s. It is not a specific dungeon route. Presets and settings do not change the fixed talent profile.

The current panda monk is based on the user's reference screenshot: a friendly round face, gray hair tuft, red-and-gold clothes and a jade belt. Ten individually generated, transparent key poses cover 12 skill states: idle, Palm, Blackout, RSK, Rushing Wind, FoF, SCK, WDP, Xuen, Conduit, Zenith and Stomp. Wind shares the Blackout body pose; Zenith shares the invocation pose. These are held skill poses, not video-derived character animation. `dist/assets/sprites/v6/manifest.json` records their dimensions, alpha bounds, hashes, source and quality checks. The artwork is a generated practice interpretation, not an extracted Blizzard model or animation.

Seven independently animated Forge FX families, a monastery background and a separate training dummy accompany the character. `dist/sprite-data.js` declares all runtime assets. `scripts/package-character-art.py` packages reviewed Forge pose outputs under the ignored `.local/windwalker-art-v6/`; `scripts/build-stage-art.py` combines the character manifest with reviewed FX and scene sources under `.local/windwalker-art-v5/`. Raw sources, the identity reference, prompts and detailed QC stay outside deployment. All ten character poses passed the Forge processor's structural checks.

The renderer uses simulation time for body states, channel effects and persistent buffs, including Xuen. SCK ground effects survive legal body weaves and cancellation while scheduled hits remain. Pause, retry and reduced-motion settings apply to the artwork too. Artwork never determines damage, hit timing or cancellation; those come from the combat engine.

Character and FX sheets preload without blocking the controls. A pose changes only after its image decodes; pending or failed replacements retain the last painted character. Asynchronous completion reads the latest requested frame and cannot restore an obsolete pose or a canceled channel. Run `npm run test:browser:sprites` with the local server running to verify cold loads, paused playback, reset, failed downloads and canceled FX in a fresh browser context.

The dedicated dragon sheet failed cross-cell spill checks and is excluded. Dragon, Jade and Zenith reuse the reviewed Conduit energy sheet; Palm shares the golden fist sheet and Stomp shares the ground ring. The seven packaged FX sheets passed the processor's empty-frame, clamping and source/output-edge checks. Raw-source safe-margin and faint-speck warnings are preserved in `.local/windwalker-art-v5/fx-qc/`; they should not be described as a clean raw-source QA pass. The deployment manifest records processed asset hashes and these reuse limits.

### Spell Assets And Tooltips

`scripts/fetch-wowhead.py` retrieves the 11 Live Chinese tooltip records through `nether.wowhead.com/tooltip/spell/{id}?dataEnv=1&locale=4`, then downloads the corresponding icons from Wowhead's `wow.zamimg.com` CDN. The resulting local snapshots are in `dist/skill-data.js` and `dist/assets/icons/`; the app does not need to contact Wowhead while training.

Hover/focus shows a safe, plain-text current-build description. The reference dialog links each spell to its Chinese Wowhead source and exposes the original plain-text tooltip separately. Base tooltips can contain multiple specializations and omit talent modifications. They do not override the pinned combat model. Raw third-party HTML is never executed or inserted into the DOM. The art assets remain the property of their respective rights holders; this is an unofficial personal training experiment.

## Verify

```powershell
node --test tests/*.test.mjs
node --check dist/combat.js
node --check dist/app.js
```

`node scripts/verify-browser.cjs --headless` launches an isolated headless Edge session and leaves the user's own Edge untouched. It verifies 1366x768 / 1920x1080 / 390x844 layouts, all five declared crit variants, independent hit labels, protected FoF, explicit Escape, dynamic slots, checkpoint retry, pause, SCK coexistence, binding persistence, stable route identity, exact branch selection, candidate comparison, local art/icons, actual SimC examples, sourced descriptions and schema 4 export. QA artifacts are outside deployable assets, under the repository's ignored `.local/windwalker-trainer-qa/`. The script uses the locally installed Playwright CLI's `playwright-core` path; adjust that import on a different machine.

## Update Data

```powershell
python scripts/extract-calibration.py --report <personal-simc-report.json>
python scripts/fetch-wowhead.py
```

A new report alone does not change talent-specific model behavior. Revalidate `dist/combat.js` against the corresponding SimC build before changing the profile or version claim.

## Scope And Privacy

The app runs entirely in the browser, does not connect to a game account, does not automate WoW, and has no server-side player database. Key bindings are stored locally. Session downloads contain combat training events and the calibration identifier. The Sites manifest identifies the private hosted app; existing analysis files elsewhere in this repository are not part of the deployment.
