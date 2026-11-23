# agent-stack

Shared skills, agents and instructions for an AI agent team, usable in Cursor, Claude Code, OpenCode and GitHub Copilot through Agent Package Manager (APM). v1.0.0 shipped five skills. v1.1.0 adds twelve engineering skills, sixteen role agents, and one orchestrator instruction file. v1.2.0 adds the git, hand-off, and hand-back skills.

This repository is the version-controlled master copy. Edit here first, through a [pull request](CONTRIBUTING.md). After a release, sync the changed skills into the Grok Bot skill library from this repository. Do not edit a skill only in the Grok Bot library, or the two copies will drift.

## Skills in v1.2.1

Skills live in `.apm/skills/<name>/`. v1.2.1 enhanced the hand-off, and hand-back skills. Skills from v1.0.0 and v1.1.0 are unchanged. This branch also adds `delegate-coding-cursor` 1.0 and updates `hand-off` to 1.2; those will be included in the next repository release.

| Skill | Version | What it is for |
|---|---|---|
| [data-science-work-check](.apm/skills/data-science-work-check/SKILL.md) | 1.0 | Scrutinize a quant data science result before it is reported or approved. |
| [quant-idea-pipeline](.apm/skills/quant-idea-pipeline/SKILL.md) | 1.0 | Move every quant trading idea through fixed gates, with a GitHub issue as the record. |
| [deep-review](.apm/skills/deep-review/SKILL.md) | 1.0 | Critique your own work or someone else's before it is handed off, approved or reported. |
| [simple-english](.apm/skills/simple-english/SKILL.md) | 1.0 | Explain technical work in everyday language a non-technical reader can follow. |
| [work-ledger](.apm/skills/work-ledger/SKILL.md) | 1.0 | Append every step of a task to one ledger file, tagged with a SHA-256 task ID. |
| [git](.apm/skills/git/SKILL.md) | 1.0 | Start each feature on its own branch, save the work there, and open a pull request or merge request instead of checking in to main. |
| [hand-off](.apm/skills/hand-off/SKILL.md) | 1.2 | Give an existing task to another agent, keep the same task ID, and record it in the work ledger. |
| [hand-back](.apm/skills/hand-back/SKILL.md) | 1.1 | Return a handed-off task to the agent that sent it, using the same task ID. |
| [delegate-coding-cursor](.apm/skills/delegate-coding-cursor/SKILL.md) | 1.0 | Hand coding work to a Cursor coding agent (cloud or in a local Docker container; the user picks each job) under a set engineering standard, then review the pull request. |
| [aws-cloud](.apm/skills/aws-cloud/SKILL.md) | 1.0 | AWS setup notes for the infrastructure, devops, and SRE agents. |
| [azure-cloud](.apm/skills/azure-cloud/SKILL.md) | 1.0 | Azure setup notes for the infrastructure, devops, and SRE agents. |
| [gcp-cloud](.apm/skills/gcp-cloud/SKILL.md) | 1.0 | Google Cloud setup notes for the infrastructure, devops, and SRE agents. |
| [cloud-security](.apm/skills/cloud-security/SKILL.md) | 1.0 | Cloud security checklist: least privilege, secrets, network, encryption, and logging. |
| [docker](.apm/skills/docker/SKILL.md) | 1.0 | Dockerfile and image practices for the devops agent. |
| [kubernetes](.apm/skills/kubernetes/SKILL.md) | 1.0 | Kubernetes manifest patterns for the devops agent. |
| [github-actions](.apm/skills/github-actions/SKILL.md) | 1.0 | GitHub Actions workflow patterns for the devops agent. |
| [owasp](.apm/skills/owasp/SKILL.md) | 1.0 | OWASP Top 10 (2021) checklist for the security reviewer. |
| [react-frontend](.apm/skills/react-frontend/SKILL.md) | 1.0 | React UI patterns for the frontend agent. |
| [nextjs-frontend](.apm/skills/nextjs-frontend/SKILL.md) | 1.0 | Next.js App Router patterns for the frontend agent. |
| [vue-frontend](.apm/skills/vue-frontend/SKILL.md) | 1.0 | Vue 3 patterns for the frontend agent. |
| [vanilla-frontend](.apm/skills/vanilla-frontend/SKILL.md) | 1.0 | HTML, CSS, and plain JavaScript patterns for the frontend agent. |

SHA-256 is a fixed-length fingerprint made from text, used here so every task has a stable ID. OWASP is a published list of common web security failures.

## Agents in v1.1.0

Agents live in `.apm/agents/<name>.agent.md`. APM requires the `.agent.md` ending. Cursor's plugin manifest points at the same folder.

