#!/usr/bin/env python3
"""Forge image generation on the owner's RTX 4090 PC, with consistent characters.

One call does: capability check -> generate (txt2img or img2img) -> optional
ESRGAN upscale -> verify. With a character profile (or --ref), EVERY call
carries the reference face through the best identity backend the server
actually offers, so the same face survives pose/outfit changes:

  auto order: pulid > instantid > faceid (IP-Adapter FaceID Plus v2)
              > reactor (face swap) > img2img-ref (composition only) > none

The mode actually used is reported in FORGE_RESULT; a downgrade is never
silent. If the server rejects a backend's payload, the next backend is
tried once (error-driven downgrade, all attempts logged in the sidecar).

Usage:
  forge_gen.py <trycloudflare-url> --prompt "..." [--preset hq|probe|square|wide]
  forge_gen.py --prompt "..."                       # reuses cached URL
  forge_gen.py <url> --check                        # health check only
  forge_gen.py <url> --probe-server                 # what identity backends exist?
  forge_gen.py --save-character vj --ref face.jpg   # create/update a profile
  forge_gen.py --character vj --prompt "..."        # generate as that character
  forge_gen.py --ref face.jpg --prompt "..."        # one-off reference face
  forge_gen.py --init pose.png --denoise 0.55 --character vj --prompt "..."
  forge_gen.py --character vj --verify result.png   # ArcFace check only

Identical-face (default ON whenever --character/--ref is given): the result
is measured against the reference with ArcFace; below --verify-threshold it
is auto-swapped locally and re-measured. Both scores land in FORGE_RESULT
(face_similarity_before_swap / face_similarity_after_swap / identity_pass).
--no-identical-face opts out; --strict-identity fails instead of shipping
a face that still does not verify.
Checkpoint family (sdxl/flux/sd15) is detected from the model name and
drives sampler/CFG defaults and adapter eligibility (--model-family wins).

Cache: last URL at ~/.cache/forge-gen/url (0600, NOT in memory).
Profiles: ~/.config/forge-gen/characters/<name>/ (face copy + profile.json).
          Images are copied there, never into this repo.
Output: last line is FORGE_RESULT {json}.
"""
import argparse, base64, json, os, shutil, sys, time
import requests

NEG = ("child, teen, underage, young looking, deformed, bad anatomy, extra fingers, "
       "missing fingers, fused fingers, blurry, low quality, cartoon, anime, cgi, "
       "plastic skin, airbrushed, watermark, text")
PRESETS = {  # w, h, steps, upscale
    "hq":    (1024, 1536, 40, 1.5),
    "probe": (512, 768, 20, 0),
    "square": (1024, 1024, 40, 1.5),
    "wide":  (1536, 1024, 40, 1.5),
}
CACHE = os.path.expanduser("~/.cache/forge-gen/url")
CHAR_DIR = os.path.expanduser("~/.config/forge-gen/characters")
FACE_MODES = ("auto", "pulid", "instantid", "faceid", "reactor", "img2img-ref", "local-swap", "none")
# Local face swap (InsightFace inswapper) runs agent-side after generation;
# it is the identity route that does not depend on Forge extensions.
SWAP_HOME = os.path.expanduser("~/workspace/forge-face-swap")
SWAP_PY = os.path.join(SWAP_HOME, ".venv", "bin", "python")
SWAP_SCRIPT = os.path.join(SWAP_HOME, "swap.py")
# Heuristic model matchers (server model names vary; --face-model overrides).
FACEID_HINTS = ("faceid-plusv2", "faceid_plusv2", "faceid-plus-v2", "ip-adapter-faceid")
PULID_HINTS = ("pulid",)
# Live-verified naming on a real Forge (2026-10-07): BOTH files use
# "instant_id" — "control_instant_id_sdxl" vs "ip-adapter_instant_id_sdxl".
# Distinguish by prefix role, not by the instant substring.
INSTANTID_MODEL_HINTS = ("control_instant_id", "controlnet_instant_id")
INSTANTID_ADAPTER_HINTS = ("ip-adapter_instant_id", "ip_adapter_instant_id")
FLUX_HINTS = ("flux", "klein", "chroma")
SDXL_HINTS = ("sdxl", " xl", "_xl", "-xl", "pony", "illustrious", "noob")
DEFAULT_VERIFY_THRESHOLD = 0.65  # stricter than the ~0.5 verifier minimum:
# near-lookalikes measure ~0.58-0.60 against the wrong reference and read as
# "not her" to a human; a real swap measures 0.9+, so the bar costs nothing.
FACE_BLUR_THRESHOLD = 35.0  # face-crop Laplacian variance; swapped faces
# measure ~23 unrestored, sharp photos 80+. Below this: blur_suspect.
# Modes that only exist for SDXL checkpoints; never send them to Flux.
SDXL_ONLY_MODES = ("instantid", "faceid")
FAMILY_SAMPLER = {"flux": "Euler", "sdxl": "DPM++ 2M Karras",
                  "sd15": "DPM++ 2M Karras", "unknown": "DPM++ 2M Karras"}
