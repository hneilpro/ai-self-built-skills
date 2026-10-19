# Browser Extensions Are Not VPNs

The critical caveat to state every time a browser extension comes up.

## What they actually are

Nearly all "VPN" browser extensions are **HTTPS proxies**. They work through
the browser's proxy settings, so they cover **only that browser's traffic**.
Firefox, Outlook, Steam, torrent clients, Zoom, and background processes
keep using the real connection.

Consequences:
- **No kill switch.** A dropped connection silently exposes browser traffic.
- **No WireGuard/OpenVPN** — the proxy API doesn't support real VPN
  protocols.
- **WebRTC can leak the real IP around a proxy.** Use an extension that
  blocks WebRTC, or disable WebRTC in the browser.

## Who offers them

**Proton VPN, Windscribe, and TunnelBear** ship Chrome/Firefox/Edge
extensions usable on free tiers. Windscribe's is the most feature-rich
(R.O.B.E.R.T. blocker, timezone/GPS spoofing, WebRTC blocking, cookie
auto-delete). Opera has a built-in free unlimited "VPN" (4 locations) —
same proxy caveat; fine for light geo-shifting, not privacy.

The one exception pattern: an extension that *drives the desktop app*
covers the device (ExpressVPN does this) — none of the free-tier
extensions work this way.

## The rule

> App for the device, extension for quick switching inside the browser.

Treat any free **standalone proxy extension from an unfamiliar publisher**
as a data-collection tool until proven otherwise — run it through the
`vpn_research` checklist before installing.
