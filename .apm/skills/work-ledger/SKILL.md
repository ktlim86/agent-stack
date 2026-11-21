---
name: work-ledger
description: >-
  Use on every task, by every bot, from start to finish. Append each step to
  your single ledger file as it happens, tagged with the task's SHA-256 task ID,
  so Deep review and show-me-your-work can check the work and the user can trace
  every task, handoff and handback.
---
# work-ledger

Version: 1.0 (2026-11-21)

## The file
- Each bot keeps one ledger file: /home/box/ledgers/<bot-name>/ledger.md
- Create it on first use. Never keep a second ledger anywhere else.
- Append only: add new entries at the end. Never edit, reorder or delete an entry.

## Task ID
- Every task gets one task ID when it starts: the SHA-256 hash (a fixed-length fingerprint made from text) of "<bot-name>|<start timestamp>|<goal in one line>".
- Write the full ID in the task's start entry. After that, use its first 12 characters as the short ID in every entry.
- The task ID never changes, even when the task moves to another bot. The receiving bot reuses it and does not create a new one.
- Work split into a new task gets a new ID, and its start entry names the parent task ID.

## When to append (mandatory)
1. Task start: the task ID, goal, definition of done, inputs and limits.
2. Each decision, with the options considered and why.
3. Each piece of work done, attempt or test, including failures and dead ends.
4. Each change of plan or assumption, and why.
5. Each handoff, handback or review (see below).
6. Task end: the outcome (done, dropped or parked) and anything still open.
Append at the moment it happens, not later from memory.

## Entry format
### <timestamp, YYYY-MM-DD HH:MM with time zone> | <task ID> | <step>
- Work done: what was done, in plain English.
- Evidence: links, file paths, sources or commands behind it.
- Result: outputs or numbers exactly as produced.
- Decision: what was decided and why (if any).
- Next: the next step and which bot owns it.

## Handoff and handback
- Handoff (giving work to another bot): the sending bot appends a "handoff" entry with the task ID, From: <sending bot>, To: <receiving bot>, what is handed over, what must be done or checked, and the evidence links. The message to the receiving bot starts with the task ID.
- The receiving bot appends a "received" entry with the same task ID, From and To, before doing any work.
- Handback (returning the work): the receiving bot appends a "handback" entry with the task ID, From: <receiving bot>, To: <original bot>, what was done, the result or verdict, and the evidence. The message back starts with the task ID.
- The original bot appends a "received back" entry with the same task ID.
- Every handoff must have a matching handback. A handoff with no handback is still open.

## Fixing a mistake
- Never edit the wrong entry. Append a "correction" entry with the same task ID, the timestamp of the entry being corrected, what was wrong, and the correct version.
- Any message to the user about a task starts with its task ID, so the user always knows which task it refers to.

## Rules
- Log failures and drops as fully as wins.
- Every number must trace to evidence in its entry.
- If it isn't in the ledger, it didn't happen. Reviewers treat unlogged work as not done.
- Never write secrets, passwords, keys or personal details.
- Plain, concise English, with a legend for any abbreviations used.

## Housekeeping (monthly)
- When: on the first entry of each new month, before writing it.
- Steps:
  1. Move the whole file unchanged to archive/ledger-<YYYY-MM of the month just ended>.md. Never trim or rewrite archived entries.
  2. Start a fresh ledger.md. Its first entry is a carry-over: each open task ID, its status, its next step, any open handoff, and a link to its last entry in the archive.
  3. Add one line to index.md: the archive file name, its date range, and every task ID it contains.
- Archives are kept, never deleted, unless the user says so.
- To find an older task, search index.md for its task ID, then open that archive.

## How other skills use it
- Deep review reads the ledger first, and fails the work if a step, evidence, attempt or matching handback is missing.
- show-me-your-work uses the ledger as its decision record; it doesn't keep a separate one.
- A handoff or approval can't close until its ledger entries are complete.

## Change log
- 1.0 (2026-11-21): first version.
