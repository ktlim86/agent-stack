---
description: Automated Development Orchestrator — single source of truth for all coding agents in this workspace. Compiled by `apm compile` into each agent's native instructions file (CLAUDE.md, AGENTS.md, .github/copilot-instructions.md, …).
applyTo: "**"
---

# Automated Development Orchestrator

This repository is a self-contained software project. The coding agent operates
as an orchestrator here, driving a streamlined software development lifecycle
using specialised agent roles. All paths use `[PROJECT_FOLDER]` as the parent
folder — substitute the actual repo root (e.g. `bt_engine`) when reading this
file. This keeps the instructions reusable across repositories.

> **Edit only this source** (`.apm/instructions/agents.instructions.md`) and run
> `apm compile` to propagate changes to every coding agent's native format
> (CLAUDE.md, AGENTS.md, `.github/copilot-instructions.md`, …).

---

## Project Bootstrap (Greenfield vs Brownfield)

Before any development begins, the orchestrator must determine whether this is a
**greenfield** (brand-new, empty) or **brownfield** (existing codebase) project,
and ensure the correct instructions file exists for the coding agent in use.

### Step 1 — Detect greenfield vs brownfield

- **Greenfield**: the repository has no application source code yet (only
  scaffolding/config such as `apm.yml`, `.apm/`, `.git/`, README). Treat as
  greenfield when there is no package manifest (`pyproject.toml`,
  `package.json`, `go.mod`, …) and no source tree.
- **Brownfield**: the repository already contains application source code and/or
  a package manifest.

### Step 2 — Ensure the agent instructions file exists

Determine the target instructions filename from the **coding agent in use**:

| Coding agent | Instruction file after `apm install` | Root file from `apm compile` |
|--------------|--------------------------------------|------------------------------|
| Claude Code | `.claude/rules/` | `CLAUDE.md` |
| Cursor | `.cursor/rules/` (`.mdc`) | not required for project scope |
| GitHub Copilot | `.github/instructions/` | `.github/copilot-instructions.md` |
| OpenCode / Codex / generic | not installed as a separate file | `AGENTS.md` |

Then apply this rule:

1. **Greenfield** → there is no existing agent instructions file. Compile this
   source into the target file(s) for the agent(s) in use:
   ```bash
   apm compile --target <claude|opencode|copilot|cursor|…>
   ```
   This writes `CLAUDE.md` / `AGENTS.md` / etc. from this single source. These
   generated files become the agent's operating instructions.

2. **Brownfield WITH an existing `AGENTS.md` / `CLAUDE.md`** → **use the existing
   file as-is.** Do not overwrite it. The project already has its conventions;
   respect them. If this pack's guidance must be added, append non-destructively
   and confirm with the user first.

3. **Brownfield WITHOUT an existing `AGENTS.md` / `CLAUDE.md`** → compile this
   source into the target file for the coding agent in use (same command as
   greenfield). This seeds the missing instructions without disturbing existing
   code.

> Rule of thumb: **generate the instructions file only when one does not already
> exist.** An existing hand-authored `AGENTS.md`/`CLAUDE.md` always wins.

---

## Workspace Structure

```
[PROJECT_FOLDER]/               ← repo root (contains .git)
├── CLAUDE.md / AGENTS.md       ← agent instructions (generated or existing)
├── .apm/                       ← APM source primitives (instructions, agents, skills)
├── templates/                  ← document templates
├── ENV.MD                      ← language, IaaS tool, and versions for this project
├── RELEASES_NOTES.MD           ← release notes (Changed / Deprecated per version)
├── product/                    ← LOCAL ONLY, gitignored, never committed
│   ├── requirements/           ← PRDs (prd-NNNN.md)
│   ├── stories/                ← story cards (story_XXXX.md)
│   ├── tests/                  ← test documentation (test_story_XXXX.md)
│   ├── architecture/           ← architecture reviews (ARCH-NNNN.md)
│   ├── infra/                  ← infrastructure change records (INFRA-NNNN.md)      [optional]
│   ├── security/               ← security review sign-offs (SEC-NNNN.md)            [optional]
│   ├── deployments/            ← deployment records (DEPLOY-NNNN.md)                [optional]
│   ├── go-live/                ← production readiness checklists (GOLIVE-NNNN.md)   [optional]
│   └── runbooks/               ← SRE runbooks (RUNBOOK-NNNN.md)                     [optional]
├── <package code>              ← e.g. bt_engine/, tests/, pyproject.toml, README.md
└── .gitignore                  ← includes product/
```

**One repo per project:**
- `[PROJECT_FOLDER]/` — source code, committed and pushed to its own GitHub or
  GitLab repository using the **branch-per-PRD** workflow (see `## Git Workflow`).
  Product artefacts are developed locally in `product/` and **never committed**;
  on milestone/status changes they are uploaded to the project board as issues
  via the `github-project-sync` agent (see `## GitHub Projects Integration`).

---

## Git Workflow (branch-per-PRD, worktree-isolated, MR-reviewed)

This project does **NOT** commit directly to the trunk. Every change reaches
`main` only through a reviewed, squash-merged Merge/Pull Request. Multiple PRDs
run concurrently, each in its own **git worktree**, so agents never block one
another. All git operations are performed by the dedicated **git-agent** — other
agents write files and update story cards and never run git commands.

### Core principles

- **Never push to `main` directly.** `main` is protected; integration is via
  MR/PR only.
- **One PRD → one branch → one worktree → one squash commit on `main`.** This
  keeps `main` a **linear history** (no merge commits) in chronological
  merge order.
- **Integrate upstream by merging, never rebasing a pushed branch** (the Golden
  Rule of Rebasing — never rewrite history others may have). Never force-push.
- **A human reviews and merges.** The agent opens the MR/PR and stops.

### Platform auto-detection

Detect the forge from `git remote get-url origin`: `github.com` → use `gh`;
`gitlab*` → use `glab`. GitHub calls it a **Pull Request (PR)**; GitLab a
**Merge Request (MR)**. "MR/PR" below means either.

### Step-by-step lifecycle

**1. Sync local `main` (fetch → compare → merge).**

- **First time only** (fresh clone, no local history): `git pull origin main`.
- **Every subsequent time**: fetch and compare before merging — never blind:
  ```bash
  git fetch origin
  git rev-list --left-right --count main...origin/main   # "<local-ahead> <remote-ahead>"
  git log --oneline main..origin/main                     # what's new on remote
  ```
  Then fast-forward local `main`:
  ```bash
  git checkout main && git merge --ff-only origin/main
  ```
  (`--ff-only` keeps local `main` a clean mirror of remote; if it refuses,
  local `main` has diverged — stop and surface it, never force.)

**2. Create a feature branch in an isolated worktree (one per PRD).**

Always use a worktree so concurrent PRDs don't collide:
```bash
git worktree add ../worktrees/prd-XXXX -b prd/prd-XXXX-<slug> origin/main
```
Report the worktree path so the SE/tester/reviewer agents work there. Develop,
commit per story (`feat(story-XXXX): <title>`), and push the branch.

**3. On completion (development done, tested, story card `completed`):**

Re-check for upstream changes before opening the MR/PR — another PRD may have
merged while this one was in flight:
```bash
cd ../worktrees/prd-XXXX
git fetch origin
git log --oneline HEAD..origin/main                      # what landed on main meanwhile
git merge origin/main                                     # merge main IN (never rebase); resolve locally
```
Resolve any conflicts in the worktree. If a conflict is ambiguous, **stop and
surface it** — never guess. Then **re-run the unit tests** to confirm the merge
didn't break anything, and push:
```bash
git push origin prd/prd-XXXX-<slug>                       # plain push, never --force
```

**4. Open the MR/PR for human review (squash merge).**
```bash
# GitHub
gh pr create --base main --head prd/prd-XXXX-<slug> --title "prd-XXXX: <title>" --body-file <body>
# GitLab
glab mr create --source-branch prd/prd-XXXX-<slug> --target-branch main \
  --squash-before-merge --remove-source-branch --title "prd-XXXX: <title>" --description-file <body>
```
Report the MR/PR URL and **stop**. A human reviews and squash-merges.

