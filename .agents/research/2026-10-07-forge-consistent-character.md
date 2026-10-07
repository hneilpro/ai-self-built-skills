# Research: consistent characters in Forge (SDXL), 2026-10-07

Question: with no training, what keeps one face identical across txt2img /
img2img generations in lllyasviel Forge, and how is each route driven via API?

## Findings
- PuLID injects identity (InsightFace + EVA-CLIP embeddings) into attention;
  in A1111/Forge it rides the ControlNet/IPAdapter machinery and needs the
  evaclip extension + a pulid model file. Widely treated as the strongest
  training-free SDXL identity route, with less style bleed than plain
  IP-Adapter. Forge support exists but the always-on arg layout differs by
  build -> must be probed, not assumed.
- InstantID: IP-Adapter unit (face embedding) + ControlNet unit (face
  keypoints, control_instant_id_sdxl). Strong identity, heavier setup,
  two units, adapter strength ~0.8 is the documented starting point.
- IP-Adapter FaceID Plus v2 (SDXL): one ControlNet unit
  (ip-adapter-faceid-plusv2_sdxl.bin) plus its companion LoRA
  (ip-adapter-faceid-plusv2_sdxl_lora.safetensors). Forge ships built-in
  IPAdapter support; the FaceID preprocessors previously errored on some
  Forge builds (onnx DLL issue) -> another reason to probe first.
- ReActor: post-generation face swap (inswapper_128.onnx), driven via
  alwayson_scripts {"reactor": {"args": [...]}}; the extension's own API
  doc says to read /sdapi/v1/script-info for the live arg layout. Reliable
  likeness, weakest at extreme angles/lighting; zero diffusion-side setup.
- img2img with the ref as init (denoise ~0.5): locks composition, NOT
  identity. Honest label: fallback only.
- LoRA training: best long-term consistency, but it is a training project,
  not an "always attach a reference" feature. Out of scope here; noted as
  the upgrade path in the skill docs.

## API facts used (primary-ish sources)
- txt2img/img2img + alwayson_scripts ControlNet unit shape: A1111 API wiki
  and the canonical gist example (controlnet args list of unit dicts).
- ReActor arg order: the extension's published API example (runpod-worker-forge
  docs mirror it with per-index comments).
- Forge ControlNet txt2img quirk: the unit must carry its own `image`
  (it does not default to the img2img init) -> our builder always sets it.

## What remains uncertain
- Which backends the owner's Forge install actually has (models on disk,
  ReActor installed?). Resolved at runtime by --probe-server, not here.
- PuLID script name/args on his build. Mitigation: error-driven downgrade.

## Decision unlocked
Auto order pulid > instantid > faceid > reactor > img2img-ref, with
--face-mode to force one, --probe-server to see the real menu first.