FAMILY_CFG = {"flux": 3.5, "sdxl": 6.0, "sd15": 7.0, "unknown": 6.0}


def detect_family(model_name):
    """Checkpoint family from a model/checkpoint name. Heuristic by design;
    --model-family overrides it. Order matters: Flux first (a Flux fine-tune
    name may still contain 'xl'-looking substrings)."""
    n = (model_name or "").lower()
    if any(h in n for h in FLUX_HINTS):
        return "flux"
    if any(h in n for h in SDXL_HINTS) or "xl" in n:
        return "sdxl"
    if "sd15" in n or "sd1.5" in n or "v1-5" in n:
        return "sd15"
    return "unknown"


def effective_family(a, caps):
    forced = getattr(a, "model_family", "auto") or "auto"
    if forced != "auto":
        return forced
    names = (caps or {}).get("checkpoints") or []
    chosen = ""
    want = (getattr(a, "checkpoint", "") or "").lower()
    if want:
        chosen = next((n for n in names if want in n.lower()), "")
    return detect_family(chosen or (names[0] if names else ""))


def cache_url(url=None):
    if url:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w") as f:
            f.write(url)
        os.chmod(CACHE, 0o600)
        return url
    try:
        with open(CACHE) as f:
            return f.read().strip()
    except OSError:
        return ""


