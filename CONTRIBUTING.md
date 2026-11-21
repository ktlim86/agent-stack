# How to change a skill

Every skill edit goes through a pull request (a merge request). Do not push to `main` directly.

## 1. Create a branch

From `main`, create a branch named `skill/<skill-id>-<short-change>`.

Example: `skill/deep-review-premortem-wording`

## 2. Edit the skill

- Edit only that skill's file: `.apm/skills/<skill-id>/SKILL.md`
- Bump the `Version:` line:
  - Minor change: add 0.1 (for example 1.0 becomes 1.1)
  - Breaking change: add 1.0 (for example 1.1 becomes 2.0)
- Add a change log line with the new version and the date (`YYYY-MM-DD`)

## 3. Open a pull request

Open a pull request against `main` and fill in every item on the pull request template.

## 4. Review

The reviewing role runs the `deep-review` skill on the change and posts the verdict on the pull request.

## 5. Approve and merge

The user approves and merges the pull request. No direct pushes to `main`.

## 6. After the merge: release and sync

1. Open a short follow-up pull request that updates `CHANGELOG.md` and bumps the version in `apm.yml`:
   - Patch (for example 1.0.0 to 1.0.1) for fixes
   - Minor (for example 1.0.0 to 1.1.0) for a skill change or a new skill
   - Major (for example 1.0.0 to 2.0.0) for a breaking change
2. After that pull request is merged, cut a repository release and tag it (for example `v1.1.0`). Do not tag individual skills.
3. Sync the changed skill into the Grok Bot skill library from this repository. This repository is the master copy.
