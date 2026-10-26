# OpenBao setup — install, engine, roles, tokens, re-issue

Verified live during the original build, OpenBao 2.7.1 (tested
version at writing; re-check the current release before installing). Vendor docs for the SSH engine
match the ground truth on the points that matter, with two
differences to note, not to copy blindly. See the notes at the end.

## Install and initialise — checklist
- [ ] Binary install, pebbledb storage, systemd service, enabled
  on boot. No developer mode. Developer mode is not a vault.
- [ ] Two listeners: public TLS, and localhost HTTP for the tunnel.
  Record which port is which in the vault config, and do not swap
  them. The tunnel points at localhost, never at the public port
  from an AI VM.
- [ ] Initialise once. Save the init file only in the vault init
  directory, in the box 1 master-material copy, and in the user's
  own password manager, offline. Init file 0600, directory 0700.
- [ ] Verify health: initialised true, sealed false, version
  as installed.
- [ ] Set the auto-unseal timer: every 5 minutes, plus on boot.
  Verify by sealing, then watching it unseal, and by a full reboot
  returning to unsealed. See the parent skill's recovery runbook
  for the tradeoff note. Do not skip the reboot test.

## SSH engine, CA, roles — checklist
- [ ] Enable the SSH engine at mount `ssh-client-signer`.
- [ ] Generate the CA inside OpenBao, RSA 4096, signer algorithm
  `rsa-sha2-256`. Record the CA public key fingerprint in the
  vault init directory. Compare that fingerprint before trusting
  a CA file on a box; never trust a fingerprint from chat alone.
- [ ] Create one role per AI, N roles for N AIs, not fixed at
  five. Role format: `<ai-name>-ssh`, for example `<ai-1-role>`,
  `<ai-2-role>`.
- [ ] Each role, exactly: `allow_user_certificates` true,
  explicitly set; extensions as a JSON map with `permit-pty`
  only; default user and only principal `<ssh-user>`; TTL 30 minutes;
  key type CA.
- [ ] Test sign with a test keypair, for one role, check the
  certificate with `ssh-keygen -L`: principal `<ssh-user>`,
  `permit-pty` only, about 30 minutes valid. Delete the test
  keypair after the test. A test sign that returns 200 but is
  never checked is not a verified sign.

## Tokens — checklist
- [ ] One periodic token per AI, period 720 hours, renewable while
  in use, policy for that AI's role only, no default policy.
- [ ] Token files 0600, directory 0700, on the vault and on the
  box 1 only. Never in a workspace, never in chat, never on
  the board.
- [ ] Hand each token privately, through that AI's secure entry
  flow only. The coordinating AI never sends a token in a message,
  even to "help" an AI that lost its entry. If an AI lost its
  entry, re-open a clean secure entry for that AI, one at a time.

## Re-issue — checklist
- [ ] Check expiry and policy first, not just age. A token unused
  for 720 hours expires, even if it worked before.
- [ ] Re-issue from the root token, for that AI's role only, same
  period, same policy. Write the new token file to the vault and
  to the box 1 copy, 0600.
- [ ] Revoke the old token, if it is still revocable, before or
  immediately after the new token is tested. An old token that is
  still valid after a re-issue is a second live token for the same
  AI, and must be revoked, not left "just in case".
- [ ] Test a sign with a test key, delete the test key, then hand
  the new token privately to that AI only, and tell it the old
  token must not be reused.


## Placeholder payloads — role, token, sign (example only)

These are field payloads, not copy-paste admin calls. Use your
OpenBao admin API or CLI to set these fields, replacing every
placeholder. If your OpenBao version's admin field names differ,
set the fields by function, not by guessing a value, and check
the role and a test certificate back before calling it done.
This series is a checklist and playbook with these placeholder
payloads; it is not a fully runnable recipe if you do not already
know the OpenBao admin API.

Role creation, fields to set for each role `<ai-name>-ssh`:
- `allow_user_certificates`: true, explicitly set.
- `allowed_users` / default user and only principal: `<ssh-user>`.
- `extensions`: a JSON map, `{"permit-pty": ""}` — permit-pty
  only, no other extension. If your OpenBao version requires a
  different empty-value form for an extension, use that version's
  form and record it; do not add another extension.
- Certificate TTL: 30 minutes (series chosen value, not a vendor
  default).
- Key type: CA. Signer algorithm: `rsa-sha2-256` for the RSA CA.
- Mount: `ssh-client-signer`.

Token creation, fields to set for each AI:
- Periodic token, renewable while in use, period: 720 hours
  (series chosen value, not a vendor default).
- Policy: that AI's role only, no default policy, no admin policy,
  no shared per-AI Vault token.
- Store the returned token file 0600, directory 0700, on the vault
  and on the box 1 copy only.

Sign request, curl example with placeholders only:
`curl -X POST https://<vault-hostname>/v1/ssh-client-signer/sign/<ai-1-role> -H "CF-Access-Client-Id: <access-client-id>" -H "CF-Access-Client-Secret: <access-client-secret>" -H "X-Vault-Token: <vault-token>" -H "Content-Type: application/json" -d '{"public_key": "<public-key>"}'`
For a single-credential appendix sign, send only the
`X-Vault-Token` header, and only after the Cloudflare appendix
checklist passes. A 200 response carries `signed_key`; save it as
the certificate next to the private key, and check it with
`ssh-keygen -L` before SSH.

Unseal threshold placeholder: the init file holds five unseal
keys (five shares). Threshold: `<unseal-threshold>` of five shares
— record your threshold; the files in this series do not state
it, do not assume a value.

## Docs differences — do not copy blindly
- Vendor SSH engine examples often use a wildcard principal and
  list several extensions. This vault uses principal `<ssh-user>` only
  and `permit-pty` only. Copying the vendor example verbatim would
  widen the vault. Do not do it.
- Vendor examples sometimes present extensions as a comma-separated
  string. In OpenBao 2.7, as verified in this rebuild, extensions
  must be sent as a JSON map for this engine, and
  `allow_user_certificates` must be set explicitly. A role written
  from the vendor example without those two corrections may fail
  silently or grant the wrong extensions. Check the role back after
  writing it, and check a test certificate, before calling the role
  done.
- Token prefixes in vendor docs for newer Vault and OpenBao
  versions may show a different prefix than the tokens observed in
  this rebuild. This skill follows the observed shape in the
  parent skill's `../../museai-vault/references/token-shapes.md`, not the vendor prefix, for
  recognising a Vault token in this system. If a future OpenBao
  version changes the prefix, update `token-shapes.md` from a live
  token's shape, with a fake example only, and record the date.
