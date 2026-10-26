# Recovery runbook — MuseAI-Vault

## What "recovery" means here
Recovery means: the vault is sealed, rebooted, or unreachable; a
token stopped working; a CA changed; or a box lost Vault-only access.
Recovery does not mean: rebuilding the whole system from scratch on
the first failure. Try the narrow fix first, in the order below, and
only rebuild what is actually broken.

## Master material — locations only, never values
- On the cloud vault server: the vault init directory, holding the
  init file (root token plus five unseal keys, five shares,
  threshold: <unseal-threshold> of five shares — record your
  threshold; the files do not state it, do not assume a value),
  per-AI token files,
  the CA public key, the auto-unseal script, and the unseal log.
  Files 0600, directory 0700.
- On the box 1: the master-material copy directory, holding the
  same files, same permissions, copied at rebuild time.
- Offline, with the user: the root token and unseal keys, in the
  user's own password manager. The user does not paste these into
  chat, and the coordinating AI does not ask them to.
- Never copy any of these files to a workspace, to chat, or to the
  board. Never post their values. A recovery that posts a value to
  "save" it has created a new incident, not fixed one.

## Auto-unseal — the continuity tradeoff, stated honestly
An auto-unseal timer runs every 5 minutes and on boot on the vault
server. It holds the unseal keys on the vault and on the box 1.
That is less strict than manual unseal, and it is the deliberate
tradeoff that prevents a repeat lockout: the vault holds an SSH CA
only, not general secrets. If the vault's scope ever widens beyond
an SSH CA, revisit this tradeoff before widening it, do not widen
it silently.
Verification, at rebuild and after any auto-unseal change:
- Seal the vault manually, wait for the timer, verify it unseals.
- Reboot the vault server fully, verify it returns unsealed.
- If either check fails, fix auto-unseal before calling the vault
  healthy. A vault that only unseals by hand will lock out again.

## If the vault seals or the server reboots
1. Wait 5 minutes. The timer should unseal it. Check the unseal log
   on the vault server.
2. If still sealed after 10 minutes, SSH to the vault server with
   its launch key, run the auto-unseal script from inside the
   server, and check health on the localhost listener from inside
   the server.
3. If the instance itself is down, check the Oracle console: RUNNING,
   STOPPED, or TERMINATED. Restart a STOPPED instance. Rebuild a
   TERMINATED instance; do not try to revive its old Vault data
   without verified unseal keys for that data.
4. After any unseal or reboot, re-run a sign test before telling
   any AI the vault is back. A health endpoint that says unsealed
   is not a sign test.

## Daily health check
- A sign health check runs daily, silent unless
  it fails. It signs a test key and verifies the certificate. A
  failure is an action item the same day: check the vault, the
  tunnel, and the Access gate, in that order, using the
  troubleshooting matrix. Do not let a health-check failure sit
  until the next sign attempt by an AI.
- After the Oracle trial ends, add one extra check: the Always Free
  instance is still RUNNING, shape unchanged, no payment method
  added. Do not terminate it thinking trial end removes it.

## CA swap on a box — full procedure, one user step at a time
This procedure was verified on both boxes on the original build. Give the
user one step at a time, per `user-one-step-protocol.md`. Never give
the whole procedure to the user at once.
1. Stage the new CA public key on the box, at a temporary path,
   for example `/tmp/new-vault-ca.pub`. Verify its fingerprint
   against the fingerprint recorded in the vault init directory.
   Do not stage a CA from chat, from a screenshot, or from an
   unverified file.
2. If the box has no working certificate yet, add a temporary
   direct key for the coordinating AI only, as a single-line
   console step by the user, verify a temporary login, and use it
   only to stage the CA and to test. A temporary key is a bridge,
   not a new access method.
3. The user runs one single-line command to copy the staged CA into
   place and reload SSH. Form, single-line only, box user, sudo:
   `sudo cp /tmp/new-vault-ca.pub /etc/ssh/vault_ca.pub && sudo chmod 644 /etc/ssh/vault_ca.pub && sudo systemctl reload ssh || sudo systemctl restart ssh`
   Give this command alone, wait for confirmation, then continue.
   Do not add a second command to the same message.
4. Verify, from the coordinating AI: the box's CA file now holds
   the new CA, the trust line in the SSH configuration directory
   is intact and points at that CA file, and a fresh certificate
   login succeeds with hostname and user confirmed.
5. Only after step 4 passes, truncate `authorized_keys` to empty
   on that box, set its permissions correctly, and verify again:
   certificate login still succeeds, and the temporary key alone
   is denied. A test that appears to succeed while a config forces
   a certificate is not a temporary-key test; test the temporary
   key alone, with a config that does not force a certificate.
6. Repeat steps 1 to 5 on the other box. A CA swap on one box does
   not prove the other box.

## Token re-issue — when a token stops working
1. Check expiry and renewal first: a periodic token expires after
   720 hours unused, even if it was valid before. Check its policy
   and its lease, not just its age.
2. If it is expired, revoked, or its policy is wrong, re-issue it
   from the root token, for that AI's role only, same period, same
   policy. Write it to the vault token file and to the box 1 copy,
   0600, and test a sign with a test key, then delete the test key.
3. Hand the new token to that AI privately, through that AI's secure
   entry flow only, never in chat, never on the board. Tell the AI
   the old token is revoked and must not be reused.
4. Never fix an expired token by sharing another AI's token, even
   temporarily, even "just to test". A shared per-AI Vault token test that
   succeeds teaches the wrong lesson and breaks the one-token-per-AI
   rule.

## What never to delete, and what to clean up later
Never delete, until every path is verified: the cloud vault
instance, the live tunnel, the `<vault-hostname>` DNS route, the
Access application, the vault init directory, or the box 1
master-material copy.
Cleanup only after verification, in this order, and only with the
owner's explicit approval for each item: a preserved old boot volume,
an unused tunnel, an old tunnel's credentials, and a temporary
keypair held by the coordinating AI after its box is Vault-only.
Deleting any of these during a rebuild removes a fallback that may
still be needed for a missed config file or a missed credential.

## If the whole vault must be rebuilt
Follow `setup-order.md` from step 1, in order. Do not reuse an old
tunnel token, do not reuse an old CA, do not reuse old tokens, and
do not skip the CA swap verification on either box. A rebuild that
skips verification is not a rebuild, it is a new incident waiting
for the next sign attempt.
