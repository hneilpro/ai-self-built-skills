"""Offline tests for forge_gen v2. Run: python3 -m pytest tests/ -q
No GPU, no real Forge: a stdlib fake server stands in for the API."""
import argparse, base64, io, json, os, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bin"))
import forge_gen as fg  # noqa: E402


def args(*argv):
    return fg.add_args(argparse.ArgumentParser()).parse_args(list(argv))


def tiny_png():
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (16, 16), (120, 60, 200)).save(buf, format="PNG")
    return buf.getvalue()


PNG_B64 = base64.b64encode(tiny_png()).decode()
CAPS = {"faceid_model": "ip-adapter-faceid-plusv2_sdxl [abc]",
        "instantid_control_model": "control_instant_id_sdxl [def]",
        "instantid_adapter_model": "ip-adapter_instantid_sdxl [ghi]",
        "checkpoints": ["epicrealismXL_vxviiCrystalclear"]}


# ---------- pure payload builders ----------

def test_faceid_txt2img_payload():
    a = args("--prompt", "portrait of a woman")
    ep, p = fg.build_payload(a, 512, 768, 20, "FACEB64", "faceid", CAPS)
    assert ep == "/sdapi/v1/txt2img"
    unit = p["alwayson_scripts"]["controlnet"]["args"][0]
    assert unit["module"] == "ip-adapter-auto" and unit["image"] == "FACEB64"
    assert unit["model"].startswith("ip-adapter-faceid-plusv2")
    assert unit["weight"] == pytest.approx(0.85)
    assert "<lora:ip-adapter-faceid-plusv2_sdxl_lora:0.8>" in p["prompt"]


def test_faceid_lora_can_be_disabled():
    a = args("--prompt", "x", "--no-faceid-lora")
    _, p = fg.build_payload(a, 512, 768, 20, "F", "faceid", CAPS)
    assert "<lora:" not in p["prompt"]


def test_instantid_two_units():
    a = args("--prompt", "x")
    _, p = fg.build_payload(a, 512, 768, 20, "F", "instantid", CAPS)
    units = p["alwayson_scripts"]["controlnet"]["args"]
    # Names verified live against a real Forge module_list (2026-10-07).
    assert [u["module"] for u in units] == [
        "InsightFace (InstantID)", "instant_id_face_keypoints"]


def test_reactor_payload():
    a = args("--prompt", "x")
    _, p = fg.build_payload(a, 512, 768, 20, "FACEB64", "reactor", CAPS)
    r = p["alwayson_scripts"]["reactor"]["args"]
    assert r[0] == "FACEB64" and r[1] is True and r[4] == "inswapper_128.onnx"


def test_pulid_payload():
    a = args("--prompt", "x")
    _, p = fg.build_payload(a, 512, 768, 20, "F", "pulid", CAPS)
    assert p["alwayson_scripts"]["pulid"]["args"] == [True, "F", pytest.approx(0.85)]


def test_none_is_v1_plain_txt2img():
    a = args("--prompt", "a cat")
    ep, p = fg.build_payload(a, 1024, 1536, 40, "", "none", CAPS)
    assert ep == "/sdapi/v1/txt2img" and "alwayson_scripts" not in p
    assert "init_images" not in p and p["sampler_name"] == "DPM++ 2M Karras"


def test_img2img_init_keeps_identity(tmp_path):
    init = tmp_path / "pose.png"
    init.write_bytes(tiny_png())
    a = args("--prompt", "x", "--init", str(init), "--denoise", "0.4")
    ep, p = fg.build_payload(a, 512, 768, 20, "FACEB64", "faceid", CAPS)
    assert ep == "/sdapi/v1/img2img"
    assert p["denoising_strength"] == pytest.approx(0.4)
    assert p["init_images"] == [base64.b64encode(tiny_png()).decode()]
    assert p["alwayson_scripts"]["controlnet"]["args"][0]["image"] == "FACEB64"


def test_img2img_ref_fallback_uses_ref_as_canvas():
    a = args("--prompt", "x")
    ep, p = fg.build_payload(a, 512, 768, 20, "FACEB64", "img2img-ref", CAPS)
    assert ep == "/sdapi/v1/img2img" and p["init_images"] == ["FACEB64"]


def test_pose_appends_controlnet_unit(tmp_path):
    pose = tmp_path / "pose.png"
    pose.write_bytes(tiny_png())
    a = args("--prompt", "x", "--pose", str(pose))
    _, p = fg.build_payload(a, 512, 768, 20, "F", "faceid", CAPS)
    units = p["alwayson_scripts"]["controlnet"]["args"]
    assert len(units) == 2 and units[1]["module"] == "openpose_full"