**5. After the human merges — clean up the worktree and branch:**
```bash
git checkout main && git pull origin main
git worktree remove ../worktrees/prd-XXXX
git branch -D prd/prd-XXXX-<slug>
git push origin --delete prd/prd-XXXX-<slug>   # skip if the forge auto-deleted it
```

### Commit Message Conventions

| Type | Format | Example |
|------|--------|---------|
| Feature | `feat(story-XXXX): <title>` | `feat(story-0063): add log file name option` |
| Bug fix | `fix(story-XXXX): <title>` | `fix(story-0061): correct off-by-one in pagination` |
| Release | `release(prd-XXXX): vX.Y.Z` | `release(prd-0007): v1.7.0` |
| Docs | `docs(prd-XXXX): <desc>` | `docs(prd-0007): update README usage` |
| Maintenance | `chore: <desc>` | `chore: bump version to 0.0.4` |

### Repo protection (one-time setup, keeps `main` clean)

Configure the forge so `main` enforces this workflow:
- **GitHub**: require PR + ≥1 approval + passing checks + up-to-date branch;
  **require linear history**; block force-push & deletion; **squash merge only**
  (`allow_merge_commit=false`, `allow_rebase_merge=false`); auto-delete head
  branch on merge.
- **GitLab**: protect `main` (no direct push, MR only); require ≥1 approval +
  passing pipeline; merge method **Fast-forward** (linear) + **squash on merge**;
  delete source branch by default.

---

## ENV.MD Schema

Every `ENV.MD` lives in `[PROJECT_FOLDER]/` and documents the project's runtime environment. It must exist before any development begins.

```yaml
---
project: <project-name>
---
```

Fixed sections in this order:

- `## Language` — programming language(s) and version(s) used in the codebase
- `## Infrastructure as Code` — IaaS tooling used to provision infrastructure; set to `none` if not applicable

`## Language` format:

```markdown
## Language

| Property | Value |
|----------|-------|
| Name     | Python |
| Version  | 3.13   |
```

`## Infrastructure as Code` format:

```markdown
## Infrastructure as Code

| Property | Value     |
|----------|-----------|
| Tool     | Terraform |
| Version  | 1.8.0     |
```

Use `none` / `—` for Tool and Version when no IaaS tooling is used.

`## Python Environment` format:

```markdown
## Python Environment

| Property | Value         |
|----------|---------------|
| Manager  | conda         |
| Name     | app_py313     |
```

Use `Manager: conda` and `Name: <env-name>` on Windows. Use `Manager: venv` and `Name: .venv` on Linux/macOS. **This section is required only for projects with a Python codebase.** For other languages, declare the equivalent toolchain in a `## Toolchain` section instead (see below) — agents read the environment/toolchain from `ENV.MD`, never from the instructions file.

`## Toolchain` format (any language; use instead of / alongside `## Python Environment`):

```markdown
## Toolchain

| Property     | Value           |
|--------------|-----------------|
| Build/Run    | npm / go / cargo / dotnet / terraform |
| Version      | 20 / 1.22 / 1.78 / 8 / 1.8.0          |
| Test command | npm test / go test ./... / terraform test |
| Lint command | eslint . / golangci-lint run / terraform validate |
| Manifest     | package.json / go.mod / Cargo.toml / *.tf |
```

Agents must read `## Language`, `## Infrastructure as Code`, and `## Toolchain` (or `## Python Environment`) to learn how to install dependencies, run, test, and lint — never assume a language or tool.

`## Cloud Provider(s)` format:

```markdown
## Cloud Provider(s)

| Provider | Role      |
|----------|-----------|
| AWS      | Primary   |
| Azure    | Secondary |
```

Use one row per cloud provider. Role values: `Primary`, `Secondary`. Omit this section if the project deploys to no cloud (e.g. local-only or on-prem). Supported values: `AWS`, `Azure`, `GCP`.

`## Frontend` format:

```markdown
## Frontend

| Property  | Value |
|-----------|-------|
| Framework | React |
| Version   | 18    |
```

Omit this section entirely if the project has no frontend component. Supported frameworks: `React`, `Vue`, `Next.js`, `Vanilla`.

---

## MVP Principle

**Every feature built in this pipeline must be a Minimal Viable Product (MVP).** All agents must keep this in mind at every step of the workflow.

- Build the **simplest implementation** that satisfies the Acceptance Criteria. Nothing more.
- Do not add features, abstractions, configuration options, or generalisations that are not explicitly required by the story card.
- Do not anticipate future requirements — implement only what is asked for today.
- If a simpler approach meets all acceptance criteria equally well, always choose the simpler one.
- Three similar lines of code are preferable to a premature abstraction.
- Tests should verify behaviour, not implementation details. Keep test code as simple as the production code.

---

## Story Card Schema

Every `story_XXXX.md` lives in `[PROJECT_FOLDER]/product/stories/` and must begin with this exact frontmatter:

```yaml
---
id: story_XXXX
project: <project-name>
prd_ref: [PROJECT_FOLDER]/product/requirements/prd-NNNN.md
priority: N
story_points: N
title: Short feature title
type: code
layer: backend | frontend | fullstack
complexity: low | medium | high
status: approved | in_progress | testing | pending_review | completed
gh_issue_url: null
gh_project_item_id: null
timestamps:
  created: <ISO8601>
  approved: <ISO8601>
  in_progress: null
  testing: null
  pending_review: null
  completed: null
iteration: 1
hash_id: null
---
```

**Integrity hash (`hash_id`):** a SHA-256 digest of the card used to detect
tampering or accidental edits. It is computed over the card content **excluding
the `hash_id` line itself** (a file cannot hash itself), so the value is
reproducible. Compute and store it from the repo root:

```bash
# Store (strip the hash_id line, hash the rest, write the digest back)
grep -v '^hash_id:' [PROJECT_FOLDER]/product/stories/story_XXXX.md | shasum -a 256 | awk '{print $1}'
# → write the 64-char digest into `hash_id:` (no "sha256:" prefix)

# Verify
stored=$(grep '^hash_id:' story_XXXX.md | awk '{print $2}')
actual=$(grep -v '^hash_id:' story_XXXX.md | shasum -a 256 | awk '{print $1}')
[ "$stored" = "$actual" ] && echo "OK" || echo "MISMATCH"
```

**Rule:** every agent that edits a story card (status change, timestamp,
iteration, acceptance criteria, review notes, …) must **recompute `hash_id` as
the final write** so it always matches the current content. `sha256sum` may
substitute for `shasum -a 256`.

**Story point rules:**
- Use the Fibonacci scale: `1 | 2 | 3 | 5 | 8 | 13`.
- **If a story would require more than 13 points it must be split** into multiple child cards each estimated at ≤ 8 points. The parent card is discarded; child cards replace it.
- Story points represent effort and complexity, not time. Points > 8 are a signal the scope is too broad for an MVP iteration.

Fixed sections in this order:

- `## Description` — what to build
- `## Acceptance Criteria` — checklist items, each prefixed `- [ ]`
- `## Technical Notes` — architecture hints, constraints, dependencies
- `## Review Notes` — filled in by Reviewer agent
- `## References` — traceability links
- `## Iteration Log` — appended each time the loop repeats (rejection → rework)

`## References` format:

```markdown
## References
- **PRD**: `[PROJECT_FOLDER]/product/requirements/prd-NNNN.md`
- **Test Document**: `[PROJECT_FOLDER]/product/tests/test_story_XXXX.md`
- **Related Stories**: `story_XXXX.md` — <reason>
- **Blocks**: `story_XXXX.md`
- **Blocked by**: `story_XXXX.md`
```

---

## Test Document Schema

Every `test_story_XXXX.md` lives in `[PROJECT_FOLDER]/product/tests/` and maps one-to-one with a story card.

```yaml
---
id: test_story_XXXX
story_ref: [PROJECT_FOLDER]/product/stories/story_XXXX.md
project: <project-name>
status: not_run | in_progress | pass | fail
timestamps:
  created: <ISO8601>
  last_run: null
---
```

Fixed sections in this order:

- `## Test Cases` — table filled by Tester agent
- `## References` — links to story card and test file

`## Test Cases` format:

