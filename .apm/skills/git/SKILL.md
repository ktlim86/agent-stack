---
name: git
description: >-
  Use when the user wants to start, save, or finish work in git: create a
  feature branch, commit on that branch, and open a pull request or merge
  request. Never commit or push to main.
---
# git

Version: 1.0 (2026-11-21)

## What this skill does
Start each feature on its own branch, save the work there, and finish by asking for a review. Do the git steps yourself when the user asks. Do not only describe them.

**Main points**
- One feature, one branch, created with `git checkout -b <branch_name>`.
- Check-in means a commit on that branch, then a push of that branch. It never means a commit or push to main.
- Finished work becomes a pull request or merge request. Do not merge it into main unless the user explicitly says to merge.

## Legend
- **Branch:** a named line of work, kept separate from the shared finished line.
- **Checkout:** switch to a branch, or create one and switch to it.
- **Commit (check-in):** save a snapshot of the current files on the current branch, with a short message that says what changed.
- **Push:** send that branch's commits to the shared copy of the repository.
- **Remote:** the shared copy, usually named `origin`, on GitHub or GitLab.
- **Main:** the shared branch everyone treats as the current finished product. Some repositories call this the default branch and name it `master` or something else. Treat that branch the same way: never check in to it.
- **Pull request (PR):** GitHub's name for a request to review a branch and bring it into main.
- **Merge request (MR):** GitLab's name for the same request. Use the name that matches the host.
- **Fetch:** download the latest remote history without changing your files.
- **Conflict:** two people changed the same lines. The feature branch must be fixed before review can finish. Never fix that by editing main.

## Hard rules
- Never commit while the current branch is main, or any other default or release branch.
- Never push commits directly to main. `git push origin main` is forbidden.
- Never force-push main. Never use `--force` or `--force-with-lease` against main.
- Never rewrite commits that have already been pushed (no amend, rebase, or reset of those commits) unless the user asks. Even then, never rewrite main.
- Do not merge the request into main unless the user explicitly says to merge.
- One feature per branch. Do not pile unrelated work onto a branch that is already open for review.
- No secrets: no passwords, keys, tokens, or real `.env` values in a commit.
- If a step would break one of these rules, stop and say so. Do not look for a workaround.

## 1. Start a feature
1. Fetch first, so the branch starts from current main, not a stale copy:

```bash
git fetch origin
git status
```

2. Read the current branch from `git status`. If it is main and there are uncommitted changes, do not commit them. Create the feature branch first. Those changes come with you:

```bash
git checkout -b <branch_name>
```

3. If the working tree is clean, still create the branch from the fetched main, not from an old local main:

```bash
git checkout -b <branch_name> origin/main
```

4. Name the branch so a reader can tell what it is. Use short lowercase words joined by hyphens, such as `add-login-check`. If the repository's contributing guide names a pattern, follow that pattern.
5. Confirm `git status` shows the new branch before any edit or commit.
6. Do not start a second feature on the same branch. Finish or park the first one, then check out a new branch for the next feature.

## 2. Check in the work
Stay on the feature branch. Before every commit, run `git status` and `git diff`. If the branch is main, stop and go back to section 1.

- Keep commits small. One idea per commit.
- Write the message in plain language, as an instruction: "Add a login check", not "wip" or "updates".
- Say why in a second paragraph only when the reason is not obvious from the change.
- If the project already uses a message style, such as `feat:` or `fix:`, follow that style.
- Stage only the files that belong to this commit. Read the list before committing. Do not use a blanket add if it would pick up secrets, local notes, or unrelated files.
- Commit on the feature branch, then push that branch only:

```bash
git push -u origin <branch_name>
```

- If the push is rejected because someone else added commits to the same branch, fetch and merge that remote branch into yours, then push again. Do not force-push a branch someone else is using.
- Do not amend or rebase a commit after it has been pushed, unless the user asks.

## 3. Ask for the merge
When the user says the work is finished, do not merge. Prepare the branch and open the request.

1. Fetch, then see whether main has moved:

```bash
git fetch origin
git status
git log --oneline HEAD..origin/main
```

2. If main has new commits, merge `origin/main` into the feature branch. Do this on the feature branch, never by checking out main and merging the feature in. Do not rebase a branch that has already been pushed, unless the user asks.
3. If the merge conflicts, fix the conflicts on the feature branch, then commit the merge. If a conflict is unclear, stop and ask. Do not guess.
4. Run the project's usual checks when they exist, and say what passed or failed.
5. Push the feature branch with a normal push. No force.
6. Open a pull request on GitHub, or a merge request on GitLab, with main as the target. If one is already open for this branch, update it instead of opening a second one.
7. Write a description a reviewer can use without reading the whole diff:
   - what changed
   - why
   - how to check it
   - anything still open, or "nothing open"
8. If the repository has a pull request or merge request template, fill every section. Leave a section as "N/A" only when it truly does not apply.
9. Give the user the link and stop. The request is now waiting for review.

## 4. Help with the open request
- Answer review comments with a short, direct reply.
- Fixes go on the same feature branch as new commits. Push those commits to the same branch. Do not open a new request for a fix to this feature.
- If checks fail, fix them on the feature branch and push.
- If main moves again before review finishes, merge `origin/main` into the feature branch and push.
- Update the description if the work changed in a way a reviewer needs to know.
- Do not resolve a review thread by hiding the comment. Fix the point, or say why it should stay as it is.

## 5. Merge only when the user says so
Merging into main is a separate, explicit step. "Open the request", "finish the feature", and "check in" do not mean merge.

When the user explicitly says to merge:
- Confirm the request targets main, the required checks have passed, and the requested review is done.
- Use the project's normal merge method. If it has no stated method, prefer a squash merge so main gets one clear commit.
- Do not skip required reviews or checks. Do not force the merge.
- After a successful merge, report the result. Delete the feature branch only if the user asks, or if the host is already set to delete it.

If the user has not said to merge, stop at the open request.

## Stop and ask
Stop instead of guessing when:
- The branch name is not obvious and the repository has no naming rule.
- The current branch is main and creating a branch would leave unrelated changes behind.
- A commit would include a secret or a file you cannot tell is safe.
- A conflict, a failed check, or a review comment needs a product decision.
- The user asks to rewrite pushed history, force-push, or merge, and the request is ambiguous.

## Change log
- 1.0 (2026-11-21): first version. Feature branches only, check-in on that branch, and a pull request or merge request instead of a direct check-in to main.
