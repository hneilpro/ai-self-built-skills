# Task: Forge v3 — verified identical-face pipeline (SDXL + Flux)

## End goal
`forge_gen.py` with a character/ref produces the SAME recognizable face on
every generation (txt2img and img2img, SDXL or Flux checkpoint), proven by an
ArcFace similarity score in FORGE_RESULT — using diffusion conditioning when
a live backend exists and a proper local face swap as the enforcement step,
never an unverified "accepted" payload.

## Acceptance criteria (checkable)
1. When `--character`/`--ref` is present, identical-face is ON by default:
   every result carries `face_similarity` (pre-swap), and if it is below
   `--verify-threshold` (default 0.55) the tool auto-runs the local swap,
   re-verifies, and reports `face_similarity_after_swap` + `identity_pass`.
   `--no-identical-face` disables the gate explicitly; `--strict-identity`
   fails the run instead of shipping a failing face.
2. `--face-mode local-swap` performs a full proper swap (not img2img-ref)
   and verifies; auto order is pulid > instantid > faceid > reactor >
   local-swap > img2img-ref > none (swap outranks the composition-only ref).
3. Checkpoint family is detected (sdxl/flux/sd15/unknown) from the model
   name, reported in FORGE_RESULT, overridable with `--model-family`;
   Flux runs never receive SDXL FaceID LoRA/ControlNet payloads and use
   Flux-appropriate defaults (Euler, low CFG) unless overridden.
4. `swap.py` gains a verify-only mode (`--verify ref target`) that prints
   the ArcFace cosine + face counts as JSON without modifying the image;
   `forge_gen.py --verify <image>` runs the same check standalone.
5. Plain txt2img with no ref behaves exactly as v1/v2 (back-compat);
   all v2 flags keep working. Offline pytest suite passes, including new
   coverage: family detection, flux payload hygiene, identical-face gate
   decisions (pass / auto-swap / strict-fail), verify-mode plumbing via the
   fake server + stubbed swap.
6. Docs (SKILL.md, references/consistent-character.md, api-notes.md) state
   what works today with zero PC installs, what a ReActor/PuLID install
   adds, and that live GPU proof still needs a fresh tunnel URL.

## Blockers / caveats
- No live tunnel at build time: live generation is `unverified` by design;
  offline + local-swap tests cover everything except real GPU pixels.
- Local swap runs on CPU here (buffalo_l + inswapper_128); slow on very
  large images — acceptable, it runs once per generation.
- PuLID-Flux is a ComfyUI-first ecosystem; via Forge API the Flux identity
  route today is verify+swap. The payload builder must not pretend otherwise.

## Plan / design
- Extend `bin/forge_gen.py` (single file, requests+Pillow as before) and
  `~/workspace/forge-face-swap/swap.py` (outside repo; venv already exists).
- Pure, unit-tested helpers: `detect_family()`, `identity_decision()`
  (scores + flags -> action), payload builder family-aware.
- Verification seam: `verify_face()` shells to swap.py `--verify`, parsed
  from its last JSON line; tests stub it, live runs use the real model.
- Owner OK: the 2026-10-07 request explicitly asks to research, design,
  build, test, iterate and self-critique this. That is the Plan-phase OK.

## Test strategy
- `pytest tests/ -q` (existing 22 + new v3 tests) under the image-organizer
  venv python (system python has no pytest).
- Local real-model check: verify-only + swap on the canonical face vs an
  existing drifted forge-test image; record before/after scores.
- Critic pass as a separate role switch after the handoff; max 2 rounds.
