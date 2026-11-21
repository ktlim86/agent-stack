# agent-stack

Shared skills, agents and instructions for an AI agent team, usable in Cursor, Claude Code, OpenCode and GitHub Copilot through Agent Package Manager (APM). v1.0.0 ships five skills: the quant research pipeline, data science work check, deep review, the work ledger, and plain-English writing.

This repository is the version-controlled master copy. Edit here first, through a [pull request](CONTRIBUTING.md). After a release, sync the changed skills into the Grok Bot skill library from this repository. Do not edit a skill only in the Grok Bot library, or the two copies will drift.

## Skills in v1.0.0

| Skill | Version | What it is for |
|---|---|---|
| [data-science-work-check](.apm/skills/data-science-work-check/SKILL.md) | 1.0 | Scrutinize a quant data science result before it is reported or approved. |
| [quant-idea-pipeline](.apm/skills/quant-idea-pipeline/SKILL.md) | 1.0 | Move every quant trading idea through fixed gates, with a GitHub issue as the record. |
| [deep-review](.apm/skills/deep-review/SKILL.md) | 1.0 | Critique your own work or someone else's before it is handed off, approved or reported. |
| [simple-english](.apm/skills/simple-english/SKILL.md) | 1.0 | Explain technical work in everyday language a non-technical reader can follow. |
| [work-ledger](.apm/skills/work-ledger/SKILL.md) | 1.0 | Append every step of a task to one ledger file, tagged with a SHA-256 task ID. |

SHA-256 is a fixed-length fingerprint made from text, used here so every task has a stable ID.

## How to use

### 1. Install the command-line tool

APM (Agent Package Manager, Microsoft's tool for installing agent packages) is the command-line tool that copies these skills into each coding tool. You also need git, which APM uses to download packages. The install commands below are from the [APM repository](https://github.com/microsoft/apm#get-started).

macOS or Linux, if you already use Homebrew (a package installer):

```bash
brew install apm
```

No extra Homebrew tap is required. Later, update this install with `brew upgrade apm`.

Linux or macOS without Homebrew:

```bash
curl -sSL https://aka.ms/apm-unix | sh
```

Open a new terminal after this install. If the terminal still cannot find `apm`, use the path command the installer prints.

Windows (PowerShell):

```powershell
irm https://aka.ms/apm-windows | iex
```

Check that the tool runs:

```bash
apm --version
```

Other official options (pip, WinGet, and Scoop) are on the [installation page](https://microsoft.github.io/apm/getting-started/installation/).

### 2. Install this stack at a fixed release

From your project, install release v1.0.0. The `#v1.0.0` at the end selects that release, not a later one:

```bash
apm install ktlim86/agent-stack#v1.0.0 --target copilot,claude,cursor,opencode
```

`--target` names the tools to write files for: GitHub Copilot (`copilot`), Claude Code (`claude`), Cursor (`cursor`), and OpenCode (`opencode`). APM can detect a tool that is already set up: a `.claude/` directory or `CLAUDE.md` for Claude Code, a `.cursor/` directory or `.cursorrules` for Cursor, a `.opencode/` directory for OpenCode, and Copilot files under `.github/` for GitHub Copilot. If it finds no tool, the install stops, so pass `--target` on a new project. The exact signals are in [apm install](https://microsoft.github.io/apm/reference/cli/install/) and the [targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/).

Each skill also has its own `Version:` line inside its `SKILL.md`. Skills are not tagged one by one. You install the repository release.

To take a newer release, run the same command with the new tag, for example `apm install ktlim86/agent-stack#v1.1.0`. `apm outdated` reports when a newer tag exists. `apm update` refreshes packages to the latest matching release and asks before it changes anything. See [Update and refresh](https://microsoft.github.io/apm/consumer/update-and-refresh/).

### Cursor / Grok Bot plugin

Cursor can install this repository as a plugin. The plugin's `skills` path is `.apm/skills/`, so Agent Package Manager and Cursor read the same skill files.

In Cursor, open Customize in the sidebar. Import the repository with From GitHub Repository and paste `https://github.com/ktlim86/agent-stack`. That import requires `.cursor-plugin/marketplace.json`, which this repository has. Then install `agent-stack` and choose user scope (an install for you, not for one project). See [Installing skills from a repository](https://cursor.com/docs/skills#installing-skills-from-a-repository) and [Installing plugins](https://cursor.com/docs/plugins#installing-plugins).

A Grok Bot skill that comes from an installed plugin is recorded with source `plugin` ([OpenTelemetry wire reference](https://cursor.com/docs/enterprise/opentelemetry-export/wire)). The docs do not describe a separate Grok Bot install step. A team can import the same URL from Dashboard → Plugins & MCPs → Add Marketplace → Import from Repo ([Add a team marketplace](https://cursor.com/docs/plugins#add-a-team-marketplace)).

### 3. Where the skills go, and how each tool uses them

`apm install` copies each skill folder into the tool's skill folder. This package ships skills only, so there is no compile step. `apm compile` builds instruction files such as `AGENTS.md` and `CLAUDE.md` from `.apm/instructions/`, which this package does not include. See [apm compile](https://microsoft.github.io/apm/reference/cli/compile/) if you add those later.

In a project, APM writes the skill file here ([skills guide](https://microsoft.github.io/apm/producer/author-primitives/skills/), [targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/)):

| Tool | Skill file after install |
|---|---|
| GitHub Copilot | `.agents/skills/<name>/SKILL.md` |
| Claude Code | `.claude/skills/<name>/SKILL.md` |
| Cursor | `.agents/skills/<name>/SKILL.md` |
| OpenCode | `.agents/skills/<name>/SKILL.md` |

`<name>` is the skill name, such as `deep-review`. The tool reads that file when a task matches the skill. A user-wide install (`apm install -g`) uses different folders for some tools. See the [targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/) rather than guessing those paths.

### 4. Manual use, without APM

Copy `.apm/skills/<name>/SKILL.md` into the skill folder in the table above, and keep the `<name>/SKILL.md` layout. For example, deep-review for Cursor or GitHub Copilot goes in `.agents/skills/deep-review/SKILL.md`. For Claude Code it goes in `.claude/skills/deep-review/SKILL.md`.

Or paste the `SKILL.md` text into the chat as instructions.

### 5. Ask for a skill by name

Say the skill name in the request. Example: "use deep-review on this".

| Skill | What to ask it for |
|---|---|
| data-science-work-check | Scrutinize a quant data science result before it is reported or approved. |
| quant-idea-pipeline | Move a quant trading idea through fixed gates, and keep a GitHub issue as the record. |
| deep-review | Critique your own work, or someone else's, before it is handed off, approved, or reported. |
| simple-english | Explain technical work in everyday language a non-technical reader can follow. |
| work-ledger | Append every step of a task to one ledger file, tagged with a SHA-256 task ID. |

SHA-256 (a fixed-length fingerprint made from text) gives each task a stable ID.

### 6. Change a skill

Do not push edits straight to `main`. Follow [CONTRIBUTING.md](CONTRIBUTING.md). In short: create a branch, bump that skill's `Version:` line and its change log, open a pull request, get a `deep-review` verdict, wait for approval and merge, then cut a repository release and sync the Grok Bot library.
