# ExcerLock product

This file owns product facts and their verification limits, not campaign priorities or CTAs. Source: the captain's product description preserved in `history/product-description-before-cleanup.md`. No app build was exercised during the marketing-repository cleanup.

## Product purpose and described behavior

ExcerLock turns attachment to chosen apps into motivation to move and follow through on fitness goals. Users choose the apps to restrict, an exercise condition, and when it applies. It does not lock the entire phone.

The captain described these distinct conditions; verify the particular condition in the current build before filming proof:

| Condition | Access behavior |
|---|---|
| Active walking | Chosen apps available while actively walking, including indoor pacing |
| At the gym | Chosen apps available while physically at the gym |
| Gym arrival | Chosen apps unlock after arrival |
| Gym duration | Chosen apps unlock after a selected time at the gym |
| Step target | Chosen apps unlock after reaching the chosen step goal |
| Walking duration | Chosen apps unlock after a selected walking duration |

One video may demonstrate one condition without redefining the product as walking-only. General combinations of conditions are not part of the described MVP; possible later support is not current proof.

### Treadmill

The captain described direct movement detection when holding the phone, and a camera scan for a phone propped on the treadmill before opening another app. The scan, Instagram lock/unlock, locked-state widget, gym-arrival map/radius and gym widget were described as demonstrable. These are owner-reported capabilities, not fresh verification of the current interface or timing.

### Permissions and failure behavior

Apple Health was identified as the step-total source. Expected permissions: app-blocking/Screen Time authorization, motion/fitness, location for gym conditions, camera for the treadmill scan, and Health for steps. Final permission flow requires build verification.

The described behavior when required permission is disabled is to leave affected apps unlocked and explain restoration. Essential apps can be left unselected. Emergency overrides, accessibility accommodations, cooldowns and other safety exceptions have not been defined in this marketing record.

## Planned, not demonstrated here

Notifications for locked apps, step/progress changes and gym-time milestones; potential later condition combinations. No final notification copy or visual design is recorded.

## Unknown / needs current verification

- Detection threshold and start/unlock latency.
- Stop/relock latency: five seconds was an internal planning assumption, never a measured marketing claim.
- Current progress indicators, widget states and readability at final video/slide size.
- Complete permission behavior and usable creator access.
- Release/access status: the last product description said unreleased. That statement has no recorded verification date and was not freshly checked on 2026-10-08. Verify current access before a download CTA; a waitlist is not known to exist.

Proof must use the actual selected-app behavior and protect personal location, Health, schedules, notifications and bystanders. Campaign positioning, chosen demonstrations and CTA contracts belong to their active work item; older marketing priorities remain history.
