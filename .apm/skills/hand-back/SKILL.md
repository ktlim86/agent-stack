---
name: hand-back
description: >-
  Use when returning a handed-off task to the agent that sent it. Works for any
  agent, including GitHub Copilot, OpenCode, Claude Code, Grok Bot, Hermes, and
  OpenClaw. Uses the same SHA-256 task ID and the same plain-language rules as
  hand-off. Does not create a second ledger.
---
# hand-back

Version: 1.0 (2026-11-21)

Send the task back to the agent who gave it to you. The note of the work stays in work-ledger. This skill only says how to return it.

## Before you return
- Use work-ledger. For this skill, add lines only to your own ledger in the project you have open: `<PROJECT_FOLDER>/ledgers/<agent-name>/ledger.md`. `PROJECT_FOLDER` is that project. `agent-name` is the same name used in the message. Create `ledgers/<agent-name>/` on first use. Do not also write `/home/box/ledgers`, and do not start a second ledger.
- Reuse the task ID from the hand-off message. Do not create a new one.
- You need an open handoff to answer: the same task ID, your agent as To, and no matching handback yet. If you cannot find that handoff, stop. Do not invent a return.
- A blocked or partial result is still a hand-back. Silence leaves the handoff open.
- Returning work is not a new hand-off. Do not change the goal. If more work is needed later, that is a new hand-off of the same task ID, after this return is received.

## The same task ID check
Use the hand-off check. Do not make a second fingerprint.

The ID input stays:

`<origin agent name>|<start time>|<goal in one line>`

Copy `ID input`, `Origin agent`, `Start time`, `Goal`, and `Task ID` from the hand-off message. The origin agent name is the ledger folder name from work-ledger, not a display name. Do not reformat them.

Before you send, hash the ID input again as UTF-8 with SHA-256 (a fingerprint made from text). One way, with no extra newline:

```text
printf '%s' '<ID input>' | sha256sum
```

If that command is missing, use `shasum -a 256` the same way. The first 64 hex characters must match the task ID. Hex characters are 0-9 and a-f. If they do not match, stop. Do not send the return, and do not invent a new ID.

This check proves the return is for the same task. It does not hash the later sentences.

## Ledger words
This skill writes `handback` and `received back`. It does not write `handoff` or `received`.

## The message
The message is the whole hand-back. It is plain text. It is the same for every agent. Do not add a wrapper. Do not add or drop fields to suit one tool.

The first line is the same task ID. Then:

```text
<full task ID, 64 lowercase hex characters>
Task ID: <same full task ID>
Short ID: <first 12 characters of the task ID>
ID input: <same ID input as the hand-off>
Origin agent: <same origin agent>
Start time: <same start time>
Goal: <same one-line goal>
Kind: hand-back
From: <agent that did the work>
From tool: <free-text tool name>
To: <agent that sent the hand-off>
To tool: <free-text tool name>
Matches handoff: <time of that handoff entry>
Done in plain words:
- <what you did, including failed tries, in a few short everyday sentences>
- <what you did not finish>
Result: <done, partial, blocked, or dropped, in everyday words>
Still open:
- <anything the original agent still owns, or "nothing">
Evidence:
- <files, links, or ledger entries>
- <file path, or "pasted, no shared file">
Legend:
- <each hard word used above, then what it means>
Next: Run the hand-back skill. Check the fingerprint. Add a received back entry. Do not create a new task ID.
```

`From` is the agent that received the work. `To` is the agent that sent it. That is the reverse of the hand-off message.

`From tool` and `To tool` are free text. Write the tool's ordinary name, such as GitHub Copilot, OpenCode, Claude Code, Grok Bot, Hermes, OpenClaw, or another agent. Those names are examples, not a list you must pick from.

## Plain words
`Done in plain words` is required. Say what you did, in concise layman English. Short sentences. One idea each.

Use an everyday word when you can. If a technical word is necessary, keep it and add one legend line that says what it means. The legend is part of the message.

## Write the ledger entry first
Add this to your own ledger before you deliver the message.

```text
### <YYYY-MM-DD HH:MM with time zone> | <short ID> | handback
- Work done: Returned this task to <original agent>. Full task ID: <full task ID>. From: <this agent>. To: <original agent>. Matches handoff: <time>.
- Evidence: <file path, or where it was pasted>
- Result: <the result, in everyday words>
- Decision: Same task ID. Fingerprint checked again.
- Next: <original agent> checks the fingerprint, adds received back, then continues or ends the task under work-ledger.
```

One handback closes one handoff. If you were given the same task twice, return each handoff on its own, with its own time in `Matches handoff`.

## How to deliver
Pass the same message to any agent. Do not change it for the tool.

1. Paste it as the whole chat message, or write that same text to `handoffs/<short ID>-to-<original agent>-handback.md`.
2. The file is a copy of the message, not a ledger. Do not add status lines to it.
3. Only when both sides are GitHub Copilot, and that app can message another session, you may also send the same text as a session message. That copy is not the record. Do not use a Copilot session message for any other agent.

Do not write the original agent's ledger. Do not mark the task ended for them.

## When the original agent receives it
1. If the first line is not the open task's 64-character ID, reject the message. Do not close the handoff.
2. Check `ID input`, `Origin agent`, `Start time`, and `Goal` match the open task. Hash the ID input again. If the fingerprint does not match `Task ID`, reject the message. Do not make a new ID.
3. Check `Kind: hand-back`, and that From and To are the reverse of the open handoff.
4. Check `Matches handoff` names that handoff's time. If it does not, do not close a different handoff.
5. Add this to your own ledger:

```text
### <YYYY-MM-DD HH:MM with time zone> | <short ID> | received back
- Work done: Accepted the handback. Full task ID: <full task ID>. From: <returning agent>. To: <this agent>. Fingerprint matched.
- Evidence: <file path, or "pasted message">
- Result: <result copied from the message>
- Decision: That handoff now has a matching handback.
- Next: <continue the task, park it, or end it under work-ledger>
```

6. The handoff is closed only after this entry exists. A pasted message alone does not close it.
7. End the task only if its definition of done is met. Ending the task is a work-ledger step. It does not replace received back.

## Rules
- A handoff with no handback is still open.
- Do not create a task ID, a ledger, or a new message format on the way back.
- No secrets or personal details.

## Check before sending
- Did you recompute the same SHA-256 fingerprint, and does it match?
- Is that same task ID the first line?
- Is the tool name free text?
- Does `Done in plain words` say what you did, with a legend for any hard word?
- Does `Matches handoff` name the open handoff?
- Is the handback entry already in your ledger?

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
