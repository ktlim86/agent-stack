---
name: delegate-coding-cursor
description: Use whenever your work needs code written or changed (scripts, tests, analysis code, tools). You design and review; a Cursor coding agent, either a cloud agent or Cursor in the user's local Docker container (the user picks), writes the code to a set engineering standard on a branch and opens a pull request.
---

# Delegate coding to a Cursor coding agent

Version: 1.0 (2026-11-23)

You own the what and the why. A Cursor coding agent owns the how. Do not write production code yourself. Short throwaway checks of a few lines are fine.

## Choose where the code is written: ask the user first

Before each coding job, ask the user which option to use. Don't pick for them, and don't reuse an earlier answer unless the user said it applies to every job.

1. **Cursor cloud agent:** runs on Cursor's servers and works on a branch of the repository on GitHub. It can't reach local databases or private machines, so it tests with small sample data.
2. **Local Docker container:** Cursor's agent runs inside the user's own Docker container (for example a VS Code or Cursor dev container) on their computer. It can reach local data, but it runs on the user's machine and needs their approval for each command.

When you ask, say in one line what each option means for this job, for example whether the code needs local data to be tested.

For the local option:
- Work only inside the container and folder named in your instructions. Ask before anything outside it, before deleting files, and before pushing to GitHub.
- Work on a new branch, never on the main branch.
- The user's computer and container must be on and reachable. If they're not, tell the user and ask whether to wait or use the cloud option.

## How this fits with hand-off, hand-back and work-ledger

This skill says what to send and what standard to hold the code to. The hand-off skill says how to send it, the hand-back skill says how it comes back, and work-ledger records each step. Don't write a separate message format here.

- Coding agent ledger name: `cursor-cloud` for the cloud option, `cursor-local` for the local option. Receiver tool: `Cursor cloud agent` or `Cursor local agent`.
- Both ledgers live in the repository named in your instructions, at `ledgers/<agent-name>/ledger.md`. The coding agent commits its ledger lines and the hand-back file on its branch, so they show up in the pull request.

## Steps

1. **Write the hand-off packet, which is the coding brief.** Follow the hand-off skill, including the ledger entry and the SHA-256 fingerprint. Fill in its fields like this:
   - Goal: one line on what the code must do.
   - Problem statement: why the code is needed; inputs and outputs, including file paths, data shapes and units; the logic, with every formula written out and where it comes from; edge cases and what should happen with bad or missing input.
   - Must do or check: the engineering standard below, pasted in full; how to test it; the definition of done; commit your ledger lines and write the hand-back to `handoffs/<short ID>-to-<your agent name>-handback.md` on the branch.
   - Do not: write the sender's ledger; merge the pull request; touch live systems; put secrets or personal details in code.
   - Inputs: the repository, the branch name, and a small sample dataset or how to make one.
2. **Start one coding agent** on the option the user chose, with the packet as its whole first message, working on a new branch of that repository. One task ID goes to one agent. Don't start a second agent for the same work.
3. **Review rounds stay inside the open hand-off.** Read the pull request line by line against the packet: the logic and formulas, the tests, and the standard. Run the Deep review skill on it. Send every fix back to the same agent in one message, quoting the task ID. Fix rounds are not new hand-offs and get no new task ID. Log each round with work-ledger.
4. **Close with hand-back.** The coding agent sends its hand-back only when the pull request is final, or when it's blocked or stopped. Verify the hand-back as the hand-back skill says (check the fingerprint, then add your received entry) before you treat the code as done.
5. **Run it where the real data lives.** A cloud agent can't reach local databases or private machines. After the hand-back, run the code in the environment your instructions name, and record the commit used for every result.
6. **Pass it through the normal gates.** Never approve or merge your own pull request. Only the user merges unless your instructions say otherwise.

## Engineering standard (paste into every brief)

- Follow the SOLID design principles:
  - Single responsibility: each function, class and module does one job and has one reason to change.
  - Open/closed: add new behaviour by extending the code, not by editing working code.
  - Liskov substitution: a subclass must work anywhere its parent class works, without surprises.
  - Interface segregation: keep interfaces small, so no code depends on methods it doesn't use.
  - Dependency inversion: depend on abstractions, such as a storage interface, not on concrete details, such as one specific database.
- Don't Repeat Yourself (DRY): every piece of logic, formula or setting lives in one place. Reuse it instead of copying it.
- Meaningful names: variables, functions, classes and files say what they hold or do, so a reader understands them without comments. Use full words (`customer_count`, not `cc`; `calculate_total_price`, not `calc_tp`). No single-letter names except short loop counters. Follow the language's naming style (for Python, `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_CASE` for constants).
- Type hints on every function.
- A docstring on every module, class and function that says what it does, its inputs and outputs, and why it exists.
- A comment on every formula and every non-obvious step that says what it computes and why.
- No magic numbers. Settings and thresholds go in a config file, not in the code.
- A unit test for every function, including edge cases. All tests pass.
- Follow the repository's existing folder structure, naming and style.
- Pass linting (automatic style and error checks) and formatting.
- No secrets, personal names or emails in code, configs or commit messages.
- Results must be reproducible: fixed random seeds and pinned library versions.
- The pull request description explains what changed, why, how it was tested and any known limits.

## Using the quota well

- One clear, complete brief costs far less than many short back-and-forth messages.
- Keep fixes on the same agent instead of starting fresh.
- Don't paste code back into chat to rewrite it there. Send changes to the agent.
- Stop or close agents once their pull request is done.

## Change log

- 1.0 (2026-11-23): First version. User chooses a Cursor cloud agent or Cursor in a local Docker container for each job. Coding brief sent as a hand-off packet; engineering standard includes SOLID, DRY and meaningful names.
