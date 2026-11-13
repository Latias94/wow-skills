# Windwalker 12.1.5 enchant and gem evidence

Checked on 2026-10-29, Asia/Shanghai. This is a read-only research handoff for the fixed 334 shoulder `272244`, H7 legs `268225`, and H7 waist `268256`, with the existing Zul'jin 341 and tentacle 341 routes evaluated separately by the main task. No simulations were run, and no DPS ordering is established here.

The local source is `E:/github/simc`, commit `710c2408bfd3ae4df71b8cd55cdf01f63fd6c926`, with live DBC `12.1.5.70575`, hotfix date `2026-10-28`. The companion `tuning-enchant-evidence.json` contains the machine-readable mapping and evidence locations. All qualities below are crafting quality 2 unless stated otherwise; enchant IDs, item IDs, and spell IDs are separate namespaces.

## Immediate handoff

- Rings: `7967` = 鹰眼神视, +2% critical strike effectiveness per ring; `8025` = 银月城之捷, +29 Haste; `7969` = 祖尔金的精通, +29 Mastery; `7997` = 自然之怒, +29 Critical Strike. Budget quality-2 alternatives `8021` / `7965` / `7995` grant +24 of the corresponding rating.
- Weapons: there is no newly identified compatibility or patch issue that makes an additional weapon screen mandatory. Keep `8689` as the baseline. If adding one comparison, prioritize `8039`, 朗多雷之锐, a 15-second +67 primary-stat proc, meaning Agility for Windwalker. Fixed-secondary alternatives are available but do not need to expand the current approximately 0.1% stat screen into another full permutation grid.
- Diamonds: `240983` = 费解之永歌钻石, +32 primary stat; `240967` = 强能之永歌钻石, +23 primary stat and +0.15% critical strike effectiveness per distinct qualifying Midnight gem color. Both work in local SimC.
- `13696` does not add a socket. `13695` adds one prismatic socket. Do not invent extra head/wrist/waist gems from `13696`.
- Hand battle arts are Delve-only effects. They must not be credited as Mythic+ damage or haste.

