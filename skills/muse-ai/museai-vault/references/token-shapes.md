# Token shapes — FAKE EXAMPLES ONLY, DO NOT ENTER

Every example in this file is fake, labelled, and made of obvious
placeholders. No real value appears in this skill, in any file, in
any message, or on the board. If an example below ever looks like a
real value, it is not; it is a placeholder that must never be entered.
If the user shows you a value that does not match the shape for the
field they are entering, stop and check the field before they submit
it. Do not let a wrong-type value be submitted and then debugged later.

## How to tell the values apart — the quick check
- If a value is short and starts with "s.", it is a Vault token.
  It is never an Access value. Never put it in an Access field.
- If a value ends with ".access", it is an Access Client ID. Enter
  it exactly, including ".access", do not trim it, do not add anything.
- If a value is long, random, and does not start with "s." and does
  not end with ".access", it may be an Access Client Secret, but only
  if it came from the second field of the same Cloudflare dialog that
  produced the Client ID. A long random string from anywhere else is
  not proof it is the Secret. Check its source, not just its shape.
- If a value came from the box 1 token file, it is a Vault token.
  If a value came from the Cloudflare dashboard, it is an Access
  value. Source plus shape, together, decide the field. Shape alone
  is not enough.

## Vault token — FAKE ONLY, DO NOT ENTER
- Source: the box 1 master-material copy, per-AI token file, handed
  privately through that AI's secure entry flow only.
- Use: sent as the `X-Vault-Token` header, for that AI's role only.
- Shape, observed the original build: short, starts with "s.", then 24
  letters and numbers, total about 26 characters.
- FAKE EXAMPLE ONLY, DO NOT ENTER: `s.AAAA1111BBBB2222CCCC3333`
- This example is all placeholders. It will never sign anything.
  Never enter it, never test with it, never send it to an AI as if
  it were a token. It exists only so the user can recognise the
  shape: "mine starts with s. and is short, so this is the Vault
  token field."

## Access Client ID — FAKE ONLY, DO NOT ENTER
- Source: Cloudflare dashboard only, Service Tokens, at creation,
  first field in the one-time Service token details dialog.
- Use: sent as the `CF-Access-Client-Id` header, together with the
  Secret, on the normal sign path. Not used on a single-credential variant sign path.
- Shape, observed the original build: a long hex ID, plus a ".access" suffix.
  The suffix is part of the ID. Enter it exactly, including
  ".access".
- FAKE EXAMPLE ONLY, DO NOT ENTER:
  `11111111-2222-3333-4444-555555555555.access`
- This example is all placeholders. It will never pass the gate.
  Never enter it. It exists only so the user can recognise the
  shape: "mine ends with .access, so this is the Access Client ID
  field." Earlier guidance that said a Client ID does not end with
  ".access" was wrong and is superseded by this shape. Do not repeat
  the old guidance.

## Access Client Secret — FAKE ONLY, DO NOT ENTER
- Source: Cloudflare dashboard only, same dialog as the Client ID,
  second field, shown only once at creation. The Secret cannot be
  seen again later in the list. If it was not copied at creation,
  recreate the token; do not guess it, and do not try to recover it
  from the list.
- Use: sent as the `CF-Access-Client-Secret` header, together with
  the Client ID, on the normal sign path. Not used on a single-credential variant
  sign path.
- Shape: a long random string, longer than the Client ID, no "s."
  start, no ".access" suffix.
- FAKE EXAMPLE ONLY, DO NOT ENTER: a long string of placeholder
  characters, for example `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`
  (FAKE, DO NOT ENTER, placeholder only, not a real secret format).
- Never paste a Secret in chat, to prove its shape or for any other
  reason. The Client ID alone, without the Secret, cannot
  authenticate by itself, but a Secret pasted in chat must still be
  treated as exposed and rotated. Do not ask the user to paste a
  Secret to "check" it.

## Root token and unseal keys — shape only, never examples to enter
- Root token: admin only, for re-issuing tokens and for Vault admin.
  Never used for signing, never typed into a browser UI, never sent
  to an AI. Shape: a short token, like a Vault token, held offline
  by the user in their password manager, plus the vault init file
  and the box 1 copy. No fake root token is given here on purpose:
  a root token example that looks usable is too easy to mistake
  for a real one. If the user asks what a root token looks like,
  say only: "short, token-shaped, stored offline, never entered in
  chat or in a browser UI."
- Unseal keys: five base64 keys (five shares, threshold:
  <unseal-threshold> of five shares — record your threshold; the
  files in this series do not state it, do not assume a value),
  held offline by the user in their password manager, plus the
  vault init file and the box 1 copy.
  Shape only: five long base64 strings, each on its own line in the
  init file. FAKE SHAPE ONLY, DO NOT ENTER: five lines of placeholder
  characters, for example `AAAA1111BBBB2222CCCC3333DDDD4444 (FAKE)`,
  repeated five times with different placeholders. Never enter any
  such line anywhere except the Vault unseal procedure run by the
  coordinating AI from inside the vault server, using the init file
  itself, never a pasted copy.

## Public key — FAKE ONLY, DO NOT ENTER
- A public key is not a secret, but a real public key from a live
  keypair must still not be copied into this skill or into chat as
  an example, because it invites confusion with the private key.
- FAKE EXAMPLE ONLY, DO NOT ENTER:
  `ssh-ed25519 AAAA1111BBBB2222CCCC3333DDDD4444 FAKEKEY`
- Real public keys are generated by the AI that owns the keypair,
  and are sent only in the sign request body, never as a chat
  example, never on the board.

## If the wrong value is in the wrong field
Stop before submitting. Close the dialog without saving, if the
secure entry flow allows it, and start that one entry again with
the correct source. Do not submit and then debug. The original build
rebuild had exactly this error: a Vault token value was placed in
an Access Client ID field, and it was caught only because the shape
check was done before submitting. Shape checks exist for this reason.
