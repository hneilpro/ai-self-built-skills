# Self-Hosted VPN — the improvement path

When free tiers aren't enough (caps, audits, region choice) but a paid
commercial VPN isn't wanted, run your own server. The core tradeoff, stated
honestly:

> You stop trusting the VPN company and start trusting the **VPS host**,
> which sees connection metadata (your IP, timing, traffic volume). A
> single-tenant exit IP is trivially attributable to one person. Good for
> defeating ISP snooping and public-Wi-Fi attacks; **poor for anonymity**
> (for that, use Tor). You also own patching, key management, and uptime.

Cost framing: a ~$5/mo VPS ≈ a discounted 2-year commercial VPN plan.
Self-hosting wins on control and flat per-server pricing for many devices,
not on price or region count.

## Options

1. **Outline VPN** (easiest) — Google Jigsaw project, run by the independent
   Outline Foundation since Jan 2026. Shadowsocks-based, often more
   censorship-resistant than WireGuard/OpenVPN. Manager app spins up a
   server on DigitalOcean etc. in ~15 min; simple clients. Software free;
   VPS typically ≤ $5/mo.
2. **WireGuard on a cheap VPS** (most control) — $2.50–$10/mo VM
   (Vultr/Linode/DigitalOcean/Hetzner; Oracle Cloud free tier possible),
   install WireGuard, generate peer keys. ~30–60 min setup, dedicated IP,
   unlimited devices for one flat price. 1–2 vCPU / 1–2 GB RAM is plenty.
3. **Algo** (Trail of Bits) — Ansible scripts deploying a hardened
   WireGuard/IPsec server in minutes. Needs Ansible + a cloud account; best
   for terminal-comfortable users. Free software, same VPS cost.
4. **Streisand** — deploys many protocols at once. Caution: development has
   slowed — verify current maintenance on GitHub before choosing it over
   Algo/Outline.
