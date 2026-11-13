# Windwalker Trainer: Current Problems and Redesign Recommendation

Date: 2026-10-27, Asia/Shanghai.

Status: evidence-based assessment and proposed direction, not an implemented redesign or an approved production specification.

Scope: `apps/windwalker-trainer`. This assessment preserves the existing eight dynamic action slots and Shaseng's fixed talent profile. It does not change the hosted app.

## 1. Intended Outcome

The trainer should help a player recognize the current state, select a strong next action, execute it with familiar input protection, and understand the consequence of choosing differently.

The primary training loop is:

1. Observe resources, cooldowns, channel progress and Jade windows in one place.
2. See a current-state continuation, with uncertainty shown at the first unresolved proc.
3. Execute a short sequence against a recognizable Pandaren monk animation.
4. Review the first meaningful decision difference.
5. Retry from that exact decision state, rather than replaying the entire opener.

Character animation, the reference sequence and the cast bar must support this loop. A decorative arena must not push the controls out of view.

## 2. Verified Current Problems

### 2.1 The training controls do not fit a common laptop viewport

An isolated Edge assessment captured the active, paused round at scroll position zero.

| Viewport | Reference panel | Skill bar | Bottom status bars | Result |
| --- | --- | --- | --- | --- |
| 1366 x 768 | y=195..461 | y=858..977 | y=977..1074 | The entire action bar is below the viewport |
| 1920 x 1080 | y=195..461 | y=858..977 | y=977..1074 | Bars fit near the bottom, but the coach extends to y=1125 |
| 390 x 844 | y=568..1162 | y=1609..1833 | y=1833..1930 | Reference, arena, actions and coach occupy separate screens |

The screenshot was captured while paused after starting FoF; it represents one reproducible UI state, not every possible text wrapping or device.

Evidence:

- `dist/index.html:32`: reference panel precedes the arena and action bar.
- `dist/index.html:58`: channel bar is placed inside the arena.
- `dist/index.html:68`: coach is a separate panel.
- `dist/style.css`: repeated layout overrides and a compact training variant do not establish a viewport-height contract.
- Local screenshots: `.local/trainer-v3-assessment/current-1366.png`, `current-1920.png`, `current-390.png`.

The previous checks for horizontal overflow and a 1440 x 1100 desktop are insufficient. Vertical visibility of the actual training controls must become an acceptance test.

### 2.2 The arena does not communicate individual skills

The arena uses one SVG monk and a generic translate animation for hits. It has no per-skill body animation, distinct wind-up, channel loop or channel release.

Evidence: `dist/index.html:45`, `dist/app.js:374`, and the `strike` / `impact` keyframes in `dist/style.css`.

The user cannot learn the visible distinction between a palm strike, rising kick, spinning kick, FoF channel and Conduit from these animations.

### 2.3 The full reference starts from the opener, not the player's current state

`renderReferencePlan()` keys the baseline by settings and bindings. It does not include current chi, cooldowns, channels or proc state. `buildReference()` constructs a new `Combat(options)` and follows one APL policy.

Evidence: `dist/app.js:95`, `dist/reference.js:11`.

The live coach does reevaluate the immediate next action. That is useful, but it is different from recomputing the strongest continuation from the current state.

The pinned SimC APL is an ordered priority list. Projecting it into the browser does not itself search alternative sequences or prove optimality.

### 2.4 Input protection is implemented only as advice

Reproduction:

```javascript
const c = new Combat({ initialChi: 6 });
c.cast('fists');
c.advance(1);
c.recommend(); // protect-fists, wait 2.36 seconds
c.cast('sun'); // accepted; cancels FoF and increments clippedFists
```

Evidence: `dist/policy.js:15`, `dist/combat.js:191`, `dist/combat.js:209`.

The public input path and the coach disagree about a protected channel. That can be intentional in a raw-input laboratory, but it does not match the requested default macro-assisted practice.

There is no per-button macro protection profile. `Escape` is not handled as an explicit channel-cancel key; `X` is.