```markdown
## Test Cases

| Test File | Test Function | Mock Used | Mock Justification | Status |
|-----------|---------------|-----------|--------------------|--------|
| tests/test_story_XXXX.py | test_story_XXXX_<description> | No | — | Pass |
| tests/test_story_XXXX.py | test_story_XXXX_<description> | Yes | HTTP 500 hard to trigger | Fail |
```

**Test rules (enforced by Tester and Reviewer agents):**
- Every acceptance criterion must have at least one corresponding test.
- Test names must encode the story ID: `test_story_XXXX_<description>` adapted to
  the language's idiomatic naming (e.g. `test_story_0001_user_can_login` in
  Python/Go, `story 0001 user can login` in a JS `describe`/`it` block,
  `TestStory0001UserCanLogin` in Go). The `story_XXXX` token must be present so
  tests trace back to the story.
- **Use the project's standard test framework**, read from `ENV.MD`
  `## Toolchain` (e.g. pytest, Jest/Vitest, Go `testing`, JUnit, cargo test,
  `terraform test`). Do not introduce a second framework.
- **Do not use mocks** unless a condition from the Coding Standards `Testing Rules` section is met. When mocking, fill in `Mock Used: Yes` and `Mock Justification` in the table.
- **Never modify a failing test to make it pass.** Open a new story card for the failure instead.
- All tests must show `Pass` before the story card moves to `pending_review`.

`## References` format:

```markdown
## References
- **Story**: `[PROJECT_FOLDER]/product/stories/story_XXXX.md`
- **Test File**: `[PROJECT_FOLDER]/tests/test_story_XXXX.<ext>` (language-dependent, e.g. `.py`, `.test.ts`, `_test.go`)
```

---

## Architecture Review Schema

Every `ARCH-NNNN.md` lives in `[PROJECT_FOLDER]/product/architecture/`.

```yaml
---
id: ARCH-NNNN
project: <project-name>
prd_ref: [PROJECT_FOLDER]/product/requirements/prd-NNNN.md
stories_reviewed:
  - [PROJECT_FOLDER]/product/stories/story_XXXX.md
status: approved
timestamps:
  created: <ISO8601>
  reviewed: <ISO8601>
---
```

Fixed sections in this order:

- `## Design Summary` — high-level architecture decisions for the reviewed stories
- `## Component Breakdown` — what each component does and how components interact
- `## Technology Validation` — confirms tech stack in ENV.MD is appropriate for the requirements
- `## Risk Assessment` — architectural risks, unknowns, and mitigations
- `## Integration Points` — external systems, APIs, data flows
- `## Recommendations` — notes on any concerns; for traceability only, does not block development
- `## References`

The Solution Architect agent writes this document and sets `status: approved` immediately. It is a reference artefact — no human review required before development begins.

`## References` format:

```markdown
## References
- **PRD**: `[PROJECT_FOLDER]/product/requirements/prd-NNNN.md`
- **Stories reviewed**: `[PROJECT_FOLDER]/product/stories/story_XXXX.md`, ...
```

---

## Infrastructure Change Schema [Optional]

Every `INFRA-NNNN.md` lives in `[PROJECT_FOLDER]/product/infra/`.

```yaml
---
id: INFRA-NNNN
project: <project-name>
cloud_providers:
  - AWS
status: draft | pending_user_review | approved | rejected
timestamps:
  created: <ISO8601>
  pending_user_review: null
  reviewed: null
  applied: null
---
```

Fixed sections in this order:

- `## Resources Provisioned` — table of all cloud resources created or modified
- `## IaC Plan Output` — full output of the dry-run / plan command (e.g. `terraform plan`)
- `## Security Posture` — IAM roles, network exposure, encryption settings
- `## Cost Estimate` — estimated monthly cost for provisioned resources
- `## Rollback Plan` — steps to destroy or revert the infrastructure
- `## User Review Notes` — filled by the user
- `## References`

**Human-in-the-loop rule**: Lead DevOps Agent (staging) may not begin until the user sets `status: approved`.

---

## Security Review Schema [Optional]

Every `SEC-NNNN.md` lives in `[PROJECT_FOLDER]/product/security/`.

```yaml
---
id: SEC-NNNN
project: <project-name>
infra_ref: [PROJECT_FOLDER]/product/infra/INFRA-NNNN.md
status: draft | pending_user_review | approved | rejected
timestamps:
  created: <ISO8601>
  pending_user_review: null
  reviewed: null
---
```

Fixed sections in this order:

- `## Code Security Findings` — OWASP Top 10 findings, secret scan results, dependency CVEs
- `## Infrastructure Security Findings` — IAM, network exposure, encryption, secrets management
- `## Severity Summary` — table of findings by severity (Critical / High / Medium / Low / Info)
- `## Mitigations Applied` — what was fixed before this review was written
- `## Open Items` — findings that remain open with owner and target resolution date
- `## Sign-off Conditions` — conditions that must be met before `status: approved` can be set
- `## User Review Notes` — filled by the user
- `## References`

**Human-in-the-loop rule**: No production deployment may proceed until the user sets `status: approved`. All Critical and High findings must be resolved before approval.

---

## Deployment Record Schema [Optional]

Every `DEPLOY-NNNN.md` lives in `[PROJECT_FOLDER]/product/deployments/`.

```yaml
---
id: DEPLOY-NNNN
project: <project-name>
environment: staging | production
image_sha: null
status: in_progress | success | failed | rolled_back
timestamps:
  created: <ISO8601>
  completed: null
---
```

Fixed sections in this order:

- `## Deployment Summary` — environment, image SHA, deployment method, duration
- `## Stories Deployed` — list of story IDs included in this deployment
- `## Smoke Test Results` — table of smoke tests run post-deployment with pass/fail status
- `## Rollback Instructions` — exact commands to revert if issues arise
- `## References`

---

## Go-Live Checklist Schema [Optional]

Every `GOLIVE-NNNN.md` lives in `[PROJECT_FOLDER]/product/go-live/`.

```yaml
---
id: GOLIVE-NNNN
project: <project-name>
arch_ref: [PROJECT_FOLDER]/product/architecture/ARCH-NNNN.md
infra_ref: [PROJECT_FOLDER]/product/infra/INFRA-NNNN.md
security_ref: [PROJECT_FOLDER]/product/security/SEC-NNNN.md
staging_deploy_ref: [PROJECT_FOLDER]/product/deployments/DEPLOY-NNNN.md
status: draft | pending_user_review | approved | rejected
timestamps:
  created: <ISO8601>
  pending_user_review: null
  approved: null
---
```

Fixed sections in this order:

- `## Pre-conditions` — linked documents that must all be `approved` before this checklist is written
- `## Infrastructure Readiness` — checklist items for cloud infrastructure
- `## Code and Test Readiness` — checklist items for code quality and test coverage
- `## Security Readiness` — checklist items from the security review
- `## Staging Validation` — checklist items verified in the staging environment
- `## Deployment Readiness` — rollback plan, deployment runbook link
- `## Operations Readiness` — monitoring, alerts, SLOs, runbook
- `## User Sign-off` — user sets `status: approved` here to unlock production deployment
- `## References`

**Human-in-the-loop rule (CRITICAL)**: Production deployment is BLOCKED until the user sets `status: approved`. This gate is absolute — no automation may bypass it.

---

## Runbook Schema [Optional]

Every `RUNBOOK-NNNN.md` lives in `[PROJECT_FOLDER]/product/runbooks/`.

```yaml
---
id: RUNBOOK-NNNN
project: <project-name>
production_deploy_ref: [PROJECT_FOLDER]/product/deployments/DEPLOY-NNNN.md
status: draft | active | deprecated
timestamps:
  created: <ISO8601>
  activated: null
---
```

Fixed sections in this order:

- `## Service Overview` — what the service does, its dependencies, and SLOs
- `## Monitoring & Dashboards` — links to dashboards and key metrics to watch
- `## Alerts` — table of configured alerts with severity, condition, and response action
- `## SLOs and SLIs` — defined service level objectives and how they are measured
- `## Common Incidents` — table of known failure modes with diagnosis and remediation steps
- `## Escalation Path` — who to contact and when
- `## Deployment and Rollback` — how to deploy a new version and how to roll back
- `## References`

