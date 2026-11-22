---
name: hand-back
description: >-
  Use when returning a handed-off task to the agent that sent it. The tool name
  is free text, so this covers GitHub Copilot, OpenCode, Claude Code, Grok Bot,
  Hermes, OpenClaw, and any other agent. The task ID is a SHA-256 fingerprint
  the receiver can check again. Writes the work-ledger hand-back entry. Does
  not create a second ledger.
---
# hand-back

Version: 1.1 (2026-11-22)

Send the task back to the agent who gave it to you. The note of the work stays in work-ledger. This skill only says how to return it.

## Ledger format
The skill name uses a hyphen. In this ledger, Type is `hand-back`.

Type comes before Task ID. Do not swap those two cells.

```markdown
# Revision history

| Created Datetime | Revision | Remarks |
|---|---|---|
| 2026-11-22 00:00 +0800 | 1.0 | Updated ledger to record the hand-back to the agent who sent the hand-off. Added SHA-256 fingerprint check for task ID xxxxxxx. |

# Ledger Records

### Write the ledger entry first
Add this to your own ledger before you deliver the message. If an open hand-back of this task ID to this same agent already exists, do not add another. Send the same message again.

| Created Datetime | Receiver | Receiver tool | Sender | Sender tool | Type | Task ID | Remarks |
|---|---|---|---|---|---|---|---|
| 2026-11-21 10:00 +0700 | Limsuwanmethwat | Grok Bot | cursor | cursor | hand-back | xxxxxxx | Handback of task with SHA-256 fingerprint check. |

## Ledger Records Details

### Task ID: xxxxxxx <sha256 fingerprint of this hand-back>

Replace hyphen with numbered list for clarity:
- Short ID: xxxxxxx <first 12 characters of the task ID>
- Sender agent: cursor
- Sender tool: cursor
- Receiver agent: Limsuwanmethwat
- Receiver tool: Grok Bot
- Created time: 2026-11-21 10:00 +0700
- Goal: <the same one-line goal as the open hand-off. Not a new goal.>
- Kind: hand-back
- Matches handoff: <created time and task ID of the open hand-off this closes>
- Returned work:
  - Done in plain words: <what is already finished, in short everyday sentences>
  - Result: <done, partial, blocked, or dropped>
  - Still open: <what the original agent still owns, or nothing>
  - Must do or check: <what the receiver must check before closing the hand-off>
  - Do not: <limits. Do not write the other agent's ledger. Do not invent a new goal.>
  - Legend: <each hard word, then what it means>
  - Inputs: <files, links, or facts, if any>
  - Evidence: <ledger path and this hand-back entry time>
```

The fingerprint check is mandatory. The receiving agent must verify the SHA-256 fingerprint of the task ID before any work. If the fingerprint does not match, the receiving agent must reject the hand-back and not start any work. The fingerprint uses the text below. For this skill the type is `hand-back`: `sha256 <sender agent>|<sender tool>|<receiving agent>|<receiving tool>|<goal in one line>|<created time>|<type (i.e hand-back)>`.

Hash that line as UTF-8. No extra newline. The task ID of this hand-back is those 64 lowercase hex characters. Compute it once from this return. The receiver must recompute it and reject a mismatch before any work.

The task ID does not change just because the tool changed. The tool names in the line are the tools named in this return. Do not make a new task ID because the other agent uses a different tool. Copy this task ID if you send the same return again.

A new goal is not a hand-back. The goal line is the open hand-off's goal. Do not rewrite it.

The open hand-off keeps its own task ID. Write that ID under `Matches handoff`. Do not replace it with this return's fingerprint. A tool change is not a reason to replace either ID.

For a return, Sender is the agent that did the work. Receiver is the agent that sent the hand-off. That is the reverse of the hand-off row.

`Sender tool` and `Receiver tool` are free text. Write the tool's ordinary name, such as GitHub Copilot, OpenCode, Claude Code, Grok Bot, Hermes, OpenClaw, or another agent. Those names are examples, not a list you must pick from.

## Before you send
- For this skill, the one ledger is in the project you have open: `<PROJECT_FOLDER>/ledgers/<agent-name>/ledger.md`. `PROJECT_FOLDER` is that project. if in doubt of the `<PROJECT_FOLDER>`, ALWAYS ASK THE USER. DO NOT ASSUME! `agent-name` is the same name used in the message. Create `ledgers/<agent-name>/` on first use. Add lines only. Do not start a second ledger without asking the user!
- You need an open hand-off to answer: you were the receiver, they were the sender, and no matching hand-back exists yet. If you cannot find that hand-off, stop. Do not invent a return.
- The task ID does not change just because the tool changed. Copy this return's task ID. Do not make a new one because the other agent uses a different tool.
- A new goal is not a hand-back. Do not change the goal. If the work splits into a new task, stop. Start that task under work-ledger, and name the open hand-off task ID as the parent. Returning work is not a new hand-off.
- A blocked or partial result is still a hand-back. Silence leaves the hand-off open.
- The agent name is the ledger folder name. Two agents need two names, even on the same tool. Use lowercase letters, digits, and hyphens.
- If you do not know the other agent's ledger name, stop. Do not guess it.
- Check the fingerprint yourself before you send. One way, with no extra newline:

```text
printf '%s' '<sender agent>|<sender tool>|<receiving agent>|<receiving tool>|<goal in one line>|<created time>|hand-back' | sha256sum
```

If that command is missing, use `shasum -a 256` the same way. Read only the first 64 hex characters. If they do not match the task ID, stop. Do not send the return, and do not invent a new ID.

Name the open hand-off under `Matches handoff`. That field points at the hand-off this return closes. It does not change this return's task ID.

## Plain words
`Done in plain words` or use `simple-english` skill is required. Say what work is already done, in concise layman English. Short sentences. One idea each.

Use an everyday word when you can. If a technical word is necessary, keep it and add one legend line that says what it means. The legend is part of the message. Do not assume the reader knows the word.

## How to deliver
Pass the same return to the agent who sent the hand-off. Do not change the message for the tool. Do not write that agent's ledger. Do not mark the task ended for them.

1. Paste the return as the whole chat message, or write that same text to `handoffs/<short ID>-to-<original agent>-handback.md` and give that agent the file.
2. The file is a copy of the message, not a ledger. Do not add status lines to it.
3. Only when both sides are GitHub Copilot, and that app can message another session, you may also send the same text as a session message. That copy is not the record. Do not use a Copilot session message for any other agent.

The first line of the message is the task ID: 64 lowercase hex characters. Then the Ledger Records Details for this return.

If delivery fails, add a correction under work-ledger, do a `sha256` hash again as updated the new task id and send the same message again.

## When you receive a hand-back
You are the agent that sent the hand-off. The sender of this message is the agent that did the work.

1. If the first line is not 64 lowercase hex characters, reject the message. Do not start work. Do not close the hand-off.
2. Rebuild the task ID input: `<sender agent>|<sender tool>|<receiving agent>|<receiving tool>|<goal in one line>|<created time>|hand-back`. Sender is the agent that did the work. Receiver is you.
3. Hash that input as UTF-8 with SHA-256. No extra newline. If the 64 hex characters do not match `Task ID` and the first line, reject the message. Do not start work, and do not make a new task ID.
4. Check `Short ID` is the first 12 characters of the task ID. If not, reject the message.
5. Check `Kind` is `hand-back`, and that Sender and Receiver are the reverse of the open hand-off. If `Matches handoff` does not name that hand-off, do not close a different one.
6. Add a received entry to your own ledger before any other work. The received entry format must be the same format highlighted in section `Ledger Records Details`.
7. The hand-off is closed only after that entry exists. A pasted message alone does not close it. End the task only if its definition of done is met. Ending the task is a work-ledger step. It does not replace the received entry.

## Rules
- Every hand-off stays open until a matching hand-back is received.
- One hand-back closes one hand-off. If you were given the same task twice, return each hand-off on its own.
- One task ID can have more than one open hand-off if each goes to a different agent. Each needs its own hand-back.
- The task ID does not change just because the tool changed. A new goal is not a hand-back.
- No secrets or personal details.

## Check before sending
- Did you recompute the SHA-256 fingerprint, and does it match the task ID?
- Is that full task ID the first line?
- Is the type `hand-back`, with no extra newline in the fingerprint input?
- Is the tool name free text, not a code from a fixed list?
- Is Sender the agent that did the work, and Receiver the agent that sent the hand-off?
- Does `Done in plain words` or use `simple-english` skill say what is already finished, with a legend for any hard word?
- Does `Matches handoff` name the open hand-off, without changing the goal?
- Is the hand-back entry already in your ledger?
- Did you avoid writing the other agent's ledger?

## Legend
- SHA-256: a fingerprint made from text. The same text always gives the same fingerprint.
- UTF-8: a common way to store text as bytes before the fingerprint is made.
- Hex: the digits 0-9 and letters a-f used to write the fingerprint.
- Ledger: the one running note for an agent. Add lines only.
- Hand-off: giving the task to another agent.
- Hand-back: sending the task back to the agent who gave it.
- Packet: the hand-off or hand-back message. The text is the same for every agent.

## Change log
- 1.1 (2026-11-22): Return skill follows the hand-off ledger, fingerprint, project-folder, and plain-language rules.
- 1.0 (2026-11-21): first version.