Evidence: `dist/app.js:565` and `dist/actionbar.js`.

The queue also accepts failed requests whenever the GCD is within 400 ms, including a Conduit request whose cooldown cannot finish by that GCD. A subsequent impossible request can overwrite a valid queued Palm. Reproduction: start Conduit, advance 0.55 seconds, press Palm and then the Xuen/Conduit slot. Both report queued, but the second request replaces Palm and fails at +0.75 seconds. This needs an explicit queue-admission and feedback contract, not merely a recheck on execution.

### 2.5 There is a channel bar, but no useful channel decision display

The existing bar displays only the channel name, remaining time and percentage.

It does not show:

- individual pending hit times;
- whether another skill can coexist;
- whether a configured macro will reject the input;
- whether cancellation will lose pending channel damage;
- whether SCK damage continues independently;
- when SCK's delayed FoF reduction will occur;
- when ending Conduit grants Great Jade;
- the difference between GCD, channel protection and an accepted input queue.

Evidence: `dist/app.js:367`, `dist/index.html:58`.

### 2.6 The scenario controls do not represent raid or dungeon scenarios

The UI offers one or five homogeneous targets, fixed duration, start-of-round Bloodlust and a single global crit mode. The policy uses a 300-second Patchwerk lifetime.

There is no target-wave schedule, invulnerable interval, per-target lifetime, priority-target objective, current-state drill editor or retry-from-checkpoint flow.

Evidence: `dist/app.js:90`, `dist/combat.js:24`, `dist/policy.js:30`, `dist/index.html:20`.

Switching target count does not switch talents. A dungeon preset must say which talent profile it uses instead of silently presenting the same profile as a different build.

### 2.7 Review compares action identity, not the value of alternatives

`reviewRoutine()` marks a nonmatching policy action for review. It does not simulate both actions from the same state. The FoF interval begins at the first reference recommendation and can include later periods when the recommendation changes.

Evidence: `dist/routines.js:80`, `:91`, `:107`.

The current wording already avoids declaring measured DPS loss. The next version should add the missing counterfactual comparison rather than merely use a more assertive label.

### 2.8 The state is not safely forkable for optimization

`pending` stores callbacks closing over the original combat instance. The observation snapshot omits scheduled effects, complete charge queues, energy/proc accumulators, complete buff state and RNG-process state.

Evidence: `dist/combat.js:155`, `:367`.

Cloning the observation snapshot or JSON-copying a combat instance cannot create an equivalent branch. Reusing the callback closures can mutate the original instance.

### 2.9 Damage calibration cannot yet support a strong optimal-damage claim

The damage table uses observed minimum noncritical hits from a personal report. Those are not isolated coefficients, and multiple passive/pet/item contributions are omitted.

Evidence: `dist/calibration.js:35`, `README.md`, "Damage Is Approximate."

A search can still compare sequences inside this model, but a confident live-game ranking of close alternatives requires better coefficients and calibration. Optimizing a weak objective can produce a highly consistent but misleading training standard.

## 3. Recommended Screen

Use one training stage with a compact control dock, rather than a report page with training controls embedded in the middle.

Recommended desktop order:

```text
Compact session header: scenario / drill / pause / settings

             Pandaren monk <-> training target(s)
             Short contextual feedback at impact

       Current channel: progress, next hit, cancellation consequence
       Jade windows + chi / energy / GCD and accepted queue

       NEXT ACTION (large) | next 3-5 actions (conditional where needed)
       Your previous 3-4 actions aligned underneath

       1 Sun/Wind | 2 Palm | 3 Blackout | 4 Xuen/Conduit
       5 Zenith/Stomp | E SCK | F FoF | G WDP

       One-line reason: what changed and why the next action changed
```

Training controls, the current channel and the next-action ribbon must remain visible together at 1366 x 768 and 1920 x 1080 without scrolling. Exact element heights should be chosen through the layout implementation, not fixed by this text sketch.