# ---------- mode selection ----------

def test_available_modes_order_and_no_ref(monkeypatch):
    monkeypatch.setattr(fg, "local_swap_available", lambda: False)
    caps = {"pulid": False, "instantid": True, "faceid": True, "reactor": False}
    assert fg.available_modes(caps, True) == ["instantid", "faceid", "img2img-ref", "none"]
    assert fg.available_modes(caps, False) == ["none"]


def test_available_modes_adds_local_swap(monkeypatch):
    monkeypatch.setattr(fg, "local_swap_available", lambda: True)
    caps = {"pulid": False, "instantid": False, "faceid": False, "reactor": False}
    assert fg.available_modes(caps, True) == ["local-swap", "img2img-ref", "none"]  # v3: swap outranks composition-only ref


def test_candidate_modes_forced_and_auto(monkeypatch):
    monkeypatch.setattr(fg, "local_swap_available", lambda: False)
    a = args("--prompt", "x", "--face-mode", "reactor")
    assert fg.candidate_modes(a, {}, "F") == ["reactor", "img2img-ref", "none"]
    a2 = args("--prompt", "x")
    assert fg.candidate_modes(a2, {"reactor": True}, "F") == ["reactor", "img2img-ref", "none"]


# ---------- profiles ----------

def test_profile_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(fg, "CHAR_DIR", str(tmp_path / "chars"))
    face = tmp_path / "face.jpg"
    face.write_bytes(tiny_png())
    prof = fg.save_character("vj", str(face))
    assert os.path.isfile(prof["face"])
    assert fg.load_character("vj")["name"] == "vj"
    assert fg.list_characters() == ["vj"]
    with pytest.raises(SystemExit):
        fg.load_character("ghost")


@pytest.mark.parametrize("bad", ["../evil", "a/b", "", " white ", "dot.name"])
def test_profile_bad_names_rejected(bad, tmp_path, monkeypatch):
    monkeypatch.setattr(fg, "CHAR_DIR", str(tmp_path / "chars"))
    face = tmp_path / "f.png"
    face.write_bytes(tiny_png())
    with pytest.raises(SystemExit):
        fg.save_character(bad, str(face))


# ---------- fake Forge server ----------

class FakeForge(BaseHTTPRequestHandler):
    reject_scripts = set()   # script names whose POST returns 400
    seen = []                # (path, payload) log
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # keep tests quiet
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/sdapi/v1/sd-models":
            self._json([{"model_name": "epicrealismXL_vxviiCrystalclear"}])
        elif self.path == "/sdapi/v1/script-info":
            self._json([{"name": "reactor"}, {"name": "pulid"}])
        elif self.path == "/controlnet/model_list":
            self._json({"model_list": ["ip-adapter-faceid-plusv2_sdxl [abc]",
                                         "control_instant_id_sdxl [def]"]})
        elif self.path == "/controlnet/module_list":
            self._json({"module_list": ["ip-adapter-auto", "instant_id_face_embedding"]})
        else:
            self._json({}, 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(n) or b"{}")
        type(self).seen.append((self.path, payload))
        scripts = payload.get("alwayson_scripts") or {}
        if set(scripts) & type(self).reject_scripts:
            self._json({"error": "script rejected"}, 400)
            return
        if self.path in ("/sdapi/v1/txt2img", "/sdapi/v1/img2img"):
            self._json({"images": [PNG_B64], "parameters": {},
                        "info": json.dumps({"seed": 424242})})
        elif self.path == "/sdapi/v1/extra-single-image":
            self._json({"image": PNG_B64, "html_info": ""})
        else:
            self._json({}, 404)


@pytest.fixture()
def server():
    FakeForge.seen = []
    FakeForge.reject_scripts = set()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), FakeForge)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def run_cli(server, *argv):
    fg.main([server, "--no-cache", *argv])


def test_probe_against_fake_server(server):
    f = fg.Forge(server)
    caps = fg.probe_capabilities(f)
    assert caps["faceid"] and caps["reactor"] and caps["pulid"]
    assert caps["faceid_model"].startswith("ip-adapter-faceid")
    # instantid needs adapter+control models; only control model is listed
    assert caps["instantid"] is False


