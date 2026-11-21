# Change log

## v1.2.0 (2026-11-21)

- Add the git skill at version 1.0. The package version in `apm.yml` is 1.2.0.
- The skill starts each feature on its own branch, checks work in on that branch, and finishes with a pull request or merge request. It does not check in to main.

| Skill | Version |
|---|---|
| git | 1.0 |
| data-science-work-check | 1.0 |
| quant-idea-pipeline | 1.0 |
| deep-review | 1.0 |
| simple-english | 1.0 |
| work-ledger | 1.0 |
| aws-cloud | 1.0 |
| azure-cloud | 1.0 |
| cloud-security | 1.0 |
| docker | 1.0 |
| gcp-cloud | 1.0 |
| github-actions | 1.0 |
| kubernetes | 1.0 |
| nextjs-frontend | 1.0 |
| owasp | 1.0 |
| react-frontend | 1.0 |
| vanilla-frontend | 1.0 |
| vue-frontend | 1.0 |

Earlier skills are unchanged. Agents are unchanged.

## v1.1.0 (2026-11-21)

- Add twelve skills, sixteen agents, and the orchestrator instructions from the universal agents and skills pack. The package version in `apm.yml` is 1.1.0.
- Leave out the example skill template, local Claude settings, and the bt_engine-only GitHub release scripts.

| Skill | Version |
|---|---|
| data-science-work-check | 1.0 |
| quant-idea-pipeline | 1.0 |
| deep-review | 1.0 |
| simple-english | 1.0 |
| work-ledger | 1.0 |
| aws-cloud | 1.0 |
| azure-cloud | 1.0 |
| cloud-security | 1.0 |
| docker | 1.0 |
| gcp-cloud | 1.0 |
| github-actions | 1.0 |
| kubernetes | 1.0 |
| nextjs-frontend | 1.0 |
| owasp | 1.0 |
| react-frontend | 1.0 |
| vanilla-frontend | 1.0 |
| vue-frontend | 1.0 |

Agents are not versioned one by one. They live in `.apm/agents/`: git-agent, github-project-sync, lead-devops-engineer, lead-frontend-engineer, lead-infrastructure-engineer, lead-reviewer, lead-software-engineer, lead-tester, release-manager, security-reviewer, solution-architect, sprint-planner, sprint-retrospective, sprint-reviewer, sre-agent, story-card-creator.

## v1.0.0 (2026-11-21)

First versioned release of the shared skill package. The repository is tagged as a whole; each skill also carries its own version.

- Add a Cursor plugin manifest and a marketplace manifest. The plugin points at `.apm/skills/`, so the skill files stay in one place. No skill version changed.

| Skill | Version |
|---|---|
| data-science-work-check | 1.0 |
| quant-idea-pipeline | 1.0 |
| deep-review | 1.0 |
| simple-english | 1.0 |
| work-ledger | 1.0 |