On narrow screens, keep the action dock and short next-action ribbon together. Reduce or collapse the arena and move configuration into a drawer. Respect safe areas and focused text inputs.

Move the full APL sequence, source links, original NGA images, logs and long review tables into preparation/review views or drawers. They remain available but do not occupy the active training viewport.

Do not show both an eleven-node historical opener rail and a competing current-state recommendation as equally authoritative. The historical opener can be a preparation overview; the live ribbon is the active standard.

## 4. Channel and Macro Contract

There are three separate questions:

1. Does the combat model permit this action during the current channel?
2. Does this input button's macro condition permit the request?
3. Does the planner recommend that action now?

All three must use the same state, but they must not be collapsed into one boolean.

### Proposed input profiles

- **Protected practice, default:** other buttons protect FoF. FoF additionally protects SCK by default, with an explicit option to allow that clipping tradeoff. Ordinary Sun/Palm/Blackout weaving during SCK remains available where the selected mechanics model permits coexistence.
- **Raw input laboratory:** allows deliberate clipping and explains its modeled consequence.
- **Explicit cancel:** Escape terminates the current cast/channel when no dialog or text interaction consumes it; X remains a compatible binding. `/stopcasting` is an equivalent deliberate action for a future macro editor, not an implicitly inserted operation.

A macro condition belongs to the button invoking it. Adding protection to FoF's own macro does not globally stop other buttons from interrupting FoF.

A rejected macro request is not an accepted delayed action. Do not execute it automatically at channel end unless there is a separately defined and validated input-queue mechanism.

Do not use blanket `[nochanneling]` protection for every button. It would also prevent allowed SCK weaving and intentional Conduit cancellation.

### Channel behavior display

| Current effect | Action | Selected-model expectation | Training feedback |
| --- | --- | --- | --- |
| FoF channel | Ordinary rotation button | Raw path can clip; protected input rejects | "FoF protected; request not cast" or actual lost pending hits |
| SCK channel | Ordinary Sun / Palm / Blackout | Pinned SimC permits coexistence after GCD | "Weave allowed; SCK continues" |
| SCK channel | Wind from the same Sun slot | Different action; do not inherit Sun coexistence | Show the selected model's channel result; retain independent effects as modeled |
| SCK channel | FoF | User-selectable protection | Either reject, or show intentional transition and effect accounting |
| Conduit channel | Zenith Stomp | Pinned model permits coexistence | Conduit bar remains; stomp and chi gain are visible |
| Conduit channel | Explicit cancel or valid interrupting action | Pinned model grants Great Jade on actual termination | Show the Great Jade start, not just disappearance of the bar |
| Any channel | Unrelated unavailable button | Failed cast | Do not terminate a channel merely because a key was pressed |

SCK needs separate indicators for its channel, its four damage pulses, and its delayed FoF CDR. Completing one is not proof that the others completed.

FoF pulse markers must use the scheduled event times. Jade expiration can change later intervals; a fixed "five equally spaced dots" display is incorrect for those branches.

Conduit needs both an observed channel progress bar and a recommended cancellation marker. SimC's APL cancellation checks at timed ticks do not mean a human is physically unable to cancel between ticks.

### Live-client evidence still required

The local guide makes two claims that differ materially from the current pinned model:

- SCK to FoF can lose 25% SCK damage.
- Conduit interrupted by a different channel can delay Great Jade until the original Conduit end, while nonchannel interruption grants it immediately.

The current browser model retains SCK ground damage after canceling its channel and grants Great Jade immediately on every actual Conduit cancellation.

The guide additionally describes one manual Stomp during Conduit as free and off-GCD. The pinned model permits coexistence but the browser gives manual Stomp a one-second GCD; SimC explicitly zeroes the automatic triggered Stomp's GCD, not the manual cast's base GCD. Record this as a separate live-validation case instead of treating coexistence as proof of off-GCD behavior.

These differences cannot be settled by retelling the source. A future live-mechanics mode should be based on short, timestamped CN 12.1.5 dummy observations for Sun, Wind, FoF and explicit cancellation separately, with macro profile and talent string recorded.

