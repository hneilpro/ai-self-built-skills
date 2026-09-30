---
name: "vpn_research"
description: "Research free VPNs and evaluate them for safety, security, and privacy — current picks, avoid-list, and an evergreen scoring rubric. Use when the user wants a trustworthy free VPN or asks whether a specific VPN is safe."
---

# VPN Research (Free Tiers)

## Purpose
Find a free VPN that is actually safe — no logs sold, no malware, real encryption — and know which ones to avoid.

## Workflow
1. Read `references/current-picks.md` (top picks + verified date). If the snapshot is older than ~6 months, re-research before recommending — free tiers change caps, owners, and jurisdictions.
2. Score any candidate — including VPNs the user names — against the 10-point checklist below. A VPN that fails points 1, 6, or 7 is disqualified outright.
3. Cross-check `references/avoid-list.md`. Never recommend anything on it.
4. Deliver the pick with: why it won, its limits (cap, locations, devices), and what the user gives up vs paid.
5. Hand off to `vpn_install` with the chosen provider + target platform.

## Evaluation checklist (evergreen)
1. **Business model.** Free must be a funnel to a paid plan or be mission-funded. No paid tier / no company site / ad-funded = fail.
2. **Jurisdiction.** Prefer Switzerland, Iceland, Malaysia, Panama, BVI (no mandatory retention, outside 5/9/14 Eyes). A 5/9/14-Eyes HQ (US, UK, Canada…) is a yellow flag — acceptable only with verified no-logs.
3. **Audits.** Independent, named auditor, dated. Distinguish no-logs audits from app-security audits; annual beats one-off.
4. **Open-source clients.** Public code = verifiable, no hidden trackers. Closed-source free apps get extra suspicion.
5. **No-logs verifiability.** Policy text is not evidence. Look for: an audit, a real-world test (court order / server seizure with nothing to hand over), RAM-only servers, transparency reports.
6. **Permissions & trackers.** Mobile apps asking for contacts/SMS/camera/mic/location = red flag. Scan with Exodus Privacy. No real VPN needs these.
7. **Company transparency.** Named team, real HQ, public incident post-mortems. Anonymous publishers = fail.
8. **Incident history.** Search "[name] data breach / server seizure / logs handed over". A handled incident with a post-mortem beats a blank slate from an unknown vendor.
9. **Technical honesty.** Real protocols (WireGuard/OpenVPN/IKEv2) with real encryption — not "military-grade" hand-waving.
10. **Cap honesty.** A stated cap is a business model. "Unlimited free" with no revenue source means *you* are the product.

## Operating Rules
1. Never recommend a VPN solely because it tops an app-store chart — check the avoid-list first.
2. State what's verified vs claimed: "claims no-logs, no audit published" is not the same as "audited no-logs".
3. Free tiers don't reliably unblock streaming — say so upfront instead of letting the user discover it.
4. When the user's needs exceed free tiers (many regions, streaming, heavy P2P), point at `references/self-hosted.md` or a paid tier — don't stretch a free pick.
5. Re-check trust annually: new audits, ownership changes, jurisdiction moves, and app-store chart scams.
