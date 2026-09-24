# ExcerLock Marketing

Marketing for ExcerLock, an app that blocks the apps a user picks until they walk, hit a step goal or go to the gym. This glossary fixes the words agents use for the repo's concepts.

## Structure

**Section**:
One kind of marketing work with its own rules, skills, workflows and per-account work, in `sections/<name>/`. Slideshows is the only one today.
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
The fictional woman shown on an account: face, body, style and her own props.
_Avoid_: model, avatar, girl

**Signature prop**:
An object that belongs to one character only (a phone case, headphones) and must never appear on another.

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
The ExcerLock blocker screen used as the image on every CTA slide.

## Images

**Style digest**:
A JSON description of another creator's photo style (camera, light, place, framing), with no person's identity in it. Kept in `library/styles/`.
_Avoid_: style reference, moodboard

**Organic reference**:
A real high-performing post whose slide we copy the idea and look of, never the person.

**Organic**:
How the photo is taken and processed (phone camera, real light, clutter, imperfection). Never a plainer or less attractive person.
_Avoid_: raw, real, amateur (for casting)