The guide also warns against opening Zenith during the Xuen GCD. The browser projection currently recommends Zenith during that GCD, and a test explicitly locks that behavior. This is not established as the default SimC scheduling behavior: `action.cpp:372` defaults `use_off_gcd` to false, `player.cpp:4339` requires it to put actions into the off-GCD scheduler, and the default Zenith APL rows do not set `use_off_gcd=1`. A zero trigger GCD and permission to schedule during an existing GCD are different concepts. The previous conclusion that the browser behavior followed automatically from the source was incorrect. Reproduce the default SimC opener and compare full-window placement before choosing the teaching default.

A new one-iteration default-APL probe confirms the discrepancy: Xuen executes at 1.003 seconds and starts a GCD ending at 1.826; Zenith executes at 1.829. The browser reference instead casts Xuen and Zenith together at 1.000, then FoF at 1.840. Exact timings are not comparable across the different raid-buff/calibration settings; the verified result is that this native default execution waits for Xuen's GCD while the browser does not. Evidence: `.local/trainer-v3-assessment/default-apl.log:3846`, `:3847`, `:4214`, with the input at `default-apl.simc`. This is a scheduling check, not a damage comparison.

## 5. Define and Compute a Strong Continuation

### Three distinct references

1. **APL continuation:** a rollout from the current state, cheap and sourced; retain as a benchmark.
2. **Searched continuation:** evaluate multiple legal next actions and waits over a finite horizon, then continue their tails using a reference policy.
3. **After-the-fact oracle:** can explain an observed branch after it resolves, but must not supply a live recommendation that reads hidden future rolls.

The user-facing live standard should move toward (2). This directly answers the requested "best next sequence" rather than renaming (1).

### Deterministic drills

For a drill with explicitly supplied outcomes, search can return the strongest continuation within the stated model and horizon. Only label a result optimal within that scope when all relevant legal candidates have been exhausted or bounded. Beam search alone returns the best found result, not a proof.

Include waiting to the next meaningful event and deliberate channel transitions where allowed by the selected input profile. Otherwise the optimizer may miss the best way to place FoF inside Jade.

### Random practice

The first action should maximize an estimate of expected value using only currently observed state and the declared scenario.

Show the next action clearly. Show a few tentative later actions with a visible branch at the first unresolved outcome. Replan immediately after an observed crit, Dawn, proc, cooldown reset, buff expiration or target transition.

Do not present a thirty-second random future as a mandatory typing script.

Each candidate may use multiple sampled futures. Comparable branches should use deliberate common samples with correct marginal distributions; sharing the same single mutable RNG seed is insufficient because different actions consume different numbers of rolls.

### Objective and horizon

Optimize expected modeled damage to the intended targets over the relevant window, with a terminal continuation value so that dumping resources or delaying cooldowns beyond the horizon is not rewarded incorrectly.

FoF count, Jade coverage, proc waste and resource overflow are explanatory metrics, not the entire objective. Maximizing FoF count alone can teach a weaker sequence.

The horizon should span the active Jade segment and enough of its successor to value a setup action. The exact depth and latency budget should be measured during a prototype, not chosen as a permanent product limit in advance.

While coefficients remain approximate, label estimated differences as core-model comparisons and treat small, uncertain differences as equivalent. Do not create a precise live DPS-loss percentage.

### Necessary engine work

Keep a small external interface: export/restore a full internal state, enumerate legal input intents, advance to the next event, and evaluate a continuation.

The necessary internal work is:

- represent pending damage/CDR/channel events as data, with cast identity and captured modifiers;
- keep complete restore state distinct from the lightweight UI observation;
- create checkpoints only after the current atomic event/complete cast resolution; `sunResult.state` is currently emitted before the same cast establishes `dragonReady`, so it is not a complete end-of-cast restore point;
- store each active cast's captured state, including delayed SCK and FoF timing;
- keep actual player randomness separate from hypothetical sampled futures;
- run search away from the rendering/input loop;
- attach a state revision to each planner result and discard stale replies;
- use the same legality and macro rules in player play, demonstration and search.

