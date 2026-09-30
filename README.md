# AI Self-Built Skills

Reusable agent playbooks, built by Muse for Harish. Each skill is a small,
focused directory with a `SKILL.md` (the operational core) plus optional
`references/` for detail that's only needed sometimes.

## Using a skill

Copy the skill directory into the agent's skills workspace (or point the
agent at this repo) — the `SKILL.md` frontmatter (`name`, `description`)
is the trigger surface:

```bash
cp -r skills/<skill-name> ~/workspace/skills/
```

## Skill series: Free VPN

| # | Skill | What it does |
|---|-------|--------------|
| 1 | `skills/vpn-research` | Research free VPNs and evaluate them for safety, security, and privacy — including which ones to avoid and why. |
| 2 | `skills/vpn-install` | Install the chosen VPN on a machine (Linux / Windows) or as a browser extension, with the full-tunnel vs proxy caveat. |
| 3 | `skills/vpn-use` | Day-to-day VPN use: connect, verify the tunnel (IP / DNS / WebRTC leaks), switch servers, disconnect, troubleshoot. |

Run them in order: research → install → use. Each skill stands alone if you
already know your VPN pick.

## Conventions

- One clear job per skill; bulky or conditional detail goes in `references/`.
- Commands and paths must be real and verified, never invented.
- Findings that go stale (prices, caps, server lists) carry a "verified as of"
  date; the evergreen evaluation method lives in the skill body.
