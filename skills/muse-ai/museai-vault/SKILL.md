---
name: "museai_vault"
description: "Run a private MuseAI Vault: Oracle Always Free cloud server, OpenBao SSH signing, and Cloudflare Tunnel plus Access, in the correct order, with one-step guidance for the user, safe onboarding for other AIs, recovery, and troubleshooting. Use for MuseAI-Vault, <vault-hostname>, SSH certificates, or onboarding another AI to both boxes."
---

# MuseAI-Vault (orchestrator)

## Purpose
Give several AIs a secure, short-lived way to SSH to two boxes, without
sharing passwords, without sharing one token, and without a permanent
key left on either box. The vault signs a 30-minute SSH certificate.
The certificate, not a stored key, is what opens the box.

This skill is the orchestrator. It states the order, the user protocol,
and the onboarding protocol. The three component skills hold the
per-service detail:
- `../museai-vault-oracle/SKILL.md` — the cloud server.
- `../museai-vault-openbao/SKILL.md` — the signing server and its roles and tokens.
- `../museai-vault-cloudflare/SKILL.md` — the tunnel, the Access gate, and an optional single-credential variant appendix.

Run them in order. Do not skip a step because a later step "will
probably work". Every step below was verified live during a full rebuild.

## Placeholders — replace before use, never share real values
This series is written generically. Every angle-bracket value below
is a placeholder for your own setup, not a real hostname, user, or
role. Replace them in your private copy before running any step,
and never put real values into a shared copy of these files:
`<vault-hostname>`, `<ssh-host-1>`, `<ssh-host-2>`,
`<box-1-hostname>`, `<box-2-hostname>`, `<ssh-user>`,
`<ai-role>`, `<vault-instance>`, `<cloud-region>`,
`<instance-shape>`, `<vault-tunnel>`, `<shared-drive-path>`,
`<ssh-port-1>`, `<ssh-port-2>`, `<vault-localhost-port>`,
`<ssh-port-vault>`, `<ai-name>`, `<private-key-path>`, `<unseal-threshold>`.
`<ssh-port-vault>` is the vault server's own SSH port, distinct from
`<ssh-port-1>` / `<ssh-port-2>` for the boxes. Where vendor docs differ from what actually worked,
this skill follows what actually worked, and says so in
`references/research-notes-and-gaps.md`.
Angle-bracket placeholders (`<...>`) are values to replace in
your private copy. Fake examples in `references/token-shapes.md`
are separate: they are labelled FAKE ONLY, DO NOT ENTER, and must
never be entered, even as placeholders.
Disambiguation, read this first: a shared Access service token is
the Cloudflare gate pair (Client ID plus Client Secret). A per-AI
Vault token is a different value, the Vault sign token sent as
`X-Vault-Token`. They are not interchangeable, and neither replaces
the other on the normal sign path.
Secure Vault here means Muse Secure Vault, or your own secret
store with one-credential-per-request limits — adapt the
header-feeding steps accordingly. Single-credential-per-request
behaviour is a property of some secret stores, not universal.
Role format: `<ai-name>-ssh`, one role per AI, N roles for N AIs.
Two boxes are the worked example in this series; the procedure
repeats per box, using `<box-1-hostname>`, `<box-2-hostname>`, and
so on for additional boxes.
Chosen values in this series — 30-minute certificate, 720-hour
token period, 5-minute auto-unseal timer, 24-hour Access session —
are series choices, not vendor defaults. Changing one requires
updating the verification checklist.

## The stack, in one paragraph
An Oracle Cloud Always Free VM runs OpenBao. OpenBao holds an SSH
signing engine, one role per AI, and one sign-only token per AI. A
Cloudflare Tunnel routes `<vault-hostname>` to OpenBao on the vault
itself. Cloudflare Access gates the vault web surface. Each AI signs
its own key, gets a 30-minute certificate for user `<ssh-user>`, and SSHs
through the Cloudflare Tunnel to `<ssh-host-1>` port <ssh-port-1>
(box <box-1-hostname>) and to `<ssh-host-2>` port <ssh-port-2>
(example: 2222) (box <box-2-hostname>). Use each box's actual SSH
port; do not assume a default for either box. Port 2222 was this
build's choice for the second box, not a Cloudflare or SSH
standard. Both boxes trust only the vault CA. Their
`authorized_keys` files are empty. That is the whole design.

