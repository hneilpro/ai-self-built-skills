# Access requirements

These skills are playbooks, not access grants. A skill can only run when
the access below is already in place, arranged by the owner.
Nothing in this repo contains credentials, tunnel URLs, or keys, and no
skill may invent or store them.

## Per skill

| Skill | Access required before it can run |
|---|---|
| forge-image-gen | See below. Owner's Windows PC + Forge + a live tunnel URL the owner pastes in chat. |
| vpn-research | Public web access only. No account. |
| vpn-install | Admin/sudo on the target machine to install a VPN client, plus an account with the chosen provider (free tier is enough). |
| vpn-use | A VPN already installed and signed in on the target machine (see vpn-install). |

## forge-image-gen in detail

This skill generates images on the owner's own PC. It does not work
standalone, on Muse's VM, or for anyone else. It requires, all at once:

1. His Windows PC (Ryzen 9 5900X / RTX 4090) powered on and signed in.
2. Forge WebUI installed there, with a checkpoint present (verified
   2026-10-07: epicrealismXL_vxviiCrystalclear), launched with
   `--api --listen` listening on port 7860.
3. A live route from the agent to that PC, opened by him:
   - Preferred: he runs `cloudflared tunnel --url http://localhost:7860`
     (from WSL) and pastes the fresh `https://....trycloudflare.com`
     URL into chat. URLs are ephemeral — a new one every session.
   - Fallback: this device approved in his Tailscale tailnet, with
     Forge reachable on the PC's tailnet address. Probed 2026-10-07:
     not reachable that way, so cloudflare is the proven route.
4. No login or API key: Forge's API is unauthenticated. The tunnel URL
   is the access. Anyone holding it can use his GPU while it lives, so
   URLs are never committed, logged to memory, or shared, and he should
   stop cloudflared when he's done.
5. Egress from the agent through its normal proxy to that URL.

If any of 1-3 is missing, the correct behavior is to ask him for a
fresh tunnel URL — not to retry, guess a URL, or fall back to another
image service without saying so.

## General rule for new skills

Every skill added here must state, in this file or its own ACCESS
note: what machine, account, permission, or live session it needs,
who grants it, and what happens without it (usually: stop and ask).
