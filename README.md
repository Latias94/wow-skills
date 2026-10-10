# wow-skills

English | [简体中文](README.zh-CN.md)

A World of Warcraft skills repository for `Codex`, `Claude Code`, and other tools that support the `Agent Skills` layout.

This repository focuses on reusable WoW skills rather than one-off prompts. The goal is to package complex, recurring workflows into skills that can be improved over time.

## Current Skills

- `wow-voidforge-roll-planner`
  - Plans weekly raid/Mythic+ bonus rolls using verified current-patch costs and reward pools
  - Optimizes attainable complete BiS candidates with reproducible raid/dungeon simulations before choosing crafting and roll routes
  - Recommends data-driven HTML reports with Chinese Wowhead tooltips, measured comparisons, clean SimC exports and boss watchlists; includes a [dated Windwalker case study](skills/wow-voidforge-roll-planner/references/case-shaseng-2026-10.md)
  - Maintains per-character weekly plans, confirmed roll results, and Great Vault offers/claims in workspace `records/`; includes a Celestial Conduit Windwalker pilot
  - Supports `class/spec`, `Hero talents`, `raid / Mythic+ / hybrid` playstyles, `main / alt` characters, accessibility constraints, crafting, Great Vault choices, and `/simc`-driven refinement
  - Output language follows the user's input language by default: Chinese input leads to Chinese-first output, English input leads to English-first output, and explicit language requests take priority
- `wow-pve-spec-coach`
  - Provides a general PvE spec coach for any WoW class/spec, covering rotations, talents, mechanics reasoning, raid/Mythic+ play, WCL review, SimC/Raidbots interpretation, and mentor-style explanations
  - Explains why a rotation or talent setup works by connecting guides to the player's current talents, skills, passives, resources, cooldown windows, and combat context
  - Uses a default roleplay mentor persona, `Yuzu`, to make dense guide content easier to absorb while keeping data, sources, and uncertainty labels strict
- `wow-wcl-performance-analyst`
  - Analyzes online Warcraft Logs reports or local exports, selects comparable high-performing references, and compares timelines, rotations, cooldown alignment, target selection, resources, gear, and survival
  - Separates kill and progression analysis, then turns repeated multi-log patterns into evidence-backed training cards
  - Includes a dependency-free local JSON summarizer for large event exports

## Repository Layout

```text
wow-skills/
├── LICENSE
├── README.md
├── README.zh-CN.md
└── skills/
    ├── wow-voidforge-roll-planner/
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
    ├── wow-pve-spec-coach/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── answer-patterns.md
            ├── cross-skill-routing.md
            ├── log-review-rubric.md
            ├── localization-rules.md
            ├── mechanics-reasoning.md
            ├── persona-cards.md
            ├── player-intake.md
            └── source-weighting.md
    └── wow-wcl-performance-analyst/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── evals/
        │   └── wcl-performance-cases.md
        ├── references/
        │   ├── benchmark-selection.md
        │   ├── experience-capture.md
        │   ├── external-prior-art.md
        │   ├── input-contract.md
        │   ├── metric-rubric.md
        │   ├── online-fetch.md
        │   └── report-template.md
        └── scripts/
            └── summarize_wcl.py
```

Notes:

- `skills/` stores all skills in the repository
- `skills/<skill-name>/SKILL.md` is the entry file for each skill
- `agents/openai.yaml` contains Codex-facing UI metadata
- `evals/` contains behavior regression cases for maintainers
- `references/` holds supporting docs for pool tables, scoring, input granularity, source weighting, coaching patterns, mechanics reasoning, and persona cards
- `records/` stores player history separately from installable skills; `records/cn-barrens-shaseng/` is the first weekly planning pilot

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

Replace `wow-voidforge-roll-planner` with `wow-pve-spec-coach` or `wow-wcl-performance-analyst` to install the corresponding skill.

Restart Codex after installation.

### Option 2: Use Codex skill-installer

```text
$skill-installer install https://github.com/Latias94/wow-skills/tree/main/skills/wow-voidforge-roll-planner
$skill-installer install https://github.com/Latias94/wow-skills/tree/main/skills/wow-pve-spec-coach
$skill-installer install https://github.com/Latias94/wow-skills/tree/main/skills/wow-wcl-performance-analyst
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

Replace the skill name in both paths with `wow-pve-spec-coach` or `wow-wcl-performance-analyst` to install the corresponding skill.

### Install to a project

Copy the skill into:

```text
.claude/skills/wow-voidforge-roll-planner/
.claude/skills/wow-pve-spec-coach/
```

Notes:

- If the top-level skills directory already exists, adding or updating a skill usually applies within the current session
- If this is the first time creating the top-level skills directory, restarting Claude Code is usually required

## Usage

You can ask for things like:

- `Analyze where an Elemental Shaman in 12.0.5 should spend Voidforge rolls for Mythic+`
- `If I am an alt only doing +10s and my Great Vault is weak, should I take gear or 6 tokens?`
- `Here is my /simc, help me decide whether to take the vault item or keep rolling one dungeon`
- `Use Yuzu to teach me how to play Assassination Rogue in Mythic+ and explain why the rotation works`
- `Review my WCL as a Frost Mage and tell me which cooldown windows I am missing`
- `I copied a Wowhead talent build for Retribution Paladin; explain what each key node changes in my rotation`
- `Give me a WCL link, compare my burst, targeting, and rotation with comparable top players, and give me the next training goals`
- `I have WCL events.json and a damage table; find the gap between me and another player and turn it into reusable experience cards`

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

The `wow-pve-spec-coach` includes:

- General PvE coaching across all classes/specs
- Rotation explanations that connect guide priority lists to talents, skills, passives, resources, and cooldown windows
- Mythic+ and raid coaching with practical survival, utility, and encounter-context advice
- WCL review patterns for uptime, cooldown count, resource waste, target selection, deaths, and utility
- Chinese-first terminology and localization rules for translating English guide terms into readable Chinese client terminology
- Source weighting across Wowhead, Icy Veins, Method, Archon, Warcraft Logs, Mythicstats, Bloodmallet, SimulationCraft, and Raidbots
- Mentor persona cards, defaulting to `Yuzu`, with roleplay kept separate from factual accuracy

The `wow-wcl-performance-analyst` includes:

- Input contracts and graceful fallback for online reports and local JSON exports
- Kill/progression mode separation, phase alignment, and cascade-death filtering
- Same-fight, comparable-ilvl, and multi-sample median benchmark selection
- A shared rubric for cast density, cooldowns, buff coverage, target splits, resources, and gear context
- Evidence chains from log fact to mechanism, training action, and verification metric
- Reusable boss/spec experience cards and documented adaptation boundaries from `jjholyfield/wcl-analyzer`

## License

This repository is released under the [MIT License](LICENSE).
