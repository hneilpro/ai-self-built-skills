---
name: "cantina_login"
description: "Log into the Cantina AI web app via phone-number SMS code — the only web login method (no Google option on web). Use when the user wants the agent to operate Cantina in the browser."
---

# Cantina Login

## Purpose
Establish an authenticated Cantina web session in the agent's browser so later
skills (chats, image/video generation) can act as the user. Verified 2026-10-19.

## Workflow
1. Open `https://cantina.com/signin` in the browser task.
   (`app.cantina.com` does not resolve; `web.cantina.com` redirects here.)
2. The page offers phone number only — a US (+1) field with a Continue button.
   There is **no "Continue with Google"** on the web login page.
3. Enter the user's phone number (ask them each time — never store it, never
   guess) and submit. Cantina texts a 4-digit SMS code.
4. Ask the user for the code, enter it in the four PIN fields, submit.
   Never guess a code and never reuse an old one.
5. Confirm landing on `https://cantina.com/homefeed` (Home page, BETA badge)
   with the account menu showing the user's name/handle.

## Output Contract
- Logged-in identity (name + handle, read from the account menu).
- Home screen summary: visible chats, rooms, friends.
- Nothing sent, uploaded, or generated during login.

## Operating Rules
1. Phone numbers and SMS codes are transient: use them for the login, never
   write them to files, memory, or skill docs.
2. If the session expired, repeat the flow from step 1.
3. Web login is phone-only. The mobile apps may offer more login options —
   unverified, so don't claim otherwise.
4. Before any later skill uploads the user's face or photos, re-surface the
   Terms §7.4 catch (perpetual, irrevocable license for Cantina to train AI
   models on uploads; no opt-out; account deletion does not revoke it) and
   get explicit per-case approval.