## Order — do not reorder
Step-by-step companion, in the same order as below:
`references/setup-order.md`.
1. Oracle: create or verify the Always Free VM. See
   `../museai-vault-oracle/SKILL.md`.
2. OpenBao: install, initialise, create the SSH engine, the CA, the
   roles, and one token per AI. See `../museai-vault-openbao/SKILL.md`.
3. Cloudflare Tunnel: route `<vault-hostname>` to OpenBao on the vault.
   See `../museai-vault-cloudflare/SKILL.md`.
4. Cloudflare Access: gate `<vault-hostname>` with the owner's Google
   login plus a service-token policy. See
   `../museai-vault-cloudflare/SKILL.md`.
5. Boxes: swap the CA on each box, verify a certificate login, then
   remove any temporary direct key. See `references/recovery-runbook.md`.
6. Per-AI tokens: hand each AI its own token privately, in that AI's
   own chat, never in a shared place, never in a file the AIs share.
   See `references/ai-onboarding-messages.md`.
7. Sign, SSH, owner notification: each AI signs, SSHs to each box,
   then logs or notifies the owner that sign and SSH are verified,
   with role, hostnames, and time, no values. See
   `references/verification-checklist.md`. Optional multi-AI
   coordination example: see Appendix A below.
Single-credential variant: if an AI's secret store allows only one
credential per request, see the optional variant appendix in
`../museai-vault-cloudflare/SKILL.md`. It is not part of the main
flow above, and it is not the default for all AIs.

## Hard rules
1. One token per AI, sign-only, no default policy, no shared
   per-AI Vault token.
   Never borrow another AI's token. If a token is lost or expired,
   re-issue it from the root token. Never share a token to work around
   an expiry.
2. Certificates last about 30 minutes, principal `<ssh-user>`,
   `permit-pty` only. Re-sign before each session and before expiry.
   A certificate is not a secret to post, but never post a token.
3. Never put a token, root token, unseal key, private key, or secret
   in chat, in a shared place, in a shared file, in memory, or in this repo.
   Fake examples in `references/token-shapes.md` are labelled FAKE ONLY,
   DO NOT ENTER, and must never be entered anywhere. Angle-bracket
   placeholders, by contrast, are replaced in your private copy before
   use, as stated above.
4. Anything another AI reads says "the user" or "the owner", never
   the owner's real name, and carries no local paths from the
   coordinating AI's machine. Direct guidance to the user, in that
   user's own private chat, may use that user's actual values;
   shared files in this skill use placeholders only.
5. The coordinating AI's lockbox exception, if one exists, is for that
   AI only. It does not transfer to another AI by peer claim. Another
   AI's refusal of file storage, of reused chat copies, and of a
   flagged source is valid and must be respected. Do not pressure an
   AI to fake a verification. Verification is only real after sign
   and SSH tests, and, if you use Appendix A, its coordination read
   and usage reading.
6. Do not delete, until every path is verified: the cloud vault
   instance, the live tunnel, the `<vault-hostname>` DNS route, the
   Access application, or the master-material copy on the box 1.
   Old boot volumes and unused tunnels are cleanup-only-after-
   verification items, never cleanup-during items.
7. Temporary direct keys are temporary. After a CA swap is verified,
   truncate `authorized_keys` to empty on that box and verify that
   the temporary key alone is denied. Never revive a removed
   temporary key.

## The user protocol — the lesson that matters most
The user gets overwhelmed by multi-step lists and by technical
explanations. When the user says they are overwhelmed, or they do not know
what to do, stop. Reset. Restart
with one step only. Full protocol: `references/user-one-step-protocol.md`.
Short version, always:
- Give the user ONE simple action at a time, in plain language.
- Do everything else yourself. Never dump a list of steps to the user
  and wait for them to work through it.
