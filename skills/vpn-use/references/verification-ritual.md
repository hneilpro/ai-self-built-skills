# Verification Ritual — run on every connect (~30 seconds)

A VPN that leaks is worse than no VPN: it gives false confidence. All three
checks must pass.

## 1. Exit IP

```bash
curl ifconfig.me
```

The returned IP and country must belong to the VPN provider, not the ISP.
Cross-check at **ipleak.net** in a browser for the geolocation the web
sees.

## 2. DNS leak test

Go to **dnsleaktest.com** → run the **extended** test. Every DNS server
listed must belong to the VPN provider (or its resolver). If the ISP's
DNS appears, traffic is leaking around the tunnel — reconnect, switch
server, or check the client's DNS settings.

## 3. WebRTC leak test

Go to **browserleaks.com/webrtc**. The real public IP must **not** appear
anywhere on the page. This one is critical when using browser extensions
(proxies don't cover WebRTC unless the extension explicitly blocks it).

## On failure

Any mismatch is a hard stop:
1. Disconnect and reconnect (new server, same country).
2. Switch protocol — WireGuard first, then an obfuscated one
   (Stealth/Scramble/GhostBear/WStunnel) if the network is hostile.
3. If it still leaks, the client or config is broken — fall back to
   `vpn_install`'s fallback chain before trusting the tunnel.
