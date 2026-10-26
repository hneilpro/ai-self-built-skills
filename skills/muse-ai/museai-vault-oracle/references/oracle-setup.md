# Oracle setup — launch checklist and post-trial check

Verified live during the original build. Vendor docs change; the Always Free allowance
for the E2.1.Micro shape has not changed in the docs checked for
this skill, but always re-check the Oracle Always Free page before
launching, and record the date checked. Do not trust a guide's
allowance numbers without that check.

## Launch checklist
- [ ] Tenancy is Always Free, home region is the region already in
  use for this vault. Do not create a second tenancy or region.
- [ ] One instance, shape `<instance-shape>`, for the vault
  only. No other service on it.
- [ ] Ubuntu image, SSH key only, no password login for the cloud
  user. Keep the launch key in the coordinating AI's own secure
  store only, never in this repo, never in chat, never on the board.
- [ ] Security list: preserve SSH, allow the OpenBao public TLS port 8200 (Vault/OpenBao default API
  port; change only if you changed the listener) for direct checks,
  do not expose the OpenBao localhost port <vault-localhost-port>
  (example: 8201)
  to the internet. The localhost port is for the tunnel only.
- [ ] Instance state: RUNNING, in the console, before any OpenBao
  work starts.
- [ ] After launch, record, with no secrets: instance name, shape,
  region, availability domain, and the date checked. That record is
  for the next rebuild, not for chat.

## Capacity and idle rules, from vendor docs and community reports
- "Out of capacity" on launch is an Oracle-side shortage. Retry
  later, or in another availability domain in the same region. Do
  not upgrade the shape to work around it.
- Always Free instances can be reclaimed if Oracle deems them idle
  over a window. The daily sign health check and the auto-unseal
  timer keep the vault visibly used. A vault that is never signed
  against looks idle, even if it is up.
- Block storage is shared: 200 GB total, boot volumes included.
  One boot volume for this vault is enough. Do not add data volumes
  "just in case"; they consume the shared allowance for the next
  instance.

## Post-trial check — do this, do not skip it
When a trial credit ends, the Always Free instance should keep
running, unchanged. Known at writing: the trial in the the original build
rebuild was due to end on that account's trial end date. After that date, and on any
future trial-end date, check, in the console, on the trial-end date
and the day after:
- [ ] Instance is still RUNNING, shape unchanged.
- [ ] No payment method was added, no upgrade was made.
- [ ] OpenBao health is unsealed, and a sign test passes.
If the instance is stopped, restart it. If it is terminated,
rebuild it from the parent skill's setup order, in order, and
re-do the CA swap on both boxes. Do not pay to recover a free
instance, and do not terminate it yourself thinking trial end
removes it.

## What this skill does not do
This skill does not install OpenBao, does not create a tunnel, and
does not gate the vault. Those are the other two component skills.
If Oracle work is done and OpenBao work has not started, the vault
is not "almost done". It is a server with no signer, and no AI can
sign until OpenBao is installed and verified.
