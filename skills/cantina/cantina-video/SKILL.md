---
name: "cantina_video"
description: "Create AI videos in the Cantina web app: image-to-video flows, the Video Editor (script, captions, multi-scene), and the pre-submit checklist. Use when the user wants Cantina to animate a character into a talking/gesturing video."
---

# Cantina Video

## Purpose
Create character videos: pick a source image and/or @-mention a character,
describe the action/dialogue, generate, QC the render, and clean up
failures. Verified 2026-10-19 (two end-to-end runs: first passed — the app
re-dressed the character in a turtleneck because the prompt named no outfit;
second run submitted via the image page's top input).

## Parameters
The character handle is a per-session parameter, never hardcoded here:
`@<handle>` (e.g. `@tori-v` for Tori). These procedures work with any
character avatar — or with no avatar at all — supplied by whoever runs the
skill. Always use the handle given for the session; never assume one.

## How Cantina video works (official model)
Cantina has two video tools (help center: "Fast Videos vs Imagine Videos"):
- **Imagine videos** — the full flow. The bottom composer ("Imagine a video.
  Type @ to add characters.") on the Create Video page: pick characters,
  write a scene prompt, tap the ✦ wand. Imagine generates dialogue + an
  action prompt per scene, then lands in the Video Editor.
- **Fast videos** — still-first, motion-second. From an existing image:
  open the image → **Create Video** (top-left/top input) → describe what
  happens → generate. Animates the chosen still.
- A bot needs **Voice enabled** (and AI Selfies on) to appear in videos —
  "Voice unlocks video." No voice = "This bot can't make a video yet."
- Each shot takes a few minutes to render; finished videos land in the
  **My Videos** queue. You can leave and come back.
- Videos are 9:16 vertical (locked in the web editor, observed 2026-10-19).
  An **HQ toggle** (HQ vs Fast mode) exists on the preview.

## Workflows (web app)

### A. Image-to-video via the gallery (simplest, verified)
1. Left nav → Images (lands on the /create-image gallery).
2. Hover a generated image card → click the sparkle "Add to video project"
   button. The image attaches as an "Image" chip in the bottom video
   composer ("Imagine a video. Type @ to add characters.").
3. In the same composer, @-mention the character (type `@<handle>`, pick
   from the typeahead so the chip attaches — e.g. `@tori-v` → Tori).
4. Type the video prompt (action + what she should talk about), leave the
   Template dropdown on default, press Send.
5. The Video Editor opens with one clip; wait for generation to finish
   (several minutes). Open/play it and QC before keeping.

### B. Imagine flow via the Create Video page
1. Left nav → Create Video (lands on /create-video).
2. Bottom composer: "Imagine a video. Type @ to add characters." — Video /
   Image tabs, Template dropdown, @-mention button, theme button, Send.
3. Attach an image chip ("Add to video project" from a gallery card) and/or
   @-mention the character, type the scene prompt, press Send.
4. The Video Editor opens; wait for generation (several minutes).

### C. Fast flow from an image's detail page (verified end-to-end 2026-10-19)
1. Click an image card → its detail page (/images/<id>). Right panel
   "Create video" tab: Video template (Auto), "Describe the video you
   want to make…" prompt box, "Add a character", "Camera style",
   "Create video" button.
2. Use the **TOP** "Describe the video you want to make…" input — on this
   page the top input is the real generator; the bottom composer is not
   (user correction, 2026-10-19). Official docs agree: "tap Create Video in
   the top left corner."
3. Add the character (@<handle> chip — see checklist), type the action
   prompt, Template on Auto, click **Create video**.

### D. Video Editor directly (verified read-only 2026-10-19)
"+ New video" → /video-editor: top bar has Advanced settings gear, aspect
9:16 (locked/disabled), Video/Script tabs, Saved, Share. Canvas: "Add your
first clip — Use the + button to add characters or images". Track header
and timeline each have an "Add clip" (+) button → picker with **Character**
and **Image** tabs. Image tab: gallery grid of generated images ("Gallery
image" + character/time), "All" filter, and a "Describe an image…"
composer (0/2000 chars) at the bottom. Bottom toolbar: Play, timer,
Cast/Locations/Wardrobes/Objects/Split/Captions/Music (marked "coming
soon" 2026-10-19), Undo/Redo, **Generate** (enables once clips are
added), Saved/Share.

### E. From a bot chat image → Animate Image (official docs, not yet
exercised on web)
Send a scene prompt in the bot's chat → bot replies with an image → tap it
→ detail view → **✦ Create** → "Animate Image" screen → type the action
prompt → Create. The multi-scene editor opens.

### F. Multi-scene (official docs, partially observed)
In the editor, **+** in the scene-thumbnails row → **Add Character** or
**Add Image**; pick media, write per-shot dialogue + action prompt. Each
shot has: Image (Change), Dialogue (**Rewrite** = app drafts the line),
Action Prompt, Regenerate-clip toggle, Delete. Bottom nav: Edit Script,
Topic/Plot, Environment, Caption Style. **Generate** at the bottom renders
everything into My Videos.

## Prompting (official formula + verified lessons)
Official recipe — **Subject → Setting → Action → Atmosphere**:
1. Subject: what your bot looks like (with the @-mention chip identifying
   the character; see checklist).
2. Setting: background/backdrop.
3. Action: what the bot does.
4. Atmosphere: "micro-movements" / setting details for quality.
Example (official): "Shark sitting in a boat as it slowly drifts down a
river while butterflies fly around and the green grass sways in the wind."
- The model reads prompts literally: the more the prompt sounds like the
  shot you're picturing, the closer the result.
- Creator tips (official): prompt one shot at a time and react to what
  rendered before writing the next; reuse the same bots across a series;
  give each bot a distinct voice in dialogue.

## Script, dialogue, captions
- After generation, **Edit Script** (tap the text, or bottom-left): per-bot
  blocks with character name, Action Prompt button, dialogue with Rewrite.
- **Topic/Plot**: auto-generates scripts, images, and action prompts; tap
  the checkmark to generate a full script from the plot, then edit manually.
- To drop dialogue for a scene, clear its Dialogue field — the Action Prompt
  still drives motion.
- Captions: font (None = off), text size, text color; toggle captions on/off.
- Audio: rendered A1 track with waveform + synced captions (audible playback
  not verified in the agent browser — confirm by listening).
- Verified 2026-10-19: the app writes its own action line and dialogue
  steered by the prompt ("explaining code" → Python-coding dialogue).

## What the app produces
- Verified runs produced ~20–23s 9:16 clips with app-written dialogue,
  voice audio, and on-screen captions.
- Outfit behavior: official docs say a source selfie "locks in the look
  (wardrobe, setting, lighting…)" and the video "inherits everything"
  (Selfies as Scene Anchors). Observed once otherwise: with no outfit in
  the prompt, the video re-dressed the character in a tame outfit (cream
  turtleneck) despite a lingerie source image. When the outfit matters,
  name it in the prompt — within the moderation limit below.

## Moderation — read before retrying
- **Two layers** (official, "Why was my video generation blocked?"):
  foundation-model filters (generic errors, outside Cantina's control) and
  Cantina's own Community Guidelines review.
- The line: suggestive/romantic/sexually-charged content is allowed; fully
  explicit pornographic video is not — and "moderation errs toward caution."
- **Verified 2026-10-19:** lingerie wording ("wearing a purple lace top and
  black lace underwear") is blocked at the VIDEO prompt stage on every
  input ("Oops! Your prompt goes against our Community Guidelines" + red
  "Prompt contains sensitive content"). Image prompts accept the same
  wording; video prompts do not.
- **Do NOT reword a blocked prompt to sneak past the filter.** Official
  policy: "Repeated attempts to evade moderation on the same content can
  lead to account restrictions." One reword attempt max; if it still blocks,
  stop and use the "Report an issue" option on the blocked result for human
  review. Occasional blocks are normal and not tracked against the account.
- Zero tolerance: sexual content of real, identifiable people without
  consent (NCII), minors, hate, IP violations. Fictional user-owned bots
  (e.g. @tori-v) are the safe working surface.
- Guideline violations can mean content removal and/or account restrictions.

## Pre-submit checklist (MANDATORY — banked 2026-10-19 after a sloppy session)
Do not click Create/Generate until the browser has confirmed ALL of these
back with the composer's actual current state:
1. The @<handle> chip is INLINE in the prompt textbox (via @ typeahead) — not
   in a separate "Add a character" area, not removed by a prompt edit.
   (Note: the Imagine composer officially uses a character bar at the top;
   on the image detail page's Create-video panel the chip must be inline —
   user-verified 2026-10-19.)
2. The prompt text contains NO bare written name ("Tori" as text) — chip
   alone identifies the character. When editing prompt text, re-verify the
   chip is still attached before submitting.
3. The prompt text contains NO clothing/outfit wording — video prompts with
   lingerie wording are moderation-blocked on every input.
4. The input used is the TOP "Describe the video you want to make…" box on
   the image detail page — the bottom composer there does not generate.
5. Template is on Auto (default).
Why this exists: in the 2026-10-19 session the browser was given loose
instructions and the user had to correct it live four times (bare name
instead of chip, chip deleted during prompt edit, chip in the wrong
location, wrong input used). Root cause: vague delegation + no intermediate
verification. Never submit a Cantina generation without this checklist.

## Output Contract
- The kept video (gallery name, link, length), what it shows, audio yes/no.
- Failed/culled videos DELETED from the Videos gallery — never leave them
  sitting there (user's standing cleanup rule: also delete unused images).

## Operating Rules
1. Requires an authenticated session — run `cantina_login` first if needed.
2. Character identity comes from the @-mention chip — never rely on a bare
   name in text (see checklist).
3. GOTCHA — source images MAY vanish after video use: in the first verified
   run, the kept gallery image was consumed/replaced after being attached
   to a video project (its slot filled with a new AI still shared into the
   character's chat). In the second run, the attached source image stayed in
   the gallery untouched. Behavior is inconsistent, so save/download any
   source image you want to keep BEFORE attaching it to a video project —
   the reliable download route is the image page's Share → Download.
4. QC every video in the editor preview: correct character, anatomy intact,
   no frozen/black frames, dialogue on topic. A1 waveform + captions = audio
   exists. One retry max on failure (never a moderation-evasion retry);
   delete failures.
5. Sharing (official): feed, Storyline, outside Cantina, camera roll, copy
   link.
6. The web app is beta and the UI drifts — findings carry their "verified
   as of" date; re-verify paths before trusting them blindly. Official
   reference: https://support.cantina.com (Video Editor 101, Prompting for
   Videos in Cantina, Selfies as Scene Anchors, Community Guidelines).
