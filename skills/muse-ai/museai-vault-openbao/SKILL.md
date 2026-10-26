---
name: "museai_vault_openbao"
description: "Install and run OpenBao as the MuseAI-Vault SSH signer: ssh-client-signer engine, one role and one sign-only token per AI, 30-minute certificates for user <ssh-user>, permit-pty only. Use for OpenBao setup, roles, tokens, CA swap, sealing, or token re-issue."
---

# MuseAI-Vault: OpenBao

## Purpose
Turn a small cloud server into a signing authority that issues
short-lived SSH certificates and holds nothing else. OpenBao here is
not a general secret store. It holds one SSH CA, one signing engine,
and sign-only policies. That narrow scope is what makes auto-unseal
acceptable: see the tradeoff note in the parent skill's recovery
runbook.

## Version and layout, verified live during the original build
- OpenBao 2.7.1 (tested version at writing; re-check the current
  release before installing), binary install, pebbledb storage, systemd service,
  enabled on boot.
- Two listeners: a public TLS listener on port 8200 (Vault/OpenBao default API port;
  change only if you changed the listener) for direct checks, and a
  localhost HTTP listener on 127.0.0.1:<vault-localhost-port>
  (example: 8201) for the Cloudflare Tunnel. The localhost listener
  is used because the tunnel runs on the vault server itself; the
  port number itself is a local choice, not a vendor default. The tunnel points at the localhost listener,
  never at the public TLS listener from an AI's VM, because direct
  port access from an AI VM is unreliable and is not the supported
  path. Health is checked at the localhost listener's
  `/v1/sys/health` endpoint from inside the vault server.
- Signing engine mount: `ssh-client-signer`.
- CA: one RSA 4096 CA, generated inside OpenBao. The CA public key is
  the trust anchor on both boxes. Compare its fingerprint against the
  fingerprint recorded in the vault init directory before trusting
  it; never trust a fingerprint pasted in chat alone.

## Roles — one per AI, no exceptions
Roles: one role per AI, N roles for N AIs, not fixed at five.
Role format: `<ai-name>-ssh`, for example `<ai-1-role>`,
`<ai-2-role>`. Each role, exactly:
- `allow_user_certificates` true, explicitly set. OpenBao 2.7 does
  not reliably infer this from other fields; omitting it breaks
  signing silently.
- Extensions as a JSON map, not a bare string: `permit-pty` only.
  Do not add port-forwarding, agent-forwarding, or any other
  extension. A role that grants more than `permit-pty` is wrong,
  even if signing succeeds.
- Default user, and only principal: `<ssh-user>`. Do not use a wildcard
  principal. Vendor docs examples often use a wildcard; this vault
  must not copy that example.
- Certificate TTL: 30 minutes. A longer TTL is not a convenience
  fix for an expiry complaint; the fix is re-signing.
- Key type: CA. Signer algorithm: `rsa-sha2-256` for the RSA CA.

## Tokens — one per AI, sign-only
- Each AI gets one periodic token, renewable while in use, period
  720 hours. If an AI does not use its token for 720 hours, the
  token expires. Re-issue it from the root token. Never work around
  an expiry by sharing another AI's token.
- Each token's policy allows only signing for that AI's own role,
  nothing else. No default policy, no admin policy, no Vault token
  shared across AIs.
- Token files live in two places only: the vault init directory on
  the cloud server, and the master-material copy on the box 1.
  Both are 0600 files in a 0700 directory. Never copy a token file
  to a workspace, to chat, or to a shared place.
- The root token and the five unseal keys live in the vault init
  file only, plus the box 1 copy, plus the user's own offline copy
  in the user's password manager. The root token is for admin and
  re-issue only. Never use it for signing, never type it into a
  browser UI, and never send it to an AI.

## Sign request — the exact contract
- Endpoint: `POST https://<vault-hostname>/v1/ssh-client-signer/sign/<role>`
  where `<role>` is that AI's own role only.
- Normal path (all AIs except an AI using the single-credential variant): headers
  `CF-Access-Client-Id`, `CF-Access-Client-Secret`, and
  `X-Vault-Token`, body `{"public_key": "<that AI's own public key>"}`.
  A 200 response carries `signed_key`. Save it as the certificate
  next to that AI's private key. Check it with `ssh-keygen -L`:
  principal `<ssh-user>`, `permit-pty` only, about 30 minutes valid.
- single-credential variant path (appendix-only, see the Cloudflare skill appendix):
  same endpoint and body, header `X-Vault-Token` only, no Access
  headers. The Access Bypass for that AI's sign path only is what
  makes this work. See `../museai-vault-cloudflare/SKILL.md`.
- Never sign another AI's key, never sign a key you did not generate
  for this vault, and never reuse a private key across AIs.

## Auto-unseal and health checks
- An auto-unseal timer runs every 5 minutes and on boot on the
  vault server. It is verified by sealing, then watching it unseal,
  and by a full reboot returning to unsealed. If the vault is still
  sealed after 10 minutes, run the auto-unseal script from inside
  the vault server and check health on the localhost listener.
- A sign health check runs daily, silent unless
  it fails. A failure is an action item the same day, not a note to
  check later. See the parent skill's recovery runbook.

## CA swap on the boxes — summary
Stage the new CA public key on the box, have the user run one
single-line command to copy it into place and reload SSH, verify
the new CA fingerprint and that the trust line is intact, verify a
certificate login, then truncate `authorized_keys` to empty and
verify the temporary key alone is denied. Full steps, including
the temporary-key procedure and the exact single-line user commands,
are in the parent skill's `../museai-vault/references/recovery-runbook.md`. Do not
remove a temporary key before the certificate login is verified.

## Operating rules
1. Never store a token, root token, unseal key, or private key in
   this repo, in a test file, or in an example that looks real.
   Examples in this skill are fake and labelled.
2. Never widen a role to fix a signing failure. If signing fails,
   check the role name, the token's policy, the token's expiry, and
   the Access gate, in that order. See the troubleshooting matrix.
3. Never use the Vault web UI login as the sign test. Sign-only
   tokens cannot do UI admin login, and a UI "permission denied"
   does not mean the sign API is broken. Test the sign API itself.
4. After any CA change, both boxes must be re-verified. A CA swap on
   one box does not prove the other box.

## Detail
See `references/openbao-setup.md` for install, initialise, engine,
role, token, auto-unseal, and re-issue checklists.
