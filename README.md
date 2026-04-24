# wow-skills

English | [简体中文](README.zh-CN.md)

A World of Warcraft skills repository for `Codex`, `Claude Code`, and other tools that support the `Agent Skills` layout.

This repository focuses on reusable WoW skills rather than one-off prompts. The goal is to package complex, recurring workflows into skills that can be improved over time.

## Current Skills

- `wow-voidforge-roll-planner`
  - Plans `Voidforge / bonus-roll / Great Vault token` decisions for WoW `12.0.5` and nearby versions
  - Supports `class/spec`, `Hero talents`, `raid / Mythic+ / hybrid` playstyles, `main / alt` characters, accessibility constraints, crafting, Great Vault choices, and `/simc`-driven refinement
  - Output language follows the user's input language by default: Chinese input leads to Chinese-first output, English input leads to English-first output, and explicit language requests take priority

## Repository Layout

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
        ├── evals/
        │   └── roll-planning-cases.md
        └── references/
            ├── analysis-template.md
            ├── decision-rules.md
            ├── input-granularity.md
            ├── player-profile-template.md
            ├── pool-table-schema.md
            ├── scoring-model.md
            ├── simc-intake.md
            └── source-weighting.md
```

Notes:

- `skills/` stores all skills in the repository
- `skills/<skill-name>/SKILL.md` is the entry file for each skill
- `agents/openai.yaml` contains Codex-facing UI metadata
- `evals/` contains behavior regression cases for maintainers
- `references/` holds supporting docs for pool tables, scoring, input granularity, and source weighting

## Install for Codex

### Option 1: Manual copy

Copy the skill directory to:

- `$CODEX_HOME/skills/<skill-name>`
- If `CODEX_HOME` is not set, the default is `~/.codex/skills/<skill-name>`

Example:

```powershell
Copy-Item -Recurse -Force `
  '.\skills\wow-voidforge-roll-planner' `
  "$HOME\\.codex\\skills\\wow-voidforge-roll-planner"
```

Restart Codex after installation.

### Option 2: Use Codex skill-installer

```text
$skill-installer install https://github.com/Latias94/wow-skills/tree/main/skills/wow-voidforge-roll-planner
```

Restart Codex after installation.

## Install for Claude Code

Common Claude Code skill locations:

- User scope: `~/.claude/skills/<skill-name>/SKILL.md`
- Project scope: `.claude/skills/<skill-name>/SKILL.md`
- Plugin scope: `<plugin>/skills/<skill-name>/SKILL.md`

### Install to user scope

```powershell
New-Item -ItemType Directory -Force "$HOME\\.claude\\skills" | Out-Null
Copy-Item -Recurse -Force `
  '.\skills\wow-voidforge-roll-planner' `
  "$HOME\\.claude\\skills\\wow-voidforge-roll-planner"
```

### Install to a project

Copy the skill into:

```text
.claude/skills/wow-voidforge-roll-planner/
```

Notes:

- If the top-level skills directory already exists, adding or updating a skill usually applies within the current session
- If this is the first time creating the top-level skills directory, restarting Claude Code is usually required

## Usage

You can ask for things like:

- `Analyze where an Elemental Shaman in 12.0.5 should spend Voidforge rolls for Mythic+`
- `If I am an alt only doing +10s and my Great Vault is weak, should I take gear or 6 tokens?`
- `Here is my /simc, help me decide whether to take the vault item or keep rolling one dungeon`

The current `wow-voidforge-roll-planner` already includes:

- Hero talent splits
- Raid / Mythic+ / hybrid weighting
- Main vs alt character logic
- Tier-slot and crafted-slot downgrades
- Mythic+ 1-core vs raid 2-core weighting
- Great Vault `6 tokens for 1 extra core`
- Bonus-roll `knockout` and same-difficulty continuation logic
- Structured main-pool `n / k / hit-rate / stop-condition` output
- More precise refinement when `/simc` is available

## License

This repository is released under the [MIT License](LICENSE).
