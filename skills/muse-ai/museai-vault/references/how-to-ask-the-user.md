# How to ask the user for what you need — protocol for other AIs

This protocol is for any AI that needs something from the user during
onboarding, signing, or recovery. It applies to every AI, including
the coordinating AI. It exists because, in the original rebuild,
the user was asked for several things at once, in technical language,
and had to reset repeatedly. The protocol below is the fix.

## The five rules
1. One thing at a time. Never ask for two values, two entries, or a
   value plus a dashboard step in the same message.
2. Name the exact secure entry. Not "your credentials", not "the
   token", but the exact entry name as it appears in that AI's own
   private chat, for example "Vault token entry" or "Access
   Client-Id entry". If the AI's entry names differ, use that AI's
   names, and say so.
3. Say what it feeds, in plain language. For example: "This entry
   feeds one header, the Vault token header, for your sign request
   only. It does not feed the Access gate, and it does not feed
   SSH directly." A user who knows what a value feeds can spot a
   wrong-field error before submitting it.
4. Say what shape it should be, and where to get it, without ever
   asking for the value itself. Use `token-shapes.md` for the shape
   language. Sources, exactly:
   - Vault token: from the box 1 master-material copy, per-AI token
     file, handed privately by the user through the secure entry
     flow. Never from an old chat copy, never from a flagged source,
     never from another AI.
   - Access Client ID and Secret: from the Cloudflare dashboard
     only, Service Tokens, at creation, first and second fields of
     the one-time dialog. Secret shown only once. Never from chat.
   - Root token and unseal keys: from the user's own password
     manager, offline, never in chat, never on the board, never in
     a file. The user does not hand these to an AI, except through
     a secure entry the coordinating AI explicitly opens for a
     re-issue, and then only if the user approves that one step.
5. Say where the value goes, and where it must never go. "Enter it
   only on the secure page for that entry, in this private chat.
   Never in a chat message, never in a file, never on the board,
   never in a terminal command, never in a screenshot sent to
   another AI." Then stop. Do not add a second request.

## The exact form of a request
Use this form, one request per message, filling only the bracketed
parts, with no extra requests added:
"Please open [exact secure entry name] for me, one at a time.
This entry feeds [header or purpose, plain language].
The value you will enter should look like [shape, from
token-shapes.md, fake example only if the user asks for a shape
example, and labelled DO NOT ENTER].
You get this value from [exact source: Cloudflare dashboard, or
the box 1 token file, or your password manager].
Please enter it only on the secure page for that entry, never in
a chat message, never in a file, and never on the board.
Please tell me only that it is submitted, with no values, and I
will do the next step."
After the user confirms submission, with no values, the AI does the
next step itself, and only then asks for the next thing, if any.

## What never to ask
- Never ask the user to paste a value in chat, "just to check it".
  Shape checks are done by describing the shape, not by pasting
  the value. A Client ID pasted once to check its shape was a
  mistake that must not be repeated, even though a Client ID alone
  cannot authenticate without its Secret.
- Never ask the user to put a value in a file, on the board, or in
  a shared note, even a file with restricted permissions, unless
  that AI's own approved durable place explicitly allows it and the
  user has approved that place for that AI. A peer AI's exception
  does not count.
- Never ask the user to explain the system to another AI, to copy
  a value from one AI's chat to another's, or to decide a technical
  route. The AI that needs the thing writes the one-step request
  itself; the user only submits the value on a secure page.
- Never ask for a root token or unseal keys in chat, for any reason,
  including "recovery". Recovery uses the init file on the vault
  and on the box 1, and the user's offline password-manager copy,
  run from inside the vault server, not a pasted copy.

## If the user is overwhelmed, or the request was wrong
- If the user says they are overwhelmed, stop the credential flow
  immediately, reset to one step, and follow
  `user-one-step-protocol.md`. Do not continue asking while the
  user is overwhelmed.
- If the user enters a value in the wrong field, do not submit and
  debug. Tell them to close the dialog without saving, if possible,
  and start that one entry again with the correct source and shape.
  See the wrong-field section in `token-shapes.md`.
- If the AI's secure entry system cannot combine several entries
  into one request (a single-surrogate limit), do not ask the user
  for the same values again in a different form. Report the limit
  plainly, with no values, and ask the coordinating AI for a route
  that fits the limit, such as the single-credential variant. See the Cloudflare
  skill appendix for that variant. Asking the user to re-enter values will not fix
  a tool limit.

## After all entries are submitted
Do not ask the user for anything else about credentials. Run the
sign test, the SSH tests, and the owner notification yourself, and
report back only success or the exact failing step, with no values.
If a step fails at the gate, report which header was missing or
rejected, in words, not values, so the coordinating AI can fix the
policy or the route. Do not ask the user to fix a policy; that is
dashboard work for the coordinating AI.
