---
name: "vpn_install"
description: "Install a chosen VPN on Linux, Windows, mobile, or as a browser extension — official clients first, manual WireGuard/OpenVPN config as fallback. Use after vpn_research picks a provider, or when the user names a VPN to set up."
---

# VPN Install

## Purpose
Get the chosen VPN installed and its tunnel verified on the target machine or browser.

## Workflow
1. Confirm the provider — from `vpn_research`, or one the user names (sanity-check it against `../vpn-research/references/avoid-list.md` first).
2. Identify the platform: Linux (which distro), Windows 11, Android, iOS, or browser-only.
3. Install via the official path — per-platform commands in `references/install-matrix.md`. Official GUI/CLI client first: it bundles kill switch + protocol selection.
4. Fallback if the official client fails: generate a WireGuard (or OpenVPN) config from the provider's account dashboard and import it — standalone WireGuard app on Windows, `wg-quick` or NetworkManager import on Linux.
5. Enable the kill switch in the client. On raw `wg-quick` setups, add the firewall kill-switch rules from the install matrix.
6. Verify before handing off: `curl ifconfig.me` shows the VPN exit IP, not the ISP's; `wg show` confirms the handshake on manual setups. Then run the `vpn_use` verification ritual.
7. If install fails on every path, walk the fallback chain — Proton VPN → Windscribe → hide.me (no signup, works when email verification fails) → PrivadoVPN → TunnelBear — then report.

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
