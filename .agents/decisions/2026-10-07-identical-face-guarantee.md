# ADR: identical-face as a verified pipeline guarantee

Status: Accepted (owner-requested, 2026-10-07). Supersedes the "auto order
is enough" assumption in 2026-10-07-identity-backend-order.md (order itself
is amended, see below).

In the context of Forge v2 shipping unverified faces because the server
accepts identity payloads it silently ignores, facing the owner's requirement
that the identical-face setting mean "feed a face, get that face back —
as reference during generation and as a swap when needed", we decided to
make identical-face a post-generation verified guarantee: condition during
diffusion with the best live backend, then measure ArcFace cosine against
the reference, auto-swap locally below threshold (default 0.55), re-measure,
and report both scores in FORGE_RESULT, to achieve consistency that is
proven per-image rather than assumed per-payload, accepting one local
CPU swap on generations that drift.

Amended auto order: pulid > instantid > faceid > reactor > local-swap >
img2img-ref > none. Rationale: a proper swap preserves identity; the
img2img-ref route preserves only composition and must rank below it.

Consequences: every character generation now depends on the local
InsightFace stack (~/workspace/forge-face-swap) being present; its absence
degrades to "unverified" reporting, never to a silent pass. Flux checkpoints
route identity through verify+swap (plus PuLID-Flux where a Forge-native
backend ever appears), never through SDXL adapter payloads.
