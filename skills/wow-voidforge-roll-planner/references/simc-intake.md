# SimC Intake

Accept pasted SimC, local files, or a character page. Preserve the raw import and
export timestamp. A Warcraft Logs character URL is not a combat report.
Keep item IDs, bonuses, gems, enchants, slots, talents, and region/server.
Read Hero talents from the user's declaration or a verified decoder; retaining
the talent string is not decoding it. Store the declaration's source.

For repeated inspection, use the PowerShell 7 helper:

```powershell
pwsh -NoProfile -File '<skill-path>/scripts/inspect_simc.ps1' `
  -SimcPath '<snapshot.simc>' -OutputPath '<snapshot.items.json>'
```

It queries Wowhead's read-only tooltip endpoint with all bonus IDs, saving level,
upgrade text, slot type, and raw secondary ratings. Results are dated third-party
lookups. It does not decode talents, simulate DPS, inspect bags, or infer history.
Errors stay explicit and suppress the average. Only complete standard 16-slot
loadouts get an average; a two-hander counts twice. Ratings exclude gems, enchants
and passives and must not be presented as character-panel percentages.

Separate offered Vault gear and unequipped items from equipped gear. Current
level, track, normal ceiling, and special-upgrade ceiling are different facts.
For close swaps run or request appropriate Top Gear/Droptimizer results; a BiS
list is not a personal sim.

For preserved-effect Catalyst comparisons, retain the source effect bonus IDs
and explicitly model the applicable tier bonus if a converted export is absent.
State this modeling assumption rather than pretending the gear was acquired.
Verify relevant procs are active in results: default item IDs can omit effects
that are attached through bonus IDs. Record commit, live/PTR mode, model length,
targets, iterations/error, talents, and consumables. Unverified special-effect
implementations must be called out; fixed-target AoE cannot rank a trinket whose
mechanic depends on repeatedly engaging new enemies as if it were a dungeon run.
