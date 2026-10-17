---
id: app-access
mode: auto
channel: sideshift
approved: 2026-10-16   # captain: "when they give email give them an account then say to download excerlock at that link and do the steps; when turned on the first condition go back to app store and give us a rating" (sign-off removed, captain 2026-10-16: "nobody says that")
fields: [email]
once: per_creator
quiet_hours: true
min_gap_minutes: 0
requires: [accepted, premium_granted]   # only after excerlock-access printed GRANTED for this email (grant.py)
replaces_unanswered: true   # it answers her message with the email
---
Your free ExcerLock account is ready! 🎉 Download ExcerLock here: https://apps.apple.com/app/id6787265352
Tap "Already have an account? Sign in" → "Continue with Google" (Gmail) or "Continue with email" with exactly {email}, then follow the setup steps.
Once you've turned on your first condition, go back to the App Store and give us a rating 🧡
