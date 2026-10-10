# Character Records and Weekly Ledger

Use workspace `records/` unless the user selects another root; resolve it once
and retain it across installations/sessions.

```text
records/<region>-<server-slug>-<character-slug>/
  profile.json
  snapshots/<export-date>.simc
  snapshots/<export-date>.items.json
  weeks/<regional-reset-date>.json
  weeks/<regional-reset-date>.md
```

Reset date identifies the game week, observation time the report time. Verify
regional reset calendar. Store timezone, patch, season; create a new week on reset
and refresh balance. A missing prior result is not a failed roll.

## Profile and Week

Profile: identity, combat/target spec, declared Hero tree, main content, goal,
snapshot paths, and history coverage. Slugs are ASCII; display names retain the
player's language. Do not duplicate weekly balance or equipped gear in profile.
A gear snapshot cannot establish where gear came from.

Week fields (unknowns are `null`, not zero/false):

- `schema_version`, `character_id`, `reset_date`, `timezone`, `patch`, `season`.
- `budget`: `reported_balance`, `reported_at`, evidence. A newer reported balance
  becomes the baseline; it already includes earlier spending.
- `vault`: `status` (`unknown`, `offered`, `claimed_item`, `claimed_currency`),
  `candidates`, chosen event ID, and actual currency amount if known.
- `rules`: verified cost/sources; unresolved caps/lockouts remain null.
- `pools`: completeness, history coverage, specs, targets, evidence, exclusion
  scope; exact remaining IDs only if verified.
- `plan`: proposed ordered actions, costs/specs, alternatives, stop rules, date.
- `events`: actual reported actions only. Plans never count as spending.

## Events

Every event has stable `event_id`, `reported_at`, nullable `occurred_at`, `kind`,
`evidence`, and `status`. `confirmed` means an unambiguous user report, not an
independent in-game verification.

Kinds: `bonus_roll`, `vault_claim_item`, `vault_claim_currency`, `normal_drop`,
`trade`, `craft`, `catalyst`, `upgrade`, `correction`.

For rolls store season, activity/boss, difficulty, loot spec, actual cost, item
ID/bonuses/level, outcome (`item`, `no_item`, `unknown`). "I rolled H8" can confirm
spending if cost is known, but not item/exclusion. Keep missing facts unknown.
For Vault claims preserve offers and chosen item/currency. Candidates are not
owned rewards. Ordinary drops/trades/crafts/Vault gear change goals, not exclusions.

## Update Procedure

1. Read character/week before edits; preserve unrelated changes.
2. Match existing event by ID or context. Repeated reports must not duplicate
   events or spending; ask narrowly if identical reports may be separate rolls.
3. Append actual facts. Fix errors via a `correction` with `supersedes_event_id`
   and reason; omit superseded events from calculations while retaining history.
4. Recompute balance: latest reported baseline plus confirmed income minus
   confirmed spending after that baseline. Do not subtract earlier spending twice.
5. Rebuild exclusions from confirmed, unsuperseded item-producing rolls under
   verified season/difficulty/shared-spec scope. Unknown scope keeps `n` unknown.
6. Update targets/tier/craft overlap from acquisitions; preserve raw snapshots.
7. Revise remaining plan/report and summarize budget/route changes.

Partial history confirms some events, not the entire excluded set. Keep exact
probabilities conditional or unknown.

Example: "Shaseng rolled Heroic Ula'tek as Brewmaster, spent one coin, got item
268216; Vault is unclaimed." Record one roll, reduce balance once, retain Vault
status, reassess weapon sources. Missing bonuses/level remain unknown.
