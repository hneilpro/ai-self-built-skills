# Cantina image prompt lessons

## Contact grounding (verified 2026-10-19)
Cantina renders exercise poses floating unless the prompt forces contact —
first wall push-up test came back with hands off the wall, body tipping into
air. Working formulation: "palms pressed flat against the wall, arms bearing
her weight, feet planted on the floor, body in a straight angled line".
Apply contact-grounding to every exercise prompt by default.

## Verified working example (2026-10-19)
`Cassy [@sosadsosexy mention] doing a wall push-up workout pose, wearing a
sheer mesh athletic top and extra-low-rise athletic shorts, athletic fitness
photo, fully clothed, SFW.` — completed with no moderation block.

## Wardrobe entries cannot be created by regular users (verified 2026-10-19)
- The Wardrobe tab is only a filter over the user's element library — no
  Create/Add button, no empty-state text, and no element-type selector
  anywhere (composer, detail pages, edit view all lack one).
- Two generations framed as wardrobe items both landed as plain Images;
  the Wardrobe tab stayed empty.
- Real wardrobe entries are creator-made character media only: Cassy's
  profile (cantina.com/profile/sosadsosexy) shows an Elements section with
  Wardrobe / Locations / Objects tabs of flat-lay outfit photos
  "Created by Cassy" (creator: Jack Baymax).
- The user owns no characters ("My characters" shows only Create
  Character), so there is no route to add wardrobe media for Cassy.
- Consequence: outfit is prompt-driven only — describe clothing in text.

## Pose limitations (verified 2026-10-19)
Supine hips-elevated poses (glute bridge: on back, hips raised) resist
generation:
- Gym wording: 1 silent block + 2 lying-flat renders (all deleted).
- Yoga reframe ("bridge pose / Setu Bandha") rendered a genuine bridge once
  (hips elevated, no defects) but the head-end camera hid one foot, failing
  the both-feet-visible check (deleted); a side-angle variant collapsed to
  lying flat again (deleted).
- Yoga wording + explicit "BOTH feet clearly visible, three-quarter camera
  angle" still hid one foot behind the body (hips properly elevated both
  times). The model defaults to a head-end-ish camera for this pose and
  will not show both feet.
- Verdict: Cantina cannot reliably produce a verifiable glute bridge —
  closed after 6 total generations (stop rule).
- Lesson: yoga wording cracks the pose; framing is the remaining enemy.
  For any pose that needs both feet visible, budget for camera-angle
  failure or pick another exercise.

## Moderation (observed 2026-10-19)
All SFW, fully-clothed exercise prompts (5 generations: wall push-up,
sit-to-stands, glute bridge, marching in place, calf raises) completed with
no moderation blocks. Modest wording plus "fully clothed, SFW" in the
prompt appears safe.
Racier wording tested on IMAGES 2026-10-19: a sheer two-piece lingerie /
extra-low-waist prompt and a "purple lace top and black lace underwear"
prompt both generated with no block. The same wording in VIDEO prompts is
blocked on every input — see cantina-video SKILL.md. Official policy:
suggestive allowed, explicit pornographic video not, and moderation "errs
toward caution"; never reword a blocked prompt to sneak past the filter
(repeated evasion risks account restrictions).

## Paths not yet verified (as of 2026-10-19)
- Composer toolbar: Theme styles, Camera styles, Upload images (theme button
  observed on the video composer; not exercised).
- Element tabs: Locations, Objects, Extras, Filter control.
- Inside a bot DM there is NO dedicated image button (only Mention, emoji,
  + Attachments, microphone) — image generation lives on the Create Image
  page, not in the DM.
- Verified since original writing: bottom-center composer ("Imagine a
  video. Type @ to add characters.") with Video/Image tabs — exercised
  end-to-end; "Add to video project" on gallery cards — verified; image
  detail page Create-video panel top input — verified end-to-end.
