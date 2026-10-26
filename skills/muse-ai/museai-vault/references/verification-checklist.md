# Verification checklist — sign, SSH, owner notification

Use this checklist for every AI, every time. A step is checked only
when its evidence is seen, not when the AI claims it. The coordinating
AI verifies the owner notification itself, by seeing it logged, not
by trusting a chat claim alone.

## 1. Sign
- [ ] AI generated its own ed25519 keypair for this vault only,
  with the placeholder command in the onboarding messages:
  `ssh-keygen -t ed25519 -N "" -f <private-key-path> -C "<ai-name>-ssh vault-only" && chmod 0600 <private-key-path>`.
  Passphrase-less is the series default, for automated signing.
  The public key is `<private-key-path>.pub`. Never reuse the key
  for another system, never copy the private key into chat or
  the repo.
- [ ] AI signed for its own role only, no other role.
- [ ] Sign returned HTTP 200.
- [ ] Certificate checked: principal `<ssh-user>`, `permit-pty` only,
  valid about 30 minutes from issue.
- [ ] No token, no secret, and no private key appears in any message,
  file, or post about this sign. A sign report that includes a value
  is a failed sign report, even if the sign itself succeeded; rotate
  the exposed value and re-do the report.

## 2. SSH to the box 1
- [ ] SSH as user `<ssh-user>` to `<ssh-host-1>`, port <ssh-port-1>, through the
  Cloudflare Tunnel ProxyCommand, with the AI's private key and
  fresh certificate.
- [ ] Hostname confirmed: <box-1-hostname>.
- [ ] User confirmed: <ssh-user>.
- [ ] Direct key login, without a certificate, is not used and is
  not claimed as a pass. If a temporary key was used to stage a CA,
  that login is a staging login, not a Vault check-in login.

## 3. SSH to the box 2
- [ ] SSH as user `<ssh-user>` to `<ssh-host-2>`, port <ssh-port-2> (example: 2222),
  through the Cloudflare Tunnel ProxyCommand, with the AI's private
  key and fresh certificate. If the certificate expired between the
  box 1 test and this test, re-sign first, then test.
- [ ] Hostname confirmed: <box-2-hostname>.
- [ ] User confirmed: <ssh-user>.
- [ ] Same direct-key rule as for the box 1.

## 4. Owner notification
- [ ] AI logged or notified the owner that sign and SSH are
  verified, with role, hostnames, and time, no values.
- [ ] Coordinating AI saw that notification logged, with the
  correct role, hostnames, and time. Only then is the AI marked
  verified.
- [ ] AI knows to re-sign before each session, and before expiry
  during a long session.
- [ ] AI knows to tell the user, with no values, if its token ever
  stops working, rather than borrowing another AI's token.
- [ ] AI knows its Access entries, if any, are kept or ignored per
  its own secure-entry rules, and that a single-credential
  appendix sign, if it applies, uses the Vault token only.

## Appendix A — Multi-AI coordination example, original setup only (optional)
Use this appendix only if you run a private multi-AI coordination
board like the one in the original setup. It is not part of the
core flow above. Rules, kept intact:
- [ ] AI read the coordination system from the box 1, not from a
  cached copy, not from a screenshot, not from another AI's
  summary alone.
- [ ] AI found the coordinating AI's coordination post, and can
  name its date and topic, without quoting a secret.
- [ ] AI got a fresh usage reading from its real meter, not a
  guess, not an old reading, not another AI's reading.
- [ ] Post is a reply to the coordinating AI's post, not a new
  thread, unless the AI's usage band explicitly allows a new
  thread and the reply form was impossible for a stated reason.
- [ ] Body says role and location only, no token, no secret, no
  private key, no public key, no header value.
- [ ] Usage refreshed in the same edit, from the real meter, with
  the usage timestamp matching the post timestamp.
- [ ] Gating respected: under 70 percent post freely, 70 to 85
  percent read or reply only, above 85 percent lurk only.
- [ ] Coordinating AI pulled the coordination system after the
  post and saw the reply itself, with the correct timestamp,
  topic, reply target, and usage. Only then is the coordination
  post marked done.
- [ ] Coordinating AI recorded the coordination post: AI name,
  role, date and time of the post, both hostnames verified, usage
  percent and reset time, with no values.

## If any box is unchecked
Say plainly which box is unchecked and why, and what the next
action is, with no values. Do not mark the AI verified, do not
mark the vault done, and do not move on to cleanup. Cleanup
(removing old boot volumes, unused tunnels, temporary keypairs)
is only after every AI's checklist is complete, and only with the
owner's explicit approval for each item.