Do not build a general APL language interpreter, port all SimC C++ into the browser, or introduce an unneeded framework migration.

## 6. Training Modes

Treat scenario, assistance level and randomness as independent controls, with useful presets.

| Mode | Initial state | Main exercise |
| --- | --- | --- |
| Burst tutorial | Valid opener snapshot | Learn body actions, channel lengths and the reference route |
| Crit-branch drill | Snapshot after an observed Sun result | Choose what changes after zero/one/two crits |
| Resource drill | Valid checkpoint with low chi, high energy or held procs | Avoid a scripted filler when the state calls for a different action |
| Single-target sustain | Longer target lifetime | Learn the interval between bursts and preparation for the next burst |
| Dungeon waves | Declared target arrivals, lifetimes and downtime | Value cooldowns across packs instead of only five eternal targets |
| Exam | Randomized valid checkpoints, hints hidden | Evaluate independent decisions; reveal comparison afterward |

Illustrative dungeon scenarios can use a short five-target pack followed by a single surviving priority target and a travel interval. These are synthetic exercises unless an actual encounter/route is independently modeled and sourced.

Known upcoming downtime can be supplied to both the player and planner. Hidden scenario changes must not be known only to the planner.

Custom states must be physically valid. Prefer checkpoints captured from a real model replay; an advanced editor must include active pending effects and validate resource, charge, buff and channel consistency.

Critical-branch exercises should be able to fix the next designated Sun event without forcing every future Sun in the round to the same result. Distinguish main-hit crit, Dawn occurrence and Dawn crit; the current single-crit drill always means main crit plus noncritical Dawn and does not cover the inverse single-crit case or no-Dawn cases.

## 7. Pandaren Animation Plan

Use a consistent Pandaren monk identity and separate per-action body sheets, with effects layered independently.

Required visible actions:

- idle/combat stance;
- Tiger Palm;
- Blackout Kick;
- Rising Sun Kick;
- Rushing Wind Kick;
- FoF loop;
- SCK loop;
- WDP leap/spin;
- Xuen summon;
- Conduit channel;
- Zenith activation and its automatic stomp;
- manual Zenith Stomp;
- explicit channel recovery/cancel transitions.

Sun/Wind and Xuen/Conduit still share their existing input slots. Different visual actions do not create additional buttons.

Start by accepting one idle identity sheet and one kick/FoF/SCK body family. Then generate other action sheets using that accepted visual reference. Do not generate all unrelated actions in one large raw sheet.

Use compact multirow grids, stable feet anchors, consistent body scale and generous safe padding. Wide Jade/Tiger/Crane effects should be separate assets so they do not shrink the body or cross frame boundaries.

Runtime behavior:

- channel body loops scale with simulation progress and pause with the fight;
- impact effects occur at actual damage events, not because an animation reached a painted frame;
- an SCK body transition to Sun does not destroy independent remaining SCK effects;
- off-GCD summons/Zenith can layer their effects without replacing a simultaneous higher-priority attack body animation;
- reduced-animation mode retains cast bars, pulse feedback and next-action visibility.

Image generation can provide original Pandaren-styled sheets; it does not automatically reproduce Blizzard's exact rig and animation. Exact game-model rendering is a separate asset pipeline and should not be implied by the proposed sprite work.

## 8. Review Should Explain the Decision

The first review screen should present at most a few high-impact teaching moments:

- "The observed crits completed FoF cooldown; this fill was no longer needed."
- "FoF was ready, but chi was insufficient: the next action needed to generate chi."
- "SCK and Sun coexisted; this was not a clipped SCK."
- "The macro rejected the key; no cast was executed or queued."
- "Two continuations are effectively tied within model uncertainty."
- "This was a legal action, but the searched alternative better preserved the next Jade window."

Selecting an event should restore the exact pre-input state. Allow an alternate action, animate both short continuations, and show which hit/window changed.

