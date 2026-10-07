# Research: why Forge v2 fails high-quality consistent character (2026-10-07)

Question: why does the current forge_gen.py not deliver built-in-generator-level
consistency, and what must change so SDXL *and* Flux produce the same face
every time, with proof?

## What v2 gets right
- Probe-first design, character profiles outside repo, error-driven downgrade,
  img2img with a character init image verified live (locks pose/body).
- Local swap (InsightFace inswapper_128) measured 0.92-0.94 ArcFace cosine
  after swap vs 0.10 drifted — the only route that passes a verifier today.

## Why v2 still fails (load-bearing findings)

1. **Accepted != effective.** Live A/B on the owner's Forge: ControlNet-routed
   FaceID and InstantID register in infotext but produce byte-identical pixels
   when the reference face is swapped for an unrelated face. The server returns
   HTTP 200, so `run_generation()` stops at the first "successful" mode and
   never reaches a working backend. A payload being accepted is not identity.
   (Source: .agents/test-reports/2026-10-07-forge-consistent-character.md
   live addendum; corroborated by upstream reports of InstantID units doing
   nothing on some Forge/ControlNet builds.)

2. **Verification only runs after a swap, never as a gate.** `face_similarity`
   is computed only when `mode_used == "local-swap"`. Every other mode ships
   unverified. There is no "is this recognizably the same person?" check, so
   drift is invisible until the user eyeballs it. Industry practice is an
   ArcFace cosine gate: same-person is typically >0.5, strict pipelines use
   0.4-0.6 depending on the model; InsightFace buffalo_l embeddings are the
   de-facto standard for this check (FaceID, PuLID, InstantID all consume an
   ArcFace-family embedding).

3. **Auto order buries the working route.** Order is
   pulid > instantid > faceid > reactor > img2img-ref > local-swap > none.
   img2img-ref (composition only, explicitly "weakest") outranks the proper
   face swap, and because of (1) the chain usually stops even earlier.

4. **No Flux path.** All identity payloads are SDXL-shaped: the FaceID LoRA
   tag `<lora:ip-adapter-faceid-plusv2_sdxl_lora:0.8>`, SDXL ControlNet model
   names, DPM++/CFG 6 defaults. Flux checkpoints need different handling:
   Flux has its own PuLID line (PuLID-Flux / PuLID-Flux II, and now Flux.2
   variants) with InsightFace + EVA-CLIP -> ID tokens injected into Flux
   double blocks, recommended weight ~0.9-1.0 (SDXL PuLID) and ~0.5-0.7 for
   Flux.2 Klein native weights, and Euler-family sampling at low CFG.
   Injecting SDXL adapters into a Flux run is at best a no-op.

5. **Identity adapter lineage (what "good" looks like).** IP-Adapter-FaceID
   (2023) < InstantID (Jan 2024) < PuLID (Apr 2024, NeurIPS): PuLID's
   contrastive alignment preserves prompt-following better than InstantID /
   FaceID, which degrade style control. Even so, all training-free routes
   drift at extreme angles; a LoRA trained on 15-25 curated refs remains the
   ceiling. Face *swap* (inswapper) is a different tool: post-hoc, highest
   measured similarity, weakest at extreme profile/lighting. A robust
   pipeline uses adapter-during-diffusion *plus* swap-if-needed *plus*
   verification — not any one alone.

6. **Quality ceiling is not the sampler.** HQ preset (1024x1536, 40 steps,
   ESRGAN 1.5x) is fine for SDXL. What is missing for "high-quality like the
   built-in generator" is: correct checkpoint-family defaults, face-aware
   post step (swap + verify, not just upscale), and not wasting the one
   strong signal (the reference face) on backends proven inert on this build.

## Design consequences
- Identical-face must be a *pipeline guarantee*, not a mode name: when a
  character/ref is present, generation MUST (a) condition on the ref during
  diffusion where a live backend exists, (b) verify the result with ArcFace,
  (c) auto-swap locally if verification fails, (d) re-verify and report both
  scores. `--identical-face` (default ON when a ref exists) names this;
  `--no-identical-face` is the explicit opt-out the owner described.
- Face swap is not a fallback afterthought; it is the enforcement step of
  the identical-face guarantee.
- Verification needs its own fast path in the swap tooling (embed + compare
  without swapping) so the gate costs seconds, not a second generation.
- Checkpoint family (sdxl / flux / sd15) must be detected from the model
  name and drive sampler/CFG/adapter eligibility; unknown family warns
  instead of silently applying SDXL assumptions.

## What remains uncertain (needs the 4090)
- Whether ReActor or PuLID gets installed on the PC; the design must work
  *today* with zero PC installs (local swap does) and improve automatically
  when they appear (probe already handles this).
- Flux checkpoint name on his Forge, if any; family detection is heuristic
  with an explicit `--model-family` override.
- Swap quality at his preferred full-body framings (small faces in frame
  swap worse); mitigation is verify + report, plus guidance to generate
  face-forward first, then img2img the outfit/pose.
