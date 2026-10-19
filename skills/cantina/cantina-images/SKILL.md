---
name: "cantina_images"
description: "Generate AI images in the Cantina web app: @-mention a character plus a free-text prompt, generate, QC the render. Use when the user wants Cantina to render a posed/outfitted image of a bot character."
---

# Cantina Images

## Purpose
Generate still images in Cantina's web app: pick a character via @-mention,
describe pose/outfit/scene in free text, generate, and QC the result before
anyone sees it. Verified 2026-10-19.

## Workflow
1. Requires an authenticated session — run `cantina_login` first if needed.
2. Open `https://cantina.com/create-image` (left nav **Images**).
3. In the prompt box, type `@<handle>` and pick the character from the
   typeahead (e.g. `@sosadsosexy` → Cassy, verified bot "Active now").
   Then type the prompt and click **Generate**.
4. Wait out the "Generating…" spinner. The render lands at the front of the
   Images gallery with Edit image / Add to video project / More actions.
5. QC every render at full size before presenting: correct pose/form, no
   limb defects, outfit as specified. **Delete failed or culled images from
   the gallery** — don't leave them sitting there. Ambiguous = keep + flag
   to the user.

## Output Contract
- The generated image(s), with a keep/cull verdict + reason per image.
- Culled images deleted from the gallery.
- Nothing uploaded, sent, or posted publicly.

## Operating Rules
1. Character identity comes from the @-mention chip — always mention the
   character explicitly; never rely on a bare name in text.
2. Ground physical contact in every pose prompt (see
   `references/prompt-lessons.md`) — Cantina floats poses otherwise.
3. Outfit is prompt-driven: the Wardrobe tab is a library filter with no
   create/add route for regular users — real wardrobe entries are
   creator-made character media only (see `references/prompt-lessons.md`).
   Describe clothing in the prompt text.
4. Before uploading the user's face/photos or building avatars from them,
   re-surface the Terms §7.4 catch (perpetual, irrevocable training license;
   no opt-out; deletion doesn't revoke) and get explicit per-case approval.
   Verified flows so far used only built-in bot characters, no user face.
5. The web app is beta and the UI drifts — findings here carry their
   "verified as of" date; re-verify paths before trusting them blindly.