def test_e2e_faceid_txt2img(server, tmp_path, capsys):
    out = str(tmp_path / "o.png")
    run_cli(server, "--prompt", "portrait", "--ref", _ref(tmp_path),
            "--preset", "probe", "--upscale", "0", "--out", out)
    result = json.loads(capsys.readouterr().out.strip().splitlines()[-1].removeprefix("FORGE_RESULT "))
    assert result["face_mode_used"] == "pulid"  # fake server advertises pulid script
    assert result["seed"] == 424242 and os.path.getsize(out) > 0
    path, payload = FakeForge.seen[-1]
    assert path == "/sdapi/v1/txt2img" and "pulid" in payload["alwayson_scripts"]


def test_e2e_downgrade_when_pulid_rejected(server, tmp_path, capsys):
    FakeForge.reject_scripts = {"pulid"}
    out = str(tmp_path / "o.png")
    run_cli(server, "--prompt", "portrait", "--ref", _ref(tmp_path),
            "--preset", "probe", "--upscale", "0", "--out", out)
    result = json.loads(capsys.readouterr().out.strip().splitlines()[-1].removeprefix("FORGE_RESULT "))
    # pulid rejected -> next available backend is faceid; downgrade is logged
    assert result["face_mode_used"] == "faceid"
    assert result["downgrades"] and result["downgrades"][0]["mode"] == "pulid"


def test_e2e_img2img(server, tmp_path, capsys):
    init = tmp_path / "init.png"
    init.write_bytes(tiny_png())
    out = str(tmp_path / "o.png")
    run_cli(server, "--prompt", "x", "--ref", _ref(tmp_path), "--init", str(init),
            "--preset", "probe", "--upscale", "0", "--out", out)
    result = json.loads(capsys.readouterr().out.strip().splitlines()[-1].removeprefix("FORGE_RESULT "))
    assert result["face_mode_used"] == "pulid"
    assert FakeForge.seen[-1][0] == "/sdapi/v1/img2img"


def test_e2e_plain_txt2img_no_ref(server, tmp_path, capsys):
    out = str(tmp_path / "o.png")
    run_cli(server, "--prompt", "a cat", "--preset", "probe", "--upscale", "0", "--out", out)
    result = json.loads(capsys.readouterr().out.strip().splitlines()[-1].removeprefix("FORGE_RESULT "))
    assert result["face_mode_used"] == "none" and result["character"] is None
    assert "alwayson_scripts" not in FakeForge.seen[-1][1]


def _ref(tmp_path):
    p = tmp_path / "face.png"
    p.write_bytes(tiny_png())
    return str(p)


# ---------- v3: family detection + Flux hygiene ----------

def test_detect_family():
    assert fg.detect_family("epicrealismXL_vxviiCrystalclear") == "sdxl"
    assert fg.detect_family("flux1-dev.safetensors") == "flux"
    assert fg.detect_family("FLUX.2-klein-9b") == "flux"
    assert fg.detect_family("realisticVisionV60_v1-5") == "sd15"
    assert fg.detect_family("some-unknown-model") == "unknown"


def test_flux_never_gets_sdxl_payloads():
    caps = dict(CAPS, checkpoints=["flux1-dev"])
    a = args("--prompt", "portrait", "--face-mode", "faceid")
    _, p = fg.build_payload(a, 512, 768, 20, "FACEB64", "faceid", caps)
    # SDXL ControlNet unit + LoRA must not be injected into a Flux run.
    assert "<lora:" not in p["prompt"]
    scripts = p.get("alwayson_scripts") or {}
    assert "controlnet" not in scripts
    assert p["sampler_name"] == "Euler" and p["cfg_scale"] == pytest.approx(3.5)


def test_sdxl_defaults_unchanged():
    a = args("--prompt", "x")
    _, p = fg.build_payload(a, 512, 768, 20, "", "none", CAPS)
    assert p["sampler_name"] == "DPM++ 2M Karras" and p["cfg_scale"] == pytest.approx(6.0)


def test_explicit_sampler_cfg_win_over_family():
    caps = dict(CAPS, checkpoints=["flux1-dev"])
    a = args("--prompt", "x", "--sampler", "DPM++ 2M", "--cfg", "5")
    _, p = fg.build_payload(a, 512, 768, 20, "", "none", caps)
    assert p["sampler_name"] == "DPM++ 2M" and p["cfg_scale"] == pytest.approx(5.0)


def test_model_family_override():
    a = args("--prompt", "x", "--model-family", "flux")
    _, p = fg.build_payload(a, 512, 768, 20, "", "none", CAPS)
    assert p["sampler_name"] == "Euler"


# ---------- v3: identical-face gate ----------

