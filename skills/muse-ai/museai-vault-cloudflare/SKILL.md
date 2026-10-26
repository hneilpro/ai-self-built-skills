---
name: "museai_vault_cloudflare"
description: "Wire MuseAI-Vault through Cloudflare: Tunnel routing <vault-hostname> to OpenBao on the vault, Access gating for the vault web surface, service tokens, and an optional narrow Bypass variant appendix for a single-credential secret store. Use for Cloudflare Tunnel, Access applications and policies, service tokens, Error 1033, or the single-credential variant appendix."
---

# MuseAI-Vault: Cloudflare

## Purpose
Make the vault reachable from AI VMs on port 443, through a tunnel
and a gate, without exposing the vault server's public ports to AIs
directly. Direct HTTPS to the vault's public port from an AI VM is
not the supported path. Port 443 via Cloudflare is.

## Tunnel — <vault-tunnel> pattern
- One tunnel for the vault, named for the vault. It routes
  `<vault-hostname>` to OpenBao's localhost HTTP listener on the
  vault server, with a fallback 404 for anything else.
- The tunnel runs as a systemd service on the vault server, enabled
  and started, as the vault server's own user, with its own config
  file. Never run the tunnel by hand when the service owns it.
- Create the tunnel with the dashboard login flow, not by copying
  an old tunnel token. An old tunnel token, once its tunnel is dead,
  returns "Unauthorized: Invalid tunnel secret" and cannot revive
  the old tunnel. If a token file on the server is an old tunnel's
  token, discard that route and do the dashboard login flow again.
  The user authorises that flow once, in the dashboard, with Google
  sign-in. The assistant does everything else.
- After the tunnel is live, verify it three ways: the tunnel shows
  connections in the dashboard, `<vault-hostname>` no longer returns
  Error 1033, and the vault health endpoint redirects to Access
  instead of returning a tunnel error. Error 1033 means the tunnel
  connector is not live, not that the vault is down. Fix the tunnel,
  not the vault, first.

## Access — the root application
- Application, example name `OpenBao Vault` (not a required name), for `<vault-hostname>`, self-hosted.
- Policy 1: Allow, only the owner, via Google sign-in. No other
  human identity is added.
- Policy 2: Service Auth, for the shared Access service token used by the
  coordinating AI and by any AI that can present two Access headers
  plus a Vault token. The service token is a pair: a Client ID and
  a Client Secret. Both headers must be sent together, plus the
  Vault token, for a normal sign. See the parent skill's token
  shapes reference for how to recognise each value without ever
  seeing a real one.
- Session duration for the web application is 24 hours. That does
  not extend a 30-minute SSH certificate. Do not confuse the two.
- Never type a service-token pair into the Vault web UI. The pair
  is for request headers, or for a secure entry that feeds headers.
  Seeing the Vault UI means the Access gate was already passed,
  usually by Google sign-in. The Vault UI is not the sign test.

## Service tokens — creation rules
- Create a service token only when an AI actually needs one, name
  it clearly for that AI, and set a duration the owner approves.
  The Client Secret is shown only once, at creation. The Client ID
  can be seen again later in the list; the Secret cannot.
- If a created token disappears from the Service Tokens list, or a
  policy for it was never saved, treat any pair copied from that
  creation as not corresponding to a working token, until a live
  sign proves otherwise. Do not keep retrying a disappeared token.
  Recreate it cleanly, or switch to Route C, and record the
  disappearance as an open item. This happened once in the
  original rebuild; its cause is unverified, see the parent
  skill's research notes.
- Never delete the existing shared Access service token, and never delete
  an existing policy, to make room for a new token. Add-only.
  A new token that requires deleting an old policy is the wrong plan.

## Appendix — Route C, narrow Bypass, for a single-credential secret store only (optional variant)
This appendix is not part of the main flow. Use it only for an
AI whose secret store allows only one credential per request.
Route C is verified live on the original build. It is not a general
loosening of the gate.
- Create a separate Access application for that AI's sign path
  only, for example
  `<vault-hostname>/v1/ssh-client-signer/sign/<ai-role>`, self-hosted,
  with one policy: Bypass, Include Everyone.
- The more specific path takes precedence over the root
  application, and no policy is inherited from the root for that
  path. The rest of `<vault-hostname>`, including the web UI and
  every other sign path, stays behind the root application's
  policies.
- That AI then signs with its Vault token only, one credential,
  no Access headers. This fits a secret store that allows only one
  stored credential per request.
- Route C does NOT make the sign path open. Vault still requires
  a valid token for that role. A request without a valid token
  returns Vault `403 permission denied`, not a certificate. Verify
  that live, with no headers and no token, before telling the AI
  to rely on Route C. Also verify that the root path and the other
  sign paths still redirect to Access login without headers.
- Do NOT create a Bypass for the whole `<vault-hostname>`
  application, and do NOT create a Bypass for any other path, to
  fix a sign failure. If a path-specific application cannot be
  created in the dashboard, stop and report that, do not broaden
  the Bypass.
- Single-header service-token mode is NOT a substitute for Route
  C for a single-credential secret store. It still needs the Vault token as
  a second header, so two credentials are still needed in one
  request. The vendor docs describe single-header mode as an
  alternative to the two-header Access pair, not as a way to
  combine Access and Vault credentials into one header.

## SSH through the tunnel — for the boxes
- Boxes are reached as `<ssh-host-1>` port <ssh-port-1> and
  `<ssh-host-2>` port <ssh-port-2> (example: 2222), through
  `cloudflared access ssh`
  as the SSH ProxyCommand. Direct SSH to those hostnames, without
  the ProxyCommand, times out on banner exchange or reaches the
  wrong address. That is a client-path problem, not proof the box
  is down. Always use the ProxyCommand form, and make sure
  `cloudflared` is installed on the client first.
- If a client reports "Permission denied" on a box, that proves
  SSH is reachable and the key or certificate is wrong or expired.
  Do not treat it as a tunnel failure.

## Operating rules
1. Cloudflare login is Google sign-in, never email and password.
   The dashboard login step is the user's one action for that
   step; the assistant does the tunnel and application work.
2. Changes in this skill are dashboard changes. Verify them in the
   dashboard list after saving, and verify them live with a
   headerless request, before telling any AI to rely on them.
3. Never report a service token's Client ID or Secret, in any form,
   in a report, a post, or a file. Report only the token name, its
   enabled state, and whether it is in the application's policy.

## Detail
See `references/cloudflare-setup.md` for the tunnel checklist, the
Access application checklist, the service-token checklist, and
the Route C appendix checklist with its live-verification steps.
