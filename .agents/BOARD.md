# BOARD — inter-agent message board

The shared, durable board for every agent working in this repo. Read the latest entries at session start before doing anything else here. Post when you: start or finish a phase, switch roles, hand off, hit a blocker, record a critic verdict, or need a human decision.

## Rules

- Append-only. Never edit or delete another agent's entry, and never rewrite your own entry after someone has replied to it; post a correction as a new entry instead.
- Newest entry at the TOP (directly under this rules block), so the current state is the first thing read.
- One entry per event. Keep it short: what happened, evidence pointer, what is needed next.
- Sign every entry with role, task id, and date (YYYY-MM-DD).
- This board is coordination, not a task tracker and not a chat log. Durable detail belongs in tasks/, handoffs/, reviews/, test-reports/, decisions/, or research/; the board entry links to it.
- No secrets, no real personal data, no raw transcripts. Distilled findings only.

## Entry format

```text
## YYYY-MM-DD — <role> — <task-id> — <event>
<2-6 lines: what changed / what was found / verdict>
Evidence: <path or command>
Next: <owner/role + exact next action, or "none">
```

---

<!-- Post new entries below this line, newest first. -->

## 2026-10-07 — critic — forge-v3-consistent-character — approve with notes
Self-review: v3 gate/family/Flux changes approved; 34/34 tests + real-model measurements (drift ~0.0 -> 0.92 post-swap). Minors N1-N3 noted, none blocking. Live GPU run remains unverified pending a fresh tunnel URL. Review: .agents/reviews/2026-10-07-forge-v3.md.
Evidence: .agents/test-reports/2026-10-07-forge-v3.md
Next: owner — paste a fresh Forge tunnel URL for the live SDXL/Flux check; branch still held for batched push.



## 2026-10-07 — builder — forge-v3-consistent-character — research+plan complete, build starting
Diagnosis: v2 trusts accepted-but-inert ControlNet payloads, verifies only after its own swap, ranks img2img-ref above the real swap, and has no Flux path. v3 makes identical-face a verified guarantee (condition -> ArcFace verify -> auto local-swap -> re-verify), adds checkpoint-family detection, and a verify-only mode. Research: .agents/research/2026-10-07-forge-v3-diagnosis.md; ADR: .agents/decisions/2026-10-07-identical-face-guarantee.md.
Evidence: .agents/tasks/2026-10-07-forge-v3-consistent-character.md
Next: builder — implement forge_gen.py v3 + swap.py verify mode, then test.



## 2026-10-07 — builder — forge-consistent-character — live A/B result
Live on owner's 4090: ControlNet-routed FaceID/InstantID register but have zero pixel effect via API on this Forge build (proven by ref-swap + signature tests); img2img character route works. True txt2img identity = install ReActor (or PuLID) on the PC; tool auto-detects it after. Docs updated with the verified table.
Evidence: .agents/test-reports/2026-10-07-forge-consistent-character.md (live addendum)
Next: owner — optional ReActor install; branch held for his batched push review, no commit made.


## 2026-10-07 — critic — forge-consistent-character — approve with notes
Self-review (same session, labelled as such): B1 name scrub, B2 auto->none fallback, M1 dual ControlNet image keys + honest "server accepted" wording fixed in revision round 1; 22/22 tests green again. Only open item: live GPU verification needs the owner's fresh tunnel URL.
Evidence: .agents/reviews/2026-10-07-forge-consistent-character.md
Next: owner — run --probe-server + one --character generation with a fresh tunnel URL; no commit until his batched push review.


## 2026-10-07 — builder — forge-consistent-character — build+test complete, to critic
forge_gen.py v2 on feat/forge-consistent-character: character profiles, always-on reference face (pulid>instantid>faceid>reactor>img2img-ref, probed + logged downgrade), txt2img+img2img. 22/22 offline tests pass (fake Forge server). Live GPU run unverified — no tunnel at build time.
Evidence: .agents/test-reports/2026-10-07-forge-consistent-character.md; handoff .agents/handoffs/2026-10-07-forge-consistent-character.md
Next: critic — independent review pass, then role-switch entry.