def test_identity_decision():
    assert fg.identity_decision(0.9, 0.55) == "pass"
    assert fg.identity_decision(0.55, 0.55) == "pass"
    assert fg.identity_decision(0.10, 0.55) == "swap"
    assert fg.identity_decision(None, 0.55) == "unverified"
    assert fg.identity_decision(0.10, 0.55, identical=False) == "skipped"


def test_auto_order_swap_outranks_img2img_ref(monkeypatch):
    monkeypatch.setattr(fg, "local_swap_available", lambda: True)
    caps = {"pulid": False, "instantid": False, "faceid": False, "reactor": False}
    assert fg.available_modes(caps, True) == ["local-swap", "img2img-ref", "none"]


def test_flux_auto_excludes_sdxl_modes(monkeypatch):
    monkeypatch.setattr(fg, "local_swap_available", lambda: True)
    caps = {"pulid": True, "instantid": True, "faceid": True, "reactor": True}
    got = fg.available_modes(caps, True, family="flux")
    assert "instantid" not in got and "faceid" not in got
    assert got[0] == "pulid" and "local-swap" in got


def test_e2e_identical_face_auto_swap(server, tmp_path, capsys, monkeypatch):
    # Generated face drifts (0.10) -> gate must swap -> 0.93 -> pass.
    calls = {}

    def fake_verify(face_path, png):
        calls["verify"] = calls.get("verify", 0) + 1
        return 0.10, 1, 100.0

    def fake_swap(face_path, png):
        calls["swap"] = calls.get("swap", 0) + 1
        return png, 0.10, 0.93, 120.0

    monkeypatch.setattr(fg, "verify_face", fake_verify)
    monkeypatch.setattr(fg, "local_swap", fake_swap)
    monkeypatch.setattr(fg, "local_swap_available", lambda: True)
    out = str(tmp_path / "o.png")
    run_cli(server, "--prompt", "portrait", "--ref", _ref(tmp_path),
            "--preset", "probe", "--upscale", "0", "--out", out,
            "--face-mode", "none")
    result = json.loads(capsys.readouterr().out.strip().splitlines()[-1].removeprefix("FORGE_RESULT "))
    assert calls.get("swap") == 1 and result["auto_swapped"] is True
    assert result["face_similarity_before_swap"] == pytest.approx(0.10)
    assert result["face_similarity_after_swap"] == pytest.approx(0.93)
    assert result["identity_pass"] is True and result["identical_face"] is True


def test_e2e_no_identical_face_skips_gate(server, tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(fg, "verify_face",
                        lambda *a: (_ for _ in ()).throw(AssertionError("gate ran")))
    out = str(tmp_path / "o.png")
    run_cli(server, "--prompt", "portrait", "--ref", _ref(tmp_path),
            "--preset", "probe", "--upscale", "0", "--out", out,
            "--face-mode", "none", "--no-identical-face")
    result = json.loads(capsys.readouterr().out.strip().splitlines()[-1].removeprefix("FORGE_RESULT "))
    assert result["identical_face"] is False and result["identity_pass"] is None


def test_e2e_strict_identity_fails(server, tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(fg, "verify_face", lambda *a: (0.10, 1, 100.0))
    monkeypatch.setattr(fg, "local_swap", lambda *a: (tiny_png(), 0.10, 0.20, 90.0))
    monkeypatch.setattr(fg, "local_swap_available", lambda: True)
    out = str(tmp_path / "o.png")
    with pytest.raises(SystemExit, match="strict-identity"):
        run_cli(server, "--prompt", "portrait", "--ref", _ref(tmp_path),
                "--preset", "probe", "--upscale", "0", "--out", out,
                "--face-mode", "none", "--strict-identity")
    result = json.loads(capsys.readouterr().out.strip().splitlines()[-1].removeprefix("FORGE_RESULT "))
    assert result["identity_pass"] is False  # reported honestly before failing


def test_default_threshold_rejects_near_lookalike():
    # Measured live: the wrong-but-similar reference scores ~0.58; at the old
    # 0.55 bar that shipped as a pass while reading as "not her" to a human.
    assert fg.DEFAULT_VERIFY_THRESHOLD >= 0.65
    assert fg.identity_decision(0.58, fg.DEFAULT_VERIFY_THRESHOLD) == "swap"


def test_profile_refs_dir_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(fg, "CHAR_DIR", str(tmp_path / "chars"))
    face = tmp_path / "face.jpg"
    face.write_bytes(tiny_png())
    refs = tmp_path / "refs"
    refs.mkdir()
    prof = fg.save_character("vj", str(face), refs_dir=str(refs))
    assert prof["refs_dir"] == str(refs)
    assert fg.load_character("vj")["refs_dir"] == str(refs)
