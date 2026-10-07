---
name: "forge_image_gen"
description: "Generate images (incl. NSFW) on the owner's Forge WebUI on their RTX 4090 PC via a pasted trycloudflare URL. Use for Forge, his 4090, epicRealism, a trycloudflare URL, or txt2img instead of the built-in generator."
---

# Forge Image Gen

Generate on the owner's PC and show them the result. Fictional adults only for NSFW; never a real person nude/sexualized.

## Run
One command does check + generate + upscale + verify:
```
python3 ~/workspace/skills/forge-image-gen/bin/forge_gen.py <pasted-url> --prompt "<prompt>"
```
- Presets: `hq` default (1024x1536, 40 steps, ESRGAN 1.5x → 1536x2304), `probe` (512x768, 20 steps, fast test), `square`, `wide`. Override any with --width/--height/--steps/--seed/--upscale 0.
- The pasted URL is cached locally (0600, not in memory), so follow-ups in the same stretch can omit it: `forge_gen.py --prompt "..."`.
- Health only: add `--check`.
- Last line of output is `FORGE_RESULT {json}` — use its file/seed/checkpoint/final_size for the reply, no extra verification calls. Still view the image before presenting it.

## Consistent characters (verified identical face)
Every generation can carry a reference face so one character keeps the same
face across poses and outfits, in both txt2img and img2img. Identical-face
is ON by default whenever a ref is present: the result is measured against
the reference with ArcFace (the face identifier), and if it scores below
`--verify-threshold` (0.65) it is auto-swapped locally and re-measured.
FORGE_RESULT always reports `face_similarity_before_swap`,
`face_similarity_after_swap`, `identity_pass`, and `face_sharpness`
(the 128px swapper returns soft faces, so swaps run a local detail
restoration by default and blur is reported, never hidden) — an accepted server
payload is never again mistaken for a verified likeness. Opt out with
`--no-identical-face`; fail instead of shipping drift with
`--strict-identity`. Check any image standalone:
`forge_gen.py --character vj --verify <image.png>`. Profiles can also carry a multi-reference set (`--refs-dir <dir>` at save time): swap/verify identity then uses the averaged template of every frontal face in it — one photo is a noisy target (two refs of the same character can score ~0.6 to each other). Swaps restore detail with GFPGAN when its model is present (models/gfpgan_1.4.onnx in the swap home), else a detail graft. Ceiling, stated plainly: a swap pastes identity onto an existing head — it cannot fix wrong geometry/expression. Accurate faces come from conditioning during generation (PuLID/InstantID where the backend truly works, or a LoRA). A curated, score-filtered LoRA pack for VJ lives at ~/workspace/vj-lora-pack/ (dataset + kohya config + validation steps); training runs on the 4090.
```
forge_gen.py --save-character vj --ref <face.jpg>     # once: profile stored locally
forge_gen.py --character vj --prompt "<prompt>"      # every call uses that face
forge_gen.py --ref <face.jpg> --prompt "<prompt>"    # one-off, no profile
forge_gen.py --character vj --init <pose.png> --denoise 0.55 --prompt "..."  # img2img
forge_gen.py <url> --probe-server                    # which identity backends exist?
```
- Backend order in `--face-mode auto` (default): PuLID > InstantID >
  IP-Adapter FaceID Plus v2 > ReActor swap > local swap (proper InsightFace
  swap, agent-side) > img2img-ref (composition only, weakest) — picked from
  what the server actually offers; if the server rejects one, the next is
  tried and the downgrade is reported, never silent. Whatever the server
  does, the identical-face gate above still verifies the pixels.
- Checkpoint family (`sdxl`/`flux`/`sd15`) is auto-detected from the model
  name (`--model-family` overrides) and drives sampler/CFG defaults; SDXL
  adapters are never sent to a Flux checkpoint — Flux identity runs through
  verify + local swap (PuLID-Flux where a Forge backend exists).
  `FORGE_RESULT.face_mode_used` says what the server accepted (view the image — an accepted payload is not a verified likeness). Force one with
  `--face-mode pulid|instantid|faceid|reactor|img2img-ref|none`.
- Strength: `--face-weight` (default 0.85). Optional pose lock: `--pose <openpose.png>`.
- Profiles live at ~/.config/forge-gen/characters/ (0600, outside any repo).
- First run on a new Forge install: run `--probe-server` once. On the owner's current build, ControlNet-routed FaceID/InstantID have no pixel effect via API (live-verified 2026-10-07) — that no longer matters for the guarantee: the gate detects the drift (drifted images measure ~0.0) and the local swap fixes it (measured 0.92+). img2img with a character init still locks pose/body today. Installing ReActor or PuLID on the PC improves the in-diffusion conditioning (fewer swaps needed); the tool picks them up automatically. A LoRA trained on the character still beats every training-free route; that is a separate project, not this flag.

## Output
Show the image as a chat attachment, plus one plain line copied from FORGE_RESULT (checkpoint, preset, seed, final size). Name any failure plainly: unreachable means tunnel/Forge is down — ask him to restart cloudflared and paste a fresh URL, don't retry-loop.

## Rules
1. Script enforces the known fixes — no hires fix, no bare sd_model_name, retries once with a re-check. Don't improvise raw API calls; details only if a call fails: `references/api-notes.md`.
2. URLs are ephemeral and unauthenticated. Never put one in memory, a file in the repo, or a post. It lives only in chat and the script's local cache.
3. Access requirements: see `ACCESS.md` in this repo / skill folder before first use on a new machine.
