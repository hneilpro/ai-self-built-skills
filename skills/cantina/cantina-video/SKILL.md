---
name: "cantina_video"
description: "Create AI videos in the Cantina web app: gallery-image-to-video composer flow and the timeline Video Editor. Use when the user wants Cantina to animate a character into a talking/gesturing video."
---

# Cantina Video

## Purpose
Create character videos: attach a generated gallery image and/or @-mention a
character in the bottom composer, describe the action/dialogue, generate, QC
the render, and clean up failures. Verified 2026-10-19 (one end-to-end run:
Tori @tori_v, image-to-video, first generation passed).

## Workflows

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

### B. Video Editor directly (verified read-only)
Click "+ New video" → /video-editor: top bar has Advanced settings gear,
Aspect ratio 9:16 (locked/disabled), Video/Script tabs, Saved, Share.
Canvas: "Add your first clip — Use the + button to add characters or
images". Track header and timeline each have an "Add clip" (+) button →
picker with "Character" and "Image" tabs. Image tab: gallery grid of
generated images ("Gallery image" + character/time), "All" filter, and a
"Describe an image…" composer (0/2000 chars) at the bottom. Bottom toolbar:
Play, timer, Cast/Locations/Wardrobes/Objects/Split/Captions/Music marked
"(coming soon)" as of 2026-10-19, Undo/Redo, disabled "Generate" (enables
once clips are added), Saved/Share.

### C. From an image's detail page (verified read-only)
Click the image card → Edit Image page (/images/<id>?type=message); right
panel "Create video" tab: Video template (Auto), "Describe the video you
want to make…" prompt box, "Add a character", "Camera style", "Create
video" button.

## What the app produces
- The verified run produced a 23-second 9:16 clip. The app wrote its own
  action line (e.g. "begins speaking immediately, looking directly into the
  camera while gesturing naturally with her raised right hand") and its own
  dialogue steered by the prompt ("explaining code" → spoken dialogue about
  Python coding, e.g. "we are optimizing your Python scripts to execute with
  absolute precision").
- Audio: rendered A1 track with a full waveform and on-screen captions
  transcribing the dialogue (audible playback not verified in the agent
  browser environment — confirm by listening).
- No moderation block on this run (racier image prompt, dialogue prompt).

## Output Contract
- The kept video (gallery name, link, length), what it shows, audio yes/no.
- Failed/culled videos DELETED from the Videos gallery — never leave them
  sitting there (user's standing cleanup rule: also delete unused images).

## Operating Rules
1. Requires an authenticated session — run `cantina_login` first if needed.
2. Character identity comes from the @-mention chip, like images — never
   rely on a bare name in text.
3. GOTCHA — the source image is consumed: after the kept gallery image was
   attached to the video project, it VANISHED from the Images gallery and
   its slot was replaced by a new AI-generated still that was also shared
   into the character's chat. Save/download any source image you want to
   keep BEFORE attaching it to a video project.
4. QC every video in the editor preview: correct character, anatomy intact,
   no frozen/black frames, dialogue on topic. A1 waveform + captions = audio
   exists. One retry max on failure; delete failures.
5. The web app is beta and the UI drifts — findings carry their "verified
   as of" date; re-verify paths before trusting them blindly.
