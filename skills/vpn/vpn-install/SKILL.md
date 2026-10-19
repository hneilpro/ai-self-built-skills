---
name: "vpn_install"
description: "Install a chosen VPN on Linux, Windows, mobile, or as a browser extension — official clients first, manual WireGuard/OpenVPN config as fallback. Use after vpn_research picks a provider, or when the user names a VPN to set up."
---

# VPN Install

## Purpose
Get the chosen VPN installed and its tunnel verified on the target machine or browser.

## Workflow
1. Confirm the provider — the default is **Proton VPN Free** (see
   `../vpn-research/references/current-picks.md` for the ranked list and
   why). If the user names another provider, sanity-check it against
   `../vpn-research/references/avoid-list.md` first.
2. Identify the platform: Linux (which distro), Windows 11, Android, iOS, or browser-only.
3. Install via the official path — per-platform commands in `references/install-matrix.md`. Official GUI/CLI client first: it bundles kill switch + protocol selection.
4. Fallback if the official client fails: generate a WireGuard (or OpenVPN) config from the provider's account dashboard and import it — standalone WireGuard app on Windows, `wg-quick` or NetworkManager import on Linux.
5. Enable the kill switch in the client. On raw `wg-quick` setups, add the firewall kill-switch rules from the install matrix.
6. Verify before handing off: `curl ifconfig.me` shows the VPN exit IP, not the ISP's; `wg show` confirms the handshake on manual setups. Then run the `vpn_use` verification ritual.
7. If install fails on every path, walk the fallback chain — Proton VPN → Windscribe → hide.me → PrivadoVPN → TunnelBear — then report. (hide.me's signup now requires an email address as of 2026-09-30; it is no longer the no-signup fallback.)

## Output Contract
- Client installed from the official source (never a third-party APK/site).
- Kill switch on.
- Exit IP verified as the VPN's.
- Note of which protocol is in use and why.

## Operating Rules
1. Download clients only from the provider's official site or the OS app store — never APK mirrors or "free VPN downloader" sites.
2. Browser extensions are HTTPS proxies covering browser traffic only — never present one as full-device protection (see `references/browser-caveat.md`).
3. Approve the OS VPN-configuration prompt on mobile on first connect — that's the OS, not the app, asking; it's normal.
4. Never reuse one WireGuard identity on two machines; regenerate the config per device from the dashboard.
5. For WireGuard configs from a dashboard, treat the private key like a password — don't paste it into chat or logs.

## Troubleshooting (field notes 2026-09-30)

- hide.me: the free signup at member.hide.me now requires an email address
  (single required "Email address" field; no username/password-only flow).
  The Linux CLI's `token` command also requires credentials despite the
  "no signup" marketing — pass them non-interactively with
  `hide.me -u <user> -P <pass> token` (piped stdin fails with
  "Credential error: not a terminal").
- Windscribe: `windscribe.com/install/desktop/linux_deb_x64_cli` returns an
  HTML page, not the .deb — fetch the CLI from the official GitHub release
  assets (Windscribe/Desktop-App) and verify the published SHA-256.
  CLI v2.24.12 refuses to run as root and needs a user D-Bus/systemd
  session (`systemctl --user`); it will not start in root-only containers.
  The dashboard OpenVPN/WireGuard config generator is Pro-only — free
  accounts cannot download manual configs.
- Sandboxed/proxied networks: clients that pin their own CA (hide.me CLI)
  fail when DNS is intercepted or DoH is blocked. Quick check: if
  `nslookup` returns 198.18.x.x for every domain, traffic is proxied and
  native VPN clients will likely fail — say so early instead of
  yak-shaving the install.
