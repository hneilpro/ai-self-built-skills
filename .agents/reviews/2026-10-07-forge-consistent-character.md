# Critic review: forge-consistent-character

Reviewer: critic role, same session as builder — **self-review, not
independent**. Verdict downgraded accordingly: nothing here counts as an
independent approval; the owner is the real second pair of eyes.

## Rubric
1. Research — PASS. Right questions (which backend, which API shape),
   named uncertainty (PuLID arg layout, InstantID module spelling),
   probe-first design follows from it.
2. Plan/Design — PASS. Checkable criteria, blockers first, ADR present,
   owner OK is the feature request itself.
3. Build — NEEDS CHANGES (findings B1, B2, M1).
4. Test — PASS with note. 22 tests exercise exactly the changed surface
   incl. a fake-server end-to-end; live GPU run honestly `unverified`.
   Note: system python lacks pytest; suite ran under a sibling project's
   venv. Repro steps are in the test report.
5. Correctness — PASS offline; live correctness UNVERIFIED (disclosed).
6. Evidence quality — PASS. A stranger can rerun the suite from the report.
7. Risk — NEEDS CHANGES (M1): the biggest real-use risk is a server that
   accepts a ControlNet unit but ignores it (wrong key spelling), yielding
   identity-less images while face_mode_used claims a backend ran.
8. Suggestions — see M2 (opinion, labelled).

## Findings

### B1 (Blocking) — owner's real name in files headed for a public repo
forge_gen.py docstring and SKILL.md say "the owner's ..." — pre-existing in
the untracked mirror, but this branch is what would publish them, and the
repo is public. House rule: placeholders only in pushed code.
Fix: scrub to "the owner's" in bin/forge_gen.py + SKILL.md (keep triggers).

### B2 (Blocking) — auto mode can fail a generation that plain txt2img would have saved
available_modes() ends at img2img-ref; if every backend 400s, the user
gets a hard error instead of an image. Forced mode already ends at "none".
Fix: append "none" to the auto chain too — face_mode_used=downgrade chain
keeps it honest, availability wins.

### M1 (Major) — ControlNet unit key spelling + claim wording
The unit uses "image"; A1111-family parsers also read "input_image".
A silently-ignored unit overclaims via "face_mode_used says what really
ran" (SKILL.md). Fix: send both keys; reword to "what the server
accepted"; keep the standing rule to view every image before presenting.

### M2 (Minor/opinion) — --face-weight is ignored in reactor mode
ReActor's strength is not weight-driven here. Labelled opinion: note it in
consistent-character.md rather than inventing a mapping.

## Verdict: NEEDS CHANGES (B1, B2 blocking; M1 major)
Builder revision round 1: fix B1/B2/M1, note M2, rerun the suite, then
critic re-scores rows 3 and 7 only.

## Re-score after builder revision round 1 (critic, same session)
- B1: grep for the owner's name across skill .md/.py is CLEAN. Fixed.
- B2: auto chain now ends img2img-ref -> none; tests updated. Fixed.
- M1: unit sends image + input_image; SKILL.md now says "what the server
  accepted", with the view-the-image rule attached. Fixed as far as
  offline work can take it; residual risk (silently ignored unit) is
  disclosed and only a live run closes it.
- M2: noted in references/consistent-character.md. Done.
Rows 3 and 7 now PASS (offline scope). Verdict: **approve with notes** —
the one note being the unverified live GPU run, which needs the owner's
fresh tunnel URL. Self-review caveat from the header stands.
