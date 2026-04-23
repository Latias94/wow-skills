# wow-skills

《魔兽世界》相关的 AI Agent Skills 仓库，面向 `Codex`、`Claude Code` 以及兼容 `Agent Skills` 开放标准的工具。

当前仓库主要收录我自己在实战中会反复复用的 WoW 技能。目标不是堆很多泛用提示词，而是把一类复杂问题沉淀成可复用、可迭代的技能包。

目前包含：

- `wow-voidforge-roll-planner`
  - 用于《魔兽世界》`12.0.5` 及相近版本的 `晦暗虚空核心 / Voidforge bonus roll / 宏伟宝库 6 代币换币` 装备规划
  - 支持按 `职业专精`、`Hero talents`、`团本 / 大秘境 / 双修`、`主号 / 小号`、`当前装等`、`可达性`、`制造业`、`宝库候选`、`/simc` 输入完整度来做分析
  - 输出默认优先使用中文副本名、Boss 名、装备名

## 仓库结构

这个仓库采用和官方 skills 仓库相近、但更轻量的结构：

```text
wow-skills/
├── README.md
└── skills/
    └── wow-voidforge-roll-planner/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── analysis-template.md
            ├── decision-rules.md
            ├── elemental-shaman-12-0-5.md
            ├── input-granularity.md
            ├── player-profile-template.md
            └── source-weighting.md
```

说明：

- `skills/`：仓库内所有技能的聚合目录
- `skills/<skill-name>/SKILL.md`：技能入口文件
- `agents/openai.yaml`：Codex 侧的 UI 元数据
- `references/`：按需读取的参考资料，不会默认全部塞进上下文

## 安装到 Codex

### 方式一：手动复制

把目标 skill 目录复制到：

- `$CODEX_HOME/skills/<skill-name>`
- 如果没有设置 `CODEX_HOME`，默认就是 `~/.codex/skills/<skill-name>`

例如：

```powershell
Copy-Item -Recurse -Force `
  '.\skills\wow-voidforge-roll-planner' `
  "$HOME\\.codex\\skills\\wow-voidforge-roll-planner"
```

安装后建议重启 Codex，让新 skill 被重新发现。

### 方式二：通过 Codex 内置 skill-installer

如果你已经把这个仓库 push 到 GitHub，可以直接在 Codex 里安装：

```text
$skill-installer install https://github.com/Latias94/wow-skills/tree/main/skills/wow-voidforge-roll-planner
```

安装后同样建议重启 Codex。

## 安装到 Claude Code

Claude Code 支持与 `Agent Skills` 兼容的技能目录，常见有三种作用域：

- 个人级：`~/.claude/skills/<skill-name>/SKILL.md`
- 项目级：`.claude/skills/<skill-name>/SKILL.md`
- 插件级：`<plugin>/skills/<skill-name>/SKILL.md`

最简单的手动安装方式：

### 方式一：安装到个人技能目录

```powershell
New-Item -ItemType Directory -Force "$HOME\\.claude\\skills" | Out-Null
Copy-Item -Recurse -Force `
  '.\skills\wow-voidforge-roll-planner' `
  "$HOME\\.claude\\skills\\wow-voidforge-roll-planner"
```

### 方式二：安装到当前项目

在你的项目根目录下创建：

```text
.claude/skills/wow-voidforge-roll-planner/
```

然后把本仓库里的 `skills/wow-voidforge-roll-planner` 复制进去。

补充说明：

- 如果 `~/.claude/skills` 或项目里的 `.claude/skills` 在 Claude Code 当前会话启动时已经存在，那么新增或修改 skill 通常会在当前会话内生效
- 如果这是第一次创建顶层技能目录，通常需要重启 Claude Code

## 如何使用当前 skill

在 Codex 或 Claude Code 中，你可以直接描述目标，例如：

- `分析 12.0.5 元素萨 Stormbringer 在大秘境应该把 R 币投给哪个本`
- `如果我是小号，只打 10 层大秘境，宝库没有好装备，是拿装备还是拿 6 代币`
- `我贴一个 /simc，你帮我判断这周是先拿宝库还是继续追某个副本`

当前 `wow-voidforge-roll-planner` 已经内置了这些关键逻辑：

- Hero talents 分流
- 团本 / M+ / 双修差异
- 主号 / 小号差异
- 套装可转化位、制造位降权
- 大秘境 1 币 vs 团本 2 币权重
- 宏伟宝库 `6 代币换额外核心`
- `R 币去重 / knockout` 的同难度连续追击逻辑
- `/simc` 输入后做更精细比较

## 后续计划

目前仓库里只有一个 WoW skill，后续准备继续补：

- 更多职业 / 专精样例参考
- 更明确的评分模型与周计划模板
- 制造业 / 火花 / 纹章路线联动建议
- 可能拆出独立的职业分析 skill

## 参考的官方结构

这个仓库的组织方式主要参考了：

- OpenAI 官方 `openai/skills`
- Anthropic 官方 `anthropics/skills`

它们的共同点都是：

- 根目录保留 `README`
- 技能统一放在 `skills/`
- 每个 skill 都是独立目录，入口是 `SKILL.md`

对个人仓库来说，采用 `README.md + skills/<skill-name>` 的结构已经足够清晰，也更方便后续继续加新的 WoW 技能。
