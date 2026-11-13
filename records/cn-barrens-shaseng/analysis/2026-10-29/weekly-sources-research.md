**CN weekly source research — 2026-10-29, Midnight Season 2 / 12.1.5**

The reported Labyrinth reward is real: three **神话灵魂残片 / Mythical Soul Fragments, item 285065**, buy a selected item from **瓦杜 / Wah'du, NPC 264886**, currently at **321, Myth 2/6**. This is a fixed merchant selection with visible item stats. It is separate from the random Hero reward assembled from Heroic Soul Fragments. For Shaseng's proposed H7/H10 route, the shoulder is a sensible first redemption candidate because neither boss supplies leather shoulders, whereas H7 supplies legs and a belt. This is a source-overlap recommendation, not a measured DPS ranking. [Current third-week report](https://www.wowhead.com/news/myth-2-6-piece-of-loot-now-available-from-labyrinths-383603), [CN preparation guide](https://news.17173.com/content/10192026/234548896.shtml).

H10's ring **281029** and chest **281236 → 271522, retained effect 14049**, and H7's trinket **270173**, are already confirmed R acquisitions. They receive **no new-target credit**. H10 has three items in the derived Windwalker base table: chest, ring and **281215 Twisted Horror's Tendril**. **281215 remains an important distinct H10 target** after the confirmed ring/chest rolls: the user relays that all five current elite samples use281215 with270175, and the main study is measuring its personal benefit. If the current reward preview still lists it, continuing H10 R has a clear purpose. Bags, full intervening history and the current remaining R preview are not established, so this does not imply a guaranteed next reward.

Scope: research only. No simulations, DPS estimates, acquisition events, currency spending, commits, profile changes or snapshot changes. The companion `weekly-sources-evidence.json` stores structured findings, 93 tooltip responses and original public source responses. Raw responses use `weekly-` keys inside that JSON; no additional archive files were created.

**Character facts and their precedence**

Latest user statements supersede the older equipped snapshot. The [confirmed R ledger](../../weeks/2026-10-22.json) supplies acquisition provenance. During final verification, the concurrent main study added an [October 29 equipped export](../../snapshots/2026-10-29-equipped.simc), which now confirms current complete equipped bonus lists, including head effect13847 and both trinkets'12856. It still omits `redirected_base_stats`, bags and resources. The [October 23 full export](../../snapshots/2026-10-23.simc) supplies historical precursor fields. Historical precursor continuity is useful evidence, but it is not a fresh full precursor export.

| Slot | Latest usable fact | Consequence |
| --- | --- | --- |
| Head | 271519, 334 Myth6/6, retained **13847** confirmed by the October29 equipped bonus list | Do not substitute the older271875 display as current; the effect is confirmed by bonus13847, while the current redirected precursor is not exported |
| Shoulder | 271517, **321 Hero 6/6**; historical precursor **251146** | Compare the precursor's crit/versatility, not the default tier shoulder's haste/mastery |
| Chest | 271522, retained **14049**; confirmed R source **281236** | Already owns the H10 chest and its retained effect; no repeat-chest gain |
| Hands | Crafted **244575** | The latest four tier slots are head, shoulder, chest and legs; hands are not an extra tier slot |
| Waist | 271516, **321 Hero 6/6**; historical precursor 271436 with crafted haste/mastery | Hero 6/6 is already at its ordinary ceiling; it is not an unupgraded Myth item |
| Legs | 271518, **321 Hero 6/6**; historical precursor **251130** | Compare preserved precursor stats; H7 legs or Labyrinth legs must be catalyzed before replacing this tier slot |
| Trinkets | **270175 and 270173, both 12856 and 341**, explicitly confirmed by user | Neither needs another ascension; no repeated H7 trinket target |
| H10 ring | **281029** already R-acquired; last complete record has it at 334 | It is unique-equipped; another copy cannot fill the second ring slot |

The shoulder's full current bonus chain is `12846/6652/13440/13694/13697/1574`, the legs use `6652/13440/13693/13698/12846`, and the chest uses `13334/6652/14049/13690/13698/12854`. These chains match the historical export; the associated historical precursor fields are respectively `redirected_base_stats=251146`, `251130` and `281236`. The new head uses `13334/6652/12854/13696/13847/13692/13698/1587`; gloves244575 use `12214/13667/12497/13751/14001/8793/13836`; both trinkets use `6652/13334/12856`. Complete equipped bonuses are available now, but the exact new merchant/conversion chains are still unknown. JSON stores the current raw export without editing its source file.

Current coin balance, fragment count, bags, Catalyst charges, Vault offers and full intervening R history are unknown. The old October 23 balance of zero is not a current budget.

**Quest and redemption rules**

The six-step quest line unlocks one step per week and awards one fragment plus **2,000 晦幽铸币 / Undercoin, currency 2803**, per completed step. Three fragments buy one item; the six steps provide at most two purchases. Missed unlocked steps can be caught up sequentially. Third week is therefore the earliest ordinary first purchase, provided the character has completed three steps. It does not mean three new quests every week or an indefinitely repeatable item every three weeks. [Third-week live report](https://www.wowhead.com/news/myth-2-6-piece-of-loot-now-available-from-labyrinths-383603), [current reward summary](https://www.icy-veins.com/wow/news/this-weekly-labyrinth-quest-lets-you-pick-the-myth-gear-slot-you-need/).

Finish the introduction, then accept Wah'du's request in the **祭仪之厅 / Chamber of Rites**, approximately **44,79** inside the Labyrinth. Complete the named chamber at **Tier 8 or higher**, then turn in and check for the next unlocked request. The first steps do not require a Tier 11 solo clear. A later quest explicitly names Kindo'jan, so the chamber-only description must not be generalized to all six steps. [CN first-quest instructions](https://ol.3dmgame.com/gl/356183.html), [six reward-bearing quests mirrored from Blizzard's API](https://needbeforegreed.com/retail/quests/zone/16913).

| Quest ID | English quest title | CN identification and release confidence |
| --- | --- | --- |
| 98951 | Akil'zon's Roost | **埃基尔松的栖台**; CN quest title independently confirmed; first step |
| 98963 | Halazzi's Lair | Area: **哈尔拉兹的巢窟**; second step; exact localized quest title not independently returned |
| 98962 | The Cave Towers | Area: **洞穴高塔**; current NA reports identify this as week three; no CN quest UI captured |
| 98961 | Jan'alai's Refuge | Area: **加亚莱的隐殿**; reward-bearing quest exists; later CN release order not independently verified |
| 98960 | Nalorakk's Rest | Area: **纳洛拉克的憩所**; reward-bearing quest exists; later CN release order not independently verified |
| 98959 | Kindo'jan, The First Hash'ey | The final-boss request exists; exact CN quest title and later CN release order not independently verified |

The quest IDs and English titles are available through the API mirror's individual pages, for example [98962](https://needbeforegreed.com/retail/quests/98962) and [98959](https://needbeforegreed.com/retail/quests/98959). Several CN tooltip queries returned `未知`, an untranslated bracketed title, or 404. Area names in this table must not be mistaken for independently confirmed localized quest strings.

The actual fragment's current Chinese tooltip name is **神话灵魂残片**. Some CN articles call it “神话灵魂碎片”; these refer to item **285065**. Early PTR articles described combining three fragments into a **Venerated Loa Armament** for Myth 1/6. That account is superseded for the present purchase mechanism by the current merchant reports. No current armament item ID or an on-use combine step is assumed.

**All published reward slots and the fixed-choice mechanism**

The published catalogue contains **56 distinct item IDs**: 32 armor pieces, four cloaks, two necklaces, four rings and fourteen weapons/shield/off-hand items. Each armor type has one fixed item in each of its eight armor slots. Choosing a slot does not permit choosing arbitrary secondary stats, a raid item, a cantrip, or a tier item's default stats. There is **no trinket** in this catalogue. Class usability and merchant filters still apply. [Published complete catalogue](https://www.wowhead.com/news/myth-2-6-piece-of-loot-now-available-from-labyrinths-383603).

The following ratings are from live-environment CN tooltip queries with **rank bonus 12850**, which returns **321 / Myth 2/6**. This identifies the rank and item properties; **12850 alone is not claimed to be the merchant's full item-link bonus chain**. Full reward links, sockets and tertiary rolls remain unobserved. Exact tooltip URLs, names, stats, requested bonuses and timestamps are in JSON. Public [Raidbots encounter item data](https://www.raidbots.com/static/data/live/encounter-items.json) independently supplies item types, stat allocations and specialization masks.

Armor entries below show `item ID — secondary ratings at 321`. Crit = 暴击, Haste = 急速, Mastery = 精通, Vers = 全能. Names belong to the 蹈火者 / Pyrewalker, 雾猎者 / Miststalker, 驭风者 / Galerider and 誓言使者 / Pledgebearer families respectively; all individual CN names are retained in JSON.

| Slot | Cloth | Leather | Mail | Plate |
| --- | --- | --- | --- | --- |
| Head | 272234 — Mastery119/Haste71 | 272242 — Vers120/Mastery71 | 272250 — Vers122/Mastery69 | 272258 — Crit117/Mastery73 |
| Shoulder | 272236 — Haste87/Vers56 | **272244 — Haste88/Crit54** | 272252 — Crit85/Mastery57 | 272260 — Mastery89/Crit53 |
| Chest | 272231 — Crit122/Mastery68 | 272239 — Mastery112/Crit79 | 272247 — Mastery115/Haste75 | 272255 — Vers119/Haste71 |
| Wrist | 272238 — Vers69/Mastery38 | 272246 — Crit69/Mastery38 | 272254 — Crit66/Haste41 | 272262 — Haste64/Crit43 |
| Hands | 272233 — Crit86/Mastery56 | 272241 — Haste91/Vers52 | 272249 — Crit91/Haste52 | 272257 — Haste92/Mastery51 |
| Waist | 272237 — Mastery87/Vers56 | 272245 — Crit84/Vers59 | 272253 — Vers88/Mastery55 | 272261 — Vers89/Crit54 |
| Legs | 272235 — Vers117/Haste73 | **272243 — Mastery115/Haste76** | 272251 — Haste113/Vers78 | 272259 — Mastery117/Vers73 |
| Feet | 272232 — Haste92/Crit50 | 272240 — Vers90/Crit53 | 272248 — Mastery88/Crit55 | 272256 — Crit84/Haste59 |

| Accessory ID | CN name | Ratings at 321 |
| --- | --- | --- |
| 272225 | 蹈火者的披风 | Haste67/Crit40 |
| 272226 | 雾猎者的斗篷 | Crit67/Vers40 |
| 272227 | 驭风者的披纱 | Crit67/Vers40 |
| 272230 | 誓言使者挂披 | Haste67/Crit40 |
| 272228 | 呢喃颈饰 | Mastery220/Vers156 |
| 272229 | 蛇纹护符 | Crit220/Haste156 |
| 272147 | 游蛇之环 | Haste258/Mastery118 |
| 272148 | 长蛇绕环 | Crit242/Vers134 |
| 272149 | 妖术指环 | Mastery263/Crit113 |
| 272150 | 衔尾蛇印玺 | Mastery236/Haste140 |

The actual four cloak entries have haste/crit or crit/versatility. A secondary summary mentioning a crit/mastery cloak is not supported by these item tooltips. The rings offer four fixed distributions, including two different haste/mastery balances.

| Weapon / off-hand ID | CN name | Actual type and primary stat | Ratings at 321 |
| --- | --- | --- | --- |
| 272266 | 被遗忘的幻灵匕首 | Intellect dagger | Crit58/Haste37 |
| 272267 | 出棺双刃斧 | Strength one-hand axe | Crit59/Vers36 |
| 272268 | 面具雕刻者 | Agility dagger | Haste56/Mastery39 |
| 272269 | 封魂者的墓碑 | Agility one-hand mace | Haste60/Mastery35 |
| 272270 | 骨粉研杵 | Intellect one-hand mace | Haste58/Crit37 |
| **272271** | **缚灵聚焦器** | **Intellect wand** | Vers57/Mastery38 |
| 272272 | 受难游击戟 | Agility polearm | Crit118/Vers73 |
| 272273 | 入龛仪祭权杖 | Intellect staff | Mastery115/Vers75 |
| 272274 | 界域撕裂者 | Strength two-hand sword | Vers122/Mastery69 |
| 272275 | 魂咏者之角 | Intellect off-hand | Vers59/Crit36 |
| 272276 | 哀嚎壁垒 | Shield, strength/intellect | Haste60/Vers36 |
| 272277 | 灵魂掠夺者 | Warglaive, agility/intellect | Vers59/Mastery36 |
| 272278 | 反曲射火弓 | Agility bow | Haste112/Crit78 |
| 272280 | 掘出的劈魂斧 | Strength two-hand axe | Crit114/Haste76 |

The current catalogue article incorrectly labels **272271** as a one-hand strength sword. Both its tooltip and the item database identify it as a wand. An agility dagger is also not a Windwalker weapon merely because it has agility. The directly relevant Windwalker weapon choices here are the agility mace and polearm; neither automatically replaces the already established H8 weapon setup.

**Catalyst preservation and the shoulder comparison**

The CN 12.1 rules explicitly state that eligible class-set conversions inherit the source item's secondary/tertiary stats and selected additional effects. Current Labyrinth reporting confirms its gear can be catalyzed. For the leather shoulder, conversion to the Monk tier display **271517** therefore preserves **272244's haste/crit**, rather than changing it to the default 271517 haste/mastery allocation. Only head, shoulders, chest, hands and legs contribute the tier two/four-piece bonuses. Other conversion appearances are not additional tier-count slots. Weapons, rings and necklaces are not tier conversions. [Official Catalyst rule](https://wow.blizzard.cn/news/24293281/index.html), [current Labyrinth conversion report](https://www.icy-veins.com/wow/news/this-weekly-labyrinth-quest-lets-you-pick-the-myth-gear-slot-you-need/).

| Comparison item | Level / track | Primary | Stamina | Armor | Preserved source secondaries |
| --- | --- | ---: | ---: | ---: | --- |
| Historical current precursor **251146 拾荒者护肩** → 271517 | **321 Hero 6/6** | 125 | 2,527 | 123 | **Crit59/Vers84** |
| Redeem **272244 雾猎者护肩**, before/after tier conversion | **321 Myth 2/6** | 125 | 2,527 | 123 | **Crit54/Haste88** |
| Same reward, upgraded | **334 Myth 6/6** | 141 | 2,932 | 135 | **Crit57/Haste93** |
| Alternative raid precursor **268246 泛沫毒液护肩** → tier | **334 Myth 6/6**, comparison query | 141 | 2,932 | 135 | **Crit99/Mastery52** |

At 321, the Labyrinth shoulder exchanges **84 versatility and 5 crit for 88 haste**, with unchanged primary/stamina/armor. At 334, compared with the old 321 shoulder, it adds **16 primary, 405 stamina and 12 armor**, and changes secondaries to Crit57/Haste93. Rounding explains small differences in the total ratings. The comparison uses the recorded precursor, not default tier stats. If the current shoulder was recatalyzed from another source after the historical export, its new `redirected_base_stats` must replace this baseline.

The new shoulder tooltip has no raid cantrip. Catalyzing it does not manufacture one or transfer an effect from a different equipped shoulder. Conversely, the H10 chest's **14049** is a real source-attached effect: **281236** has Crit58/Haste143 at 334 and a Void Eruption proc; the user confirms the converted 271522 retained it. The default 271522 tooltip's haste/mastery is therefore unsuitable for the character's converted chest. `redirected_base_stats=281236` preserves the stat provenance, while **14049** identifies the retained effect. An item ID alone establishes neither.

The old leg precursor **251130 巧手交易马裤** has **Crit112/Mastery79 at 321**. At 334, the alternative sources are **268225 盘卷妖术护腿: Haste63/Mastery138**, and **272243 雾猎者腿甲: Haste80/Mastery121**. Either can supply tier legs while retaining its own distribution. They are not interchangeable with the default 271518 Crit130/Vers71 tooltip. No new simulation establishes which full loadout wins.

**Ordinary upgrades and ascension**

| Myth rank | Item level | Rank bonus used in independent tooltip query |
| --- | ---: | ---: |
| 1/6 | 318 | 12849 |
| 2/6 | **321** | **12850** |
| 3/6 | 324 | 12851 |
| 4/6 | **328** | 12852 |
| 5/6 | 331 | 12853 |
| 6/6 | **334** | **12854** |

Myth 2→6 ordinarily requires four upgrades, nominally **80 神话迷雾纹章 / Myth Mistcrests, currency 3446**, plus gold, before slot/Warband discounts. Current vendor quotes determine the actual cost. A character's existing 321 Hero 6/6 shoulder cannot simply continue up this Myth track: acquiring the Myth-track replacement is what creates the higher ordinary ceiling. Crest caps were removed from the CN October 22 week. [Upgrade rules and discounts](https://www.wowhead.com/cn/guide/midnight/item-level-gear-upgrades-dawncrests), [official cap removal](https://wow.blizzard.cn/news/24304162/).

**晋升毒液石 / Ascendant Venomstone, item 280562**, costs **10 per eligible item** and applies to fully upgraded Season 2 **weapons, trinkets and necklaces**, including the applicable maximum-quality Tidal crafts. It does **not** ascend shoulders, chest, legs, waist, cloaks, wrists, hands, feet or rings. A redeemed shoulder or ring therefore ordinarily stops at **334**, while an eligible redeemed weapon or necklace can first reach 334 and then ascend to **341**. Do not turn the raid's exceptional Mythic 9/6 drops into an attainable shoulder upgrade path for this character. [Official scope and unlock](https://wow.blizzard.cn/news/24304162/).

The October 23 reporting corrects Myth noncrafted ascension **340→341** and Myth crafted ascension **338→337**; the CN cumulative hotfix notes also acknowledge an item-level correction. The queried 12856 trinket tooltips still return **340** without a verifiable data-build date. They are archived as stale conflicting evidence. The character's two trinkets remain **341** by the latest user confirmation, corroborated by the hotfix report. Exact 341 stat/proc amounts are not extrapolated from the stale 340 tooltip. [Ascension level correction](https://www.wowhead.com/news/item-level-changes-for-ascended-venomforged-gear-383552), [CN hotfix archive](https://wow.blizzard.cn/24266320/index.html).

**H7/H10 identities and complete base Windwalker tables**

H7 means **Heroic 盘卷祭坛 / The Coiled Altar**, seventh boss of **烈毒之渊 / The Venomous Abyss**. Public journal source IDs are instance **1320**, encounter **2883**. The trinket's reference to Zul'jin does not rename the encounter. H10 is the user's shorthand for **Heroic 基希克斯 / Kith'ix**, in the separate single-boss raid **基希克斯破封 / The Unbinding of Kith'ix**; source IDs are instance **1324**, encounter **2896**. It is not a tenth boss inside the eight-boss Venomous Abyss. [H7 encounter guide](https://www.wowhead.com/guide/midnight/raids/venomous-abyss-coiled-altar-boss-strategy-abilities), [Kith'ix encounter guide](https://www.wowhead.com/guide/midnight/raids/the-unbinding-of-kithix-boss-strategy-abilities-rewards).

The database contains all **14 H7** and **10 H10** base gear items, agreeing with the complete encounter guide tables. Applying Windwalker **269** trinket masks, leather armor, appropriate primary stats and Monk weapon proficiency yields **five H7** and **three H10** base gear candidates below. This is a complete derived base loot table, **not an observed character-specific remaining R preview**. JSON preserves every base ID and the rejected items, so the lists are not derived from a BiS selection.

Ratings below describe comparable **334** tooltip queries, not initial drops or new acquisitions. The `13334/12854` comparison query supplies context/rank; it is not asserted to be the full awarded item link. For chest effects the additional required **14049** is retained explicitly.

| H7 item | Slot and 334 properties | Current marginal status |
| --- | --- | --- |
| **268209 阿曼穆索，督军的复仇** | Agility main-hand axe; Haste30/Mastery70; very rare; Venomfang effect | Conditional weapon alternative. Must compare a legal dual-wield package against the existing 341 polearm; not an automatic upgrade |
| **268225 盘卷妖术护腿** | Leather legs; Haste63/Mastery138; can become 271518 | Relevant 321 Hero6/6 replacement if still missing; retain four-piece through conversion |
| **268253 丝质巫毒斗篷** | Cloak; Haste33/Mastery80 | Conditional alternative to the crafted cloak; changing an embellished cloak also affects the embellishment layout |
| **268256 孤寂容器束带** | Leather waist; Haste47/Mastery103 | Relevant 321 Hero6/6 replacement if still missing; waist does not supply a tier-set count |
| **270173 祖尔金的处斩技法** | Agility/strength damage trinket; spec mask includes 269 | **Already R-acquired and ascended341. No new-target credit** |

The axe and owned 270173 participate in **祖尔加之咬 / Zul'ga's Bite**. The two-piece effect gives the execution an additional target and applies Venomfang; this is a real reason to retain the axe as a conditional alternative. It does not establish that its entire dual-wield setup beats the existing ascended weapon. The other very rare axe **268213** is a **two-hand axe** whose specialization mask excludes Windwalker; agility on its tooltip does not make it a Monk target.

H7's excluded base items are **268211** intellect sword, **270169** intellect trinket, **268213** two-hand axe, and non-leather armor **268222/268231/268237/268243/268255/268259**. In particular, the mail shoulder **268231** is not a leather-shoulder opportunity. The full derived Windwalker list has **no necklace, ring or shoulder**. [Full base data and spec masks](https://www.raidbots.com/static/data/live/encounter-items.json).

| H10 item | Slot and 334 properties | Current marginal status |
| --- | --- | --- |
| **281029 虫群召唤者指环** | Unique-equipped ring; Haste110/Mastery295; damage proc; database includes socket bonus13668 | **Already R-acquired. No new-target credit and cannot equip two copies** |
| **281236 具象恐惧护胸** | Leather chest; Crit58/Haste143; **bonus14049** Void Eruption | **Already R-acquired and converted to271522 with14049. No new-target credit** |
| **281215 扭曲恐兽触须** | Damage trinket; spec mask includes269; new-target crit-stack mechanic | **Important remaining distinct target** after ring/chest. User relays5/5 current elite samples pair it with270175; verify bags/current preview; personal benefit is being measured separately |

The damage trinket **281215 is not 270173** and should never be described as another copy of the user's H7 trinket. It would compete with the two owned trinkets for an equipped slot and require its own upgrade/ascension resources. A separate **explicit341 tooltip query** returns **191 agility/strength/intellect**, **35 crit per stack for15 seconds**, and a guaranteed **three stacks on the first attack against a new target, subject to the five-second interval**. The source is Kith'ix. This independently matches the user-relayed tooltip findings. The explicit level parameter is transparent and does not claim a full observed reward link. [281215 at341](https://nether.wowhead.com/tooltip/item/281215?dataEnv=1&locale=4&bonus=13334:12856&ilvl=341).

The user also relays that the elite agent's **five of five current samples use281215+270175**, and that SimC supports `twisted_horrors_tendril`. Those samples and implementation checks belong to the main study, not an independent audit in this task. They strengthen its remaining R priority without establishing a personal DPS delta. The main study is separating Slice with newly engaged targets from fixed-target tests because of this mechanic. This source task ran no simulation and assigns no encounter-drop percentage from Wowhead's generic tooltip statistics.

H10's excluded items are **280617** tank trinket, **280835** healer trinket, **280799** strength two-hand sword, **281056** intellect sword, and other armor types **281235/281238/281239**. In particular, **281235 is cloth legs**, not a leather leg option. H10 has **no necklace, leather shoulder, belt, cloak or leather legs**. Changing to Brewmaster would expose the tank-trinket mask and lose the damage-trinket eligibility shown for 281215; a spec switch is not justified as a way to improve this Windwalker target pool. [Full base data and spec masks](https://www.raidbots.com/static/data/live/encounter-items.json).

**R rules, confirmed exclusions and stop conditions**

The current CN seasonal rule is **one core per raid item**, with Heroic raid R rewards matching the Vault's **318 Myth 1/6**, rather than the boss's ordinary Hero-track drop. For example, ordinary Heroic Kith'ix drops are 311 Hero 3/6; that is not the Heroic R reward track. Ordinary Myth 6/6 ceiling is 334. Rolls require an eligible loot opportunity; having more coins does not authorize multiple rolls at once on the same encounter opportunity. [Official seasonal R rules](https://wow.blizzard.cn/news/24293281/index.html), [current R guide](https://www.wowhead.com/guide/midnight/bonus-rolls-item-upgrades).

The official knockout design removes R-earned items from the matching pool until its eligible rewards have been collected. A different source difficulty has separate eligibility. Ordinary drops, trading, crafting and Vault ownership must not be silently treated as R exclusions. The confirmed local R provenance is:

| Activity | Confirmed previously R-acquired source IDs | Effect on this week's target accounting |
| --- | --- | --- |
| H7 | **270173** | No repeat-trinket benefit |
| H8 | **271875 / 268265 / 270175 / 268215** | No new credit for the already acquired head, neck, heart or weapon |
| H10 | **281029 / 281236** | No new credit for ring or converted-effect chest |

The [official design description](https://wow.blizzard.cn/news/24271858/) is from Season 1; the current seasonal rules and current R guide retain the system, but exact shared-spec exclusion scope and the character's current cycle are not established by that old article. Complete history is unknown. These are confirmed acquisitions and conditional knockout exclusions, **not proof that the current preview contains only the unlisted items**. No exact chance, equal-weight assumption, `1/n`, guaranteed next item, or fixed remaining-attempt count is assigned.

Orin's unlocked weekly exchange provides an additional core, and the Vault can offer a core alternative subject to its unlock conditions. The current guide requires at least three offered Vault item slots for that alternative. Neither possible source establishes the character's present coin balance or makes a future week's currency available now. [CN weekly exchange rule](https://wow.blizzard.cn/news/24304162/), [current Vault/core guide](https://www.wowhead.com/guide/midnight/bonus-rolls-item-upgrades).

| Slot / objective | H7 | H10 | Useful other source or stop rule |
| --- | --- | --- | --- |
| Shoulder321 Hero6/6 | No leather shoulder | None | Labyrinth272244 is a direct gap-filler; **Vashnik the Malignant** also supplies268246 with a different crit/mastery distribution |
| Legs321 Hero6/6 | **268225**, haste/mastery | No leather legs | Labyrinth272243 is an alternative; choosing shoulder first reduces overlap with the H7 plan |
| Waist321 Hero6/6 | **268256**, haste/mastery | None | Relevant H7 objective; crafted replacement also exists, but no current resource budget is known |
| Necklace | None | None | Existing H8 **268265** already R-acquired and previously recorded ascended341; no unfilled H7/H10 necklace target |
| Second ring | None | **281029 already R-acquired and unique-equipped** | **268249 邪恶炼金师指环 from Vashnik** is a distinct candidate; at334 it has Crit73/Mastery332. Labyrinth offers four fixed alternatives |
| Cloak | **268253** | None | Reassess the existing crafted cloak's embellishment before treating it as a simple slot upgrade |
| Trinket | **270173 already341** | **281215**, important distinct target | User-relayed5/5 elite adoption supports H10 priority; verify it is still missing and present in the current preview; main study measures personal benefit |

Vashnik's public source encounter is **2882**, and both **268246** and **268249** point to it. Use the boss name to avoid old shorthand/order ambiguity. The H10 ring does not erase the usefulness of a different second ring; it does erase the case for treating another H10 ring as a new target.

If staying with H7/H10, reserve the first Labyrinth purchase for the shoulder **conditionally on the current251146 precursor and desired stat distribution**, catalyze it to retain four-piece, and upgrade when affordable. H7 spending can still pursue missing belt/legs, with cloak and axe judged against the full loadout. **Continue to treat H10 as a meaningful R target for281215**, provided it remains missing and listed in the current reward preview; the already owned ring and effect chest contribute no additional benefit. Once281215 is obtained, reassess H10 before spending another coin, since the three-item derived Windwalker base table then has no unowned distinct target established here. Stop spending on a boss once its useful objectives are satisfied; neither the old R history nor this base table supports blindly continuing indefinitely.

**Unresolved checks and evidence limits**

- No live merchant, Catalyst conversion, upgrade-cost quote or character-specific remaining R preview was captured. The browser host was unavailable. Public database eligibility and the published catalogue are the strongest available fallback, not a fabricated game UI observation.
- Actual full merchant/new-conversion bonus chains and socket/tertiary results are unknown. Rank-only lookup bonuses are explicitly labeled as such. The newly available October29 equipped export does confirm current full equipped bonuses, head13847 and crafted gloves244575; it still supplies no explicit redirected precursor or crafted-stat fields.
- The current shoulder/leg precursor baseline is supported by the historical full export. A new full export with `redirected_base_stats` would resolve continuity without using default tier stats.
- All six quest IDs exist, but later CN weekly order and most exact CN quest strings are not independently verified. The third-week Cave Towers identification has current NA support; this is not a CN UI observation.
- User bags, current coin balance, current fragment count, Catalyst charges, Vault offers, complete R history and pool-cycle completion are unknown. A past acquisition date is not invented.
- Both ascended trinkets are341. The stale340 tooltip is retained as a conflict, not used to downgrade them or recalculate their current stats.
- No conclusion here is a new simulated DPS result or exact roll probability.

**Tool-call brief / 工具调用简报**

Research date: **2026-10-29, Asia/Shanghai**; per-request timestamps and SHA-256 hashes are in JSON. MCP web search used up to four queries per request and long responses to locate current official CN rules, current third-week reports, quest IDs and reward tables. Sources include `wow.blizzard.cn`, `wowhead.com`, `news.17173.com`, `ol.3dmgame.com`, `icy-veins.com` and `needbeforegreed.com`. PowerShell performed read-only public page/tooltip requests, with four concurrent independent item lookups, plus local record reads. CUA attempted one hidden vendor-page session because the merchant list required JavaScript; its browser host was unavailable. Several item/NPC pages returned a JavaScript challenge, direct Icy retrieval returned403, and some CN quest tooltips returned unknown/404; evidence fell back to accessible current articles, the API mirror and public item data. No challenge was solved or bypassed, no repeated retry loop was used, and no game state was changed.
