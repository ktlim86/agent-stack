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

## Install with Agent Package Manager

Agent Package Manager (APM) is Microsoft's tool for sharing agent skills. To install this release:

```bash
apm install ktlim86/agent-stack#v1.0.0
```

The `#v1.0.0` pin installs this repository release. Each skill also has its own `Version:` line and a change log inside its `SKILL.md`. Skills are not tagged one by one.

## How to change a skill

Every edit goes through a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md). In short: branch from `main`, bump the skill's `Version:` and change log, open a pull request, get a `deep-review` verdict, wait for the user to approve and merge, then cut a repository release and sync the Grok Bot library.
