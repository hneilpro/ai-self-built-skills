# Access required for forge-image-gen

This skill grants no access. It only works when the owner has already opened
all of the following, and stops to ask when any piece is missing:

1. His Windows PC (RTX 4090) on and signed in.
2. Forge WebUI there, checkpoint present (verified 2026-10-07:
   epicrealismXL_vxviiCrystalclear), launched `--api --listen` on :7860.
3. A live route he opens: he runs
   `cloudflared tunnel --url http://localhost:7860` (WSL) and pastes the
   fresh https://....trycloudflare.com URL in chat. New URL each session.
   Tailscale fallback exists but Forge was not reachable that way
   (probed 2026-10-07).
4. No login/key — the API is unauthenticated, so the URL itself is the
   access. Never commit, log to memory, or share a URL; he should stop
   cloudflared when done.

Full repo-wide access table: ACCESS.md at the ai-self-built-skills repo root.
