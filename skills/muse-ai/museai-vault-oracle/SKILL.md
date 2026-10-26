---
name: "museai_vault_oracle"
description: "Create and keep an Oracle Cloud Always Free VM for MuseAI-Vault, Always Free only, no paid shapes, no payment method added. Use for the cloud vault server, <vault-instance>, <cloud-region>, <instance-shape>, or when the vault instance is down, sealed, or missing after a trial ends."
---

# MuseAI-Vault: Oracle

## Purpose
Provide the one tiny, always-free cloud server that runs OpenBao.
Nothing else runs on it. It is not a general server, not a GPU box,
and not a place to store other data.

## The shape, and why
- Shape: `<instance-shape>`, 1/8 OCPU, 1 GB RAM each, up to two
  such instances per Always Free tenancy. This skill uses one.
- Region and availability domain are set at launch and are recorded
  in the tenancy console. Do not guess them in chat; read them from
  the console or from the launch record held by the coordinating AI.
- Storage: block storage is shared across boot volumes, 200 GB total
  in the Always Free allowance. One boot volume is enough. Do not add
  data volumes for this vault.
- Cost rule, absolute: Always Free only. No paid shapes, no upgrade,
  no payment method added. A trial credit, if present, does not change
  this rule. After a trial ends, check that the Always Free instance
  is still RUNNING. Do not terminate it thinking trial end removes it.
  If it is stopped, restart it; if it is gone, rebuild it from
  `museai-vault-openbao`, do not pay to recover it.

## Workflow
1. Confirm the tenancy is Always Free and the home region is the one
   already in use. Creating a second tenancy or a second region splits
   the vault from its DNS, tunnel, and Access records.
2. Launch, or verify, one E2.1.Micro instance for the vault only.
   Ubuntu, SSH key only, no password login for the cloud user.
   Keep the launch SSH key in the coordinating AI's own secure store
   only, never in this repo, never in chat, never on the board.
3. Open only what the vault needs, in the instance security list:
   SSH for administration on port <ssh-port-vault> (use the vault
   server's actual SSH port; do not assume a default), and the
   OpenBao public TLS port 8200 (Vault/OpenBao default API port;
   change only if you changed the listener) for the tunnel-era
   checks. Preserve the existing SSH rules; do not open
   the vault localhost port to the internet. The localhost port is
   for the tunnel only.
4. Verify the instance is RUNNING in the console, then verify from
   inside it that OpenBao is running. See
   `../museai-vault-openbao/SKILL.md` for the OpenBao checks.
5. Set the daily sign health check (see the parent skill's recovery
   runbook) so a silent vault failure is caught the next morning,
   not at the next sign attempt.

## If the instance is down
- Check the console first: RUNNING, STOPPED, or TERMINATED. A
  STOPPED instance can be restarted. A TERMINATED instance cannot
  be restarted; rebuild it, then rebuild OpenBao, then re-do the CA
  swap on both boxes. Do not try to revive a terminated instance's
  Vault data from a boot volume unless the unseal keys for that data
  are known and verified; in the original rebuild, old Vault data
  was unrecoverable without its lost unseal keys, and the correct
  move was a fresh rebuild, not a boot-volume rescue.
- Capacity errors ("out of capacity") are an Oracle-side shortage,
  not a configuration error. Retry later, or in another availability
  domain in the same region. Do not upgrade the shape to work around
  a capacity error.
- If an instance is reclaimed for idleness, the same rebuild path
  applies. The auto-unseal and health-check steps in the parent skill
  exist to keep the instance visibly used and visibly healthy.

## Operating rules
1. One vault instance, one purpose. Do not co-locate other services
   on it, and do not use it as a jump host for general work.
2. Never add a payment method to "fix" a free-tier problem. The fix
   is a rebuild, a restart, or a capacity retry, in that order.
3. Old boot volumes are backup only. Do not delete a preserved old
   boot volume until the new vault, tunnel, both boxes, and every
   AI path are verified. Deleting it early removes the only fallback
   for a tunnel credential or a config file that was missed.
4. Record the instance state, not its secrets, after every change:
   RUNNING or not, shape, region, and the date checked. Secrets stay
   in the vault init directory and in the box 1 master-material copy
   only, never in this skill or in a status note.

## Detail
See `references/oracle-setup.md` for the launch checklist, the
security-list checklist, and the post-trial check.