The weapon-screen priority above is a research recommendation, not a personal simulation result. [Method's 12.1.5 guide](https://www.method.gg/guides/windwalker-monk/stats-races-and-consumables) and [Icy Veins' 12.1.5 guide](https://www.icy-veins.com/wow/windwalker-monk-pve-dps-gems-enchants-consumables) both recommend 哈谢仪式. Method lists 鹰眼神视 for rings, while Icy Veins lists 银月城之捷 or 自然之怒 according to the character's other stats; that disagreement supports retaining the main task's ring comparisons.

## Ring IDs and exact values

| Chinese name | English name | Enchant ID | Quality-2 scroll item ID | Effect per ring | Local support |
| --- | --- | ---: | ---: | --- | --- |
| 附魔戒指 - 鹰眼神视 | Eyes of the Eagle | 7967 | 243957 | +2% critical strike effectiveness | Explicit passive handler, driver `1236701` |
| 附魔戒指 - 银月城之捷 | Silvermoon's Alacrity | 8025 | 244015 | +29 Haste rating | Native static enchant |
| 附魔戒指 - 祖尔金的精通 | Zul'jin's Mastery | 7969 | 243959 | +29 Mastery rating | Native static enchant |
| 附魔戒指 - 自然之怒 | Nature's Fury | 7997 | 243987 | +29 Critical Strike rating | Native static enchant |
| 附魔戒指 - 萨拉斯急速 | Thalassian Haste | 8021 | 244011 | +24 Haste rating | Native static enchant |
| 附魔戒指 - 阿曼尼精通 | Amani Mastery | 7965 | 243955 | +24 Mastery rating | Native static enchant |
| 附魔戒指 - 自然之愤 | Nature's Wrath | 7995 | 243985 | +24 Critical Strike rating | Native static enchant; Chinese item name checked separately |

All these permanent ring enchants require an item of at least item level 120. Their regional profession-specialization labels, such as 阿曼尼增强 - 祖阿曼热忱, are not tooltip restrictions to the named zone. There is no Delve-only or outdoor-only clause on these ring effects.

The higher-tier static enchants use coefficient `0.8623`; the budget ones use `0.7136`. Their scaling level is capped at 80. Local level-80 item budget `33.63146077` gives rounded ratings `29` and `24`. This does not grow with the target ring's 334/341 item level. 鹰眼神视 modifies critical strike effectiveness, not Critical Strike rating or critical chance; do not translate two ring enchants into a flat 4% total DPS gain.

The recipe spell tooltip may display rank-1 values: for example +27 instead of +29, or 1% instead of 2%. The quality-2 scrolls are the relevant observations: [鹰眼神视](https://nether.wowhead.com/tooltip/item/243957?dataEnv=1&locale=4), [银月城之捷](https://nether.wowhead.com/tooltip/item/244015?dataEnv=1&locale=4), [祖尔金的精通](https://nether.wowhead.com/tooltip/item/243959?dataEnv=1&locale=4), and [自然之怒](https://nether.wowhead.com/tooltip/item/243987?dataEnv=1&locale=4).

## Weapon scope and modeling caveats

| Chinese name | Enchant ID | Quality-2 scroll item ID | Tooltip effect | Screening priority |
| --- | ---: | ---: | --- | --- |
| 附魔武器 - 哈谢仪式 | 8689 | 273072 | Proc +139 random secondary rating for 15 seconds; favors the highest secondary while health is above 80% | Existing baseline |
| 附魔武器 - 朗多雷之锐 | 8039 | 244029 | Proc +67 primary stat for 15 seconds | First optional comparison |
| 附魔武器 - 狂战士之怒 | 7983 | 243973 | Proc +124 Haste rating for 15 seconds | Optional only when checking fixed Haste against Hash'ey's stat selection |
| 附魔武器 - 奥术精通 | 8041 | 244031 | Proc +124 Mastery rating for 15 seconds | Optional fixed Mastery comparison |
| 附魔武器 - 加亚莱的精准 | 7981 | 243971 | Proc +124 Critical Strike rating for 15 seconds | Optional fixed Critical Strike comparison |
| 附魔武器 - 辛多雷之焰 | 8037 | 244027 | 2,456 Fire damage over 10 seconds, then 5,220 Fire damage split among nearby enemies | Implemented, low priority for this stat-tuning handoff |
| 附魔武器 - 哈尔拉兹之力 | 7979 | 243969 | 1,893 bleed damage over 18 seconds | Implemented, low priority for this stat-tuning handoff |

The scalar values above are tooltip-rounded level-90 amounts. Local proc calculations retain floating-point amounts: approximately `139.292220` for `8689`, `124.374015` for the three secondary enchants, and `66.800058` for `8039`. The local DBC and scaling code account for the `-7` proc rating multiplier; do not apply the static ring/gem level-80 calculation to weapon procs. These weapon effects are not restricted to Delves or their profession flavor regions, and require target item level 120 or higher. [哈谢仪式 quality-2 tooltip](https://nether.wowhead.com/tooltip/item/273072?dataEnv=1&locale=4), [朗多雷之锐](https://nether.wowhead.com/tooltip/item/244029?dataEnv=1&locale=4), [狂战士之怒](https://nether.wowhead.com/tooltip/item/243973?dataEnv=1&locale=4).

`unique_gear_midnight.cpp` implements all seven listed weapon effects. In particular, `rite_of_the_hashey()` has a version check: the old forced expiration of the Crit buff occurs only before 12.1.5. This local build therefore includes the 12.1.5 behavior adjustment.

Hash'ey's health condition is approximated by `midnight.rite_of_the_hashey_uptime`, default **0.6** in `player.hpp`. On each proc, the model chooses the current highest secondary in that configured fraction of rolls; otherwise it chooses randomly from four secondaries. The option is not enchant-proc uptime and does not simulate the player's health trajectory. Preserve/report the same value when comparing the two trinket routes. A fixed-secondary enchant is a useful optional sensitivity check if the relevant health condition or the highest-stat selection is central to the decision.

Hash'ey, the fixed-secondary enchants, and the primary-stat enchant use proc callbacks; the same enchant on two weapons has explicit duplicate handling. This task only verifies the current main-hand choice and does not recommend extrapolating independent buff behavior for a new dual-wield configuration. 哈尔拉兹之力 also has an implementation note about the absent tank-role penalty matching observed behavior; that is not a Windwalker restriction.

## Gems: exact Chinese names, ratings, and color counting

| Item ID | Exact Chinese name | English name | Effect | Color family / SimC description ID |
| ---: | --- | --- | --- | --- |
| 240898 | 无瑕致命紫晶 | Flawless Deadly Amethyst | +16 Mastery, +7 Critical Strike | 紫晶 / 14278 |
| 240900 | 无瑕迅捷紫晶 | Flawless Quick Amethyst | +16 Mastery, +7 Haste | 紫晶 / 14278 |
| 240892 | 无瑕精湛榄石 | Flawless Masterful Peridot | +16 Haste, +7 Mastery | 榄石 / 14262 |
| 240908 | 无瑕精湛榴石 | Flawless Masterful Garnet | +16 Critical Strike, +7 Mastery | 榴石 / 14276 |
| 240890 | 无瑕致命榄石 | Flawless Deadly Peridot | +16 Haste, +7 Critical Strike | 榄石 / 14262 |
| 240906 | 无瑕迅捷榴石 | Flawless Quick Garnet | +16 Critical Strike, +7 Haste | 榴石 / 14276 |
| 240983 | 费解之永歌钻石 | Indecipherable Eversong Diamond | +32 primary stat | Does not add a qualifying color |
| 240967 | 强能之永歌钻石 | Powerful Eversong Diamond | +23 primary stat; +0.15% critical strike effectiveness per distinct qualifying color | Does not add a qualifying color |

The six rare gems are quality 2 and provide **23 total secondary rating each**, split 16/7. Their primary rating follows the gem family; the adjective identifies the smaller secondary component. For example, 无瑕迅捷紫晶 is **Mastery-heavy**, despite the word 迅捷. Their static scaling is capped at level 80, so replacing equipment with 334 gear does not increase the listed gem ratings. [无瑕迅捷紫晶 tooltip](https://nether.wowhead.com/tooltip/item/240900?dataEnv=1&locale=4), [无瑕精湛榄石 tooltip](https://nether.wowhead.com/tooltip/item/240892?dataEnv=1&locale=4).

Both diamonds are unique-equipped in the 萨拉斯钻石 category, maximum one. Both are supported: 费解之永歌钻石 is a native static stat entry; 强能之永歌钻石 has explicit handler `powerful_eversong_diamond()`, registered for driver `1258209`. The handler counts unique family description IDs from 榄石, 榴石, 青金石, and 紫晶, then applies the critical-effectiveness override to its damage/healing effects. The diamond itself and duplicate cuts in the same family do not increase that count. [费解之永歌钻石 tooltip](https://nether.wowhead.com/tooltip/item/240983?dataEnv=1&locale=4), [强能之永歌钻石 tooltip](https://nether.wowhead.com/tooltip/item/240967?dataEnv=1&locale=4).

For the current four exported sockets, `240983 + 240892 + 240908 + 240908` contains two qualifying families. Substituting only `240967` gives +23 primary and +0.30% critical strike effectiveness, trading away 9 primary stat. With three non-diamond sockets, the maximum is three qualifying colors, or +0.45%; the global four-color cap is +0.60% and requires at least four non-diamond gems. Changing between `240898` and `240900` never creates an additional color. These are bookkeeping facts, not a prediction that either diamond wins.

## Sockets and excluded effects

`item_bonus.inc` is keyed by its **second** column, `bonus_id`, not its first row ID. The relevant live records are:

```text
{ 30782, 13695, 6, 1, 7, 0, 0, 0 }  // type 6 adds one prismatic socket
{ 30785, 13696, 0, 0, 0, 0, 0, 0 }  // no socket effect
```

`data_enums.hh` defines `ITEM_BONUS_SOCKET = 6`; `sc_item_data.cpp` adds `value_1` sockets of color `value_2`. Existing head `271519`, wrist `244576`, and waist `271516` have zero native sockets, and their exact exported live tooltip bonus lists showed no socket markup. The old no-socket observation is consistent with current DBC. The intended replacement waist `268256` also has zero native sockets; actual sockets must come from the full item instance's genuine socket bonus, not its base item or `13696`.

| Excluded effect | Enchant ID | Driver | Actual applicability | Local support finding |
| --- | ---: | ---: | --- | --- |
| 猎鹰猛击（哈谢战艺） / Ancient Hash'ey Battle Art: Falco Strikes | 8727 | 1315100 | Explicitly while exploring Delves; item-level range 266–344 | DBC entry exists; no explicit implementation/registration found in non-generated engine sources |
| 山猫锐眼（哈谢战艺） / Ancient Hash'ey Battle Art: Eye of the Lynx | 8730 | 1315099 | Explicitly while exploring Delves; item-level range 266–344 | DBC entry exists; no explicit implementation/registration found in non-generated engine sources |

The driver tooltips currently describe 猎鹰猛击 as a Nature-damage proc with a 20% repeat chance, and 山猫锐眼 as a 15-second Haste/Leech benefit for the player and a nearby ally. Neither text grants these effects in Mythic+ or raids. The lack of a dedicated local handler means neither is established as a supported Delve simulation here; merely seeing the enchant ID in DBC is insufficient. [猎鹰猛击 live driver](https://nether.wowhead.com/tooltip/spell/1315100?dataEnv=1&locale=4), [山猫锐眼 live driver](https://nether.wowhead.com/tooltip/spell/1315099?dataEnv=1&locale=4).

## Evidence limits and tool trace

The official [12.1.5 content-update search result](https://worldofwarcraft.blizzard.com/en-us/news/24304162) identifies the October 2026 live patch. Direct page fetch returned HTTP 403, including one retry with the article slug. No item-specific hotfix claim is inferred from that unavailable page. Both current class guides were readable. Search-service requests could not retrieve the tooltip endpoint, so the same public `nether.wowhead.com` endpoints were read successfully with PowerShell `Invoke-RestMethod`, using `dataEnv=1` (live) and `locale=4` (Simplified Chinese). Recipe/driver versus finished-scroll quality differences were checked explicitly. PTR search hits were excluded from numeric evidence.

Tool-call brief, recorded 2026-10-29 Asia/Shanghai: local `exec_command`/`rg` read DBC and source without running SimC; Search Service `web_run` used targeted patch/guide/item queries, at most four queries per call, and short scoped page opens. Sources were `worldofwarcraft.blizzard.com`, `method.gg`, `icy-veins.com`, and `nether.wowhead.com`. The official-page retry and tooltip fallback are described above; no rate-limit backoff was needed. No external messaging, repository rollback, or commit occurred. Only this Markdown file and its companion evidence JSON are task outputs.
