# Handoff: forge-consistent-character (builder -> critic)

## Changed files
- skills/forge-image-gen/bin/forge_gen.py — v2: character profiles,
  --ref/--character/--init/--denoise/--pose, identity backends
  (pulid/instantid/faceid/reactor/img2img-ref) with probe + downgrade,
  --probe-server, FORGE_RESULT gains face_mode_used/downgrades/character.
  v1 CLI and plain-txt2img behaviour unchanged.
- skills/forge-image-gen/tests/test_forge_gen.py — 22 offline tests incl.
  a fake Forge server (ThreadingHTTPServer; single-threaded deadlocks on
  keep-alive — already fixed, do not revert).
- skills/forge-image-gen/SKILL.md — consistent-character section.
- skills/forge-image-gen/references/consistent-character.md — PC install guide.
- skills/forge-image-gen/references/api-notes.md — v2 endpoints section.
- .agents/{tasks,research,decisions,test-reports}/ — this task's records.

## Verified
- 22/22 tests pass; evidence in the test report.
- CLI smoke: profile save/list with sandboxed HOME; face copy is 0600.

## Known risks / unverified
- PuLID always-on arg layout and ReActor arg tail vary by build. Both are
  documented-layout best efforts behind error-driven downgrade; a wrong
  layout costs one failed POST, then the next backend runs. Live check:
  1. `forge_gen.py <fresh-url> --probe-server`
  2. `forge_gen.py --character vj --preset probe --prompt "portrait photo"` x3
     prompts; confirm face_mode_used and eyeball likeness.
- InstantID module names (instant_id_face_embedding/keypoints) follow the
  A1111 ControlNet naming; Forge's built-in ControlNet may spell them
  differently — probe output will show it; --face-model/weights are the
  escape hatches.
- No face-similarity metric is computed (no InsightFace on this VM);
  likeness judgement stays visual until a PC-side scorer is added.

## Next step for the critic
Grade against .agents/workflows/05-critic-review.md; poke at: downgrade
loop safety (does any mode get retried forever? no — each once), profile
path traversal, v1 back-compat, and whether docs overclaim live status.

## Live addendum
Live A/B done 2026-10-07 (see test report). Owner's next step for real
txt2img identity: install the ReActor extension in Forge + restart, then
`--face-mode reactor` (or auto) just works. Until then, img2img with a
character init image is the working consistent-character route.
