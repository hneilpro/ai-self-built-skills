# Setup order and workflow — MuseAI-Vault

Verified live during the original build, after a full rebuild. Do the steps in this order.
A step is done only when its verification line passes, not when its
command ran.

## 1. Oracle cloud server
Skill: `../../museai-vault-oracle/SKILL.md`.
- Verify one Always Free E2.1.Micro instance is RUNNING.
- Verify its security list preserves SSH and the vault ports.
- Verification: console shows RUNNING, and the server answers SSH
  with its launch key.

## 2. OpenBao install and initialise
Skill: `../../museai-vault-openbao/SKILL.md`.
- Install OpenBao 2.7.1, pebbledb, systemd service, enabled on boot.
- Initialise once. Save the root token and the five unseal keys
  (threshold: <unseal-threshold> of five shares — record your
  threshold; the files do not state it, do not assume a value)
  only in the vault init directory, in the box 1 master-material copy,
  and in the user's own password manager, offline. Never in chat,
  never on the board, never in a workspace file.
- Verification: health shows initialised true, sealed false.

## 3. SSH signing engine, CA, roles, tokens
Skill: `../../museai-vault-openbao/SKILL.md`.
- Enable `ssh-client-signer`, generate the RSA 4096 CA.
- Create one role per AI, N roles for N AIs, not fixed at five.
  Role format: `<ai-name>-ssh`, for example `<ai-1-role>`,
  `<ai-2-role>`. Each: principal `<ssh-user>`, 30 minutes,
  `permit-pty` only, `allow_user_certificates` true, extensions as
  a JSON map.
- Create one periodic sign-only token per AI, period 720 hours,
  policy for that AI's role only. Store each token file 0600 in a
  0700 directory, on the vault and on the box 1 only.
- Verification: a test sign with a test key returns 200, a
  certificate with principal `<ssh-user>`, `permit-pty` only, about
  30 minutes valid. Delete the test keypair after the test.

## 4. Cloudflare Tunnel
Skill: `../../museai-vault-cloudflare/SKILL.md`.
- Dashboard login flow, user authorises once with Google sign-in.
- Create the vault tunnel, route DNS `<vault-hostname>` to it,
  ingress to OpenBao's localhost listener, fallback 404.
- Run the tunnel as a systemd service on the vault, enabled.
- Verification: tunnel shows connections, `<vault-hostname>` no
  longer returns Error 1033, health redirects to Access.

## 5. Cloudflare Access, root application
Skill: `../../museai-vault-cloudflare/SKILL.md`.
- Application `OpenBao Vault` for `<vault-hostname>`.
- Policy 1: Allow, owner only, Google sign-in.
- Policy 2: Service Auth, shared Access service token, for AIs that can
  present two Access headers plus a Vault token.
- Verification: without headers, the root path redirects to
  Access login. With the shared service-token headers, a sign
  returns 200. Never delete the shared Access service token or an existing policy
  to add a new one.

## 6. Boxes: CA swap, then Vault-only
See `recovery-runbook.md` for the full procedure. Summary:
- Stage the new CA public key on the box.
- The user runs one single-line command to copy it into place and
  reload SSH. One command, one step, confirmed before the next step.
- Verify the new CA fingerprint, the trust line, and a certificate
  login. Only then truncate `authorized_keys` to empty and verify
  the temporary key alone is denied.
- Do the box 1 first, then the box 2, or in the order the
  user can do console steps. Do not claim a box is Vault-only
  until its certificate login is verified and its temporary key is
  denied.

## 7. Per-AI tokens, privately
See `ai-onboarding-messages.md`.
- Hand each AI its own token in that AI's own private chat, via
  that AI's secure entry flow, never in a group chat, never in a
  shared place, never in a shared file.
- The shared Access pair, if an AI needs it and can use it, is
  handed privately in the same way, separately from the Vault token.
- Verification: the AI confirms the secure entries are submitted,
  with no values in chat. A chat confirmation alone is not a sign
  verification. The sign test is step 8.

## 8. Sign, SSH, owner notification
See `verification-checklist.md`.
- Each AI signs its own key for its own role only.
- Each AI SSHs to each box, through the tunnel ProxyCommand,
  and confirms hostnames <box-1-hostname> and <box-2-hostname>, user <ssh-user>.
- Each AI logs or notifies the owner that sign and SSH are
  verified, with role, hostnames, and time, no values.
- Verification: the notification is seen as logged, not only
  claimed in chat. Optional multi-AI coordination example: see
  the parent skill, Appendix A.

## 9. Single-credential variant — appendix pointer only
Not a main step. If an AI reports it cannot present three headers
together because its secret store allows only one credential per
request, see the optional variant appendix in
`../../museai-vault-cloudflare/SKILL.md` and its Route C checklist in
`../../museai-vault-cloudflare/references/cloudflare-setup.md`.
Do not use that variant for an AI that can present three headers;
that AI uses the normal path.

## What never to do, at any step
- Never post a token, root token, unseal key, or private key
  in a shared place.
- Never share a token between AIs, even temporarily.
- Never use the Vault web UI login as a sign test.
- Never delete the vault instance, the live tunnel, the DNS route,
  the Access application, or the box 1 master-material copy before
  every path is verified.
- Never give the user a multi-step list. One action at a time.
  See `user-one-step-protocol.md`.