def b64_of(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def profile_dir(name):
    # Names become directory names; refuse anything path-like.
    if not name or name.strip() != name or any(c in name for c in "/\\.") \
            or not all(c.isalnum() or c in "-_" for c in name):
        raise SystemExit(f"Bad character name: {name!r} (use letters, digits, - or _)")
    return os.path.join(CHAR_DIR, name)


def save_character(name, face_path, body_path="", refs_dir=""):
    d = profile_dir(name)
    os.makedirs(d, exist_ok=True)
    os.chmod(CHAR_DIR, 0o700)
    prof = {"name": name}
    if refs_dir:
        if not os.path.isdir(refs_dir):
            raise SystemExit(f"Refs directory not found: {refs_dir}")
        prof["refs_dir"] = os.path.abspath(refs_dir)
    for kind, src in (("face", face_path), ("body", body_path)):
        if not src:
            continue
        if not os.path.isfile(src):
            raise SystemExit(f"Reference image not found: {src}")
        ext = os.path.splitext(src)[1].lower() or ".png"
        dst = os.path.join(d, kind + ext)
        shutil.copyfile(src, dst)
        os.chmod(dst, 0o600)
        prof[kind] = dst
    pj = os.path.join(d, "profile.json")
    with open(pj, "w") as f:
        json.dump(prof, f, indent=1)
    os.chmod(pj, 0o600)
    return prof


def load_character(name):
    p = os.path.join(profile_dir(name), "profile.json")
    if not os.path.isfile(p):
        raise SystemExit(
            f"No character profile {name!r}. Create it: --save-character {name} --ref <face.jpg>")
    with open(p) as f:
        return json.load(f)


def list_characters():
    out = []
    if os.path.isdir(CHAR_DIR):
        for n in sorted(os.listdir(CHAR_DIR)):
            if os.path.isfile(os.path.join(CHAR_DIR, n, "profile.json")):
                out.append(n)
    return out


class Forge:
    def __init__(self, base, tunnel=False):
        self.base = base
        self.s = requests.Session()
        if tunnel:
            hp = os.environ.get("HTTPS_PROXY") or ""
            if ":" in hp:
                p = hp.rsplit(":", 1)[0] + ":3130"
                self.s.proxies.update({"http": p, "https": p})

    def get(self, path, timeout=30):
        r = self.s.get(f"{self.base}{path}", timeout=timeout)
        r.raise_for_status()
        return r

    def post(self, path, payload, timeout=900):
        return self.s.post(f"{self.base}{path}", json=payload, timeout=timeout)

    def model_names(self):
        return [m.get("model_name") or "" for m in self.get("/sdapi/v1/sd-models").json()]

    def script_names(self):
        try:
            data = self.get("/sdapi/v1/script-info").json()
            return [(s.get("name") or "").lower() for s in data]
        except Exception:
            return []

    def controlnet(self):
        """Return (models, modules) lowercase lists, or ([], []) if absent."""
        try:
            models = self.get("/controlnet/model_list").json().get("model_list") or []
        except Exception:
            return [], []
        try:
            modules = self.get("/controlnet/module_list").json().get("module_list") or []
        except Exception:
            modules = []
        return [m.lower() for m in models], [m.lower() for m in modules]


def pick(models, hints):
    for h in hints:
        for m in models:
            if h in m:
                return m
    return ""


def probe_capabilities(fg):
    """What identity backends does THIS server offer? Pure reporting."""
    scripts = fg.script_names()
    cn_models, cn_modules = fg.controlnet()
    caps = {
        "checkpoints": fg.model_names(),
        "scripts": scripts,
        "controlnet_models": cn_models,
        "controlnet_modules": cn_modules,
        "pulid": any("pulid" in s for s in scripts) or bool(pick(cn_models, PULID_HINTS)),
        "instantid": bool(pick(cn_models, INSTANTID_MODEL_HINTS))
                     and bool(pick(cn_models, INSTANTID_ADAPTER_HINTS)),
        "instantid_control_model": pick(cn_models, INSTANTID_MODEL_HINTS),
        "instantid_adapter_model": pick(cn_models, INSTANTID_ADAPTER_HINTS),
        "faceid": bool(pick(cn_models, FACEID_HINTS)),
        "faceid_model": pick(cn_models, FACEID_HINTS),
        "reactor": any(s == "reactor" for s in scripts),
    }
    caps["auto_order_available"] = [m for m in ("pulid", "instantid", "faceid", "reactor") if caps[m]]
    return caps


def local_swap_available():
    return os.path.isfile(SWAP_PY) and os.path.isfile(SWAP_SCRIPT)


def available_modes(caps, has_ref, family="sdxl"):
    """Ordered candidate identity modes for auto, given server caps + a ref.
    A proper face swap outranks the composition-only img2img-ref route, and
    SDXL-only adapters are never offered to a Flux checkpoint."""
    if not has_ref:
        return ["none"]
    order = [m for m in ("pulid", "instantid", "faceid", "reactor") if caps.get(m)]
    if family == "flux":
        order = [m for m in order if m not in SDXL_ONLY_MODES]
    if local_swap_available():
        order.append("local-swap")
    order.append("img2img-ref")
    order.append("none")
    return order


def controlnet_unit(image_b64, module, model, weight, control_mode="Balanced",
                    guidance_start=0.0, guidance_end=1.0, processor_res=512):
    return {
        # Both spellings: A1111-family parsers read one or the other across
        # versions; unknown keys are ignored, a missing one is a silent no-op.
        "enabled": True, "image": image_b64, "input_image": image_b64, "mask": None,
        "module": module, "model": model, "weight": weight,
        "control_mode": control_mode, "guidance_start": guidance_start,
        "guidance_end": guidance_end, "processor_res": processor_res,
        "resize_mode": "Crop and Resize", "low_vram": False,
        "pixel_perfect": False, "threshold_a": 64, "threshold_b": 64,
    }


def build_payload(a, w, h, steps, face_b64, mode_used, caps):
    """Pure payload builder (unit-tested). mode_used in FACE_MODES (not auto)."""
    family = effective_family(a, caps)
    sampler = getattr(a, "sampler", "") or FAMILY_SAMPLER[family]
    cfg = getattr(a, "cfg", 0) or FAMILY_CFG[family]
    if family == "flux" and mode_used in SDXL_ONLY_MODES:
        # SDXL adapter payloads are inert-to-harmful on Flux; the identity
        # guarantee for Flux is verify + local swap after generation.
        mode_used = "local-swap" if local_swap_available() else "none"
    payload = {"prompt": a.prompt, "negative_prompt": a.negative, "steps": steps,
               "width": w, "height": h, "cfg_scale": cfg, "sampler_name": sampler,
               "seed": a.seed, "batch_size": 1, "n_iter": 1}
    scripts = {}
    endpoint = "/sdapi/v1/txt2img"

    if a.init:  # img2img: init image is the canvas; ref still drives identity
        endpoint = "/sdapi/v1/img2img"
        payload["init_images"] = [b64_of(a.init)]
        payload["denoising_strength"] = a.denoise
        payload["resize_mode"] = 1

    if mode_used == "pulid" and face_b64:
        # Forge exposes PuLID as an always-on script; weight rides in args.
        # Exact arg layout varies by Forge build -> error-driven downgrade
        # in run_generation() covers a mismatch honestly.
        scripts["pulid"] = {"args": [True, face_b64, a.face_weight]}
    elif mode_used == "instantid" and face_b64:
        units = [
            controlnet_unit(face_b64, "InsightFace (InstantID)",
                            caps.get("instantid_adapter_model") or "ip-adapter_instantid_sdxl",
                            a.face_weight),
            controlnet_unit(face_b64, "instant_id_face_keypoints",
                            caps.get("instantid_control_model") or "control_instant_id_sdxl",
                            a.face_weight),
        ]
        scripts["controlnet"] = {"args": units}
    elif mode_used == "faceid" and face_b64:
        model = a.face_model or caps.get("faceid_model") or "ip-adapter-faceid-plusv2_sdxl"
        unit = controlnet_unit(face_b64, "ip-adapter-auto", model, a.face_weight)
        scripts["controlnet"] = {"args": [unit]}
        if a.faceid_lora and family != "flux" and "plusv2" in model and "<lora:" not in a.prompt:
            payload["prompt"] = a.prompt + " <lora:ip-adapter-faceid-plusv2_sdxl_lora:0.8>"
    elif mode_used == "reactor" and face_b64:
        # Gourieff ReActor API layout (see skill references/api-notes.md).
        scripts["reactor"] = {"args": [
            face_b64, True, "0", "0", "inswapper_128.onnx", "CodeFormer", 1.0,
            True, "None", 1.0, 1.0, False, False, "0", "0", False, "Cuda",
            True, 0.5, 0.99,
        ]}

    if getattr(a, "pose", ""):
        unit = controlnet_unit(b64_of(a.pose), "openpose_full",
                               getattr(a, "pose_model", "") or "None",
                               getattr(a, "pose_weight", 0.7))
        if "controlnet" in scripts:
            scripts["controlnet"]["args"].append(unit)
        else:
            scripts["controlnet"] = {"args": [unit]}

    if mode_used == "img2img-ref" and face_b64 and not a.init:
        # Weakest identity route: the ref becomes the img2img canvas.
        endpoint = "/sdapi/v1/img2img"
        payload["init_images"] = [face_b64]
        payload["denoising_strength"] = a.denoise

    if scripts:
        payload["alwayson_scripts"] = scripts
    return endpoint, payload


def candidate_modes(a, caps, face_b64):
    family = effective_family(a, caps)
    if a.face_mode == "auto":
        return available_modes(caps, bool(face_b64), family)
    if a.face_mode == "none" or not face_b64:
        return ["none"]
    if family == "flux" and a.face_mode in SDXL_ONLY_MODES:
        a.face_mode = "local-swap" if local_swap_available() else "none"
        if a.face_mode == "none":
            return ["none"]
    tail = []
    if local_swap_available():
        tail.append("local-swap")
    tail += ["img2img-ref", "none"]
    if a.face_mode in ("img2img-ref", "local-swap"):
        return [a.face_mode] + [t for t in tail if t != a.face_mode]
    return [a.face_mode] + tail


def identity_decision(similarity, threshold, identical=True):
    """Pure gate (unit-tested): what to do with a measured similarity.
    None means no face could be measured -> unverified, never a silent pass."""
    if not identical:
        return "skipped"
    if similarity is None:
        return "unverified"
    return "pass" if similarity >= threshold else "swap"


def _swap_cli(args, what):
    import subprocess
    r = subprocess.run([SWAP_PY, SWAP_SCRIPT, *args],
                       capture_output=True, text=True, timeout=1200)
    if r.returncode != 0:
        raise SystemExit(f"{what} failed: {(r.stderr or r.stdout)[-400:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def verify_face(face_path, png_bytes):
    """ArcFace check between the reference face and an image, no edit.
    Returns (similarity|None, target_face_count, face_sharpness|None).
    Similarity says "same person?"; sharpness catches the blur identity
    embeddings ignore."""
    import tempfile
    if not local_swap_available():
        return None, 0, None
    try:
        with tempfile.TemporaryDirectory() as d:
            tgt = os.path.join(d, "t.png")
            with open(tgt, "wb") as f:
                f.write(png_bytes)
            info = _swap_cli(["--verify", face_path, tgt], "face verification")
            return (info.get("similarity"), int(info.get("target_faces") or 0),
                    info.get("face_sharpness"))
    except SystemExit:
        # No measurable face (or the local stack is broken) means
        # "unverified" — it must never kill an otherwise good generation.
        return None, 0, None


def local_swap(face_path, png_bytes):
    """Agent-side InsightFace swap (the proper face swap, with detail
    restoration — the 128px swapper alone returns a soft face). Returns
    (png_bytes, similarity_before, similarity_after, face_sharpness)."""
    import tempfile
    if not local_swap_available():
        raise SystemExit("local-swap requested but ~/workspace/forge-face-swap is not set up")
    with tempfile.TemporaryDirectory() as d:
        tgt = os.path.join(d, "t.png")
        out = os.path.join(d, "o.png")
        with open(tgt, "wb") as f:
            f.write(png_bytes)
        info = _swap_cli([face_path, tgt, out], "local face swap")
        with open(out, "rb") as f:
            return (f.read(), info.get("similarity_before"),
                    info.get("similarity"), info.get("face_sharpness"))


def run_generation(fg, a, w, h, steps, face_b64, caps):
    """Try candidate modes in order; a server rejection downgrades once each.
    Returns (raw_png_bytes, info_dict, mode_used, attempts_log)."""
    attempts = []
    last_err = ""
    for mode in candidate_modes(a, caps, face_b64):
        endpoint, payload = build_payload(a, w, h, steps, face_b64, mode, caps)
        if a.checkpoint:
            names = caps.get("checkpoints") or []
            t = next((n for n in names if a.checkpoint.lower() in n.lower()), "")
            if t:
                payload["override_settings"] = {"sd_model_checkpoint": t}
        try:
            r = fg.post(endpoint, payload)
        except Exception as e:  # connection-level: tunnel died, do not downgrade blindly
            raise SystemExit(f"Generation request failed ({mode}): {e}") from e
        if r.status_code >= 400:
            attempts.append({"mode": mode, "status": r.status_code, "error": r.text[:200]})
            last_err = f"{mode}: HTTP {r.status_code}"
            continue
        data = r.json()
        imgs = data.get("images") or []
        if not imgs:
            attempts.append({"mode": mode, "status": "no-images"})
            last_err = f"{mode}: no images returned"
            continue
        info = {}
        try:
            info = json.loads(data.get("info") or "{}")
        except Exception:
            pass
        return base64.b64decode(imgs[0]), info, mode, attempts
    raise SystemExit(
        f"All identity modes failed. Attempts: {json.dumps(attempts)} Last: {last_err}")


def add_args(ap):
    ap.add_argument("base", nargs="?", default="")
    ap.add_argument("--prompt", default="")
    ap.add_argument("--negative", default=NEG)
    ap.add_argument("--preset", choices=PRESETS, default="hq")
    ap.add_argument("--width", type=int, default=0)
    ap.add_argument("--height", type=int, default=0)
    ap.add_argument("--steps", type=int, default=0)
    ap.add_argument("--cfg", type=float, default=0, help="0 = family default (flux 3.5, sdxl 6)")
    ap.add_argument("--sampler", default="", help="empty = family default")
    ap.add_argument("--seed", type=int, default=-1)
    ap.add_argument("--checkpoint", default="")
    ap.add_argument("--upscale", type=float, default=-1, help="-1 = preset default")
    ap.add_argument("--upscaler", default="ESRGAN_4x")
    ap.add_argument("--tunnel", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--probe-server", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--clear-cache", action="store_true")
    ap.add_argument("--out", default="")
    # Consistent character
    ap.add_argument("--character", default="", help="profile name (see --save-character)")
    ap.add_argument("--save-character", default="", help="create/update profile NAME from --ref")
    ap.add_argument("--list-characters", action="store_true")
    ap.add_argument("--ref", default="", help="one-off face reference image path")
    ap.add_argument("--body-ref", default="", help="body reference, stored with --save-character")
    ap.add_argument("--refs-dir", default="", help="multi-reference identity set (dir of face images); the swap/verify identity is the averaged template of all of them — steadier than one photo")
    ap.add_argument("--face-mode", choices=FACE_MODES, default="auto")
    ap.add_argument("--identical-face", action=argparse.BooleanOptionalAction, default=True,
                    help="verify every character result with ArcFace and auto-swap below threshold")
    ap.add_argument("--verify-threshold", type=float, default=DEFAULT_VERIFY_THRESHOLD)
    ap.add_argument("--strict-identity", action="store_true",
                    help="fail the run if the final face still does not verify")
    ap.add_argument("--model-family", choices=("auto", "sdxl", "flux", "sd15"), default="auto")
    ap.add_argument("--verify", default="", help="verify-only: ArcFace-check this image against --ref/--character and exit")
    ap.add_argument("--face-weight", type=float, default=0.85)
    ap.add_argument("--face-model", default="", help="override ControlNet/IPAdapter model name")
    ap.add_argument("--faceid-lora", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--init", default="", help="img2img init image (pose/composition canvas)")
    ap.add_argument("--denoise", type=float, default=0.55)
    ap.add_argument("--pose", default="", help="optional OpenPose control image")
    ap.add_argument("--pose-model", default="")
    ap.add_argument("--pose-weight", type=float, default=0.7)
    return ap


def main(argv=None):
    a = add_args(argparse.ArgumentParser()).parse_args(argv)

    if a.clear_cache:
        try:
            os.remove(CACHE)
        except OSError:
            pass
        print('FORGE_RESULT {"cleared": true}')
        return
    if a.list_characters:
        print(json.dumps({"characters": list_characters()}))
        if not (a.prompt or a.save_character):
            return
    if a.save_character:
        if not a.ref:
            raise SystemExit("--save-character needs --ref <face image>")
        prof = save_character(a.save_character, a.ref, a.body_ref, a.refs_dir)
        print(json.dumps({"saved_character": prof["name"], "face": prof.get("face", "")}))
        if not a.prompt:
            return
        a.character = a.save_character

    if a.verify:
        _prof = load_character(a.character) if a.character else {}
        face_path = a.refs_dir or _prof.get("refs_dir", "") or a.ref or _prof.get("face", "")
        if not face_path:
            raise SystemExit("--verify needs --ref <face>, --refs-dir <dir> or --character <name>")
        if not os.path.isfile(a.verify):
            raise SystemExit(f"Image to verify not found: {a.verify}")
        with open(a.verify, "rb") as f:
            sim, nfaces, sharp = verify_face(face_path, f.read())
        passed = None if sim is None else sim >= a.verify_threshold
        print(f"FORGE_RESULT {json.dumps({'verify': a.verify, 'face_similarity': sim, 'target_faces': nfaces, 'face_sharpness': sharp, 'blur_suspect': (sharp is not None and sharp < FACE_BLUR_THRESHOLD), 'threshold': a.verify_threshold, 'identity_pass': passed})}")
        return

    base = (a.base or os.environ.get("FORGE_URL")
            or ("" if a.no_cache else cache_url())).rstrip("/")
    if not base:
        raise SystemExit(
            "No Forge URL: paste a trycloudflare URL, set FORGE_URL, "
            "or run once with a URL to cache it.")
    if a.base and not a.no_cache:
        cache_url(base)

    fg = Forge(base, tunnel=a.tunnel)
    try:
        names = fg.model_names()
    except Exception as e:
        raise SystemExit(
            f"Forge unreachable at {base}: {type(e).__name__} — tunnel down or Forge off.") from e
    if a.check:
        print(json.dumps({"FORGE_RESULT": {"ok": True, "checkpoints": names}}))
        return

    caps = probe_capabilities(fg)
    caps["checkpoints"] = names
    if a.probe_server:
        print(json.dumps({"FORGE_RESULT": {"probe": caps}}, indent=1))
        return
    if not a.prompt:
        raise SystemExit("--prompt is required (or use --check / --probe-server)")

    # Resolve the reference face: explicit --ref wins, else the profile.
    face_path = a.ref
    character = a.character or ""
    swap_source = a.refs_dir
    if character:
        prof = load_character(character)
        if not face_path:
            face_path = prof.get("face", "")
        if not swap_source:
            swap_source = prof.get("refs_dir", "")
    swap_source = swap_source or face_path
    face_b64 = ""
    if face_path:
        if not os.path.isfile(face_path):
            raise SystemExit(f"Reference image not found: {face_path}")
        face_b64 = b64_of(face_path)

    w, h, steps, up = PRESETS[a.preset]
    w, h, steps = a.width or w, a.height or h, a.steps or steps
    up = up if a.upscale < 0 else a.upscale

    t0 = time.time()
    family = effective_family(a, caps)
    raw, info, mode_used, attempts = run_generation(fg, a, w, h, steps, face_b64, caps)

    # Identical-face gate: measure, auto-swap below threshold, re-measure.
    # Runs for EVERY mode (v2 only measured its own swap, so inert server
    # backends shipped unverified drift).
    sim_before = sim_after = None
    face_sharpness = None
    identity_pass = None
    swapped = False
    if face_path and mode_used == "local-swap":
        raw, sim_before, sim_after, face_sharpness = local_swap(swap_source, raw)
        swapped = True
    elif face_path and a.identical_face:
        sim_before, _, face_sharpness = verify_face(swap_source, raw)
        if identity_decision(sim_before, a.verify_threshold) == "swap":
            if local_swap_available():
                try:
                    raw, sb, sim_after, face_sharpness = local_swap(swap_source, raw)
                    sim_before = sb if sb is not None else sim_before
                    swapped = True
                except SystemExit:
                    pass  # keep the unswapped image; identity_pass says why
    similarity = sim_after if sim_after is not None else sim_before
    if face_path and a.identical_face:
        identity_pass = None if similarity is None else similarity >= a.verify_threshold

    if up and up != 1:
        u = {"image": base64.b64encode(raw).decode(), "resize_mode": 0,
             "show_extras_results": True, "gfpgan_visibility": 0,
             "codeformer_visibility": 0, "codeformer_weight": 0,
             "upscaling_resize": up, "upscaling_resize_w": int(w * up),
             "upscaling_resize_h": int(h * up), "upscaling_crop": True,
             "upscaler_1": a.upscaler, "upscaler_2": "None",
             "extras_upscaler_2_visibility": 0, "upscale_first": False}
        r = fg.post("/sdapi/v1/extra-single-image", u)
        r.raise_for_status()
        raw = base64.b64decode(r.json()["image"])

    out = a.out or os.path.expanduser(
        f"~/workspace/forge-test/forge_{time.strftime('%Y%m%d_%H%M%S')}_{info.get('seed', 'x')}.png")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as f:
        f.write(raw)

    verify = {}
    try:
        from PIL import Image
        import io, statistics
        im = Image.open(io.BytesIO(raw))
        im.load()
        px = im.convert("L").resize((32, 32))
        vals = list(px.getdata())
        verify = {"size": list(im.size), "blank_suspect": statistics.pstdev(vals) < 2}
    except Exception as e:
        verify = {"error": str(e)}
    result = {"file": out, "seed": info.get("seed"), "checkpoint": names[0] if names else "",
              "model_family": family, "preset": a.preset, "steps": steps,
              "sampler": a.sampler or FAMILY_SAMPLER[family],
              "cfg": a.cfg or FAMILY_CFG[family],
              "character": character or None, "face_mode_requested": a.face_mode,
              "face_mode_used": mode_used, "downgrades": attempts,
              "identical_face": bool(face_path and a.identical_face),
              "verify_threshold": a.verify_threshold,
              "face_similarity": similarity,
              "face_similarity_before_swap": sim_before,
              "face_similarity_after_swap": sim_after,
              "auto_swapped": swapped, "identity_pass": identity_pass,
              "face_sharpness": face_sharpness,
              "blur_suspect_face": (face_sharpness is not None
                                    and face_sharpness < FACE_BLUR_THRESHOLD),
              "final_size": verify.get("size"), "bytes": len(raw),
              "blank_suspect": verify.get("blank_suspect"),
              "seconds": round(time.time() - t0, 1)}
    with open(out.rsplit(".", 1)[0] + ".json", "w") as f:
        json.dump({**result, "prompt": a.prompt, "negative_prompt": a.negative,
                   "face_weight": a.face_weight,
                   "denoise": a.denoise if (a.init or mode_used == "img2img-ref") else None},
                  f, indent=1)
    print(f"FORGE_RESULT {json.dumps(result)}")
    if a.strict_identity and identity_pass is False:
        raise SystemExit(
            f"strict-identity: final similarity {similarity} < threshold "
            f"{a.verify_threshold} (file kept: {out})")


if __name__ == "__main__":
    main()