| Agent | What it is for |
|---|---|
| [git-agent](.apm/agents/git-agent.agent.md) | The only agent that runs git. One branch and worktree per piece of work; a human merges. |
| [github-project-sync](.apm/agents/github-project-sync.agent.md) | Syncs local product notes to a GitHub Project. The only agent that runs `gh issue` and `gh project` commands. |
| [story-card-creator](.apm/agents/story-card-creator.agent.md) | Splits a requirements document into story cards. |
| [solution-architect](.apm/agents/solution-architect.agent.md) | Reviews story cards for design risk before implementation starts. |
| [sprint-planner](.apm/agents/sprint-planner.agent.md) | Groups approved stories into a sprint. |
| [lead-software-engineer](.apm/agents/lead-software-engineer.agent.md) | Implements an approved backend or general story. |
| [lead-frontend-engineer](.apm/agents/lead-frontend-engineer.agent.md) | Implements an approved frontend story. |
| [lead-tester](.apm/agents/lead-tester.agent.md) | Writes and runs tests for a story that is in testing. |
| [lead-reviewer](.apm/agents/lead-reviewer.agent.md) | Reviews a story against its acceptance criteria after tests pass. |
| [sprint-reviewer](.apm/agents/sprint-reviewer.agent.md) | Reviews a sprint when every story is done, or when the end date arrives. |
| [sprint-retrospective](.apm/agents/sprint-retrospective.agent.md) | Writes the sprint reflection after the sprint closes. |
| [lead-infrastructure-engineer](.apm/agents/lead-infrastructure-engineer.agent.md) | Writes infrastructure changes and waits for approval before anything is deployed. |
| [lead-devops-engineer](.apm/agents/lead-devops-engineer.agent.md) | Builds, deploys to staging, writes the go-live checklist, and promotes to production after approval. |
| [security-reviewer](.apm/agents/security-reviewer.agent.md) | Reviews code and infrastructure after staging, and waits for approval before production. |
| [release-manager](.apm/agents/release-manager.agent.md) | Updates release notes and version metadata, then stops for review. Does not run git. |
| [sre-agent](.apm/agents/sre-agent.agent.md) | Sets up production monitoring and writes a runbook after an infrastructure sprint. |

## Instructions

The orchestrator instructions live in [`.apm/instructions/agents.instructions.md`](.apm/instructions/agents.instructions.md). `apm install` copies that file into each tool's instruction folder. `apm compile` also merges it into a root file such as `CLAUDE.md`, `AGENTS.md`, or `.github/copilot-instructions.md`. Do not commit a generated root file in this repository. It would become this repository's own instructions.

The Cursor plugin manifest also points `rules` at that folder, so the file is part of a plugin install. `apm install` is what turns `applyTo: "**"` into a Cursor rule under `.cursor/rules/`. A plugin-only install may list the file without that conversion. See the [targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/).

## Not included

- `.claude/` in the source pack is local Claude settings.
- `github-release-tooling` is a set of scripts written for one project (`bt_engine`), with hardcoded paths and package names. It is not a shared skill. Four agents still mention it and stop if it is not installed locally.

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

From your project, install release v1.2.0 after that tag is cut. The `#v1.2.0` at the end selects that release, not a later one. Until the tag exists, v1.0.0 is the last tagged release. It does not include the agents, or the git, hand-off, and hand-back skills.

```bash
apm install ktlim86/agent-stack#v1.2.0 --target copilot,claude,cursor,opencode
```

