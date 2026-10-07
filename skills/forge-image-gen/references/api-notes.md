# Forge API notes (verified live 2026-10-07 on his RTX 4090)

Base: the pasted `https://....trycloudflare.com` URL (no trailing path).
Proxy: normal egress proxy env handles public URLs automatically.
Tailscale route: same proxy with port changed to 3130 (--tunnel flag).

## Endpoints used
- GET /sdapi/v1/sd-models -> [{"model_name": "epicrealismXL_vxviiCrystalclear", ...}]
- GET /sdapi/v1/options -> confirms Forge is up and which model is loaded
- GET /sdapi/v1/upscalers -> None, Lanczos, Nearest, DAT x2/x3/x4, ESRGAN_4x, R-ESRGAN 4x+, ScuNET, SwinIR 4x (no "Latent" here)
- GET /sdapi/v1/latent-upscale-modes -> Latent, Latent (antialiased), etc.
- GET /sdapi/v1/samplers -> DPM++ 2M (karras) etc. Note: sampler_name "DPM++ 2M Karras" was accepted even though list shows "DPM++ 2M" with scheduler karras.
- POST /sdapi/v1/txt2img -> {"images": [base64 png], "info": "{json string with seed/width/height/sampler_name/steps/cfg_scale}"}
- POST /sdapi/v1/extra-single-image -> body {image: base64, resize_mode: 0, upscaling_resize: 1.5, upscaling_resize_w/h, upscaling_crop: true, upscaler_1: "ESRGAN_4x", upscaler_2: "None", gfpgan_visibility: 0, codeformer_visibility: 0} -> {image: base64, html_info}

## Working high-quality recipe (2026-10-07)
- txt2img: 1024x1536, 40 steps, DPM++ 2M Karras, CFG 6.0, seed -1 -> ~12s, seed 1525680682 on the test run
- extra-single-image ESRGAN_4x 1.5x -> 1536x2304, ~22s
- Small probe: 512x768, 20 steps -> ~3.3s. 832x1216, 35 steps -> ~7.6s

## Consistent-character endpoints (v2, code-verified offline 2026-10-07; live run pending)
- GET /sdapi/v1/script-info -> [{name, ...}] — used to detect reactor/pulid scripts.
- GET /controlnet/model_list, /controlnet/module_list -> Forge's built-in
  ControlNet; absence (404) means no ControlNet identity route.
- POST /sdapi/v1/img2img -> like txt2img plus init_images [b64], denoising_strength.
- ControlNet units ride in alwayson_scripts {"controlnet": {"args": [unit...]}};
  every unit must carry its own `image` (txt2img does not inherit one).
- ReActor rides in alwayson_scripts {"reactor": {"args": [...]}}; arg layout
  follows the extension's published API example — if a build differs, the
  server 400s and forge_gen downgrades to the next backend automatically.
- PuLID arg layout varies by Forge build; same downgrade safety net applies.
  Details: references/consistent-character.md.

## Bugs / gotchas
- enable_hr: true fails every time (Latent AND ESRGAN_4x): {"error":"TypeError","message":"argument of type 'NoneType' is not iterable"} after the base pass. Do not use hires fix until he updates Forge.
- First python requests POST with override_settings + a bare sd_model_name field dropped at the proxy (RemoteDisconnected). Curl with a clean payload worked. Keep payloads minimal; use override_settings only when switching checkpoints.
- Tunnel is unauthenticated while live. URLs die when cloudflared stops; never reuse a saved one.

## v3 additions (2026-10-07, offline + local-model verified; live GPU pending)
- No new Forge endpoints. Family detection is client-side from the
  /sdapi/v1/sd-models names; Flux runs get Euler/CFG 3.5 defaults and no
  SDXL adapter payloads.
- The face identifier is local: ~/workspace/forge-face-swap/swap.py
  --verify <ref> <target> prints {"similarity", "target_faces"} (ArcFace
  cosine, buffalo_l). Swap mode now also reports similarity_before.
- Live check still owed (needs a fresh tunnel URL): --probe-server, then
  one SDXL and — if installed — one Flux generation with --character vj,
  confirming identity_pass and the reported family in FORGE_RESULT.
