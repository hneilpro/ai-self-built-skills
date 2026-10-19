---
name: "vpn_use"
description: "Day-to-day VPN operation: connect, verify no leaks (IP/DNS/WebRTC), switch servers, manage data caps, handle blocked servers, disconnect. Use whenever the user wants to actually use their VPN."
---

# VPN Use

## Purpose
Operate the VPN correctly every session: connected, verified leak-free, and
used within its limits. Defaults below assume **Proton VPN Free** (the
standing recommendation — see `../vpn-research/references/current-picks.md`
for the ranked list); provider-specific differences are noted inline.

## Workflow
1. Connect — default to the app's **Quick Connect** / fastest server.
   Manual country pick only when needed (Windscribe/PrivadoVPN/hide.me
   allow it; Proton Free auto-selects).
2. Run the verification ritual (`references/verification-ritual.md`):
   exit IP matches the VPN, DNS resolves through the provider, WebRTC
   shows no real IP. Any mismatch = hard stop: reconnect or switch server.
3. Respect the data cap on metered tiers — check the usage meter in the
   app. When capped: PrivadoVPN drops to 1 Mbps emergency servers instead
   of cutting off; otherwise switch to an unlimited free tier
   (Proton/hide.me) or wait out the month.
4. If a site/service blocks the server: switch server in-country → switch
   to an obfuscated protocol (Stealth/Scramble/GhostBear/WStunnel) →
   clear cookies and retry → accept that free tiers are systematically
   blocked by major streaming services.
5. Split tunneling (optional): route only sensitive apps through the VPN
   to save cap — warn that excluded apps are ISP-visible.
6. Disconnect via the app (don't just close the lid); confirm the tunnel
   is down if it matters.

## Output Contract
- Connected server + exit IP/country stated.
- Verification ritual passed (IP/DNS/WebRTC), or the failure and the fix.
- Cap status noted when on a metered tier.

## Operating Rules
1. Never skip verification on a new server — one `curl ifconfig.me` is the
   minimum.
2. A VPN hides the IP; it doesn't stop tracking — pair with uBlock Origin
   and HTTPS-only mode for real privacy.
3. **WireGuard is the default protocol** (fastest, modern, audited).
   Obfuscated protocols are for networks that block VPNs (hotels,
   campuses, restrictive countries), not for daily speed. IKEv2 is a
   legacy fallback.
4. Re-verify after any reconnect, network change, or wake-from-sleep.
5. For manual WireGuard setups, regenerate the keypair/config every few
   months from the provider dashboard.
