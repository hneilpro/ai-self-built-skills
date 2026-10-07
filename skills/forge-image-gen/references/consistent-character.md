# Consistent characters in Forge — what to install on the PC

forge_gen.py probes the server (`--probe-server`) and uses the best identity
backend present. Install in this order; stop when one strong route works.

## 1. PuLID (best training-free identity, SDXL)
- Needs: PuLID model for SDXL + InsightFace `antelopev2` + EVA-CLIP support
  in the ControlNet/IPAdapter stack.
- Put the PuLID ip-adapter model with the other IP-Adapter models, restart
  Forge, re-run `--probe-server` — `pulid: true` means the tool will use it.
- Starting weight: `--face-weight 0.85`. Raise toward 1.0 for a tighter
  likeness, lower if the face starts overriding the prompt's styling.

## 2. InstantID (strong, heavier)
- Two ControlNet models: `control_instant_id_sdxl` (keypoints) and the
  InstantID IP-Adapter (`ip-adapter_instantid_sdxl`). Both must be listed
  by `--probe-server` before auto mode will choose it.
- Uses two ControlNet units; slower than FaceID, stronger at odd angles.

## 3. IP-Adapter FaceID Plus v2 (light, very reliable)
- Files: `ip-adapter-faceid-plusv2_sdxl.bin` (IPAdapter models folder) and
  `ip-adapter-faceid-plusv2_sdxl_lora.safetensors` (LoRAs folder). The tool
  appends the LoRA to the prompt automatically (`--no-faceid-lora` to stop).
- Known Forge gotcha: FaceID preprocessors have failed on some builds with
  an onnx DLL error; if generations 400 with that trace, update onnxruntime
  on the PC or use ReActor (below) meanwhile — the tool downgrades by itself.

## 4. ReActor (face swap, zero diffusion setup)
- Install the ReActor extension in Forge, restart. `inswapper_128.onnx`
  goes in models/insightface. Best when the prompt already produces a
  well-posed face; weakest at extreme profiles and dramatic lighting.

## Honest limits
- All four are training-free: likeness is strong head-on, drifts at extreme
  angles. For a character used hundreds of times, a LoRA trained on 15–25
  curated references still wins; treat that as its own project.
- img2img-ref (the built-in last resort) locks composition, not identity —
  the tool labels it in FORGE_RESULT so it is never mistaken for a face lock.
- Note: `--face-weight` drives PuLID/InstantID/FaceID strength. ReActor's
  swap has no equivalent weight here; face_weight is ignored in reactor mode.

## Verified on the owner's build (2026-10-07, live A/B)
| Route | Result via API |
|---|---|
| FaceID / InstantID via ControlNet units | Registered in infotext, **zero pixel effect** on this build (ref-swap test: byte-identical). Do not rely on it until the PC-side IPAdapter path is fixed. |
| img2img with a character init image | **Works today.** Locks pose/body/composition; raise --denoise (0.6+) when the prompt must change the outfit. |
| ReActor / PuLID | Not installed on the PC yet. Install ReActor first — simplest — then auto mode uses it with no code change. |

## Local swap — the route that passes a FaceID check (added 2026-10-07)
`--face-mode local-swap`: generate normally (txt2img or img2img), then the
agent swaps the reference face in locally with InsightFace inswapper (the
same model ReActor uses) and reports `face_similarity` — the ArcFace cosine
a FaceID program computes. Measured on the owner's build: drifted img2img
output scored 0.10 (different person), after local swap 0.92–0.94 (same
person by any verifier threshold). Setup lives at ~/workspace/forge-face-swap/
(.venv + inswapper_128.onnx); auto mode falls back to it when present.
This beats every server-side route on a Forge build whose IPAdapter path
is inert, because it does not depend on Forge extensions at all.

## v3: the identical-face guarantee (2026-10-07)
Diagnosis (full note: .agents/research/2026-10-07-forge-v3-diagnosis.md):
v2 trusted any payload the server accepted — but on this Forge build the
ControlNet identity units are pixel-inert, so "face_mode_used: faceid" shipped
unverified drift. v3 inverts the trust: pixels are measured, not payloads.

Pipeline for every character generation:
1. Condition during diffusion with the best live backend (auto order above).
2. Verify: ArcFace cosine (InsightFace buffalo_l) between the reference and
   the result — `forge_gen.py --character vj --verify <image>` runs this
   check alone, no server needed.
3. Below `--verify-threshold` (default 0.55; same-person is ~>0.5, a good
   swap measures 0.9+): auto-run the proper local face swap
   (inswapper_128, same model ReActor uses), then re-verify.
4. Report both scores + `identity_pass`; `--strict-identity` fails the run
   rather than shipping a face that still does not verify.

Measured locally on the owner's stack: drifted Forge outputs score
-0.02..0.08; after the local swap 0.92-0.94. Reference vs itself: 1.0.

### SDXL vs Flux
Family is detected from the checkpoint name (`--model-family` overrides)
and sets sampler/CFG defaults (SDXL: DPM++ 2M Karras, CFG 6; Flux: Euler,
CFG 3.5). SDXL-only adapters (FaceID/InstantID ControlNet, the FaceID LoRA)
are never sent to a Flux checkpoint. Flux identity today = generate, verify,
swap; PuLID-Flux exists in the ComfyUI ecosystem and would slot into the
probe order if a Forge-native backend appears. A character LoRA (SDXL or
Flux) remains the long-term ceiling for hundreds of generations.
