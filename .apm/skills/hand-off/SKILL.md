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

Version: 1.0 (2026-11-21)

Give a task to another agent. The note of the work stays in work-ledger. This skill only says how to pass it on.

## Before you send
- Use work-ledger. For this skill, the one ledger is in the project you have open: `<PROJECT_FOLDER>/ledgers/<agent-name>/ledger.md`. `PROJECT_FOLDER` is that project. `agent-name` is the same name used in the message. Create `ledgers/<agent-name>/` on first use. Add lines only. Do not also write `/home/box/ledgers`, and do not start a second ledger.
- The task ID never changes when the task moves. Copy it. Do not make a new one because the other agent uses a different tool.
- A new goal is not a hand-off. If the work splits into a new task, stop. Start that task under work-ledger, and name this task ID as the parent.
- The agent name is the ledger folder name. Two agents need two names, even on the same tool. Use lowercase letters, digits, and hyphens.
- If you do not know the other agent's ledger name, stop. Do not guess it.

## The task ID check
The task ID is a SHA-256 fingerprint of one exact line. SHA-256 is a fingerprint made from text: the same text always gives the same fingerprint, and any change gives a different one.

The line is the one work-ledger already uses:

`<origin agent name>|<start time>|<goal in one line>`

The origin agent name is the `<bot-name>` from work-ledger: the ledger folder name, not a display name. Copy the origin agent, the start time, and the goal character for character from the task's start entry. Do not trim them, translate them, or rewrite the time. Join them with one `|` between parts and no space around that `|`. Do not add a line break at the end.

Hash that line as UTF-8 text (text stored as bytes). The task ID is the 64 lowercase hex characters from SHA-256. Hex characters are 0-9 and a-f. A short label made up by a tool is not a task ID.

Check it yourself before you send. One way, with no extra newline:

```text
printf '%s' '<ID input>' | sha256sum
```

If that command is missing, use `shasum -a 256` the same way. Read only the first 64 hex characters. If they do not match the task ID, stop. Do not send the message, and do not invent a new ID.

This check proves the ID belongs to this task. It does not hash the later sentences. Those sentences still travel in the message, but they are not part of the ID.

## Ledger words
The skill names use a hyphen. The ledger step names do not.

| Moment | Ledger step | Who writes it |
|---|---|---|
| You give the work | handoff | Sending agent, before the message is delivered |
| You accept the work | received | Receiving agent, before any work |
| You return the work | handback | Receiving agent, using hand-back |
| You accept the return | received back | Original agent, using hand-back |

## The message
The message is the whole hand-off. It is plain text. It is the same for every agent. Do not add a wrapper. Do not add or drop fields to suit one tool. Do not use a fixed list of tools.

The first line is the task ID alone. Then:

```text
<full task ID, 64 lowercase hex characters>
Task ID: <same full task ID>
Short ID: <first 12 characters of the task ID>
ID input: <origin agent>|<start time>|<goal in one line>
Origin agent: <agent that started the task>
Start time: <same start time, copied exactly>
Goal: <same one-line goal, copied exactly>
Kind: hand-off
From: <sending agent name>
From tool: <free-text tool name>
To: <receiving agent name>
To tool: <free-text tool name>
Done in plain words:
- <what is already finished, in a few short everyday sentences>
- <what is not finished>
Must do or check:
- <one action per line, in everyday words>
Do not:
- <limits. Never include secrets or personal details>
Inputs:
- <files, links, or facts the receiver needs>
Evidence:
- <ledger path and the handoff entry time>
- <file path, or "pasted, no shared file">
Legend:
- <each hard word used above, then what it means>
Next: Run the hand-off skill. Check the fingerprint before any work. Then add a received entry. Return with the hand-back skill. Do not create a new task ID.
```

`From tool` and `To tool` are free text. Write the tool's ordinary name, such as GitHub Copilot, OpenCode, Claude Code, Grok Bot, Hermes, OpenClaw, or another agent. Those names are examples, not a list you must pick from.

## Plain words
`Done in plain words` is required. Say what work is already done, in concise layman English. Short sentences. One idea each.

Use an everyday word when you can. If a technical word is necessary, keep it and add one legend line that says what it means. The legend is part of the message. Do not assume the reader knows the word.

## Write the ledger entry first
Add this to your own ledger before you deliver the message. Use the short ID in the heading. Put the full task ID in the body.

```text
### <YYYY-MM-DD HH:MM with time zone> | <short ID> | handoff
- Work done: Gave this task to <receiving agent>. Full task ID: <full task ID>. From: <sending agent>. To: <receiving agent>.
- Evidence: <file path, or where it was pasted>
- Result: Message written. Fingerprint checked.
- Decision: Same task ID, because the goal did not split.
- Next: <receiving agent> checks the fingerprint, adds received, does the work, then runs hand-back.
```

If an open handoff of this task ID to this same agent already exists, do not add another. Send the same message again.

## How to deliver
Pass the same message to any agent:

1. Paste it as the whole chat message, or write that same text to `handoffs/<short ID>-to-<receiving agent>-handoff.md` and give the other agent that file.
2. The file is a copy of the message, not a ledger. Do not add status lines to it.
3. Only when both sides are GitHub Copilot, and that app can message another session, you may also send the same text as a session message. That copy is not the record. Do not use a Copilot session message for any other agent.

Do not change the message for the tool. Do not write the other agent's ledger.

If delivery fails, add a correction under work-ledger and send the same message again.

## When you receive a hand-off
1. If the first line is not 64 lowercase hex characters, reject the message. Do not start work.
2. Rebuild the ID input from `Origin agent`, `Start time`, and `Goal`, joined with `|`. It must match the `ID input` line exactly.
3. Hash that ID input as UTF-8 with SHA-256, as above. If the 64 hex characters do not match `Task ID` and the first line, reject the message. Do not start work, and do not make a new task ID.
4. Check `Short ID` is the first 12 characters of the task ID. If not, reject the message.
5. Add a received entry to your own ledger before any other work:

```text
### <YYYY-MM-DD HH:MM with time zone> | <short ID> | received
- Work done: Accepted the handoff. Full task ID: <full task ID>. From: <sending agent>. To: <this agent>. Fingerprint matched.
- Evidence: <file path, or "pasted message">
- Result: No work done yet.
- Decision: Reused the task ID. Did not start a new one.
- Next: Do the requested work, then run hand-back.
```

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
- Does `Done in plain words` say what is already finished, with a legend for any hard word?
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
- 1.0 (2026-11-21): first version.
