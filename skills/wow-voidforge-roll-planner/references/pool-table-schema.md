# Reward Pools and Probability

Identify a pool by region, season, activity, difficulty, and loot specialization.
Record exclusion scope separately: it may span specs for the same activity and
difficulty. Switching spec does not automatically reset exclusions.

For each pool save:

- Boss/raid name and ID, difficulty, reward track, actual cost, and loot spec.
- Complete eligible IDs, including filler, shared drops, tokens, or off-role
  items only when actual reward eligibility is confirmed.
- Completeness: `verified`, `partial`, or `unknown`; source and verification date.
- History coverage: `complete` or `unknown`; confirmed exclusions and their scope.
- Remaining targets categorized as long-term power, temporary upgrade, or
  item-level-achievement progress. Do not combine these into one success claim.
- Weights: `verified`, `equal_weight_assumption`, or `unknown`.

## Table

| Activity/boss | Loot spec | Cost | Remaining n | Target k | Probability status | Targets | Stop condition |
|---|---|---:|---:|---:|---|---|---|
| Named boss, Heroic | Named spec | Verified cost | Unknown | Known targets | Pool incomplete | IDs and slots | Reassess after key item |

List the verified full pool when a probability depends on it. A BiS list or
special-effect article is not exhaustive. Vault, trade, and ordinary drops may
lower `k` without lowering `n`. Missing history is not an empty exclusion set.

## Equal-Weight Model

For a verified complete remaining pool of `n` items and `k` current targets,
assuming an equally likely item reward:

```text
P(next target | item reward) = k / n
P(at least one target in r draws) = 1 - C(n-k,r) / C(n,r)
```

The second expression also requires a fixed target set, removal after each
success, the same pool/spec, and `0 <= r <= n`. Recompute if targets change.
If a no-item outcome is possible, distinguish conditional and unconditional
probability. Only claim 100% when every verified possible outcome meets the goal.

Use `E(draws to obtain all k) = k(n+1)/(k+1)` only for a justified uniform random
order without replacement. A certain Vault reward can beat this expectation when
one target is much more valuable. Unknown pool/weights mean unknown probability.

## Loot-Spec Comparison

| Spec | Targets retained | Extra filler | Full preview verified? | Recommendation |
|---|---|---|---|---|
| Combat spec | IDs | IDs | Yes/no | Conditional explanation |
| Alternative spec | IDs | IDs | Yes/no | Switch only if justified |

A class guide's alternate-spec recommendation supports a conditional choice;
a verified filtered reward preview is needed for exact `n`.