`--target` names the tools to write files for: GitHub Copilot (`copilot`), Claude Code (`claude`), Cursor (`cursor`), and OpenCode (`opencode`). APM can detect a tool that is already set up: a `.claude/` directory or `CLAUDE.md` for Claude Code, a `.cursor/` directory or `.cursorrules` for Cursor, a `.opencode/` directory for OpenCode, and Copilot files under `.github/` for GitHub Copilot. If it finds no tool, the install stops, so pass `--target` on a new project. The exact signals are in [apm install](https://microsoft.github.io/apm/reference/cli/install/) and the [targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/).

Each skill also has its own `Version:` line inside its `SKILL.md`. Skills are not tagged one by one. You install the repository release.

To take a newer release, run the same command with the new tag, for example `apm install ktlim86/agent-stack#v1.3.0`. `apm outdated` reports when a newer tag exists. `apm update` refreshes packages to the latest matching release and asks before it changes anything. See [Update and refresh](https://microsoft.github.io/apm/consumer/update-and-refresh/).

### Cursor / Grok Bot plugin

Cursor can install this repository as a plugin. The plugin manifest points `skills` at `.apm/skills/`, `agents` at `.apm/agents/`, and `rules` at `.apm/instructions/`. Agent Package Manager reads those same folders from `.apm/` without using the plugin manifest.

In Cursor, open Customize in the sidebar. Import the repository with From GitHub Repository and paste `https://github.com/ktlim86/agent-stack`. That import requires `.cursor-plugin/marketplace.json`, which this repository has. Then install `agent-stack` and choose user scope (an install for you, not for one project). See [Installing skills from a repository](https://cursor.com/docs/skills#installing-skills-from-a-repository) and [Installing plugins](https://cursor.com/docs/plugins#installing-plugins).

A Grok Bot skill that comes from an installed plugin is recorded with source `plugin` ([OpenTelemetry wire reference](https://cursor.com/docs/enterprise/opentelemetry-export/wire)). The docs do not describe a separate Grok Bot install step. A team can import the same URL from Dashboard → Plugins & MCPs → Add Marketplace → Import from Repo ([Add a team marketplace](https://cursor.com/docs/plugins#add-a-team-marketplace)).

### 3. Where the skills go, and how each tool uses them

`apm install` copies each skill folder into the tool's skill folder, and each agent file into the tool's agent folder. Instructions are copied into the tool's instruction folder. `apm compile` merges the same instructions into a root file where that tool reads one. See [apm compile](https://microsoft.github.io/apm/reference/cli/compile/) and the [targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/).

In a project, APM writes the skill file here ([skills guide](https://microsoft.github.io/apm/producer/author-primitives/skills/), [targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/)):

| Tool | Skill file after install | Agent file after install |
|---|---|---|
| GitHub Copilot | `.agents/skills/<name>/SKILL.md` | `.github/agents/<name>.agent.md` |
| Claude Code | `.claude/skills/<name>/SKILL.md` | `.claude/agents/<name>.md` |
| Cursor | `.agents/skills/<name>/SKILL.md` | `.cursor/agents/<name>.md` |
| OpenCode | `.agents/skills/<name>/SKILL.md` | `.opencode/agents/<name>.md` |

`<name>` is the skill or agent name, such as `deep-review` or `git-agent`. The tool reads a skill when a task matches it. A user-wide install (`apm install -g`) uses different folders for some tools. See the [targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/) rather than guessing those paths.

### 4. Manual use, without APM

Copy `.apm/skills/<name>/SKILL.md` into the skill folder in the table above, and keep the `<name>/SKILL.md` layout. For example, deep-review for Cursor or GitHub Copilot goes in `.agents/skills/deep-review/SKILL.md`. For Claude Code it goes in `.claude/skills/deep-review/SKILL.md`. Copy an agent file into that tool's agent folder in the same table.

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
| git | Start each feature on its own branch, save the work there, and open a pull request or merge request instead of checking in to main. |
| hand-off | Give an existing task to another agent, keep the same task ID, and record it in the work ledger. |
| hand-back | Return a handed-off task to the agent that sent it, using the same task ID. |
| delegate-coding-cursor | Hand coding work to a Cursor coding agent (cloud or in a local Docker container; the user picks each job) under a set engineering standard, then review the pull request. |
| aws-cloud | Look up AWS setup notes before writing infrastructure or a deploy. |
| azure-cloud | Look up Azure setup notes before writing infrastructure or a deploy. |
| gcp-cloud | Look up Google Cloud setup notes before writing infrastructure or a deploy. |
| cloud-security | Check least privilege, secrets, network, encryption, and logging. |
| docker | Check Dockerfile and image practices. |
| kubernetes | Check Kubernetes manifest patterns. |
| github-actions | Check GitHub Actions workflow patterns. |
| owasp | Review code against the OWASP Top 10 (2021) checklist. |
| react-frontend | Follow React UI patterns for a frontend story. |
| nextjs-frontend | Follow Next.js App Router patterns for a frontend story. |
| vue-frontend | Follow Vue 3 patterns for a frontend story. |
| vanilla-frontend | Follow HTML, CSS, and plain JavaScript patterns for a frontend story. |
| git-agent | Run git for one branch and worktree. Do not merge; a human merges. |
| github-project-sync | Sync product notes to a GitHub Project. |
| story-card-creator | Split a requirements document into story cards. |
| solution-architect | Review story cards for design risk before implementation. |
| sprint-planner | Group approved stories into a sprint. |
| lead-software-engineer | Implement an approved backend or general story. |
| lead-frontend-engineer | Implement an approved frontend story. |
| lead-tester | Write and run tests for a story that is in testing. |
| lead-reviewer | Review a story against its acceptance criteria after tests pass. |
| sprint-reviewer | Review a sprint when every story is done, or when the end date arrives. |
| sprint-retrospective | Write the sprint reflection after the sprint closes. |
| lead-infrastructure-engineer | Write infrastructure changes and wait for approval before deploy. |
| lead-devops-engineer | Build, deploy to staging, and promote to production only after approval. |
| security-reviewer | Review code and infrastructure after staging, before production. |
| release-manager | Update release notes and version metadata, then stop for review. |
| sre-agent | Set up production monitoring and write a runbook. |

SHA-256 (a fixed-length fingerprint made from text) gives each task a stable ID. OWASP is a published list of common web security failures.

### 6. Change a skill

Do not push edits straight to `main`. Follow [CONTRIBUTING.md](CONTRIBUTING.md). In short: create a branch, bump that skill's `Version:` line and its change log, open a pull request, get a `deep-review` verdict, wait for approval and merge, then cut a repository release and sync the Grok Bot library.