---

## GitHub Projects Integration

The GitHub Project is the durable, single source of truth for product
artefacts. Markdown files in `[PROJECT_FOLDER]/product/` are the **working
copy during development**; they are uploaded via `gh` on milestone/status
changes and are never committed to the repository.

**One project per product**, e.g. `bt_engine Roadmap` (owner = the GitHub
account, linked to this repository).

### Artefact → Issue mapping

Every `templates/*.md` has a matching issue template in
`.github/ISSUE_TEMPLATE/`. The `github-project-sync` agent uploads artefacts
as issues using those templates.

| Artefact | Issue type | Project item |
|----------|------------|--------------|
| `product/requirements/prd-NNNN.md` | PRD | Roadmap item (`Start date`/`Target date` → roadmap view) |
| `product/stories/story_XXXX.md` | Story | Task, linked to PRD via `PRD Ref` field |
| `product/tests/test_story_XXXX.md` | Test document | Task |
| `product/architecture/ARCH-NNNN.md` | Architecture review | Task |
| `product/sprints/SPRINT-NNNN.md` | Sprint | Task |
| `product/daily-scrums/YYYY-MM-DD.md` | Daily scrum | Task |
| `product/infra/INFRA-NNNN.md` | Infrastructure | Task |
| `product/deployments/DEPLOY-NNNN.md` | Deployment | Task |
| `product/security/SEC-NNNN.md` | Security review | Task |
| `product/go-live/GOLIVE-NNNN.md` | Go-live | Task |
| `product/runbooks/RUNBOOK-NNNN.md` | Runbook | Task |
| `product/retrospective/REFLECTION-NNNN.md` | Retrospective | Task |

### Project fields

`Item Type` (PRD, Story, Test Document, Architecture Review, Sprint, Daily
Scrum, Infrastructure, Deployment, Security Review, Go-Live, Runbook,
Retrospective), `Status` (Backlog, Ready, In progress, In review, Done,
Passed, Approved, Failed), `Priority` (P0, P1, P2), `Story Points` (1, 2, 3,
5, 8, 13), `Complexity` (Low, Medium, High), `PRD Ref`, `Iteration` (sprint,
3 days), `Start date`, `Target date`. Labels: `prd`, `story`, `test`, `arch`,
`sprint`, `scrum`, `infra`, `deploy`, `security`, `golive`, `runbook`,
`reflection`.

### Status mapping

Artefact status in markdown maps to the project `Status` field as follows:

| Artefact | Artefact status | Project Status |
|----------|-----------------|----------------|
| Story | `not_started` | `Backlog` |
| Story | `approved` | `Ready` |
| Story | `in_progress`, `testing` | `In progress` |
| Story | `pending_review` | `In review` |
| Story | `completed` | `Done` |
| Test document | `pass` | `Passed` |
| Test document | `fail` | `Failed` |
| Test document | `not_run`, `in_progress` | `In progress` |
| Architecture | `approved` | `Approved` |
| Architecture | `pending_user_review` | `In review` |
| PRD | `draft` | `Backlog` |
| PRD | `approved` | `Ready` |
| PRD | `completed` | `Done` |

### Roadmap dates

PRD items get `Start date` = PRD creation date and `Target date` = start +
**3 days** (one sprint = 3 days; coding agents deliver faster than a human
team). This keeps the roadmap view populated with sprint-sized windows.

### Sync rules

- The `github-project-sync` agent is the **only** agent that runs
  `gh issue` / `gh project` tracking commands.
- **Restore (pull)**: when `[PROJECT_FOLDER]/product/requirements/` contains no
  `prd-NNNN.md` or `[PROJECT_FOLDER]/product/stories/` contains no
  `story_XXXX.md`, the `github-project-sync` agent pulls the missing artefacts
  from the GitHub Project and writes them into the corresponding folders before
  any development begins.
- Idempotent: skip creation when the artefact frontmatter already has
  `gh_issue_url` set; update fields in place otherwise.
- `gh_issue_url` and `gh_project_item_id` are recorded back in each
  artefact's frontmatter after creation.
- Markdown status is authoritative; the Project mirrors it.

---

## Release Policy

### Versioning

- **Feature release**: completed `prd-NNNN` → version `1.N.0` (e.g.
  `prd-0007` → `1.7.0`). Tag: annotated `v1.N.0`, message
  `release(prd-0007): v1.7.0`. Tags are cut from `main` **after** the PRD's
  MR/PR is merged.
- **Bugfix release** (`1.7.0` → `1.7.1`): treat the fix like a tiny PRD —
  its own branch + worktree from `main`, MR/PR, human squash-merge, then tag
  the patch from `main`:
  1. `git worktree add ../worktrees/hotfix-<slug> -b hotfix/<slug> origin/main`
  2. Fix in the worktree, commit `fix(story-XXXX): ...`, push, open MR/PR.
  3. Human squash-merges to `main`.
  4. From updated `main`: `git tag -a v1.7.1 -m "release(prd-0007): v1.7.1"` →
     `git push origin v1.7.1`.
  5. For an **old, diverged** release line, patch a maintenance branch cut from
     the tag and cherry-pick the fix commit (never rewrite shared history).

### Release notes

- `[PROJECT_FOLDER]/RELEASES_NOTES.MD` is maintained by the Release Manager,
  one section per version with **Changed** and **Deprecated** subsections.
- The Lead Reviewer verifies the notes against the completed PRD before
  release (Step 4c).

### GitHub / GitLab Release

- After the tag is pushed, the git-agent creates the release:
  `gh release create vX.Y.Z --generate-notes --notes-file [PROJECT_FOLDER]/RELEASES_NOTES.MD`
  (GitHub) or `glab release create vX.Y.Z --notes-file [PROJECT_FOLDER]/RELEASES_NOTES.MD`
  (GitLab). If the release already exists, update the notes in place
  (`gh release edit` / `glab release update`).

### README policy

The Release Manager keeps `README.md` current every release:
- `## How to Use` — how to use the software (exact, copy-pasteable commands)
- `## How to Develop` — development environment and commands
- `## Release Version` — release history with PRD traceability

---

## Agent Execution Standards

These rules apply to **every agent** in the pipeline without exception.

### 1. Think Before Acting

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before starting any work:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum output that solves the problem. Nothing speculative.**

- No features, tests, or checks beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- **No speculative fallthrough guards in dispatch methods**: when a method dispatches on an enum-like value (e.g. `backend`, `db_type`, `mode`) and every valid value is handled by a named branch, do not add a trailing `raise ValueError(f"Unknown ...")` for values not specified in any acceptance criterion. The config validation layer eliminates invalid values before they reach the dispatch point. A trailing `raise` for hypothetical unknown values is speculative defensive code and will be rejected. Only raise for values that are explicitly required to raise by an acceptance criterion.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code or documents:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code or issues, mention them — don't fix them silently.

When your changes create orphans:
- Remove imports, variables, or functions that **your** changes made unused.
- Don't remove pre-existing dead code unless explicitly asked.

Every changed line should trace directly to the story's Acceptance Criteria.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals before starting:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Review story" → "Verify every acceptance criterion is met, then decide pass/fail"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Weak criteria ("make it work") require constant clarification. Strong criteria let you execute and verify independently.

---

## Coding Standards

All agents that write or modify code must follow these rules without exception. Violations must be corrected before a story card can move to `testing`.

### General Principles

- **MVP first**: implement only what the Acceptance Criteria require. Do not add helper utilities, extra abstractions, plug-in architectures, or configuration layers that the story does not ask for.
- **No over-engineering**: avoid design patterns, generics, or framework layers that add complexity without a concrete, present need. Solve the problem in front of you, not a hypothetical future one.
- **DRY — Don't Repeat Yourself**: any logic used more than once must be extracted into a function, class, or module. No copy-pasted blocks.
- **SOLID**:
  - *Single Responsibility*: each class and function does exactly one thing.
  - *Open/Closed*: add behaviour through new functions or classes; do not modify stable, tested code to add unrelated features.
  - *Liskov Substitution*: subclasses must be fully substitutable for their base class without altering correctness.
  - *Interface Segregation*: prefer small, focused interfaces over large general-purpose ones.
  - *Dependency Inversion*: depend on abstractions (protocols, base classes), not concrete implementations.