Compare alternatives from the same observed decision state. Do not attribute the difference between two entire random runs to one keypress.

Preserve the input attempt separately from accepted queue input, executed action, rejection reason and explicit cancellation. Current cast-only records cannot explain every failed attempt.

## 9. Recommended Delivery Order

1. Establish the input/channel contract and separate full restore state from UI observations. Reproduce known CN-client discrepancies before calling them live-accurate.
2. Rebuild the active training viewport: short live sequence, large cast bar, resources/windows and the eight buttons visible together.
3. Add current-state APL rollout and checkpoint retry, then candidate search with deterministic small fixtures and random expected-value evaluation.
4. Integrate the accepted Pandaren per-action sheets into the same event-driven stage.
5. Add scenario presets and counterfactual review around that shared engine.

The animation and viewport work can proceed alongside solver work once event timing and input semantics are stable. Do not deliver a beautiful arena while leaving the old static opener rail as the training standard.

## 10. Acceptance Tests for the Redesign

- At 1366 x 768, the current channel, next action, chi/energy, active Jade window and all eight buttons are visible together without document scrolling.
- On mobile, the active action dock and short reference do not require switching between separate page sections.
- Protected FoF rejects an ordinary attack without clipping or silently auto-casting it later.
- Protected SCK-to-FoF is independently configurable and does not block legal SCK-to-Sun weaving.
- Escape behavior respects open dialogs/focused inputs, otherwise performs the explicit channel-cancel action.
- The displayed pulse and Great Jade start times come from model events.
- Restoring a state during FoF, SCK or Conduit produces equivalent future events under the same replay conditions.
- A hypothetical branch cannot mutate the real combat.
- The random planner cannot access the live future RNG state.
- Equivalent observed states produce equivalent recommendations under the same scenario and planner configuration.
- Deliberately changing current resources/cooldowns changes the continuation when its optimum changes.
- Deterministic short fixtures compare the search with exhaustive enumeration, including wait/cancel candidates.
- A searched continuation can retain the APL baseline when it cannot establish an improvement.
- Stale background results never overwrite recommendations for a later combat state.
- A scenario transition is available to both player and planner under the same information rules.
- Sprite playback never advances a combat clock or changes damage timing.
- Review can retry the first consequential decision without replaying the opener.

## Sources and Evidence

- Local current application files and the assessment captures named above.
- A new local default-APL debug probe in `.local/trainer-v3-assessment/default-apl.simc` / `default-apl.log`; one iteration, 60 seconds, a compatible version of the existing equipment probe, no action-list override. This validates ordering, not an estimate of DPS.
- Local guide: `C:/Users/Administrator/Downloads/12.1 超级跟风踏风速成指南.md`, macro section at lines 23-33; pseudo-interrupt claims at lines 48-49; Xuen/Zenith timing warning at line 58. These are guide claims, not independently verified live-client facts.
- Pinned SimC source revision: `73a372b76188c703e48729caded3258cdc5b726b`.
- SimC `engine/class_modules/monk/sc_monk.cpp`: action coexistence at 234/269, Sun at 1116, SCK driver at 1591/1596/1649, FoF at 1699+, Conduit at 3856+, Stomp at 3919/3930.
- SimC `engine/class_modules/apl/apl_monk.cpp`: Conduit conditions and cancel expression at 232/263, Zenith usage at 236+, single/multi lists at 262+.
- Macro conditional explanation on the Blizzard-hosted community UI forum: <https://us.forums.blizzard.com/en/wow/t/macros-essential-information/21139>. This explains button-level `channeling` conditions; it is not a Blizzard guarantee of present client queue behavior.
- A dated first-hand report of channel-conditional queue problems, March 1, 2026: <https://us.forums.blizzard.com/en/wow/t/using-channel-in-macros-bugs-your-spell-queue/2146131/43>. It is a user report, not proof that the October CN build still has that issue.
- The 2024 forum discussion about SCK cancellation is historical context only, not evidence of 12.1.5 behavior.
