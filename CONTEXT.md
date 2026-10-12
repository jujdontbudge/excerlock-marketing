# ExcerLock Marketing

Marketing for ExcerLock, an app that blocks the apps a user picks until they walk, hit a step goal or go to the gym. This glossary fixes the words agents use for the repo's concepts.

## Structure

**Section**:
One kind of marketing work with its own rules, skills, workflows and per-account work, in `sections/<name>/`. See `sections/README.md` for the current sections.
_Avoid_: channel, program, pipeline

**Core**:
Skills, workflows and product facts every section can use. Never names a section or an account.
_Avoid_: shared, common, global

**Skill**:
One capability, written as `SKILL.md` in its own folder with any tools it needs.
_Avoid_: guide, playbook, procedure

**Workflow**:
An ordered set of skills and directions that produces one deliverable.
_Avoid_: pipeline, process, flow

**House rule**:
A section-wide default with an ID (`H-…`) and a reason, kept in that section's `rules.md`.
_Avoid_: preference, standing rule, guideline

**Override**:
An account's replacement for one house rule, written under `## Overrides` in `sections/<section>/accounts/<name>/README.md`.

**Make universal**:
The captain's instruction to turn a correction into a permanent rule in the file that caused the mistake (`core/skills/make-universal/SKILL.md`).

## Accounts

**Account**:
One of our own TikTok accounts and the fictional person who posts on it. Who she is lives in `accounts/<name>/account.md`.
_Avoid_: persona, profile, page

**Character**:
The fictional adult woman shown on an account: face, body and style. Accessories are chosen for each scene.
_Avoid_: model, avatar, girl


**Audience**:
The group an account is made for, such as gym girls or walking girls.
_Avoid_: niche, lane, demographic

**Captain**:
The owner. His rules and reviews override agent judgment and older research.

## Slideshows

**Deck**:
One TikTok photo slideshow: its script, prompts, review notes and build log in `decks/NN-slug/`.
_Avoid_: carousel, post, slideshow (for a single one)

**Slide**:
One image in a deck with its on-screen text.

**Hook**:
The first slide's text and picture, meant to stop the scroll.
_Avoid_: title card, opener

**Format**:
The slide-by-slide shape of a deck, such as the pain funnel or the swap format.
_Avoid_: template, structure

**Receipt**:
A real phone screenshot used as proof on a slide, such as a steps total or a Screen Time summary.
_Avoid_: proof screenshot

**CTA screen**:
The product screen or store asset explicitly chosen by the active section's CTA contract.

## Creators

**Creator**:
A real person we might pay to make videos, with one record for all their handles.
_Avoid_: influencer (for the person), talent, lead (after vetting)

**Handle**:
One account of a creator on one platform.

**Snapshot**:
A dated set of stats for one handle. Never overwritten.

**Track**:
How a deal is run: `ugc` (production and fast format tests) or `influencer` (buying their audience's trust).

**Deal**:
One agreement with one creator: terms, brief, contract, deliverables and payments. A creator can have several.
_Avoid_: contract (that's one document of a deal)

**Deliverable**:
One video a deal owes, with its due date and, once live, its post.

**Stage**:
Where a creator is in the pipeline (`sections/creators/creatorops/pipeline.py`).

## Images

**Organic reference**:
A real photo someone else posted that one of our images copies: scene, camera, light and pose stay, the person is swapped (`core/skills/reference-swap/SKILL.md`).
_Avoid_: style digest, moodboard, inspiration

**Master reference**:
The approved image that defines a character's face and hair. Every swap with her in it attaches it as image 2.
_Avoid_: casting image, character ref

**Organic**:
How the photo is taken and processed (phone camera, real light, clutter, imperfection). Never a plainer or less attractive person.
_Avoid_: raw, real, amateur (for casting)