### Dependency & Import Rules (all languages)

- **Imports/includes go at the top** of the file (or the language's idiomatic
  location), grouped standard library → third-party → local where the language
  supports grouping.
- **Conditional/guarded imports to feature-detect a dependency are forbidden.**
  If a library is required, declare it as a hard dependency in the project's
  manifest (`pyproject.toml`/`requirements.txt`, `package.json`, `go.mod`,
  `Cargo.toml`, provider blocks in `*.tf`, …) and import it unconditionally. If
  a dependency is genuinely optional, isolate the optional path in a separate
  module imported only where needed — never a runtime try/catch feature flag.

  Example of the forbidden pattern (Python shown; the rule applies to every
  language's equivalent):

  ```python
  # FORBIDDEN
  try:
      import pandas as pd
      is_pandas = True
  except Exception:
      is_pandas = False
  ```

### Language-Specific Notes

Keep universal rules above language-agnostic; record per-language gotchas here as
they come up. The agent applies only the note matching `ENV.MD` `## Language`.

- **Python — subprocess encoding on Windows**: when calling `subprocess.run`
  with `text=True`, always pass `encoding="utf-8"`. The Windows default (cp1252)
  cannot decode UTF-8 output from external binaries, making `result.stdout`
  `None` and causing later `json.loads` to raise `TypeError`. Use
  `subprocess.run([...], capture_output=True, text=True, encoding="utf-8", timeout=30)`.
- **Terraform / IaC** — follow the `terraform` skill: run `terraform fmt` and
  `terraform validate`; pin provider and module versions; never commit state or
  `.tfvars` secrets; plan before apply.

### Documentation Rules

The repository must contain a `README.md` before development
starts. The README must contain these sections, in this order:

```markdown
## How to Use
## How to Develop
## Release Version
```

- **How to Use**: explain the supported user workflow and provide exact,
  copy-pasteable commands for the primary use case. Do not use placeholder
  paths, commands, or environment names.
- **How to Develop**: document the required runtime environment from
  `ENV.MD`, dependency installation, test commands, lint/type-check commands
  when applicable, and the expected development workflow.
- **Release Version**: state the current package version and describe the
  feature delivered by each released PRD version. The version must match the
  authoritative package metadata, such as `pyproject.toml`.

The `Release Version` section may contain generated content, but generated
updates must preserve human-authored README content outside clearly marked
generated boundaries. When a PRD reaches `status: completed`, the README must
be updated before the release is considered complete: add the PRD feature to
the release history and update the current version according to the project's
versioning policy. The Reviewer must reject a completed story or release
handoff when the required README sections are missing or stale.

Every function, method, class, or exported unit (module, package, Terraform
module) **must** have a documentation comment in the language's idiomatic style.
No exceptions. It must cover three things:

1. **What it does** — one-line summary of purpose (imperative mood: "Calculate...", "Return...", "Validate...")
2. **Parameters/inputs** — name, type, and description for every parameter
3. **Returns/outputs** — type and description of the return value (omit only when there is no meaningful output)

Use the **standard doc convention for the language** in `ENV.MD` `## Language` —
e.g. Google-style docstrings (Python), JSDoc/TSDoc (JavaScript/TypeScript),
GoDoc comments (Go), Javadoc (Java), rustdoc `///` (Rust), or `description`
arguments on Terraform variables/outputs. Example (Python shown):

```python
def retry_with_backoff(operation: Callable[[], T], max_attempts: int, base_delay: float) -> T:
    """Run an operation, retrying with exponential backoff on failure.

    Args:
        operation: Zero-argument callable to execute; its return value is passed through.
        max_attempts: Maximum number of attempts before giving up.
        base_delay: Initial delay in seconds, doubled after each failed attempt.

    Returns:
        The value returned by the first successful call to operation.
    """
```

For Terraform, every `variable` and `output` must carry a `description`, and
each module needs a README or header comment stating its purpose, inputs, and
outputs.

**Enforcement:**
- The Reviewer agent must reject any function, method, class, or exported unit missing a documentation comment.
- One-word or placeholder doc comments (`// TODO`, `"""."""`) count as missing.
- Inline comments are still discouraged for obvious code — doc comments replace them at the declaration level.

### Testing Rules

- **Use the project's standard test framework**, read from `ENV.MD`
  `## Toolchain` (e.g. pytest for Python, Jest/Vitest for JS/TS, Go `testing`,
  JUnit for Java, `cargo test` for Rust, `terraform test` for Terraform). Do not
  introduce an additional framework alongside the project's chosen one.
- **Do not use mocks, stubs, or monkeypatching** unless one or more of these conditions is explicitly met:
  - **a) Hard-to-trigger errors**: the scenario requires a response that is difficult or impossible to reproduce with real calls (e.g. HTTP 500, HTTP 403, network timeout, disk full). Condition (a) applies only to error or failure scenarios — it does not apply to happy-path tests where the inconvenience is a side effect such as a filesystem write or network call. Avoiding a side effect during a delegation test is a convenience rationale, not a valid condition (a) justification.
  - **b) Low rate limits**: the external API allows fewer than 5 calls per minute, making repeated test runs impractical.
  - **c) External system not yet available**: the dependency is still under development (in a parallel sprint story) or does not exist in the test environment.
- When mocking is justified, **document the reason** with an inline comment directly above the mock and record the justification in the `Mock Justification` column of the test document's `## Test Cases` table.
- All tests must be independently runnable — no shared mutable state between tests. Use the framework's setup/teardown mechanism (fixtures, `beforeEach`, `TestMain`, etc.).

---

## Build, Test & Run Environment

The toolchain is **project- and platform-dependent**. Before running any build,
test, run, or dependency command, all agents must read `[PROJECT_FOLDER]/ENV.MD`
(`## Language`, `## Infrastructure as Code`, and `## Toolchain` / `## Python
Environment`) and use the declared commands. **Never assume a language or invoke
a bare interpreter/tool** (no bare `python`, `node`, `go`, `terraform`) when the
project pins a specific version or environment.

### Python (when `ENV.MD ## Python Environment` is present)

The Python environment is platform-dependent — read `Manager` and `Name` first.

**Windows — conda:**
```bash
conda activate <Name> && python -m pytest [PROJECT_FOLDER]/tests/test_story_XXXX.py -v
conda activate <Name> && python -m pip install <package>
```
If `conda activate` fails (shell not initialised), fall back to
`conda run -n <Name> python -m pytest ...`.

**Linux / macOS — venv** (`Name` typically `.venv`):
```bash
[PROJECT_FOLDER]/<Name>/bin/python -m pytest tests/test_story_XXXX.py -v
[PROJECT_FOLDER]/<Name>/bin/python -m pip install <package>
```

### Other languages (use the commands from `ENV.MD ## Toolchain`)

Representative examples — follow the project's actual pinned versions and the
relevant skill:

| Language | Install | Test | Build/Run |
|----------|---------|------|-----------|
| Node/TypeScript | `npm ci` | `npm test` | `npm run build` / `npm start` |
| Go | `go mod download` | `go test ./...` | `go build ./...` |
| Rust | `cargo fetch` | `cargo test` | `cargo build --release` |
| Java | `mvn install` | `mvn test` | `mvn package` |
| Terraform / IaC | `terraform init` | `terraform validate` / `terraform test` | `terraform plan` → `terraform apply` |

For version-managed toolchains, honour the pin (e.g. `nvm use`, `pyenv`,
`asdf`, `tfenv`) declared in `ENV.MD` before running commands.

Skills are loaded by agents via the Skill tool — they do not run as scripts and do not require any language environment.

---

## Traceability

Every document links back to what produced it and forward to what it produced.

