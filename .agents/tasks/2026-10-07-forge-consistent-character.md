# Task: Forge consistent-character feature (forge-image-gen v2)

## End goal
forge_gen.py always carries a reference face for txt2img/img2img so a named
character keeps the same face across poses/outfits, using the best identity
backend the owner's Forge server actually offers.

## Acceptance criteria (checkable)
1. `--character vj` / `--ref face.jpg` attaches the ref on every generation;
   FORGE_RESULT reports `face_mode_used`; a downgrade is listed, never silent.
2. txt2img and img2img (`--init`, `--denoise`) both work; plain txt2img with
   no ref behaves exactly as v1 (back-compat CLI, same FORGE_RESULT keys plus new ones).
3. `--probe-server` reports which of pulid/instantid/faceid/reactor the
   server offers, from script-info + ControlNet model/module lists.
4. Profiles live outside the repo (~/.config/forge-gen/characters/, 0600);
   no image, URL, or personal data is committed.
5. Offline test suite passes, including a fake-Forge-server end-to-end run:
   txt2img+faceid, img2img, reactor downgrade on HTTP 400, profile CRUD.
6. Live-PC generation is `unverified` until the owner runs it with a fresh
   tunnel URL; the exact live commands are documented in the handoff.

## Blockers / caveats
- Exact PuLID always-on arg layout varies by Forge build -> error-driven
  downgrade (try in auto order, log, fall through) instead of blind trust.
- ReActor arg layout follows the extension's published API example; same
  downgrade safety net applies.
- No live tunnel at build time: live generation is unverified by design;
  the fake-server suite covers everything except real GPU output.

## Plan / design
- Extend bin/forge_gen.py only (no new dependency; requests + Pillow as v1).
- Pure builders (build_payload, available_modes, probe parsing) so they are
  unit-testable without a server.
- Auto order: pulid > instantid > faceid > reactor > img2img-ref > none.
  Rationale + sources: .agents/research/2026-10-07-forge-consistent-character.md;
  decision record: .agents/decisions/2026-10-07-identity-backend-order.md.
- Owner OK: the owner's 2026-10-07 request explicitly asked to research,
  plan, implement, test, and self-criticize this feature. That is the
  Plan-phase OK for this build.

## Test strategy
- pytest suite in skills/forge-image-gen/tests/ (payload builders, profile
  validation, fallback order, fake-server end-to-end). Evidence in
  .agents/test-reports/.
- Critic pass is a separate role switch after the handoff.
