# Cloudflare setup — tunnel, Access, service tokens, Route C appendix

Verified live during the original build. Dashboard layout changes; the names below are
the names seen in the the original build dashboard. If a name has moved,
find it by the function (Tunnels, Access Applications, Service
Tokens), not by guessing a URL.

## Tunnel — checklist
- [ ] Dashboard login: Google sign-in, never email and password.
  The user authorises this once; the assistant does the rest.
- [ ] Tunnels are under Networking, then Tunnels, in the unified
  dashboard. Legacy tunnel pages that say tunnels have moved are
  not the current page; follow the move, do not work on the legacy
  page.
- [ ] Create a new tunnel, named for the vault. Do not copy an old
  tunnel token. If a token file on the server belongs to an old,
  dead tunnel, discard that route and do the dashboard login flow
  again. An old token returns "Unauthorized: Invalid tunnel secret"
  and cannot be revived.
- [ ] Route DNS `<vault-hostname>` to the new tunnel. Overwrite the
  old DNS route if it still points at a dead tunnel; do not leave
  two routes for the same hostname.
- [ ] Ingress: `<vault-hostname>` to OpenBao's localhost HTTP
  listener on the vault server, fallback 404 for anything else.
- [ ] Run the tunnel as a systemd service on the vault server,
  enabled and started, as the vault server's own user, with its own
  config file. Never run it by hand when the service owns it.
- [ ] Verify: tunnel shows connections in the dashboard,
  `<vault-hostname>` no longer returns Error 1033, and the vault
  health endpoint redirects to Access, not to a tunnel error.

## Access, root application — checklist
- [ ] Applications are under Zero Trust, then Access, then
  Applications. Access applications are under Access controls in
  some dashboard views; find them by function, not by a single
  menu label.
- [ ] Application: `OpenBao Vault`, self-hosted, for
  `<vault-hostname>`.
- [ ] Policy 1: Allow, owner only, Google sign-in. No other human
  identity.
- [ ] Policy 2: Service Auth, shared Access service token. Verify the
  token name is in the policy, and its state is Enabled, in the
  dashboard list, without ever reporting a value.
- [ ] Session duration: 24 hours, for the web application only.
  This does not extend a 30-minute SSH certificate.
- [ ] Verify: without headers, the root path redirects to Access
  login. With the shared service-token headers, a sign returns 200.
  Never type a service-token pair into the Vault web UI; the pair
  is for headers or for a secure entry that feeds headers.

## Service tokens — checklist
- [ ] Create only when an AI actually needs one. Name it clearly
  for that AI. Set a duration the owner approves.
- [ ] At creation, copy both fields immediately: Client ID first,
  Client Secret second. The Secret is shown only once. The Client
  ID can be seen again later; the Secret cannot.
- [ ] Add that exact token name to the root application's Service
  Auth policy, keeping the existing policies intact. Save, then
  verify the policy list shows it. A token created but never added
  to a policy will not pass the gate, and a policy draft left
  unsaved is not a policy.
- [ ] Never delete the shared Access service token, and never delete an existing
  policy, to make room for a new token. Add-only.
- [ ] If a created token disappears from the list, or its policy
  was never saved, treat any pair copied from that creation as not
  working, until a live sign proves otherwise. Recreate cleanly, or
  switch to Route C, and record the disappearance as an open item.

## Appendix — Route C checklist, for one AI's sign path only (optional variant)
- [ ] Trigger confirmed: that AI cannot present three headers
  together because its secure entry system allows only one
  credential per request, and its sign failed with
  `credential_ambiguity` or a similar single-credential error.
  Do not use Route C for an AI that can present three headers;
  that AI uses the normal path.
- [ ] Create a separate Access application, self-hosted, for that
  AI's sign path only, for example
  `<vault-hostname>/v1/ssh-client-signer/sign/<ai-role>`. Name it
  clearly, for example `OpenBao Vault sign <ai-role> bypass`.
- [ ] One policy for that application only: Bypass, Include
  Everyone. Save it. Verify the dashboard confirms the application
  and the policy were saved, and that the Applications list count
  increased by one, with the new application showing that exact
  domain and path and that Bypass policy.
- [ ] Verify the existing root application is unchanged: same
  policies, same token state, not edited, not deleted, not saved.
  If the root application was edited to create Route C, stop and
  undo that edit; Route C must be a separate application, not a
  change to the root.
- [ ] Live-verify, with no headers and no token, before telling
  the AI to rely on Route C:
  - That AI's sign path returns Vault `403 permission denied`,
    not an Access redirect. That proves the gate is bypassed for
    that path, and Vault still requires a valid token.
  - The root path still redirects to Access login, without headers.
  - Another sign path, for a different role, still redirects to
    Access login, without headers. That proves the Bypass is
    narrow, not broad.
- [ ] Tell that AI to sign with its Vault token only, no Access
  headers, using Appendix Message A in the parent skill's
  onboarding references, only after this appendix checklist passes. Its Access entries, if already submitted,
  are kept but not used for that sign.
- [ ] Do NOT create a Bypass for the whole `<vault-hostname>`
  application, and do NOT create a Bypass for any other path, to
  fix a sign failure. If a path-specific application cannot be
  created, stop and report that, do not broaden the Bypass.
- [ ] Single-header service-token mode is not a substitute here.
  It still needs the Vault token as a second header. See the
  parent skill's Single-credential variant — pointer only section for why.

## SSH through the tunnel — checklist for the boxes
- [ ] Boxes: `<ssh-host-1>` port <ssh-port-1> and `<ssh-host-2>`
  port <ssh-port-2> (example: 2222), user `<ssh-user>`, ProxyCommand
  `cloudflared access ssh` with the box hostname.
- [ ] `cloudflared` is installed on the client before any SSH test.
  A missing `cloudflared` is a client setup failure, not a box
  failure.
- [ ] A "Permission denied" after the ProxyCommand means SSH is
  reachable and the key or certificate is wrong or expired. It
  does not mean the tunnel is down.