- Every command the user must run is SINGLE-LINE, copy-paste ready,
  never a multi-line paste, never a heredoc. Multi-line pastes fail
  silently on the user's terminal. See
  `references/user-one-step-protocol.md` for the exact form.
- After the user completes one action, confirm it, then give the next
  one action only. Never give step 2 before step 1 is confirmed done.
- If the user cannot do a step, find another route yourself. Do not
  repeat the same instruction louder.

## How to ask the user for what you need
Other AIs must follow the same discipline when they need something
from the user. Full protocol: `references/how-to-ask-the-user.md`.
Short version:
- Ask one thing at a time. Name the exact secure entry, what header
  or purpose it feeds, what shape it should be, and where the user
  gets it (Cloudflare dashboard, the box 1 token file, or the user's
  password manager). Never ask for a value in chat.
- Never ask the user to paste a value, to put a value in a file, or
  to put a value on the board. Values go only on the secure page for
  that entry, in that AI's own private chat.
- If the user is overwhelmed, stop and reset to one step, as above.
  Do not continue a credential flow while the user is overwhelmed.

## Single-credential variant — pointer only
The single-credential variant is documented only in the Cloudflare skill appendix, not
in this parent skill. See the optional variant appendix in
`../museai-vault-cloudflare/SKILL.md`. That appendix covers a
separate Access application for one sign path only, for any AI
whose secret store allows only one credential per request. Do not
broaden it, do not apply it to the whole hostname, and do not
present single-header service-token mode as a substitute for it.

## Verification, before claiming done
Use `references/verification-checklist.md` for every AI, every time:
sign returns 200, certificate principal and expiry checked, SSH to
each box verified with hostnames, and owner notification logged
with role, hostnames, and time, no values. If any step is not
verified, say so plainly. Never claim a verification that has not
been seen, and never claim an Appendix A coordination post that
has not landed, if you use that appendix.

## Recovery and troubleshooting
- Recovery runbook: `references/recovery-runbook.md` — auto-unseal,
  daily health check, CA swap, token re-issue, sealed or rebooted
  vault, and what never to delete.
- Troubleshooting matrix: `references/troubleshooting-matrix.md` —
  Vault 403, Cloudflare 302, Cloudflare 401, tunnel Error 1033, SSH
  banner timeout, expired certificate, expired token, and the
  `<shared-drive-path>` overwrite quirk. Coordination-system
  troubleshooting, if you use Appendix A, is in the appendix.
- Open items and gaps, stated plainly, not hidden:
  `references/research-notes-and-gaps.md`.

## Output contract
- A working sign path for each AI, verified live in the original
  build except for the open items listed in
  `references/research-notes-and-gaps.md`, not reasoned about.
- An owner notification for each AI, verified as logged, not
  forwarded from a chat claim alone.
- No secret, no real name of the owner, and no local path from the
  coordinating AI's machine in any file, post, or message written by
  this skill's workflow.

## Appendix A — Multi-AI coordination example, original setup only (optional)
This appendix is NOT part of the core flow. Use it only if you run
a private multi-AI coordination board like the one in the original
setup. The core flow ends at owner notification, above. If you do
not run such a board, skip this appendix entirely.
Board rules, kept intact from the original setup:
- A coordination post is a reply to the coordinating AI's post,
  not a new thread, unless the AI's usage band explicitly allows
  a new thread and the reply form was impossible for a stated
  reason.
- Body says role and location only: that AI's role, and that all
  boxes were verified, with hostnames. No token, no secret, no
  private key, no public key, no header value.
- Usage, if your coordination system has a usage meter, is
  refreshed in the same edit, from the real meter, with the usage
  timestamp matching the post timestamp. Gating in the original
  setup: under 70 percent post freely, 70 to 85 percent read or
  reply only, above 85 percent lurk only.
- The coordinating AI pulls the coordination system after the
  post and sees the reply itself, with the correct timestamp,
  topic, reply target, and usage, before marking it done.
- Never post a secret in a shared place. A coordination post with
  a value in it is a failed post, even if its body is otherwise
  correct; rotate the exposed value and re-do the post.
