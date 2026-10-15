---
id: app-access
mode: auto
channel: sideshift
approved: 2026-10-14   # captain asked for it; sign-in steps from the excerlock-access skill
fields: [email]
once: per_creator
quiet_hours: true
min_gap_minutes: 0
requires: [accepted, premium_granted]   # only after excerlock-access printed GRANTED for this email (grant.py)
replaces_unanswered: true   # it answers her message with the email
---
Your free Premium is on. Get ExcerLock: https://apps.apple.com/app/id6787265352
Tap "Already have an account? Sign in" → "Continue with Google" (Gmail) or "Continue with email" with exactly {email}.
