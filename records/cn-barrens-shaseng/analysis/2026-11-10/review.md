# Shaseng attainable Windwalker Mythic+ review — 2026-11-10

Latest complete user snapshot:22:03 CN/Barrens,Live12.1.5.70783. Equipped gear,talents and Omnium are identical to the21:35 import;bag ring268252 and current currency change are retained separately. User explicitly excludes inaccessible Mythic7/8 9/6 gear. Current roll balance is zero,already including the new H5 result.

The341 neck,weapon,Heart,Tendril and334 Swarmcaller ring match the current hero-filtered top-five item IDs. Four-piece is already active with five tier pieces. The321 leg is the clearest gear-level gap. Prioritize334 haste/mastery legs,then evaluate H7 waist/cloak as a complete set. Move the cloak Arcanoweave lining to the existing crafted boots before equipping the raid cloak.

Target A retains the owned331 crafted crit/mastery ring and334 tier hands. It adds H7 legs/waist/cloak,three real head/wrist/waist sockets,and240900 rare gems. Target B changes both the second ring and gem allocation;their difference is a complete-loadout comparison. Neither is a global BiS proof. Target A is the practical default because it retains the ring and performs better in the five-target workload. The standalone owned331 haste/mastery glove is not a universal upgrade.

|Stat|Current unbuffed|Target A unbuffed|Top-five displayed range|
|---|---:|---:|---|
|暴击|1069 / 37.24%|795 / 31.28%|前五27–33%；等级593–886|
|急速|777 / 17.66%|890 / 20.23%|前五18–23%；等级814–1011|
|精通|1110 / 74.82%|1353 / 87.13%|前五71–91%；等级1035–1431|
|全能|105 / 1.94%|105 / 1.94%|前五2–7%；多数约2%|

|Configuration|DungeonSlice|Single target|Five targets|
|---|---:|---:|---:|
|当前实装：11月10日22:03|+0.000%|+0.000%|+0.000%|
|只换334盘卷妖术护腿（H7）|+1.255%|+0.880%|+0.716%|
|只换334雾猎者腿甲（迷宫备选）|+1.090%|+0.740%|+0.740%|
|只换背包331急精制作手（保四件套）|+0.444%|-0.125%|-0.112%|
|334邪恶炼金师指环替换制作戒（同孔）|+0.825%|+0.093%|+0.059%|
|334爪戒替换制作戒（升满、有孔、镶嵌附魔）|-2.021%|-2.020%|-6.323%|
|已有318爪戒替换制作戒（补镶嵌附魔）|-2.383%|-2.499%|-6.667%|
|H7腿＋腰＋披风；奥纹由披风移到鞋|+1.855%|+0.923%|+0.648%|
|目标B：H7三件＋邪炼戒＋三孔＋致命紫晶|+3.157%|+1.705%|+1.290%|
|目标A：保留制作戒，H7三件＋三孔＋迅捷紫晶|+2.976%|+1.823%|+1.662%|

The318 H5 ring is owned but remains in bags. Prepared318 and max334 versions both preserve one socket and use the current ring enchant/gem,so their loss is not an empty-socket or missing-enchant artifact. Do not prioritize its upgrades for this loadout. H7 legs and Myth-track Labyrinth legs are close;the existing305 bag leg must not be treated as the new Myth-track copy. Retain at least four tier pieces when switching gloves.

## Measurement and acquisition boundaries

Source commit de11f57df75dda668bae6ac7043a43b98831fa96 was built in a detached local worktree with native70783 data. The original SimC checkout and binary were preserved. Screening used2000 iterations/seed26111011;finalists used6000/seed26111029. DungeonSlice360s,Patchwerk240s single-target,andPatchwerk90s five-target are supported models. Finalist reports have5999 samples,valid_fight_style=true,no severe diagnostics,at least four tier pieces and exactly two Arcanoweave instances. CI fields are95% half-widths of each mean,not practical prediction intervals or paired-difference tests.

Damage comparisons hold the supplied talents,Omnium,race and consumables constant. Raid buffs and Bloodlust are disabled. Consumables are explicitly mastery flask2,Harandar Celebration,Void-Touched augmentation,Recklessness potion2 andPhoenix oil2. Static stat snapshots disable all these consumables. Short20-iteration identity runs supply static stats only and are not DPS evidence.

Engine assumptions still include non-split chest/Swarmcaller damage and the Rune of Unleashed Fire trigger target. Models cannot establish an actual dungeon route or eliminate mechanic uncertainty. Population stats have unknown buff basis and rounded percentages;they are not hard breakpoints. The current player sample is the first five in the November10 Conduit Mythic+ page,not an unfiltered monk list;US/EU/KR/TW only,not CN. The complete sample has50 characters and4026–4259 score.

Actual H7 reward-preview eligibility,knockout scope,Vault offers and socket-token availability remain unresolved. Current balance is not an income rate. Targets and clean target exports are hypothetical acquisitions,not ledger events. No exact bonus-roll success probability is claimed.

## Artifacts and sources

- report.html / report-data.json:Chinese user-facing report.
- comparison-results.json:all native70783 result summaries and final comparisons.
- elite-evidence.json:original-site timestamps,equipment and top-five profiles.
- candidate-tooltips.json:dated item/gem source responses.
- simc-manifest.json:engine/source/input hashes.
- ../../snapshots/2026-11-10-2203.simc:exact latest full import.
- ../../weeks/2026-11-05.json:zero balance and confirmed H5 acquisition;the latest balance is never double-debited.

- [Murlok天神御师大米前50：11月10日18:03更新](https://murlok.io/monk/windwalker/conduit-of-the-celestials/m%2B)
- [Method J-Funk装备指南（10月14日，12.1.5）](https://www.method.gg/guides/windwalker-monk/gearing)
- [Method属性与消耗品（10月14日）](https://www.method.gg/guides/windwalker-monk/stats-races-and-consumables)
- [Icy Veins装备与化生来源属性说明（10月12日）](https://www.icy-veins.com/wow/windwalker-monk-pve-dps-gear-best-in-slot)
- [迷宫神话2/6兑换物品与三碎片要求](https://www.wowhead.com/news/myth-2-6-piece-of-loot-now-available-from-labyrinths-383603)
- [顶级蛮兵爪戒334完整提示](https://nether.wowhead.com/tooltip/item/268252?dataEnv=1&locale=4&bonus=13334:12854:13668&ilvl=334)
- [邪恶炼金师指环334提示](https://nether.wowhead.com/tooltip/item/268249?dataEnv=1&locale=4&bonus=13334:12854:13668&ilvl=334)
- [无瑕迅捷紫晶：16精通＋7急速](https://nether.wowhead.com/tooltip/item/240900?dataEnv=1&locale=4)
- [SimulationCraft官方70783源码：de11f57](https://github.com/simulationcraft/simc/tree/de11f57df75dda668bae6ac7043a43b98831fa96)
