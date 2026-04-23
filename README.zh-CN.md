# wow-skills

[English](README.md) | 简体中文

《魔兽世界》相关的 AI Agent Skills 仓库，面向 `Codex`、`Claude Code` 以及兼容 `Agent Skills` 结构的工具。

当前仓库主要收录可复用的 WoW 技能，而不是一次性的提示词。目标是把复杂、反复出现的分析流程沉淀成可以持续迭代的 skill。

## 当前包含

- `wow-voidforge-roll-planner`
  - 用于《魔兽世界》`12.0.5` 及相近版本的 `晦暗虚空核心 / Voidforge bonus roll / 宏伟宝库 6 代币换币` 装备规划
  - 支持按 `职业专精`、`Hero talents`、`团本 / 大秘境 / 双修`、`主号 / 小号`、`当前装等`、`可达性`、`制造业`、`宝库候选`、`/simc` 输入完整度来做分析
  - 输出语言默认跟随用户输入语言：中文输入优先中文输出，英文输入优先英文输出；若显式指定语言，则以显式要求为准

## 仓库结构

```text
wow-skills/
├── LICENSE
├── README.md
├── README.zh-CN.md
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
- `agents/openai.yaml`：Codex 侧 UI 元数据
- `references/`：按需读取的参考资料

## 安装到 Codex

### 方式一：手动复制

把目标 skill 目录复制到：

- `$CODEX_HOME/skills/<skill-name>`
- 如果没有设置 `CODEX_HOME`，默认是 `~/.codex/skills/<skill-name>`

示例：

```powershell
Copy-Item -Recurse -Force `
  '.\skills\wow-voidforge-roll-planner' `
  "$HOME\\.codex\\skills\\wow-voidforge-roll-planner"
```

安装后建议重启 Codex。

### 方式二：通过 Codex 内置 skill-installer

```text
$skill-installer install https://github.com/Latias94/wow-skills/tree/main/skills/wow-voidforge-roll-planner
```

安装后同样建议重启 Codex。

## 安装到 Claude Code

Claude Code 常见技能目录：

- 个人级：`~/.claude/skills/<skill-name>/SKILL.md`
- 项目级：`.claude/skills/<skill-name>/SKILL.md`
- 插件级：`<plugin>/skills/<skill-name>/SKILL.md`

### 安装到个人目录

```powershell
New-Item -ItemType Directory -Force "$HOME\\.claude\\skills" | Out-Null
Copy-Item -Recurse -Force `
  '.\skills\wow-voidforge-roll-planner' `
  "$HOME\\.claude\\skills\\wow-voidforge-roll-planner"
```

### 安装到当前项目

把 skill 复制到：

```text
.claude/skills/wow-voidforge-roll-planner/
```

补充说明：

- 如果顶层技能目录已存在，新增或修改 skill 通常可在当前会话内生效
- 如果是第一次创建顶层技能目录，通常需要重启 Claude Code

## 如何使用

你可以直接描述目标，例如：

- `分析 12.0.5 元素萨 Stormbringer 在大秘境应该把 R 币投给哪个本`
- `如果我是小号，只打 10 层大秘境，宝库没有好装备，是拿装备还是拿 6 代币`
- `我贴一个 /simc，你帮我判断这周是先拿宝库还是继续追某个副本`
- `Please analyze whether my Arms Warrior should keep rolling Pit of Saron this week`

当前 `wow-voidforge-roll-planner` 已内置这些关键逻辑：

- Hero talents 分流
- 团本 / M+ / 双修差异
- 主号 / 小号差异
- 套装可转化位、制造位降权
- 大秘境 1 币 vs 团本 2 币权重
- 宏伟宝库 `6 代币换额外核心`
- `R 币去重 / knockout` 的同难度连续追击逻辑
- `/simc` 输入后的更精细比较

## 许可证

本仓库使用 [MIT License](LICENSE)。
