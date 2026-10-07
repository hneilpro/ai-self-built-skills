# ADR: identity backend order + probe-first design

Status: Accepted (owner-requested feature, 2026-10-07)

In the context of adding consistent characters to forge_gen.py, facing four
incompatible identity backends (PuLID, InstantID, IP-Adapter FaceID, ReActor)
whose availability depends on the owner's Forge install, we decided for a
probe-first auto order (pulid > instantid > faceid > reactor > img2img-ref)
with per-attempt error-driven downgrade and the used mode always reported,
to achieve a tool that works on whatever his Forge actually has today and
improves itself when he installs a stronger backend, accepting that the
first live run doubles as the capability survey.
