# Test report: forge-consistent-character (builder)

Date: 2026-10-07. Branch: feat/forge-consistent-character.
Runner: ~/workspace/image-organizer-ai/.venv/bin/python -m pytest (system
python has no pytest; sandbox pip mirror too slow to install one — the
existing venv has pytest+requests+Pillow).

## Commands and results
- `python3 -m py_compile bin/forge_gen.py` -> OK
- `python3 bin/forge_gen.py --help` -> new flags present, parses clean
- `pytest tests/ -q` first run: 20 passed, 2 failed.
  Root cause: InstantID hints let the adapter and ControlNet picks collapse
  onto one model ("instant_id" matched both). Fixed by exploiting the real
  file naming ("control_instant_id_sdxl" vs "ip-adapter_instantid_sdxl"),
  with a code comment. Not a test-only fix: the probe would have claimed
  InstantID on servers that lack the adapter model.
- After fix + profile.json 0600 hardening: **22 passed** (2.7s).
- CLI smoke with sandboxed HOME: --save-character vj (from a real face
  photo) -> profile + 0600 face copy; --list-characters -> ["vj"].

## Coverage
- Payload builders: faceid (+LoRA on/off), instantid (2 units), reactor,
  pulid, none (v1-identical), img2img+init keeps identity unit,
  img2img-ref fallback, pose unit append.
- Mode selection: auto order, forced mode candidate lists, no-ref -> none.
- Profiles: roundtrip, missing profile error, 5 bad-name rejections.
- Fake Forge server end-to-end: probe caps, txt2img face flow, PuLID
  rejection -> logged downgrade to faceid, img2img endpoint routing,
  plain no-ref txt2img (v1 regression).

## Unverified
- Live generation on the owner's RTX 4090 Forge: no tunnel URL existed at
  build time. PuLID/ReActor arg layouts follow published API docs and are
  protected by error-driven downgrade, but only a live `--probe-server` +
  generation run settles them. Exact live commands are in the handoff.

## Live addendum (same day, owner's tunnel still up — supersedes "unverified")
Probe of the real server: checkpoints epicrealismXL; ControlNet models
include ip-adapter-faceid-plusv2_sdxl, ip-adapter_instant_id_sdxl,
control_instant_id_sdxl, openpose/depth; NO pulid or reactor script.
A/B (seed 777, cafe prompt, ref = character face):
- faceid+LoRA vs LoRA-only vs faceid-no-LoRA vs none: ControlNet-routed
  IPAdapter units register in infotext but have ZERO pixel effect
  (identical luminance signature at weight 0.85 and 2.0, two module
  spellings; byte-identical output when the ref was swapped for an
  unrelated face). The visible change in the first faceid run was the
  prompt LoRA alone.
- InstantID (both units registered): pixel-identical to none.
- img2img (--init character front-body, denoise 0.45): WORKS — locks
  pose/body/composition; prompt outfit needs higher denoise to apply.
Conclusion for this build: true txt2img identity needs a PC-side install
(ReActor extension simplest; code already supports --face-mode reactor).
Probe/auto pick it up automatically once installed.
