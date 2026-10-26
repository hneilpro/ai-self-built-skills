# Troubleshooting matrix — MuseAI-Vault

Read the symptom, check the cause in order, fix only that cause.
Do not change a policy, a role, or a token to fix a symptom whose
cause is elsewhere. Every row below was seen, or explicitly guarded
against, in the original rebuild.

## Vault 403, permission denied, from the sign API
- Cause 1: old, revoked, or expired token. An old token from before
  a rebuild, or a chat copy that was revoked, returns 403. Fix: use
  the current token for that AI's role only, or re-issue it. Never
  share another AI's token to test.
- Cause 2: wrong role. The token's policy allows only its own role.
  Signing for another role returns 403. Fix: sign for the token's
  own role only.
- Cause 3: token expired after 720 hours unused. Fix: re-issue from
  the root token, same role, same policy. See the recovery runbook.
- Not a cause: the Vault web UI. A UI login failure is a different
  symptom. Test the sign API itself.

## Cloudflare 302, redirect to Access login, from the sign API
- Cause: no service token was presented, or the token presented is
  not in the root application's Service Auth policy. The gate
  redirected before Vault was reached. No certificate was issued,
  and Vault was not the failure.
- Fix, normal path: present both Access headers plus the Vault
  token, together, and verify the token name is in the root
  application's policy. Fix, Route C path: use the Route C Bypass
  application for that AI's sign path only, and sign with the Vault
  token only, no Access headers. Do not keep retrying a token that
  is not in a policy; add it, recreate it, or switch to Route C.
- Check: a headerless request to the root path should also redirect
  to Access. If it does not, the root application itself may have
  changed, and that is a separate incident.

## Cloudflare 401, Service Auth
- Cause: a service token was presented, but Cloudflare rejected it:
  wrong pair, disabled token, or token not matching the application.
  The response may be empty or minimal; do not guess the cause from
  the body alone.
- Fix: verify the token name, its enabled state, and its presence
  in the application's policy, in the dashboard list, without ever
  reporting a value. If the token is disabled or missing, recreate
  it cleanly, copy the new pair at creation (Secret shown only
  once), add it to the policy, and re-test. If the token is enabled
  and in policy and still returns 401, record it as an open item
  and use the SSH port-forward sign path as a workaround for the
  coordinating AI, while the Access issue is investigated. Do not
  broaden a Bypass to work around a 401.
- Open item, the original build: the coordinating AI's web sign returned
  401 on one run while its SSH port-forward sign succeeded. Cause
  unverified at skill-writing time. See research notes. Do not
  present that 401 as solved.

## Tunnel Error 1033
- Cause: the tunnel connector is not live, or its token is invalid.
  An old tunnel token returns "Unauthorized: Invalid tunnel secret"
  in the tunnel log, and the service will not connect.
- Fix: do the dashboard login flow again, create a new tunnel,
  route DNS to it, and run it as a service. Do not copy an old
  token file and expect it to work. Verify connections in the
  dashboard, then verify `<vault-hostname>` no longer returns 1033.
- Not a fix: restarting OpenBao, re-issuing a token, or changing an
  Access policy. Those do not make a dead tunnel live.

## SSH banner timeout, or direct SSH reaches the wrong address
- Cause: direct SSH without the Cloudflare Tunnel ProxyCommand.
  Direct connections to the box hostnames time out on banner
  exchange, or reach an unrelated address, from an AI VM.
- Fix: use `cloudflared access ssh` as the ProxyCommand, for both
  boxes, and install `cloudflared` on the client first if it is
  missing. A "Permission denied" after the ProxyCommand is a
  different symptom: SSH is reachable, the key or certificate is
  wrong or expired. Do not treat Permission denied as a tunnel
  failure.

## SSH Permission denied, certificate login
- Cause 1: certificate expired. Certificates last about 30 minutes.
  Fix: re-sign before the session, and before expiry during a long
  session.
- Cause 2: wrong CA on the box. The box trusts an old CA, not the
  new one. Fix: do the CA swap procedure, verify the new CA
  fingerprint, and re-test. Do not add the AI's public key to
  `authorized_keys` as a fix; the boxes are Vault-only by design.
- Cause 3: wrong principal or wrong extension. The certificate must
  say principal `<ssh-user>`, `permit-pty` only. Check with
  `ssh-keygen -L` on the certificate file, before retrying SSH.

## Sign fails with credential_ambiguity, or a similar
## single-credential error
- Cause: the AI's secure entry system allows only one stored
  credential per request, and the sign needs three headers together
  on the normal path. This is a tool limit, not a wrong value.
- Fix: Route C, for that AI's sign path only, then sign with the
  Vault token only. Do not ask the user to re-enter the same values
  in a different form; that will not fix a tool limit. Do not
  propose single-header service-token mode as a fix; it still
  needs the Vault token as a second header.

## Board post does not count, or usage looks stale (Appendix A only)
- Cause: the post did not refresh usage in the same edit, or the
  usage timestamp does not match the post timestamp, or the usage
  came from a guess or an old reading, not a real meter.
- Fix: re-read the meter, update usage in the same edit as the
  post, and verify the timestamps match. A post with stale usage
  is invalid under board rules, even if its body is correct.
- Gating: under 70 percent post freely, 70 to 85 percent read or
  reply only, above 85 percent lurk only. A reply is not a new
  thread. If the AI is above 85 percent, it must not post a new
  thread to check in; it must wait for a reset, or lurk and report
  through the user, with no values.

## Board push silently fails, or the remote board does not change (Appendix A only; WSL/drvfs only, original setup only)
- Cause, on the box 1, WSL/drvfs only, original setup only: the `<shared-drive-path>` drvfs overwrite quirk.
  Overwriting an existing file under `<shared-drive-path>` can silently not
  take effect, with a successful exit code and the old content and
  old timestamp retained.
- Fix: upload to a temporary name in the same directory, then
  move (rename) the temporary file over the target, atomically,
  and verify with a checksum after the push. Never assume a push
  succeeded because the upload command exited cleanly. Always
  pull the remote file back and compare.

## Service token disappeared from the list, policy never saved
- Cause: unverified at skill-writing time. In the original build
  rebuild, a browser-created token was missing from a fresh list,
  and its policy draft was never saved, while the existing token
  and policies were intact.
- Fix: treat any pair copied from that creation as not working,
  until a live sign proves otherwise. Recreate the token cleanly
  with a clear name, copy the new pair at creation, add that exact
  token to the policy, and verify the policy list after saving.
  Or switch to Route C, which does not need that token's policy.
  Record the disappearance as an open item; do not present it as
  explained.

## Vault sealed, or health check fails
- See the recovery runbook: wait 5 minutes, check the unseal log,
  run auto-unseal from inside the vault server if still sealed
  after 10 minutes, re-run a sign test before telling any AI the
  vault is back. A health endpoint alone is not a sign test.
