# Install Matrix — verified 2026-09-30

Always prefer the provider's current official install page over these notes;
package names drift. The paths below are the known-good routes.

## Linux

**Official clients (first choice):**
- **Proton VPN:** add Proton's APT repo (`repo.protonvpn.com/debian`),
  install the `protonvpn-cli` / GUI package, then `protonvpn-cli login`,
  `protonvpn-cli connect`, `protonvpn-cli status`. An official Linux GUI
  also exists.
- **Windscribe:** ships a Linux CLI (`windscribe-cli` via their APT repo)
  plus a GUI.
- **hide.me:** Linux GUI available. **TunnelBear:** limited CLI support.
  **PrivadoVPN:** manual config only on Linux.

**Manual WireGuard (any distro, no vendor app):**
1. Provider account dashboard → Downloads → generate a **WireGuard
   `.conf`** (all five recommended providers offer manual configs).
2. `sudo apt install wireguard-tools`, copy the config to
   `/etc/wireguard/<name>.conf`, then `sudo wg-quick up <name>`.
3. Or import into NetworkManager GUI: "Add connection → Import VPN
   connection" → select the `.conf` (native WireGuard support, no plugin).
4. `wg show` confirms the handshake; `curl ifconfig.me` shows the exit IP.
5. Persistence: `systemctl enable wg-quick@<name>`. Kill switch for raw
   wg-quick = firewall rules (nftables/iptables) that drop everything not
   leaving through the tunnel interface — test by killing the tunnel and
   confirming traffic halts.

**Manual OpenVPN fallback:** download the `.ovpn` from the dashboard,
`sudo openvpn --config file.ovpn`, or import into NetworkManager via the
`network-manager-openvpn` plugin. Note: Proton uses separate
OpenVPN/IKEv2 credentials from the dashboard, not the account password.

## Windows 11

- **Official GUI clients** (recommended): Proton VPN, Windscribe,
  TunnelBear, PrivadoVPN, and hide.me all ship Windows apps with one-click
  connect, kill switch, and protocol selection. Download from the
  provider's official site only.
- **Manual WireGuard app:** official WireGuard for Windows
  (wireguard.com) → "Import tunnel(s) from file" → import the
  provider-generated `.conf` → Activate. Lightweight fallback when the
  vendor app misbehaves.

## Android / iOS

1. Install the official app from **Google Play / App Store only**.
2. Create the account (or skip on hide.me), pick the free tier.
3. Approve the OS **VPN configuration prompt** on first connect (normal).
4. Enable **kill switch** (Android) and **auto-connect on untrusted Wi-Fi**
   where offered. Quick Connect to start.

## Browser extensions

See `references/browser-caveat.md` — extensions from Proton VPN,
Windscribe, and TunnelBear exist for Chrome/Firefox/Edge, but they are
proxies, not VPNs. Install the full-device client alongside; use the
extension only for quick in-browser switching.
