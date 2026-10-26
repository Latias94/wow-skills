# WoW 12.1 元素萨：风暴守护者与升腾顺序研究

> 研究状态：已完成，可用于后续问答；涉及实战收益的结论仍应以角色自身模拟和正式服热修为准。
> 抓取日期：2026-08-17（Asia/Shanghai）。
> 适用版本：《魔兽世界：至暗之夜》12.1「乌拉泰克的诅咒」，元素萨满，重点为先知（Farseer）与 12.1 赛季套装。
> SimulationCraft 快照：`midnight` 分支提交 [`7177c29f5d9c699a4e0a12fae23ee378bf6d4097`](https://github.com/simulationcraft/simc/commit/7177c29f5d9c699a4e0a12fae23ee378bf6d4097)。

## 结论先行

下表专门回答“进入爆发点、两个技能都可用”时的先后顺序，不表示整场战斗都要强行捆绑。冷却已经错开时，当前 SimC 只在升腾还差约 10 秒以内才保留风暴守护者；差得更久通常先正常使用风暴守护者。

| 场景 | 推荐起手 | 结论强度 | 理由 |
| --- | --- | --- | --- |
| 没有 12.1 四件套，或只有二件套 | `风暴守护者 → 升腾 → 消耗风暴守护者充能` | 高 | 没有四件套就不存在提前取得“元素奔涌”的收益；当前 SimC 默认 APL 也这样配对。 |
| 四件套，单体或能完整打完升腾及后续奖励的长战 | 默认 `风暴守护者 → 升腾 → 在升腾中消耗充能` | 中高 | 当前 SimC 的单体 APL 明确采用此顺序；风暴守护者在升腾中消失后，奖励延迟到升腾结束并一次获得 4 层。视频所述两种方案差距不到 1%，但其原始模拟配置不可复核。 |
| 四件套，短时 AOE／大秘境小怪波次 | 可用 `风暴守护者 → 把全部充能打空 → 获得 2 层 → 升腾` | 中 | 能把两次强化构筑技与免费消耗技前置，避免奖励在升腾结束后才出现、届时小怪已死或坦克已拉走。它是视频作者的短波次实战方案；通用 SimC AOE APL 仍采用上一行的配对顺序，因此不是无条件的理论最优。 |
| 四件套，长寿命 AOE／首领式多目标 | 默认 `风暴守护者 → 升腾` | 中高 | 目标能活过升腾并让你完整消耗后置 4 层时，延迟结算的损失较小；当前 SimC 3+ 目标 APL 也不先打空充能。 |

对用户问题最直接的回答是：

- **单体默认不要先打一发闪电箭，风暴守护者后直接接升腾（允许中间穿插既定的非充能准备技能），然后在升腾里消耗充能。**
- **短命 AOE 且已有四件套时，可以先把风暴守护者的全部充能用闪电链打空，再开升腾。**
- “先打一发拿 buff”这个说法不准确。四件套在风暴守护者 **消失（fade）** 时触发；基础风暴守护者有两次强化充能，所以通常需要两发对应法术，而不是一发。若实战中有额外充能，以 buff 是否归零为准。
- “风暴守护者和升腾同时开”不是同一个 GCD，而是指二者紧邻配对，并且在升腾前不消耗风暴守护者充能。

## 四件套到底怎样工作

### 暴雪公开说明

暴雪 12.1 PTR 开发说明中的套装效果为：

- 二件套：大地震击、元素冲击与地震术伤害提高 25%。
- 四件套：风暴守护者或升腾消失时，接下来的 2 次闪电箭、闪电链或熔岩爆裂伤害提高 25%，并使下一次地震术、大地震击或元素冲击不消耗漩涡值。

来源：[暴雪 12.1 PTR 开发说明，Shaman / Elemental / Class Sets](https://eu.forums.blizzard.com/en/wow/t/midnight-curse-of-ulatek-ptr-development-notes/621832/1)。该帖是暴雪一手资料，但属于持续修改过的 PTR 开发记录，不是可冻结的最终正式服法术快照。

结构化法术数据可交叉检查：

- [元素萨 12.1 二件套，法术 1296625](https://www.wowhead.com/ptr/spell=1296625/shaman-elemental-12-1-class-set-2pc)
- [元素萨 12.1 四件套，法术 1296626](https://www.wowhead.com/ptr/spell=1296626/shaman-elemental-12-1-class-set-4pc)
- [Flowing Elements，法术 1300219](https://www.wowhead.com/ptr/spell=1300219/flowing-elements)
- [Overcharge，法术 1300222](https://www.wowhead.com/ptr/spell=1300222/overcharge-tier)

Wowhead 法术页是从游戏数据整理出的数据库证据，不等同于暴雪发布的设计文档。文中暂用视频译名“元素奔涌”和“过载”；其正式简体中文本地化名称尚未独立核实。

### SimC 对“延迟结算”的建模

当前 SimC 12.1 源码把这段交互实现为两个回调：

1. 风暴守护者归零时，如果升腾正在持续，不立刻给 2 层，而是设置 `buffer_tier = true`。
2. 升腾归零时，若这个标记存在，一次触发 4 层；否则只触发升腾自身的 2 层，然后清除标记。

可复核代码：

- [升腾结束：根据 `buffer_tier` 触发 4 或 2 层](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp#L12515-L12522)
- [风暴守护者结束：升腾中只缓存，否则立即给 2 层](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp#L12550-L12565)

因此，常见的两条时间线是：

```text
提前兑现：风暴守护者 → 消耗至 0 → 立即得到 2 层 → 升腾 → 升腾结束再得到 2 层

延迟合并：风暴守护者 → 升腾 → 升腾中消耗至 0（先缓存）→ 升腾结束一次得到 4 层
```

边界情况：若风暴守护者没有在升腾期间消失，而是留到升腾结束以后才消失，就不会一次给 4 层；升腾结束先给 2 层，之后风暴守护者消失再给 2 层。

SimC 还将每一层“元素奔涌”的消耗与免费消耗技 buff 连接起来：层数减少时触发一次 `overcharge_tier`。对应源码见 [Flowing Elements 与 Overcharge 的 buff 定义](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp#L12835-L12845)。

可复核的法术消费位置：

- 闪电链消耗一层：[源码](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp#L6562-L6565)
- 熔岩爆裂消耗一层：[源码](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp#L7192-L7200)
- 闪电箭消耗一层：[源码](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp#L7332-L7340)
- 元素冲击、大地震击、地震术分别消费免费消耗技 buff：[元素冲击](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp#L7608-L7618)、[大地震击](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp#L8141-L8145)、[地震术](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp#L7917-L7927)

这也解释了实战中的一个操作原则：有“元素奔涌”且已经有免费消耗技 buff 时，应先打消耗技，再打下一发构筑技，避免刷新或覆盖尚未使用的免费消耗。SimC 单体 APL 在下一发构筑技前专门检查这两个 buff，并优先打元素冲击或大地震击：[APL 第 88–90 行](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/ActionPriorityLists/default/shaman_elemental.simc#L88-L90)。

> 证据边界：SimulationCraft 是公开、可执行且可版本固定的战斗模型，但不是暴雪服务器源码。它强力佐证视频所说的延迟合并机制，仍不能替代正式服战斗日志或暴雪对该特殊交互的明确说明。

## 当前 SimC 默认顺序

### 单体与双目标

当前默认 APL 的相关条件为：

```text
stormkeeper,if=cooldown.ascendance.remains>10|cooldown.ascendance.remains<gcd|fight_remains<20
...
ascendance,if=cooldown.stormkeeper.remains>15|fight_remains<20
```

位置：[单体 APL 第 78–102 行](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/ActionPriorityLists/default/shaman_elemental.simc#L78-L102)。预战斗列表也提前施放风暴守护者：[第 18 行](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/ActionPriorityLists/default/shaman_elemental.simc#L18)。

按优先级解释：

1. 升腾还差 10 秒以内时，保留风暴守护者等待配对；超过约 10 秒则可正常使用风暴守护者。
2. 风暴守护者施放后进入冷却，`cooldown.stormkeeper.remains > 15` 成立，于是升腾会排在强化闪电箭之前。
3. 即使中间经过先祖迅捷、补烈焰震击或电能烈焰等准备动作，APL 也不会先用闪电箭消耗风暴守护者充能。

所以，对单体问题，当前可复核的默认答案是 **风暴守护者后接升腾，不先打空充能**。

### 三目标以上

AOE 列表采用同一组同步条件：

- 风暴守护者：[第 48–49 行](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/ActionPriorityLists/default/shaman_elemental.simc#L48-L49)
- 升腾在强化闪电链之前：[第 50–68 行](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/ActionPriorityLists/default/shaman_elemental.simc#L50-L68)

也就是说，通用的 3+ 目标模拟仍是 **风暴守护者 → 升腾 → 强化闪电链**，并没有因为四件套自动改成“先打空再升腾”。

但 APL 文件开头明确说明：默认列表追求简单、可实践、能给出有意义的好结果，未必是绝对最高 DPS；见 [第 2–6 行](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/ActionPriorityLists/default/shaman_elemental.simc#L2-L6)。因此它不能否定短命小怪波次中的前置兑现策略。

## 单体为何倾向紧邻配对

单体或长时间战斗中，选择“风暴守护者 → 升腾”有三个可验证的支点：

1. 这是当前 SimC 单体默认 APL 的实际执行顺序，而不只是攻略作者的口头建议。
2. 只要在升腾期间把风暴守护者消耗至 0，四件套奖励不会丢失，而是合并成升腾结束后的 4 层。
3. 暴雪 12.1 调整后，升腾仍强化元素过载伤害；把风暴守护者的强化法术放在升腾窗口内，至少能让相关过载部分吃到窗口收益。

需要注意 12.1 的后续修订：暴雪最初的 PTR 文案容易让人以为风暴守护者仍会让闪电箭额外产生一次过载，但 2026-06-23 的更新明确移除了这项闪电箭额外过载；其他风暴守护者效果不变。闪电链的全目标必定过载仍保留。来源仍为同一份[暴雪 12.1 PTR 开发说明](https://eu.forums.blizzard.com/en/wow/t/midnight-curse-of-ulatek-ptr-development-notes/621832/1)。

因此，不能再用“强化闪电箭固定多一次过载”作为单体配对升腾的理由。当前结论主要来自 APL 顺序和奖励不丢失，而不是这个已经被移除的旧机制。

视频在 3–4 分钟单体模拟中称，紧邻配对方案略高、差距不到 1%。由于视频没有提供可导入的角色串、天赋、装备、战斗长度随机范围、迭代数与自定义 APL，这个数值只能作为作者经验，不能当成可独立复现的定量证据。

## 短时 AOE 为何可能反过来

短波次的核心不是“总共能不能拿到 4 层”，而是 **奖励何时可用**：

```text
紧邻配对：升腾开始 ───────── 升腾结束 → 4 层才出现
提前兑现：先打空 SK → 2 层出现 → 升腾开始，可更早转化为免费地震术／元素冲击
```

当小怪预计在升腾结束前后死亡、坦克即将拖走或目标数量会快速下降时，延迟合并的 4 层可能来不及在高目标数阶段消费。提前用强化闪电链打空风暴守护者，则可先拿 2 层，再进入升腾，把对应免费消耗技前置到仍有足够目标的时间段。

视频作者对约 30–90 秒的大秘境短波次推荐此前置方案，并报告其 1 分钟自定义模拟约为 96 万对 95 万。这个比较方向符合四件套的时间价值机制，但无法从公开视频字幕还原完整模拟条件，所以本文不把约 1% 差值当成普适结论。

实战决策可以简化为：

- **优先提前兑现**：小怪寿命短；拉怪阶段已经能安全命中多目标；升腾结束后很可能无目标可打；你需要更早的地震术爆发。
- **优先紧邻配对**：怪群能稳定活过升腾并留出后续消费时间；优先目标需要升腾内爆发；移动、打断或机制会让你无法在升腾前顺利打空充能。
- **不应提前兑现**：没有四件套。此时提前打空只是在把强化法术移出升腾窗口，没有换来套装层数。

AOE 应用闪电链消耗风暴守护者，单体才通常用闪电箭。基础风暴守护者提供两次强化施法；任何使实际层数变化的效果都应以界面剩余层数为准，目标是让该 buff 真正归零，而不是机械地记“一发”或“两发”。

## 先知构筑的适用性

当前 SimC 元素 APL 是共享列表，但其中包含先知相关条件与先祖技能逻辑，没有为先知另写一套相反的风暴守护者／升腾顺序。暴雪 12.1 还将先祖的闪电链目标数由 3 提高到 5，并调整先祖熔岩爆裂的暴击缩放；这些改动会影响 AOE 构成，却没有改变四件套的触发时点。

因此，本文的顺序判断可用于先知：

- 单体基准仍用紧邻配对。
- 大秘境短波次是否提前兑现，主要由目标寿命和四件套奖励能否及时消费决定，而不是仅由“先知”标签决定。

## 外文攻略交叉检查（二手资料）

截至 2026-08-17，检索到的主流公开轮转页仍主要标注 12.0.7，尚不能直接回答 12.1 四件套的两种顺序比较：

| 来源 | 页面标注/抓取状态 | 可用信息 | 不能证明的内容 |
| --- | --- | --- | --- |
| [Icy Veins：Elemental Shaman Rotation](https://www.icy-veins.com/wow/elemental-shaman-pve-dps-rotation-cooldowns-abilities) | 页面标注 12.0.7，2026 年 6 月更新 | 单体起手为风暴守护者后，在消耗其充能前开升腾；也建议配对时不要为升腾保留超过约 10 秒 | 没有评价 12.1 四件套的延迟 4 层与短 AOE 取舍 |
| [Method：Elemental Shaman Playstyle and Rotation](https://www.method.gg/guides/elemental-shaman/playstyle-and-rotation) | 页面标注 12.0.7，2026-06-16 更新 | 建议风暴守护者总是在升腾之前使用 | 不是 12.1 套装攻略，不能证明哪种四件套顺序更高 |
| [Wowhead：Elemental Shaman Rotation](https://www.wowhead.com/guide/classes/shaman/elemental/rotation-cooldowns-pve-dps) | 抓取内容仍包含旧赛季套装语境 | 支持升腾在风暴守护者之后使用的传统配对逻辑 | 旧套装与 12.1 套装不是同一机制，不能直接外推 |

这些页面只能作为“没有四件套或传统起手”的专家二手佐证。它们没有比版本固定的 SimC 12.1 APL 和源码更高的证据权重。

## 如何用自己的角色验证

若要把“单体不到 1%”或“短 AOE 提前兑现更高”变成适合自己角色的结论，应保持角色、装备、天赋、敌人数和随机种子一致，只改 APL 顺序：

1. 从游戏导出 `/simc` 字符串，并确认已装备 12.1 四件套。
2. 建立两个 APL：A 方案在升腾前把风暴守护者层数消耗至 0；B 方案在风暴守护者后优先升腾。
3. 至少比较单体 240–300 秒，以及 3/5 目标的 30、60、90 秒固定时长。
4. 同时观察总伤害、升腾窗口伤害、四件套触发次数、未消费的 Flowing Elements/Overcharge 层数，而不只看平均 DPS。
5. 大秘境最终还要用真实战斗日志核对每波存活时间；固定时长木桩模拟无法表达拉怪、断档与转场。

## 已知限制与待验证项

- 本次没有取得一份已发布、可复核且明确标注 12.1 的英文 PvE 攻略来直接比较两种四件套顺序；Icy Veins、Method 与 Wowhead 的相关轮转页仍是旧版本语境。
- 暴雪的[正式版 12.1 内容更新说明](https://worldofwarcraft.blizzard.com/en-us/news/24293281)在本次抓取环境中返回错误，故职业细节引用官方 PTR 开发记录，并用当前 SimC 与法术数据库交叉核对。
- 未运行用户角色的 SimulationCraft/Raidbots，也没有视频作者的原始模拟配置；因此本文不独立确认视频中的 96 万、95 万及“不到 1%”数值。
- SimC 的延迟合并是模型实现，不是暴雪服务器源码；正式服若出现热修或模型 issue，应以最新战斗日志、SimC 提交与暴雪说明重新核验。
- `Flowing Elements`、`Overcharge` 的简体中文正式名称尚未核实，后续整理用户文档时应优先采用游戏客户端中的实际名称。

## 来源清单

### 一手与高可信技术证据

1. 暴雪官方：[Midnight: Curse of Ula'tek 12.1 PTR Development Notes](https://eu.forums.blizzard.com/en/wow/t/midnight-curse-of-ulatek-ptr-development-notes/621832/1)，首次发布 2026-06-18，后续持续更新；抓取于 2026-08-17。
2. 暴雪官方：[Curse of Ula'tek Content Update Notes](https://worldofwarcraft.blizzard.com/en-us/news/24293281)，正式版文章；本次抓取返回错误，未用其正文支撑具体机制。
3. SimulationCraft 默认元素 APL：[固定提交文件](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/ActionPriorityLists/default/shaman_elemental.simc)，`midnight` 分支快照；抓取于 2026-08-17。
4. SimulationCraft 元素萨实现：[固定提交源码](https://github.com/simulationcraft/simc/blob/7177c29f5d9c699a4e0a12fae23ee378bf6d4097/engine/class_modules/sc_shaman.cpp)，重点为第 12515–12565、12835–12845 行；抓取于 2026-08-17。

### 数据库与专家二手资料

1. Wowhead PTR 法术数据库：[12.1 四件套](https://www.wowhead.com/ptr/spell=1296626/shaman-elemental-12-1-class-set-4pc)；抓取于 2026-08-17。
2. Icy Veins：[Elemental Shaman Rotation](https://www.icy-veins.com/wow/elemental-shaman-pve-dps-rotation-cooldowns-abilities)，标注 12.0.7；抓取于 2026-08-17。
3. Method：[Elemental Shaman Playstyle and Rotation](https://www.method.gg/guides/elemental-shaman/playstyle-and-rotation)，标注 12.0.7；抓取于 2026-08-17。
4. Wowhead：[Elemental Shaman Rotation and Cooldowns](https://www.wowhead.com/guide/classes/shaman/elemental/rotation-cooldowns-pve-dps)，抓取内容仍是旧赛季语境；抓取于 2026-08-17。

### 用户提供材料

- `C:\Users\Administrator\Downloads\[12.1]个人向元素萨PVE入门教学.srt`，重点时间段 32:12–44:44。它记录了作者对四件套机制、两种顺序及短 AOE 实战取舍的解释；作为视频字幕证据使用，不替代版本固定的一手资料或可复现模拟。
