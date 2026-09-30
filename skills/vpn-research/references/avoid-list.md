# Free VPNs to Avoid

Never recommend these. Each entry has a documented reason — cite it if the
user asks why.

1. **Hola VPN** — routes your traffic through other users' devices; strangers'
   activity can originate from your connection. Sells logs via its
   Luminati/Bright Data proxy network.
2. **Betternet** — documented logging record, frequent leaks; same parent as
   Hotspot Shield.
3. **Hotspot Shield (free)** — by its own admission keeps a record of which
   domains users open; free mobile apps run targeted ads on user data.
4. **Urban VPN** — leaks the real IP and sells user records to third parties.
5. **VPN Super Unlimited Proxy** — topped Apple's free-apps chart while
   privacy labels showed it records usage data, tracks users across apps,
   and collects location + identifiers.
6. **Free VPN by Freevpn.org** — no real encryption info, vague privacy
   policy, implicated in a data-breach scandal; the company may not exist.
7. **Free VPN: Unlimited VPN Proxy** — harvests location, usage data, and
   identifiers to track users across the web.
8. **Qihoo 360 cluster** (Super VPN, Secure VPN, Melon VPN, Fast Potato VPN,
   X-VPN, Turbo VPN, …) — near-identical code across "independent" apps,
   weak encryption, hard-coded Shadowsocks passwords, location tracking,
   concealed Chinese ownership. Hundreds of millions of installs.
9. **Turbo VPN / VPN Proxy Master / VPN 360 / Secure VPN** — connect to
   Chinese/Russian infrastructure, embed ByteDance/Yandex tracker SDKs, use
   plaintext HTTP, request dangerous permissions (camera, mic, SMS).

## The studies behind the warnings

- **CSIRO / UNSW / UC Berkeley (2016), 283 free Android VPN apps:** ~38%
  contained malware/adware, 18% didn't encrypt traffic at all, ~75%
  embedded third-party tracking libraries.
- **Top10VPN (2024), 100 free Android VPN apps:** ~90% leaked some user
  data, 17 leaked more than DNS, a third used substandard encryption, ~70%
  requested unjustifiable permissions (location, app scanning), half sent
  data to third parties including ByteDance and Yandex.

Rule of thumb: if a free VPN app asks for contacts, SMS, camera, or
microphone, it's a red flag — no legitimate VPN needs them.