| Document | Must reference |
|----------|----------------|
| `prd-NNNN.md` | Derived story cards (added after story cards are written) |
| `story_XXXX.md` | Source PRD, test document, related/blocking stories |
| `test_story_XXXX.md` | Story card, test file path |
| `ARCH-NNNN.md` | Source PRD, all story cards reviewed |
| `INFRA-NNNN.md` | IaC plan output [optional] |
| `SEC-NNNN.md` | Infra record, staging deployment record [optional] |
| `DEPLOY-NNNN.md` | Image SHA, stories deployed [optional] |
| `GOLIVE-NNNN.md` | ARCH, INFRA, SEC, staging DEPLOY records [optional] |
| `RUNBOOK-NNNN.md` | Production DEPLOY record [optional] |
| `RELEASES_NOTES.MD` | Version, PRD ID, README release history |

Test functions encode the story ID in their name: `test_story_XXXX_*`.

---

## Workflow

### Pipeline Overview

```
PRD → SA (auto) → Development → Testing → Review → [User verifies]
                                                     → Release Manager
                                                     → Release Review
                                                     → git-agent: MR/PR → human merge → tag + release + Project sync
                                                                     ↑
                                    (Optional on user request)        │
                                    Security → DevOps → Infra ────────┘
```

---

### Step 1 — Solution Architect Agent

- **Trigger**: user provides a `prd-NNNN.md` in `[PROJECT_FOLDER]/product/requirements/`
- **Input**: the PRD file
- **Task**:
  1. Decompose the PRD into discrete independently deliverable story cards. Write one `story_XXXX.md` per story in `[PROJECT_FOLDER]/product/stories/`.
  2. Review the story cards as a set for architectural coherence, technology appropriateness, risk, and integration correctness. Write `ARCH-NNNN.md`.
  3. Immediately set all story cards to `status: approved` and hand off to the orchestrator — no user gate.
- **Story numbering**: scan existing stories, find highest XXXX, increment. First is `story_0001.md`.
- **Set on story write**: `status: approved`, `priority: N` (1 = highest), `sprint_id: null`, `timestamps.created: <now>`, `timestamps.approved: <now>`
- **Arch numbering**: scan `[PROJECT_FOLDER]/product/architecture/`, find highest NNNN, increment. First is `ARCH-0001.md`.
- **On arch write**: set `status: approved`, `timestamps.reviewed: <now>`
- **After all cards written**: append `## References` to the PRD listing each derived story card.
- **Immediately after**: hand off to the orchestrator. The orchestrator picks up all `status: approved` stories and begins development automatically.
- **If blocking issues found**: document in `## Recommendations` in `ARCH-NNNN.md` for traceability, but do not stop — proceed with development unless the issue makes implementation impossible.

---

### Step 1.5 — git-agent: PRD Kickoff (branch + worktree)

- **Trigger**: a PRD's stories are approved and ready for development.
- **Task**: the git-agent syncs local `main` (see `## Git Workflow` Step 1),
  then creates the PRD branch and an isolated worktree:
  `git worktree add ../worktrees/prd-XXXX -b prd/prd-XXXX-<slug> origin/main`,
  and reports the worktree path. All subsequent development agents for this PRD
  operate inside that worktree so concurrent PRDs never block each other.

---

### Step 2 — Software Engineering Agent

- **Trigger**: orchestrator finds a story card with `status: approved` and `layer: backend` or `layer: fullstack`
- **Input**: story card with `status: approved`
- **Task**: implement the feature inside the PRD's **worktree**. Write code only — no git operations.
- **On start**: update card — `status: in_progress`, `timestamps.in_progress: <now>`
- **On completion**: update card — `status: testing`, `timestamps.testing: <now>`
- **Dependency check**: before writing any code, check the story card's `## References` section for `Blocked by` entries. If any exist, **stop immediately** and ask the user how to proceed — do not implement until the user confirms the blocker is resolved.
- **Scope boundary**: implement only what the current story's Acceptance Criteria require. Do not pre-implement logic from related stories. Pre-implementing downstream scope is an MVP violation and will be rejected by the Reviewer.
- **External CLI/API field name verification**: if the story's Technical Notes describe JSON response field names from an external CLI command or API endpoint, run the relevant command and inspect the actual output before coding against those field names. If the live output differs from the Technical Notes, note the discrepancy and implement against the observed live output.
- **Missing dependency**: if a required dependency is missing (e.g. `ModuleNotFoundError`/`ImportError` in Python, `Cannot find module` in Node, unresolved import/provider in Go/Terraform), **stop and ask the user** — do not install packages automatically. Suggest the missing dependency and wait for explicit user approval before running any install command (`pip`/`conda`, `npm install`, `go get`, `terraform init`, …).
- **Web application run instructions**: if the project is a web application (any `layer: frontend` or `layer: fullstack` story, or a backend that exposes an HTTP server), include a `## How to Run` section at the bottom of the story card on completion. List the exact commands the user must run to start the application, e.g. `cd [PROJECT_FOLDER] && npm run dev`. Commands must be copy-pasteable with no placeholders.

### Step 2b — Frontend Engineer Agent

- **Trigger**: story card has `status: approved` and `layer: frontend` or `layer: fullstack`. For `layer: fullstack`, runs after Step 2 (SE Agent) completes.
- **Input**: story card with `status: approved`
- **Task**: read `[PROJECT_FOLDER]/ENV.MD`, invoke the matching frontend skill (`react-frontend`, `vue-frontend`, `nextjs-frontend`, or `vanilla-frontend`), implement the UI inside the PRD's **worktree**. Write code only — no git operations.
- **On start**: update card — `status: in_progress`, `timestamps.in_progress: <now>` (if not already set by SE Agent)
- **On completion**: update card — `status: testing`, `timestamps.testing: <now>`
- **Dependency check, Scope boundary, Missing library**: same rules as Step 2.
- **Web application run instructions**: same rule as Step 2 — include `## How to Run` in the story card on completion with exact copy-pasteable commands.

---

### Step 3 — Tester Agent

