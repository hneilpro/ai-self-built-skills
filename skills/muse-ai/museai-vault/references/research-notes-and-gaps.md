# Research notes and gaps — MuseAI-Vault, the original build

This file is the honest record of what was verified live, what came
from vendor docs, where they differ, and what is still open. Do not
present an open item as solved, and do not delete an open item
because a later step worked around it. A workaround is not a root
cause fix.

Terminology note (2026-10-25): "Route C" in this dated record means the single-credential variant in current guidance. New guidance does not use the Route C label.

## Verified live, the original build — ground truth for this skill
- Full rebuild: Oracle Always Free VM, OpenBao 2.7.1,
  ssh-client-signer, RSA 4096 CA, one role per AI, one sign-only periodic
  token per AI, 720-hour period, 30-minute certificates, principal
  <ssh-user>, permit-pty only.
- Cloudflare Tunnel live, routing `<vault-hostname>` to OpenBao's
  localhost listener, with a systemd service on the vault.
- Cloudflare Access root application, owner-only Google plus a
  shared service token, verified by signs returning 200 with the
  shared headers.
- CA swap verified on both boxes: new CA, trust line intact,
  certificate login verified, `authorized_keys` truncated to empty,
  temporary key alone denied. Both boxes Vault-only.
- Board: coordinating AI posted a rebuild check-in request. One AI
  checked in after the rebuild, replying to that post, role and
  location only, usage refreshed in the same edit from a real meter.
- Route C verified live: separate Bypass application for one AI's
  sign path only, Bypass Everyone, more specific path takes
  precedence, rest of the vault stays protected. That AI then
  signed with its Vault token only, SSHed to both boxes, and
  checked in. Live headerless checks proved the Bypass was narrow:
  that sign path returned Vault 403 without a token, while the
  root path and another sign path still redirected to Access.

## Vendor docs checked, and where they differ
- Cloudflare Access, common policies: a public endpoint can be
  bypassed by a separate Access application for a specific path,
  with a Bypass policy for Everyone, and the more specific path
  takes precedence. This matches the live Route C result. The
  vendor docs also describe Worker destination overrides that can
  make a matching path public; that mechanism is not the mechanism
  used here, and must not be confused with it. Route C here is a
  separate self-hosted application for a path, not a Worker override.
- Cloudflare service tokens, single-header mode: vendor docs
  describe reading a service token from a single header as an
  alternative to the two-header Access pair, with the header value
  as a JSON object holding both the Client ID and the Secret.
  That mode does not solve a single-surrogate limit, because the
  Vault token is still a second credential in the same request.
  This skill states that plainly, and does not propose single-header
  mode as a fix for that limit.
- OpenBao SSH engine: vendor docs match the live role fields on
  `allow_user_certificates`, `permit-pty`, TTL, and CA key type,
  with two differences noted in the OpenBao setup reference:
  vendor examples use a wildcard principal and list several
  extensions, while this vault uses principal `<ssh-user>` only and
  `permit-pty` only; and extensions must be a JSON map, with
  `allow_user_certificates` set explicitly, in OpenBao 2.7.
- Oracle Always Free: vendor and community docs agree the
  E2.1.Micro allowance is up to two instances, 1/8 OCPU and 1 GB
  each, with 200 GB shared block storage, and a 30-day trial credit
  that does not change the Always Free rule. The Ampere A1 allowance
  was halved in 2026 in vendor docs, from 4 OCPU / 24 GB to 2 OCPU /
  12 GB; that change does not affect this vault, which uses the
  E2.1.Micro shape, but it is a warning not to trust old guides'
  numbers without re-checking the Always Free page.

## Gaps and open items — explicitly open, do not hide these
1. Coordinating AI web sign 401, during the original build: a web sign
   through `<vault-hostname>` with the shared Access headers
   returned 401 on one run, while an SSH port-forward sign with
   the same Vault token succeeded the same run. Cause unverified.
   Possible causes, not conclusions: shared token state, policy
   precedence after the Route C application was added, or a
   transient Access failure. Do not present the web sign path as
   fully healthy until it is re-tested and passes. The SSH
   port-forward path and the daily health check use the SSH route,
   so this open item does not block AI sign paths that use Route C
   or a working shared token, but it must be re-tested before the
   next rebuild relies on the web sign path.
2. First browser-created service token disappeared, the original build:
   a token created for one AI was missing from a fresh Service
   Tokens list, and its policy draft was never saved, while the
   existing shared token and policies were intact. Cause
   unverified. It may have been a dashboard refresh issue, a
   creation that did not commit, or a list filter issue. Do not
   present that token as working, and do not retry its copied pair.
   The skill's Cloudflare setup reference states the rule: treat
   a disappeared token's pair as not working until a live sign
   proves otherwise.
3. Other AI check-ins still pending, at skill-writing time: the
   AIs for the remaining roles have not yet verified sign, SSH to
   both boxes, and board check-in on the new vault. Their tokens
   exist, their roles exist, and the vault, tunnel, and boxes are
   verified, but their check-ins are not. Do not claim the vault
   is fully adopted until each AI's verification checklist is
   complete. The general onboarding messages in this skill are
   written for those pending check-ins, with no values and no
   local paths.
4. User offline copy of root and unseal material: the user was
   advised to save the root token and unseal keys offline in their
   password manager, from the box 1 master-material copy, without
   pasting output or a screenshot into chat. Completion was not
   confirmed at skill-writing time. Do not claim the offline copy
   exists until the user confirms it, with no values, only that
   it is saved.
5. Cleanup pending, after verification only: a preserved old boot
   volume, an unused tunnel, and old tunnel credentials. None of
   these were deleted at skill-writing time, correctly, because
   verification of all AI paths was not complete. Do not delete
   them in a cleanup pass that is not explicitly approved item by
   item by the owner.

## Additional skills or tools that would make this smoother
These are suggestions, not part of this series, and must not be
built silently as extra skills in this branch:
- A small, local sign-and-SSH test script, one per AI, that signs,
  checks the certificate, SSHs to both boxes, and reports only
  pass or the failing step, with no values in its output. That
  would replace the current manual curl-plus-SSH verification
  with a repeatable check, and would have caught the web sign 401
  earlier if it ran against both sign paths.
- A board pull-and-verify script that pulls the remote board,
  checks a check-in reply's timestamp, reply target, and usage
  timestamp, and reports only pass or the failing field. That
  would replace the manual board pull used for the original build
  check-in verification.
- A Cloudflare dashboard checklist card, for the user, with one
  tap per step, for the tunnel login flow and for the Route C
  application. That would reduce the dashboard steps the user must
  do themselves to the minimum the assistant cannot do for them.
Each of these, if built later, must follow the same rules as this
series: no secrets in code, no owner name in AI-facing text, fake
examples only, and one user step at a time.
