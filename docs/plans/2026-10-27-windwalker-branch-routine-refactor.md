# Windwalker Branch Routine Refactor

Date: 2026-10-27, Asia/Shanghai.

Status: implementation plan. This document does not describe a deployed feature.

## Intended experience

Turn the supplied burst diagrams into a stable, interactive routine map. Keep the
full burst phase outline visible, show concrete skills and bindings in the active
phase, preview meaningful unresolved branches, and highlight the observed route
after an actual combat result. The map must remain readable while playing.

The primary reference is the user's single-target, multi-target and Bloodlust
diagrams. Their phase structure is instructional material, not proof that a fixed
sequence is optimal for the pinned personal build.

## Preserve

- The pinned combat rules, cooldown work, discrete events and channel timing.
- Eight dynamic action slots, input protection, queue validation and key bindings.
- Local spell assets, generated action sprites and critical-result feedback.
- Full and compact Combat state cloning and event identity.
- Existing applicable mechanics, planning and browser regression tests.

The implementation stays buildless with native ES modules. New dependencies need
a concrete capability that the existing platform cannot provide reasonably.

## Replace

- The single sampled continuation as the primary routine representation.
- Repeated replacement of the visible route after every planning revision.
- Milestone inference from final cast history as the live route cursor.
- Independent UI-local lifecycle flags and checkpoint bookkeeping inside app.js.
- Time-based matching between routine nodes, actual inputs and review records.

Remove superseded paths after their callers migrate. Retain source explanations
and factual combat review where they remain applicable.

## Responsibilities

1. `combat.js`: physical state and authoritative cast, hit and control results.
2. `policy.js` and the bounded planner: legal candidate decisions and evaluation.
3. `routine-graph.js`: phase templates, concrete action segments, conditional
   result edges, shared visual prefixes and bounded branch generation.
4. `routine-runner.js`: stable node cursor, observed edge resolution, accepted
   alternatives, deviations and recovery attachment.
5. `session.js`: clock, input lifecycle, planner jobs, atomic training checkpoints
   and export. It owns Combat and routine-runner state together.
6. `routine-view.js`: map rendering, bindings, phase bands, current-node focus
   and local branch emphasis. It does not simulate damage or decide legality.
7. `app.js`: page composition, DOM bindings and existing inspection panels.

These are bounded application modules, not a generic workflow or graph framework.
Introduce each module only with its actual callers.

## Routine contract

Nodes need stable IDs and represent an instant skill, a channel, an explicit
channel end, a meaningful wait, or an unresolved result. Edges carry explicit
conditions and a teaching reason. Phase labels identify first Zenith, ordinary
Jade, Great Jade, second Zenith and the tail without conflating their instances.

The model must retain both the physical input slot and resolved spell identity.
Display the real input binding at render time. A queued or rejected input does
not complete a node; the linked executed action does.

Branch status includes unresolved, observed-selected and observed-not-selected.
Later choices can also be accepted alternatives or need inspection. A state with
no implemented reference is explicitly unknown rather than a fabricated route.

## Branch generation and selection

At an RSK-family decision, fork the exact pre-execution state and enumerate the
next result only: main critical/noncritical, with absent, noncritical or critical
Dawn. Never inspect the live RNG stream. Fixed-result drills may declare their
next outcome explicitly.

Resolve the selected edge using the actual executed cast's `sunResult`, including
cast identity, chi, cooldown and active windows. A critical label alone cannot
select the next skill independently of the resulting combat state.

Expand concrete filling actions until the next meaningful decision or bounded
phase segment. Keep the existing ordered APL as a reproducible baseline; use
bounded candidate comparison where useful and report its uncertainty.

Equivalent visible segments can share presentation. Distinct underlying combat
states and histories remain separate unless future-relevant equivalence has
actually been established. Equal rounded cooldowns, the same critical count, or
the same next skill are not sufficient to merge simulation states.

Keep the phase outline for the entire burst while expanding only nearby decisions.
Do not eagerly enumerate every combination of future random procs. Meaningful
highlighting and branch selection must not depend on a slow deep search.

## Stable layout and playback

The routine map becomes the central teaching surface. The sprite stage supports
it and yields space. Resources, channels and all eight action slots remain visible
at 1366x768 and 390x844.

Use discrete skill order for diagram geometry and simulation time for readiness,
channel spans and coverage. A fixed musical tempo is not a combat timing rule.
Keep completed nodes, selected edges and nonselected nearby edges spatially stable.
Scroll/focus deliberately at phase boundaries or player request, not every frame.

Use brief critical feedback, an explicit observed branch label and a highlighted
path together. Retain text when animation or audio is disabled.

## Deviations, review and retry

Keep the original reference route and the player's observed route identifiable.
When the player makes a different legal choice, record it and attach a recovery
continuation from the resulting actual state. Do not silently rewrite the original
reference so that a deviation becomes an apparent correct input.

Review uses the same node IDs and observed decisions as practice. Physical facts
such as a clipped channel remain distinct from model-dependent recommendations.
An alternative is accepted only when there is supporting legality and evaluation
evidence. No exact live DPS-loss claim is derived from the approximate model.

A retry checkpoint includes Combat, route cursor, phase/window identity, branch
selection and input-history position. Restore these atomically. Preserve pending
ticks, accepted queues, RNG state and same-timestamp action order.

## Delivery sequence

1. Add a small single-target route fixture and pure graph/runner tests; preserve
   the current UI while proving unresolved -> observed -> continued transitions.
2. Extract session ownership and integrate atomic route checkpoints and review.
3. Replace the main continuation with the stable phase map and branch display.
4. Expand the same mechanism to multi-target and Bloodlust contexts; keep the
   pinned talent profile and target-dependent cooldown effects explicit.
5. Remove superseded teaching paths, run independent Codex review, complete
   regression checks and update the existing owner-private Site.

Keep the main workspace uncommitted until the user's requested commit checkpoint.
Use the existing separate Site source repository for publication and preserve the
current audience.

## Verification contract

- Before an unresolved RSK, multiple supported result edges are visible.
- Main-only, Dawn-only, double, no-crit and absent-Dawn results select correctly.
- Identical crit counts with different chi or cooldown states need not share a route.
- A successful queued execution advances once; rejection never advances.
- Normal RSK/SCK coexistence, Rushing Wind replacement, FoF protection and explicit
  Conduit/FoF/SCK endings retain their physical behavior and teaching meaning.
- Node identity and position survive ordinary ticks and asynchronous planning.
- Old Worker results cannot alter a restored or newly started session.
- Different legal choices retain their observed history and support recovery.
- Retry restores both physical and teaching state, including same-time controls.
- Existing mechanics tests remain applicable; replace obsolete UI assertions with
  actual route interaction tests rather than tests of DOM implementation details.
- Edge checks cover desktop/mobile visibility, keyboard/touch, reduction of motion,
  critical branches, route progression, deviation, retry, export and local assets.
- The final Site deployment must return success before it is reported as published.

## Remaining accuracy boundary

The current damage model omits several pet, item and passive contributions. Route
labels describe a pinned reference or a bounded core-model recommendation, not a
mathematical global optimum. Live-client cancellation discrepancies remain marked
until supported by real logs or direct testing.
