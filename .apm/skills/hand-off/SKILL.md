---
name: hand-off
description: >-
  Use when giving an existing task to any other agent. The tool name is free
  text, so this covers GitHub Copilot, OpenCode, Claude Code, Grok Bot, Hermes,
  OpenClaw, and any other agent. The task ID is a SHA-256 fingerprint the
  receiver can check again. Writes the work-ledger handoff entry. Does not
  create a second ledger.
---
# hand-off

Version: 1.1 (2026-11-22)

Give a task to another agent. The note of the work stays in work-ledger. This skill only says how to pass it on.

## Ledger format
The skill names use a hyphen. The ledger step names do not.

```markdown

# Revision history

| Created Datetime | Revision | Remarks |
|---|---|---|
| 2026-11-21 00:00 +0700 | 1.0 | Updated ledger to include handoff to receiving agent and handback to sending agent. Added SHA-256 fingerprint check for task ID xxxxxxx. |

# Ledger Records

### Write the ledger entry first
Add this to your own ledger before you deliver the message. If an open handoff of this task ID to this same agent already exists, do not add another. Send the same message again.

| Created Datetime | Receiver | Receiver tool | Sender | Sender tool | Type | Task ID | Remarks |
|---|---|---|---|---|---|---|
| 2026-11-21 00:00 +0700 | cursor | cursor | Limsuwanmethwat | Grok Bot | xxxxxxx | hand-off | Handoff of task with SHA-256 fingerprint check. |
| 2026-11-21 10:00 +0700 |  Limsuwanmethwat | Grok Bot | cursor | cursor | xxxxxxx | hand-back | Handback of task with SHA-256 fingerprint check. |

## Ledger Records Details

### Task ID: xxxxxxx <sha256 fingerprint of the task>

Replace hyphen with numbered list for clarity:
- Short ID: xxxxxxx <first 12 characters of the task ID>
- Sender agent: Limsuwanmethwat
- Sender tool: Grok Bot
- Receiver agent: cursor
- Receiver tool: cursor
- Created time: 2026-11-21 00:00 +0700
- Goal: To request for <SUMMARY OF THE TASK>. 
- Kind: hand-off
- Requested work: 
  - Problem statement: <DETAILS OF THE PROBLEM OR TASK TO BE HANDED OFF>
  - Must do or check: <LIST OF ACTIONS OR CHECKS REQUIRED BY THE RECEIVER>
  - Do not: <LIST OF LIMITS OR RESTRICTIONS FOR THE RECEIVER>
  - Legend: <EXPLANATION OF ANY HARD WORDS USED IN THE MESSAGE>
  - Inputs: <FILES, LINKS, OR FACTS THE RECEIVER NEEDS IF ANY>
  - Evidence: <LEDGER PATH AND THE HANDOFF ENTRY TIME IF ANY>
```

The fingerprint check is mandatory. The receiving agent must verify the SHA-256 fingerprint of the task ID before starting any work. If the fingerprint does not match, the receiving agent must reject the handoff and not start any work. The fingerprint shall shall use the text content marked below. e.g `sha256 <sender agent>|<sender tool>|<receiving agent>|<receiving tool>|<goal in one line>|<created time>|<type (i.e hand-off)>`. The fingerprint check is a security measure to ensure that the task ID is valid and has not been tampered with.

`Sender tool` and `Receiver tool` are free text. Write the tool's ordinary name, such as GitHub Copilot, OpenCode, Claude Code, Grok Bot, Hermes, OpenClaw, or another agent. Those names are examples, not a list you must pick from.

## Before you send
- For this skill, the one ledger is in the project you have open: `<PROJECT_FOLDER>/ledgers/<agent-name>/ledger.md`. `PROJECT_FOLDER` is that project. if in doubt of the `<PROJECT_FOLDER>`, ALWAYS ASK THE USER. DO NOT ASSUME! `agent-name` is the same name used in the message. Create `ledgers/<agent-name>/` on first use. Add lines only. Do not start a second ledger without asking the user!
- The task ID never changes when the task moves. Copy it. Do not make a new one because the other agent uses a different tool.
- A new goal is not a hand-off. If the work splits into a new task, stop. Start that task under work-ledger, and name this task ID as the parent.
- The agent name is the ledger folder name. Two agents need two names, even on the same tool. Use lowercase letters, digits, and hyphens.
- If you do not know the other agent's ledger name, stop. Do not guess it.
- Check it yourself before you send. One way, with no extra newline.

## Plain words
`Done in plain words` or use `simple-english` skill is required. Say what work is already done, in concise layman English. Short sentences. One idea each.

Use an everyday word when you can. If a technical word is necessary, keep it and add one legend line that says what it means. The legend is part of the message. Do not assume the reader knows the word.

## How to deliver
Pass the same message to any agent:

1. Paste it as the whole chat message, or write that same text to `handoffs/<short ID>-to-<receiving agent>-handoff.md` and give the other agent that file.
2. The file is a copy of the message, not a ledger. Do not add status lines to it.
3. Only when both sides are GitHub Copilot, and that app can message another session, you may also send the same text as a session message. That copy is not the record. Do not use a Copilot session message for any other agent.

Do not change the message for the tool. Do not write the other agent's ledger.

If delivery fails, add a correction under work-ledger, do a `sha256` hash again as updated the new task id and send the same message again.

## When you receive a hand-off
1. If the first line is not 64 lowercase hex characters, reject the message. Do not start work.
2. Rebuild the task ID input using the highlighted fingerprint above.
3. Hash that ID input as UTF-8 with SHA-256, as above. If the 64 hex characters do not match `Task ID` and the first line, reject the message. Do not start work, and do not make a new task ID.
4. Check `Short ID` is the first 12 characters of the task ID. If not, reject the message.
5. Add a received entry to your own ledger before any other work. The received entry format must be the same format highlighted in section `Ledger Records Details`.
6. Do the work. Log each step with work-ledger, under this same task ID.
7. When the work is done, blocked, or stopped, run hand-back. Silence does not close the handoff.

## Rules
- Every handoff stays open until a matching hand-back is received.
- One task ID can have more than one open handoff if each goes to a different agent. Each needs its own hand-back.
- No secrets or personal details.

## Check before sending
- Did you recompute the SHA-256 fingerprint, and does it match the task ID?
- Is that full task ID the first line?
- Is the tool name free text, not a code from a fixed list?
- Does `Done in plain words` or use `simple-english` skill say what is already finished, with a legend for any hard word?
- Is the handoff entry already in your ledger?
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
- 1.1 (2026-11-22): Ledger format, SHA-256 fingerprint, and project-folder ledger path.
- 1.0 (2026-11-21): first version.
