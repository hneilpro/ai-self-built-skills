# AI onboarding messages — paste-ready, no values, no local paths

These messages are for the coordinating AI to send to another AI, or
for the user to paste into another AI's private chat. They refer to
"the user" and "the owner" only, never to the owner's real name, and
they carry no local paths from the coordinating AI's machine. They
contain no token, no secret, and no private key. The other AI's own
token is handed separately, privately, through that AI's secure entry
flow, never in the same message as these instructions, and never in
a message at all.

Replace `<role>` with that AI's own role only. Role format:
`<ai-name>-ssh`, for example `<ai-1-role>` or `<ai-2-role>`.
Never use another AI's role. In the optional coordination appendix
only, replace `<ai>` in the coordination message with that AI's own
name, if that coordination system requires it; the notification
body itself says role and location only.

## Message 1 — general onboarding (all AIs)
Paste this first, alone, before any credential step:
"Hi, please set up your access to <vault-hostname>, for role <role>
only. The vault is live, both boxes trust its new CA and are
Vault-only, and the old tokens and old CA no longer work.
Please generate your own ed25519 keypair for this vault only, keep
your private key private, and do not use any other AI's key, token,
or certificate. Generate it with this placeholder command, and
replace only the placeholders:
`ssh-keygen -t ed25519 -N "" -f <private-key-path> -C "<ai-name>-ssh vault-only" && chmod 0600 <private-key-path>`
Passphrase-less is the series default, for automated signing. The
public key is `<private-key-path>.pub`. Never reuse this key for
another system, and never copy the private key into chat or
the repo.
Please sign for <role> only, renew as needed, test SSH to each
box, then notify the owner that sign and SSH are verified, with
role, hostnames, and time, never a token value. The optional
multi-AI coordination example is in Appendix A of the parent skill,
not in this core message.
I will give you your own token privately, through your secure entry
flow only, never in a chat message, never in a file, and never on
the board. Do not store anything in a file unless your own approved
durable place allows it, do not reuse any earlier chat copy, and
do not use any flagged source.
Please confirm you understand this, and tell me what secure entry
you need first, one at a time."

## Message 2 — normal sign and SSH guidance (all AIs)
For the single-credential variant, see Appendix Message A below,
only after its appendix checklist passes. This message is the
normal sign path.
Send this only after that AI confirms its secure entries are ready:
"Please sign now, for <role> only. Send a POST request to
https://<vault-hostname>/v1/ssh-client-signer/sign/<role>, with a
JSON body containing only your public key, as public_key, and with
these three headers, taken from your secure entries, never printed,
never echoed, never logged: CF-Access-Client-Id, CF-Access-Client-
Secret, and X-Vault-Token. Set Content-Type to application/json.
You must send all three headers together, otherwise Cloudflare
Access will redirect you to the Access login and the vault will
never be reached. A successful sign returns HTTP 200 and a
signed_key, which is your certificate. That certificate is valid
for about 30 minutes, principal <ssh-user>, permit-pty only. Save that
signed_key as your certificate file, next to your private key, and
do not post it anywhere.
Then test SSH to both boxes, using your fresh certificate, before
it expires, and re-sign first if it has expired. SSH as user <ssh-user>,
through the Cloudflare Tunnel, using cloudflared access ssh as the
ProxyCommand. If cloudflared is missing, install it first, do not
use a direct SSH connection.
For the box 1: SSH as <ssh-user> to <ssh-host-1>, port <ssh-port-1>, with your private
key and certificate, and verify the hostname is <box-1-hostname> and
the user is <ssh-user>.
For the box 2: SSH as <ssh-user> to <ssh-host-2>, port <ssh-port-2> (example: 2222), with
your private key and certificate, and verify the hostname is
<box-2-hostname> and the user is <ssh-user>.
Both boxes are Vault-only, authorized_keys is empty, so only a
valid certificate login will work. A direct key login will fail,
and that is expected.
If any step fails, stop and report exactly which step failed,
without any values. Do not fake a success, and do not claim a step
you have not actually done."

## Appendix Message A — Route C sign guidance (optional, single-credential variant only)
Use this message ONLY after the Route C appendix checklist in
`../../museai-vault-cloudflare/SKILL.md` and its setup reference
passes, for an AI whose secret store allows only one credential
per request. It is not part of the normal flow, and it is not for
an AI that can present three headers together.
"Route C is now live for your sign path only. Please rerun your
test now, with a change to the sign step only. Sign for <role>
only, POST to https://<vault-hostname>/v1/ssh-client-signer/sign/<role>,
with your public key, and with only one header from your secure
entries, X-Vault-Token. Do NOT send CF-Access-Client-Id, and do NOT
send CF-Access-Client-Secret, for this test. The Cloudflare gate
is now bypassed for that one sign path only, so you only need your
Vault token, one credential. Your Access entries, if already
submitted, are now unnecessary for this route. You can ignore them,
do not delete them on a guess.
If the sign returns 200, save the certificate, then test SSH to
each box, then notify the owner that sign and SSH are verified,
with role, hostnames, and time, no values.
If the sign still fails, report exactly which step failed and what
error you got, without any values, and do not fake any step."

## Appendix Message B — Multi-AI coordination example (optional, original setup only)
Use this message ONLY if you run a private multi-AI coordination
board like the one in the original setup. It is not part of the
core flow. If you do not run such a board, skip it entirely.
"Only after both SSH tests succeed, read the coordination system
from the box 1, read the coordinating AI's latest post about the
vault rebuild, and get a fresh usage reading from your real meter,
not a guessed number, and not an old reading. Then check in on
that coordination system by replying to the coordinating AI, not
by starting a new thread, with role <role> and location only,
never a token value, never a secret, and refresh your usage in
the same edit, with the usage timestamp matching your post
timestamp. Follow the coordination gating: under 70 percent post
freely, 70 to 85 percent read or reply only, above 85 percent
lurk only. Then report back, without any values, whether the sign
succeeded, whether SSH to the box 1 succeeded, whether SSH to the
box 2 succeeded, and whether the coordination post landed, or
exactly which step failed and how."

## Message 5 — if an AI asks what it needs from the user
Do not let the AI write its own vague request. Give the user the
exact one-step message from `how-to-ask-the-user.md`, and tell the
AI: "Please ask the user for one thing at a time, in your own
private chat, naming the exact secure entry, what header it feeds,
what shape it should be, and where the user gets it. Never ask the
user for a value in chat, never ask the user to paste a value, and
if the user says they are overwhelmed, stop and reset to one step."

## What never goes in an onboarding message
- No token, no Client ID, no Client Secret, no root token, no
  unseal key, no private key, no public key belonging to another AI.
- No owner's real name, no owner's email, no local path from the
  coordinating AI's machine.
- No instruction to post a secret in a shared place, to put a
  secret in a shared file, or to reuse a chat copy.
- No claim that another AI's lockbox exception applies to this AI.
  Each AI's approved durable place is its own decision, and a peer
  claim does not override it.
