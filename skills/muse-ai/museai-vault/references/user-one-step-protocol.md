# User one-step protocol — read this before talking to the user

This is the protocol that prevents the resets that happened repeatedly
in the original rebuild. For a non-technical user, explaining this system to other AIs
is hard, and multi-step instructions cause overwhelm. The assistant's job is to absorb the
complexity, not to hand it over.

## The rule
One simple action at a time, in plain language, with the assistant
doing everything else. Never more.

## How to give a step
1. Say what the step is, in one plain sentence. No background, no
   alternatives, no "by the way".
2. If the step needs the user to run a command, give exactly one
   command, single-line, copy-paste ready, on its own. Never give
   two commands in one message as "step 1 and step 2".
3. Wait. Do not give the next step until the user confirms this step
   is done, or shows you its output.
4. Confirm the step yourself, in plain language: "Good, that step is
   done." Then, and only then, give the next one action.
5. If the step needs the user to tap, sign in, or authorise something
   in a dashboard, say exactly where to tap, in plain words, and
   nothing else. Example form, not a script: "Open the Cloudflare
   dashboard, tap Continue with Google, and tell me when you see
   the home page." Do not add tunnel names, policy names, or header
   names to a user step unless the user must type them, and then
   give them exactly as shown, one at a time.

## Commands for the user — single-line only
- Every command the user runs must be ONE line. Chain with `&&`
  on that one line if needed. Never a heredoc, never a multi-line
  block, never a script pasted as several lines. Multi-line pastes
  fail silently on the user's terminal: no output, no error,
  nothing runs. A single long line works.
- After a file write or a service change, verify with a second
  single-line command that prints a short, distinctive value, for
  example a line count or a service state. "No output" is not a
  pass; it usually means nothing ran.
- Never ask the user to type a secret, a token, or a key into a
  terminal command. Secrets go only on a secure page, in the
  relevant AI's own private chat, never in a terminal, never in
  chat, never in a screenshot sent to another AI.

## When the user says they are overwhelmed
Stop immediately. Do not continue the current flow, do not explain
why the step matters, and do not re-pitch the step.
Say, in plain language, that the hard part is done by you, and
restart with one tiny action only. Example form:
"You do not need to understand this part. I will do everything
else. Your only next step is this one thing: [one action]."
If the user says they are overwhelmed, that is a reset
signal, not a request for more detail.
Reset, do not explain.

## What the user must do themselves, and what they must not
The user must do only these kinds of things, one at a time:
- Authorise a dashboard login with Google sign-in.
- Run a single-line console command on a box, when the assistant
  cannot sudo there remotely.
- Enter a value on a secure page, in the relevant AI's own private
  chat, never in a message.
- Save the root token and unseal keys offline, in their own password
  manager, from the box 1 master-material copy, without pasting the
  output or a screenshot into chat.
The user must never be asked to:
- Explain this system to another AI.
- Copy a token from one AI's chat to another's.
- Paste a multi-line block, a script, or a token into a terminal.
- Decide between technical routes (for example, Route A, B, or C)
  without a one-line recommendation from the assistant first, with
  a clear pick and a short reason, and with the assistant ready to
  do the chosen route itself.

## Example: a good user step, and a bad one
Good, one step at a time:
"Your only next step is this one command, on the box 1, as the
box user. Copy and paste this one line, then tell me what it prints."
Then the command, single-line, alone. Then wait.
Bad, never do this:
"Here are the five steps: first do X, then Y, then Z, and if that
fails try A or B, and also save C and D, and tell the other AIs E."
That message is what caused the resets. Do not write it again.

## A worked sequence, sent one message at a time, never together
The following is an example of how a CA swap is actually walked
through. Send message 1 alone, wait for confirmation, then send
message 2 alone, and so on. Never send all three together as a list.
Message 1, alone: "Your only next step is to open the box 1
console, as the box user, and tell me when you are there. Nothing
else yet."
Message 2, alone, after confirmation: "Your only next step is this
one command. Copy and paste this one line, then tell me what it
prints." Then the single-line command, alone. Then wait.
Message 3, alone, after the command output is confirmed: "Good,
that step is done. Your only next step is to tell me the hostname
you see, so I can verify the box. Nothing else yet."
That is the whole pattern. If any message in the sequence contains
two actions, split it before sending it.

## The assistant's side of the bargain
While the user does one step, the assistant does all of this
without asking the user to do it: research, design, dashboard work
that does not need the user's login, signing, SSH tests, board
pulls and pushes, verification, and writing the next one-step
message. If a step can be done by the assistant, it must be done
by the assistant, even if it is slower. The user's time and attention
are the scarce resource, not the assistant's.
