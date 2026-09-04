# 在线 WCL 获取流程

本参考文件只规定“取哪些数据、如何分页和如何降级”，不要求技能绑定某一种 API 客户端。

## 官方接口边界

WCL v2 公共 GraphQL 接口是 `https://www.warcraftlogs.com/api/v2/client`，公开报告可用 OAuth 客户端凭据流程访问；私密报告需要用户授权流程。事件类型包括施法、增益、伤害、死亡、资源、召唤和战斗信息等。使用前核对 Warcraft Logs 官方 API 文档的当前字段定义与版本。

不要在技能正文或聊天中写入真实客户端密钥，也不要让用户把密钥粘贴到对话里。若没有安全凭据，优先使用用户已提供的公开页面或本地导出。

## 推荐查询顺序

1. `report`：代码、标题、开始/结束时间、区域/版本。
2. `fights`：战斗编号、首领、难度、击杀、开始/结束时间、阶段/百分比。
3. `masterData` / `playerDetails`：玩家源 ID、名称、专精、职责、天赋/装备可用性。
4. `table(dataType: DamageDone)`：总伤害、技能构成、命中次数和目标拆分。
5. `events(dataType: Casts)`：完成施法和起始施法，用于技能次数与时间线。
6. `events(dataType: Buffs/Debuffs/Resources/Summons)`：覆盖率、触发链、资源和宠物归属。
7. `events(dataType: Deaths/DamageTaken)`：死亡时间、致死技能和死亡前伤害序列。
8. `worldData` 排名：只用于寻找参考样本，不替代事件证据。

## 分页伪代码

```text
all = []
cursor = null
重复：
  请求同一 fight/source/filter，若 cursor 存在则加入 startTime=cursor
  追加 data
  若 nextPageTimestamp 为空，结束
  若 nextPageTimestamp 不大于 cursor，报错并停止
  cursor = nextPageTimestamp
按事件唯一键去重并按 timestamp 排序
```

分页时必须保留 `nextPageTimestamp`，因为事件结果是分页数据；不要只取第一页。报告事件可能随修正而变化，缓存结果要记录抓取时间和查询条件。

## 查询最小化

- 先用单个战斗和单个 source 过滤，再扩大到同 Boss 的多场战斗。
- 先取 `Casts`、`DamageDone`、`Buffs` 和 `Deaths`；只有问题需要时再取完整伤害承受、打断或驱散。
- 多场开荒统计可按 5-8 个 fight 分批查询，避免单次请求过大。
- 对同一报告/战斗/查询类型缓存本地 JSON；重试采用退避，不并发重复请求。

## 在线不可用时的降级

按以下顺序降级，并在报告中标注等级：

1. 页面可见但事件不可见：做摘要级比较，只说总伤害、排名和公开构筑。
2. 只有报告代码：列出需要用户导出的最小文件，不猜技能序列。
3. 有部分本地文件：用 `summarize_wcl.py` 生成可比较摘要，并列出缺失字段。
4. 只有截图：只解释截图中可验证的内容，避免推断未显示的覆盖率或死亡原因。

## 地区和版本

URL 域名、报告元数据和用户指定地区优先于默认值。不要把外部项目的地区过滤规则直接套用到中国报告；跨地区样本要在基准表里标注地区、版本和排名环境。