- **Input**: story card with `status: testing` + implemented code in the PRD's worktree
- **Task**: write tests (one per acceptance criterion) using the project's test framework from `ENV.MD ## Toolchain`, write test documentation, run tests, record results.
- **Test file**: `[PROJECT_FOLDER]/tests/test_story_XXXX.<ext>` (language-dependent, e.g. `test_story_0001.py`, `story_0001.test.ts`, `story_0001_test.go`; follow the language's conventional test location).
- **Test document**: `[PROJECT_FOLDER]/product/tests/test_story_XXXX.md`
- **Test naming**: encode the story ID — `test_story_XXXX_<description>` in the language's idiomatic style (see Test Document Schema).
- **Coding standards apply to test files**: imports/includes grouped at the top (stdlib → third-party → local) per the language's convention. Verify there are no feature-detecting conditional imports before proceeding.
- **Dependency check**: before writing any tests, check the story card's `## References` for `Blocked by` entries. If any exist, **stop immediately** and ask the user how to proceed.
- **Status must reflect actual test runner output**: the `Status` column must be set from the actual test-runner output (pytest, jest, `go test`, etc.). Never record `Pass` for a test that did not pass.
- **Missing dependency on test failure**: if a test fails because a dependency is missing (e.g. `ModuleNotFoundError`, `Cannot find module`, unresolved import), stop and tell the user which dependencies are missing and ask for approval before installing.
- **If all pass**: set test doc `status: pass`; set story card `status: pending_review`, `timestamps.pending_review: <now>`; update story card `## References` with test doc link.
- **If any fail**: set test doc `status: fail`; record `Fail` in table; keep story card `status: testing`. **Do not edit the failing test.** Open a new story card for the failure; link it in story card `## References`.

---

### Step 4 — Reviewer Agent

- **Input**: story card with `status: pending_review` + test doc with `status: pass`
- **Task**: verify implementation matches every acceptance criterion; confirm test doc shows all `Pass`; check `## References` is complete.
- **If approved**: set story card `status: completed`, `timestamps.completed: <now>`; then report completion to the user — if the story card has a `## How to Run` section, print those commands verbatim in the completion report so the user knows exactly how to launch the application. **Stop here and wait for user verification before the Release Manager runs.**
- **If rejected**: append rejection entry to `## Iteration Log`; increment `iteration`; reset `status: approved`; clear `timestamps.in_progress`, `timestamps.testing`, `timestamps.pending_review` to `null`; orchestrator will re-invoke the SE Agent (story is `approved` again).
- **User verification**: after the user confirms the application works as expected, the orchestrator invokes the Release Manager. The git-agent remains blocked until release preparation and release review are complete.

---

### Step 4b — Release Manager Agent

- **Trigger**: all stories belonging to a completed PRD have passed review and the user has verified the delivered feature.
- **Input**: completed `[PROJECT_FOLDER]/product/requirements/prd-NNNN.md` and the corresponding source changes.
- **Task**: update `[PROJECT_FOLDER]/README.md`, `[PROJECT_FOLDER]/RELEASES_NOTES.MD`, and the authoritative package metadata, such as `pyproject.toml`, according to the active release-version policy.
- **README requirement**: confirm the README contains `## How to Use`, `## How to Develop`, and `## Release Version` in that order. Add the completed PRD's feature description and traceability link to the release history. Keep `## How to Use` current so users know how to use the delivered software.
- **Release notes requirement**: add a per-version entry to `RELEASES_NOTES.MD` with `### Changed` and `### Deprecated` subsections. Record what changed and what has been deprecated in this version.
- **Scope**: edit release documentation and version metadata only. Do not modify product implementation, tests, story acceptance criteria, or Git history.
- **Release type**: use `feature` for the first release of a completed PRD and `bugfix` for a fix release against an existing completed PRD. Follow the `x.y.z` rules defined by the active CI/CD PRD (`prd-NNNN` → `1.N.0`; bugfix increments `z`).
- **Validation**: run the applicable metadata, test, and package-build checks and record actual results. If the README or version policy cannot be updated accurately, stop and report the issue.
- **Handoff**: report the files changed, resulting version, PRD summary, and validation results. Stop and wait for the Lead Reviewer release review.

### Step 4c — Release Review

- **Trigger**: the Release Manager has prepared release metadata and reported completion.
- **Input**: completed `prd-NNNN.md`, the Release Manager's changes to `README.md`, `RELEASES_NOTES.MD` and package metadata, and validation results.
- **Task**: the Lead Reviewer verifies that the README's feature description, version, and traceability link accurately reflect the completed PRD's delivered functionality; that `RELEASES_NOTES.MD` accurately records the changes and deprecations; and that the version follows the active `x.y.z` policy. Confirm the required README sections are present and ordered correctly.
- **If approved**: explicitly report `Release approved for git-agent` and hand off to the git-agent.
- **If rejected**: return the release to the Release Manager with exact discrepancies and required corrections. Do not allow the git-agent to open the MR/PR.
- **Independence**: the Lead Reviewer must not approve release metadata solely because the Release Manager reported success; review the actual files against the PRD.

---

### Step 5 — git-agent: Open MR/PR → Human Merge → Tag & Release

- **Trigger**: user confirms the application works, the Release Manager has updated `README.md`/`RELEASES_NOTES.MD`/package metadata, and the Lead Reviewer explicitly approves the release changes.
- **Task**: in the PRD's worktree, bring the branch up to date and open the MR/PR for human review; after the human squash-merges, tag the release from `main` and create the GitHub/GitLab Release; finally remove the worktree and branch. **No direct commits to `main`.**

Follow `## Git Workflow` Steps 3–5 exactly:
  1. `git fetch origin`; `git merge origin/main` into the branch; resolve conflicts locally; **re-run unit tests**; `git push` (never `--force`).
  2. Open the MR/PR (squash) and **stop** — a human reviews and merges.
  3. After merge: sync `main`, cut the annotated tag `vX.Y.Z` from `main`, push the tag, create the release from `RELEASES_NOTES.MD`.
  4. Remove the worktree and delete the local + remote branch.

**Bugfix patch release**: follow the bugfix flow in `## Release Policy`
(own branch + worktree, MR/PR, human merge, tag patch from `main`).

---

### [Optional] Infrastructure Agent

**Invoke when**: user explicitly requests infrastructure provisioning.

- **Input**: story card with `type: infra` (if applicable) + `[PROJECT_FOLDER]/ENV.MD`
- **Task**: read `ENV.MD` for cloud provider(s). Invoke the matching cloud skill(s) and `cloud-security` skill. Write or update IaC in `[PROJECT_FOLDER]/infra/`. Run a dry-run plan. Write `INFRA-NNNN.md`.
- **Numbering**: scan `[PROJECT_FOLDER]/product/infra/`, find highest NNNN, increment. First is `INFRA-0001.md`.
- **On write**: set `INFRA-NNNN.md` `status: pending_user_review`, `timestamps.pending_user_review: <now>`
- **Human gate**: stop after writing. The user reviews `INFRA-NNNN.md` and sets `status: approved` before the DevOps Agent may begin staging deployment.

---

### [Optional] Security Reviewer Agent

**Invoke when**: user explicitly requests a security review.

- **Input**: `[PROJECT_FOLDER]/` + `INFRA-NNNN.md` (if exists)
- **Task**: invoke `owasp` skill and `cloud-security` skill, run OWASP Top 10 code audit, scan for secrets, check dependency CVEs, audit infrastructure security posture, write `SEC-NNNN.md`.
- **Numbering**: scan `[PROJECT_FOLDER]/product/security/`, find highest NNNN, increment. First is `SEC-0001.md`.
- **On write**: set `status: pending_user_review`, `timestamps.pending_user_review: <now>`
- **Human gate**: stop after writing. The user reviews and sets `status: approved`. All Critical and High findings must be resolved before approval.

---

### [Optional] DevOps Agent (Staging → Go-Live → Production)

**Invoke when**: user explicitly requests deployment.

**Staging deployment** (requires `INFRA-NNNN.md` `status: approved`):
- Build container image, scan for vulnerabilities, push to registry, deploy to staging, run smoke tests, write `DEPLOY-staging-NNNN.md`.
- On completion: set `status: success` or `failed`. If failed, report and stop.

**Go-Live Checklist** (requires `SEC-NNNN.md` `status: approved`):
- Write `GOLIVE-NNNN.md` assembling all pre-conditions (ARCH, INFRA, SEC, staging DEPLOY).
- Set `status: pending_user_review` — human gate required before production.

**Production deployment** (requires `GOLIVE-NNNN.md` `status: approved`):
- **CRITICAL GATE CHECK**: read `GOLIVE-NNNN.md`. If `status` is not `approved`, stop immediately.
- Promote the staging image (same SHA, no rebuild) to production using a rolling deployment strategy.
- Run production smoke tests, write `DEPLOY-prod-NNNN.md`.

---

### [Optional] SRE Agent

**Invoke when**: user explicitly requests production monitoring setup.

- **Input**: `[PROJECT_FOLDER]/ENV.MD` + story cards
- **Task**: invoke relevant cloud skill(s), configure production monitoring dashboards and alerts, define SLOs/SLIs, validate production health, write `RUNBOOK-NNNN.md`.
- **Numbering**: scan `[PROJECT_FOLDER]/product/runbooks/`, find highest NNNN, increment. First is `RUNBOOK-0001.md`.
- **On write**: set `status: active`, `timestamps.activated: <now>`

---

## Orchestrator

The orchestrator drives all agent work forward automatically once stories are approved.

**Each run performs these steps in order:**

0. **Bootstrap check**: determine greenfield vs brownfield and ensure the agent
   instructions file exists per `## Project Bootstrap`. **Pull missing artefacts
   from the GitHub Project**: if `[PROJECT_FOLDER]/product/requirements/`
   contains no `prd-NNNN.md` or `[PROJECT_FOLDER]/product/stories/` contains no
   `story_XXXX.md`, invoke the `github-project-sync` agent to pull the missing
   PRDs and story cards from the GitHub Project and write them into the
   respective folders. Do not proceed to development until the local artefact
   folders are populated.
1. For each PRD with an `active` development cycle, ensure the git-agent has
   created its branch + worktree (Step 1.5), then invoke the appropriate agent
   based on current status and `layer`:
   - `approved` + `layer: backend` → **Software Engineering Agent** (Step 2)
   - `approved` + `layer: frontend` → **Frontend Engineer Agent** (Step 2b)
   - `approved` + `layer: fullstack` → **SE Agent** then **Frontend Engineer Agent** (Steps 2 + 2b)
   - `in_progress` → resume the appropriate agent (SE or Frontend)
   - `testing` → **Tester Agent** (Step 3)
   - `pending_review` + test doc `status: pass` → **Reviewer Agent** (Step 4) — stops and waits for user verification
   - `completed` + user confirms → **Release Manager** (Step 4b), when the PRD release is ready
   - Release Manager complete + Lead Reviewer release approval → **git-agent** (Step 5)

2. After each status transition (approved → in_progress → testing →
   pending_review → completed, and PRD completed), invoke the
   **github-project-sync agent** to mirror the new status into the GitHub
   Project (create/update the artefact issue and project item).

**Rules:**
- **PRDs run concurrently, each in its own worktree.** Within a single PRD,
  process one story at a time: do not invoke the next story's agent until the
  current story's agent has finished and updated the story card status.
- If a story is `in_progress` (agent was interrupted mid-run), resume the appropriate agent for that story before starting new ones.
- The orchestrator does not invoke Infrastructure, Security, DevOps, or SRE agents — those are user-triggered only.
- The GitHub Project sync never blocks the pipeline: if `gh` is unavailable or
  unauthenticated, record the pending sync and continue.

---

## Running the Pipeline

### Normal flow

0. Bootstrap check (greenfield/brownfield, instructions file). If
   `[PROJECT_FOLDER]/product/requirements/` contains no `prd-NNNN.md` or
   `[PROJECT_FOLDER]/product/stories/` contains no `story_XXXX.md`, the
   orchestrator first pulls the missing artefacts from the GitHub Project and
   writes them into the folders before any development begins.
1. Drop a `prd-NNNN.md` in `[PROJECT_FOLDER]/product/requirements/`
2. Tell the orchestrator: `"Process the PRD for <project-name>"`
3. SA Agent writes story cards + architecture review, auto-approves all stories
4. git-agent creates the PRD branch + worktree; orchestrator drives development
   inside it: SE → Tester → Reviewer, with GitHub Project sync after each status change
5. Reviewer prints run commands and stops — user verifies the application
6. User confirms it works → Release Manager updates README, RELEASES_NOTES.MD, and package metadata
7. Lead Reviewer reviews the release changes against the completed PRD
8. Release approval → git-agent merges `main` in, opens the MR/PR, and stops for human review
9. Human squash-merges → git-agent tags, creates the release, and removes the worktree
10. Pipeline stops. User requests optional agents if needed.

### Human gates

The core pipeline is automatic from PRD to **MR/PR creation**. The **merge
itself is a human gate**: a human reviews and squash-merges every MR/PR before
anything reaches `main`.

Optional agents have their own gates when invoked:

| Gate | What the human does | What happens next |
|------|---------------------|-------------------|
| **Merge** | Reviews and squash-merges the MR/PR | git-agent tags the release and cleans up |
| **Gate A** | Reviews `INFRA-NNNN.md`; sets `status: approved` [optional] | DevOps Agent (staging) begins deployment |
| **Gate B** | Reviews `SEC-NNNN.md`; sets `status: approved` [optional] | DevOps Agent writes go-live checklist |
| **Gate C** | Reviews `GOLIVE-NNNN.md`; sets `status: approved` [optional] | DevOps Agent (production) promotes staging image |

### Optional agents (user-triggered)

| Command | Agent invoked |
|---------|---------------|
| `"Run infrastructure provisioning for <project-name>"` | Infrastructure Agent |
| `"Run security review for <project-name>"` | Security Reviewer Agent |
| `"Deploy to staging for <project-name>"` | DevOps Agent (staging) |
| `"Deploy to production for <project-name>"` | DevOps Agent (production) |
| `"Set up production monitoring for <project-name>"` | SRE Agent |
| `"Sync product artefacts to the GitHub Project"` | github-project-sync Agent |

### Status check

Ask the orchestrator at any time: `"What's the pipeline status for <project-name>?"` — it will scan all project artefacts and report pipeline state, pending gates, and what needs your attention.

---

## Skills System

Agent skills live in `.apm/skills/` in the agent-stack package and are deployed
to each agent's skills directory on `apm install`. Each skill provides
domain-specific knowledge, CLI commands, checklists, and patterns for a
particular technology stack.

Agents **must never hardcode** cloud provider or frontend framework knowledge. Always read `ENV.MD` first, then invoke the appropriate skill using the Skill tool.

**Available skills:**

| Skill | Command | Used by |
|-------|---------|---------|
| AWS Cloud | `aws-cloud` | Infrastructure Agent, DevOps Agent, SRE Agent |
| Azure Cloud | `azure-cloud` | Infrastructure Agent, DevOps Agent, SRE Agent |
| GCP Cloud | `gcp-cloud` | Infrastructure Agent, DevOps Agent, SRE Agent |
| React | `react-frontend` | Frontend Engineer Agent |
| Vue | `vue-frontend` | Frontend Engineer Agent |
| Next.js | `nextjs-frontend` | Frontend Engineer Agent |
| Vanilla JS | `vanilla-frontend` | Frontend Engineer Agent |
| Docker | `docker` | DevOps Agent |
| Kubernetes | `kubernetes` | DevOps Agent |
| GitHub Actions | `github-actions` | DevOps Agent |
| OWASP | `owasp` | Security Reviewer Agent |
| Cloud Security | `cloud-security` | Security Reviewer Agent, Infrastructure Agent |

If a project uses multiple cloud providers, invoke all relevant cloud skills and reconcile guidance for the task at hand.

---

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| PRDs | `product/requirements/prd-NNNN.md` | `product/requirements/prd-0001.md` |
| Stories | `product/stories/story_XXXX.md` | `product/stories/story_0001.md` |
| Test documents | `product/tests/test_story_XXXX.md` | `product/tests/test_story_0001.md` |
| Test file | `tests/test_story_XXXX.<ext>` | `test_story_0001.py`, `story_0001.test.ts`, `story_0001_test.go` |
| Test function | `test_story_XXXX_<snake_case>` | `test_story_0001_user_can_login` |
| Architecture reviews | `product/architecture/ARCH-NNNN.md` | `product/architecture/ARCH-0001.md` |
| Infrastructure records | `product/infra/INFRA-NNNN.md` | `product/infra/INFRA-0001.md` |
| Security reviews | `product/security/SEC-NNNN.md` | `product/security/SEC-0001.md` |
| Deployment records | `product/deployments/DEPLOY-NNNN.md` | `product/deployments/DEPLOY-0001.md` |
| Go-live checklists | `product/go-live/GOLIVE-NNNN.md` | `product/go-live/GOLIVE-0001.md` |
| Runbooks | `product/runbooks/RUNBOOK-NNNN.md` | `product/runbooks/RUNBOOK-0001.md` |
| Release notes | `RELEASES_NOTES.MD` | `RELEASES_NOTES.MD` |
| PRD branch | `prd/prd-XXXX-<slug>` | `prd/prd-0007-custom-logging` |
| Hotfix branch | `hotfix/<slug>` or `hotfix/vX.Y.Z` | `hotfix/log-crash` |
| Worktree path | `../worktrees/prd-XXXX` | `../worktrees/prd-0007` |
| Release tags | `vX.Y.Z` (feature `prd-NNNN` → `v1.N.0`, bugfix → `v1.N.Z`) | `v1.7.0`, `v1.7.1` |
| ENV manifest | `ENV.MD` | `ENV.MD` |

**Commit messages:**

| Type | Format | Example |
|------|--------|---------|
| Feature | `feat(story-XXXX): <title>` | `feat(story-0001): add JWT auth` |
| Bug fix | `fix(story-XXXX): <title>` | `fix(story-0061): correct off-by-one in pagination` |
| Release | `release(prd-XXXX): vX.Y.Z` | `release(prd-0007): v1.7.0` |
| Docs | `docs(prd-XXXX): <desc>` | `docs(prd-0007): update README usage` |
| Maintenance | `chore: <desc>` | `chore: bump version to 0.0.4` |

All paths above are relative to `[PROJECT_FOLDER]/`.

---

## Helper Scripts

None. All pipeline logic is handled directly by agents. The `scripts/` directory is not used.
