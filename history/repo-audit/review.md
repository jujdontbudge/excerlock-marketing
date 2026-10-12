# ExcerLock repo cleanup review

## Verdict

The primary failure is competing authority: current work, old assignments, historical research, global skills and recalled memories can all steer the next task. Deleting files without repairing that authority chain will not solve it.

The core/sections/accounts split is worth keeping. The repository does not need another architecture rewrite, another universal checklist, or another layer of agents. It needs fewer active instructions, explicit status and one owner for each decision.

Nothing was deleted or changed in the operational repo for this review. Audit artifacts were written only under `raw/repo-audit/`.

## Coverage and verification

- Inventoried and full-text structurally scanned **125 repository Markdown files**, excluding ignored runtime work/transcripts, caches, virtual environments, media and symlink aliases. Every file has a proposed disposition in `inventory.md` and a machine-readable record in `inventory.json`.
- Read operational root docs, all 12 project skills, central workflows, account definitions, writing/review rules, selected skeletons, research direction/briefing documents and related tools. Historical bulk reports were examined structurally and by relevant sections, not revalidated creative-by-creative against original media. This is a cleanup review, not a fresh audit of every historical performance claim.
- Checked the active project Mem0 wiring, status and all **291 project memory records** with read-only SQLite inspection. `memory-inventory.json` contains identifiers and triage flags, not raw memory content. Flags are candidates, not approved deletions; each proposed memory deletion still requires semantic/source review. No memory was deleted.
- Examined default-profile global skill filesystem aliases and selected marketing skills; did not audit the complete contents of all global skills or other Hermes profiles.
- `scripts/lint`: passed.
- Crawler integration: **18 tests passed**.
- Repo-local Mem0 integration: **12 tests passed**. These tests cover the repo-local worker, not the different shared engine actually imported by Pi.
- Found **34 broken local Markdown link occurrences**, all in `research/competitor-universe/report.md` pointing into an old `.treehouse` checkout.
- Current workspace contains substantial pre-existing staged deletions and unstaged edits. Do not mix cleanup with those changes or assume they were introduced by this review.

## Highest-priority repairs

### 1. Current UGC direction has no correct authoritative home

`research/ugc-formats-2026/current-creative-direction.md:5-11` still instructs three guides, defines POV as a first-person gym/treadmill app demo, and includes talking head. The latest assignment is two formats on one shared page, creator-recorded footage, no name on screen by default, TikTok/Reels, and Hayden's kitchen-walk reference for the movement format.

The global `ugc-creator-program` skill explicitly requires reading this old direction and embeds the older three-format interpretation. It also says to supply prerecorded product demos by default. Those are not the current assignment.

**Repair:** put the current assignment in an active real-UGC section/campaign home. Keep the short generic brief-writing capability separate. Archive the old assignment and remove it from required-read routing. Do not globally prohibit supplied footage forever: the captain excluded it from this test, not every future format.

The accepted one-page brief and its generator currently live only in Google Docs and ignored `raw/briefs/`. Promote the active source, document ID and reference manifest into the campaign home so another checkout/agent can discover them. Keep temporary exports and rejected versions in raw.

### 2. Research is used as an instruction store

`research/README.md:3` says research contains evidence, not instructions. But current creative direction, shoot lists, hooks, draft decks and campaign economics all live there. Global skills then direct agents to follow them.

**Repair:** separate evidence, approved decisions and current assignments. Preserve dated evidence under research; move live instructions into the appropriate section/account; archive rejected or superseded plans. A research author recommending a format is not the captain assigning that format.

### 3. Image writing and review contradict the latest house rules

- `sections/slideshows/rules.md:56-61` says choose gym/fitness pictures, not literal illustrations of each tip, and at most one treadmill per deck.
- `sections/slideshows/skills/write-script/SKILL.md:92` requires a photo that shows what the words say and caps face photos at two.
- `core/skills/review-images/SKILL.md:48` fails a photo that does not show the slide's text.
- `sections/slideshows/accounts/zoey/README.md:15-17` requires matching walking images and treats treadmills as the default after the faces are spent.

A writer can satisfy the current rules and be failed by the reviewer, or follow the account notes and repeat treadmills.

**Repair:** define the distinction between photo-level coherence with the account/deck and literal text illustration once. The reviewer should apply the calling section's policy, not enforce a universal slide-story policy. Express intentional account deviations under Overrides; remove superseded ones.

### 4. CTA rules conflict inside the writing/review path

- `rules.md:15-16` mandates final “GO GET THIS” plus the App Store bar.
- `write-script/SKILL.md:29` allows ending on the last useful slide.
- `review-script/SKILL.md:29` demands a value-adding ending, while `:36` demands the fixed CTA ending.
- `core/product.md:211-217` describes an unreleased app and profile/waitlist actions.

**Repair:** the product file owns release/access facts. The active campaign/section owns the ending and CTA. The reviewer checks the chosen contract, not competing endings. Verify release/access status before choosing the call to action; do not erase it by assumption.

### 5. Skeleton precedence is unresolved

`sections/slideshows/skeletons/README.md:8` locks the source slide count even for two/eight-slide formats. `rules.md:11-13` mandates five to seven and never eight; `review-script:38` fails exceptions; `hooks-and-formats/formats.md:3` says fit the format into house slots.

Skeletons also carry fixed image choices and hook templates that can conflict with gym-only imagery and captain-only hook permission. The source reference is not automatically permission to reuse that exact image on every deck.

**Repair:** distinguish a source-format description from an approved production specification. Before building, record the captain-approved adaptation and explicit exceptions. Preserve the source's mechanism without silently rewriting the hook or overriding house rules. Don't delete all skeletons: the ambiguity is in their application.

### 6. Captain hooks are not reliably verbatim

`sections/slideshows/hook-bank.md:3-7` describes spelling-normalized/cleaned text. `research/slideshow-formats-2026/captain-hooks.md` combines verbatim text, cleaned text and assistant-written ideas. `research/ugc-formats-2026/captain-picks.md` combines cleaned captain hooks, old format ideas and third-party frameworks.

**Repair:** one exact approved-hook bank with provenance. Keep original wording unchanged. Separate source inspiration and assistant ideas from approved copy; archive the prohibited assistant-written alternatives after preserving any useful research separately. Third-party hook taxonomies can stay as reference-only material.

### 7. Retired signature-prop rules remain active

`docs/adr/0004-reference-swap-images.md:3-7` retires signature props. `CONTEXT.md:43-44`, `core/workflows/new-account.md:6,9`, and account notes still define/enforce them.

**Repair:** remove the obsolete signature-prop setup requirement and glossary entry. Keep distinct account identity/master references. Natural per-scene accessories are different from mandatory signature props; describe that distinction only where needed.

### 8. Hayden is missing a required identity field

`reference-swap/SKILL.md:28,39` requires an account Identity line. Hayden's account file has Body and Makeup lines but no Identity line, unlike Zoey.

**Repair:** derive it from the approved master reference when image work resumes; do not invent it from prose. This is a concrete missing input, not a reason to add more universal rules.

### 9. Reference-swap's promise and requirements conflict

The skill says keep everything except the person, then requires changing outfit colours, adding multiple organic touches, and adding five to seven random objects on every slide (`:32,40-42,65`). These overlapping amendments no longer form one short stable edit contract. `review-images:27` simultaneously expects the original objects/scene to be unchanged.

**Repair:** state what is fixed and which bounded modifications are authorized. Consolidate the superseding object-touch rules rather than layering their counts. Preserve the captain's latest goal; do not choose a new object count without approval. Review allowed differences as allowed differences.

### 10. Spend approval happens after generation in the slideshow workflow

`make-slideshow.md:29` tells the agent to roll an image; `:30` then says ask before the first paid roll. AGENTS/reference-swap allow a bounded three-roll policy, whereas the workflow additionally requires first-deck approval.

**Repair:** put the spend gate before submission and define its owner once. Record the approved scope/cost, maximum rolls and exception conditions. Current wording can trigger unauthorized calls or redundant permission requests.

### 11. Image scripts bypass the written limits

`swap.py:23-25,76` permits arbitrary parallel roll counts and 2K/4K without an explicit exception gate. `batch.py` submits arbitrary sets; `fal_swap.py:73` runs every job concurrently. The skill says one at a time, another roll only after failure, and approval beyond three/1K.

**Repair:** retain one default image runner with enforced limits, output protection and truthful error status. Keep alternative providers only if actively needed, behind an explicit mode/approval gate; otherwise archive batch/fal experiments. No paid calls were made for this review.

### 12. Successful process exits do not necessarily mean images were generated

`swap.py` catches HTTP/no-image failures and prints them, then exits normally. `fal_swap.py` similarly returns FAIL strings without making the overall process fail. All three runners can overwrite destinations. `fal_swap.py` polls without a failure-state branch/deadline.

**Repair:** return structured per-item results, nonzero exit on failure, bounded polling and refusal to overwrite. Verify output files before a caller records success. These are real operational fixes, not documentation cleanup.

### 13. “No upscale” conflicts with actual finishing code

`ugc-finish/SKILL.md:33` forbids upscaling, but `finish.py:50-53` always resizes the short side to 1080, including smaller images; video scaling also forces that dimension.

The skill says always use Telegram but its command presents it as optional. The script can fall back to an unrelated existing bot/chat configuration. It treats local JPEG/H.264 settings as equivalent to a messaging-app round trip without this audit establishing that equivalence.

**Repair:** decide the intended output-size rule and encode it. Choose one explicit compression route, require explicit destination for external sends, and avoid fallback to an unrelated bot. Preserve original approved files; make finishing idempotence/overwrite behavior testable. No Telegram message was sent.

### 14. Reproducible setup is incomplete

The root manifest omits directly used image/export packages including Pillow and numpy; the brief generator also uses python-docx and PyMuPDF. They happen to be installed in the current environment. Root pytest is absent. Tool dependencies across environments are not clearly owned.

**Repair:** declare dependencies by the tools that require them and maintain a reproducible setup/smoke test. Keep the crawler's isolated environment: its existing tests passed. Don't merge every environment merely to simplify the directory tree.

### 15. The linter's green result does not verify policy consistency

`scripts/lint:101-103` skips research bodies; it only validates certain backticked paths, not ordinary Markdown links. It misses the 34 dead `.treehouse` links and every semantic contradiction above. `.pi` extension references to deleted image-prompt are not covered by the existing universal-file checks.

**Repair:** keep the linter, extend explicit link/runtime-path checks, and add small fixtures for rule IDs, overrides, skill aliases and retired-path references. Don't pretend a regex can prove creative policy coherence; that requires ownership and review.

### 16. Runtime instructions still point to retired tooling

`.pi/extensions/00-marketing-env.ts:25` advertises image-prompt and an old provider/default-quality route. That skill has already been removed from the working tree. The extension also hardcodes the original checkout rather than the active worktree.

`.pi/extensions/codex-image.ts` exposes an alternative image path that does not point to the reference-swap contract. Keep it only as a deliberate exception capability, not a competing default.

**Repair:** remove stale guidance and use the project/worktree root. Do not automatically remove browser/research tools solely because they are old: determine their active callers first. Review headed-login/rich-editor behavior against the captain's headless-agent preference; human-invoked tools can remain optional.

### 17. Mem0 documentation and tests describe the wrong engine

The project extension imports `/Users/johansardar/.local/share/firstmate-projects/local-memory.ts`, which launches the shared machine-level worker. `integrations/mem0-local/README.md:13,27` says no automatic capture and explicit-request-only storage. The active shared engine reports **autoCapture=true** and capture model `opencode-go/deepseek-v4.1-flash`.

**Repair:** choose one implementation owner. If the shared engine is intended, replace the repo-local implementation/README with a thin integration contract and tests of the actual hook. Archive the old standalone worker only after checking callers. Its 12 passing tests do not establish the behavior of the imported shared engine.

### 18. Memory is another competing rule store

Read-only triage of 291 project records found 23 containing imperative language, 13 with transient-execution indicators, 10 with numerical commercial terms, six mentioning retired tooling and one with old slide-four CTA language. Counts overlap. No exact normalized-text duplicate groups were found. These are triage flags: some records may be valid historical facts or records explicitly saying a tool was retired.

**Repair:** curate by meaning and provenance, not keywords. Move approved procedures to their canonical skill/section home; keep memory as a short fact/pointer. Remove resolved task state and replace superseded facts only after source verification. Automatic capture needs a quality/promotion gate if it is to remain enabled; changing fleet-wide settings is a separate approved action.

The always-loaded Hermes memories supplied to this session also contain unrelated nootropic/peptide/other-project operations and duplicate clean-username guidance. Do not delete useful personal facts just because ExcerLock doesn't need them. Scope project-specific operations to project context; deduplicate truly universal preferences; keep secret lookup metadata out of the everyday marketing prompt unless needed.

### 19. Global skills contain ExcerLock's campaign history

`~/.hermes/skills/marketing/ugc-creator-program/SKILL.md` embeds old formats, named accounts, historical pricing thresholds, compensation formulas, writer choices and one-off repair instructions. Generic workflows pay for this material and ExcerLock work can inherit stale instructions.

**Repair:** make the global capability short and reusable; put ExcerLock-specific policy, assignments and deal proposals in this repo. Split creative briefing from recruiting/commercial operations so a creative-only task doesn't load a commercial encyclopedia.

### 20. Global skill aliases inflate the discovery surface

The default-profile filesystem scan found **243 SKILL.md entries resolving to 194 distinct targets**. This includes aliases and archived paths and is not a verified runtime-loaded count. Examples: plan, writing-plans, coding-agent-delegation, computer-use and hermes-agent appear through flat and categorized paths.

**Repair:** audit discovery configuration and preserve one discoverable name per capability. Remove redundant aliases, not their shared canonical targets. Don't mass-delete unrelated global skills: they serve other projects and were not semantically audited here. Other profiles were not changed.

### 21. Logs are large generated views, not authoritative current policy

`log/LOG.md` is about 504 KB and `LOG-all.md` about 601 KB. Both are regenerated from events. The scheduled `com.excerlock.decision-log` launch agent is installed; removing the files without changing that generator will recreate them. The global session-decision-log skill duplicates implementation detail.

**Repair:** keep the event source and transcript history. Offer a small current-decision view plus an on-demand timeline. Put full generated views in ignored/cold output. A log entry reporting a decision isn't an alternative home for the operative rule.

### 22. Account/deck state is not systematically indexed

Zoey's index declares decks 03–05 dropped, but their files remain mixed with current work. Hayden's index is only a stub despite multiple deck folders. Two script files are byte-identical across accounts: Zoey 06 and Hayden 01 joke-tip-list.

**Repair:** maintain one small work index with active/draft/approved/posted/rejected/superseded states and post/artifact references. Archive abandoned deck directories after preserving decisions. Keep the duplicate's provenance as a recast/transfer record; don't assume identical text alone makes either creative asset disposable. Remove batch-specific reference bans/asides from account-wide rules and keep them with the batch.

### 23. Final assets and scratch are conflated

AGENTS assigns final images to gitignored assets folders with tracked assets.md manifests, but `make-slideshow.md:18` and `reference-swap:72` keep outputs in raw. Approved videos/briefs/reference manifests also remain in raw without a canonical project index.

**Repair:** raw is for downloads, experiments and temporary exports. Approved output belongs in the section's asset home with a tracked manifest, source/reference provenance, status and external post/doc IDs. Before reclaiming raw disk space, copy or reference approved outputs and necessary source evidence; don't blanket-delete raw.

## Removal and archive proposal

### Remove without losing useful content

- `untitled.md`: empty.
- Redundant generated log views from tracked/active context, after the generator is adjusted. Preserve events/transcripts.
- Redundant global discovery aliases, after confirming how the runtime discovers them. Preserve the canonical skill targets.
- Installed-tool caches/build products when regenerable. This is disk cleanup, not an agent-context fix.
- Old rejected brief exports and visual previews once the accepted source and reference/audit evidence have a durable home. Keep the current Google Doc generator until it is migrated.

### Archive from active routing

- `research/skeleton-pipeline-review.md` and `research/skeleton-pipeline-review-pi.md`: two proposal reports. Distill only accepted decisions; retain the reports cold.
- `research/ai-ugc-reference-first/audit.md`: audit of the retired JSON pipeline.
- `research/ai-ugc-reference-first/swap-method.md`: superseded one-image/old expression instructions.
- `research/ai-ugc-omni-notes.md`: old experiment recipe; notably includes video generation via the Gemini API, whereas current repo instructions restrict that key to images.
- `research/slideshow-formats-2026/top2.md` and `four-decks.md`: old assignments/CTA/image choices.
- `research/ugc-formats-2026/shoot-today.md`: an old broad shot list, not this two-format assignment.
- `research/ugc-formats-2026/jake-creator-plan-review.md`: historical commercial proposal, not agreed terms.
- Zoey decks 03–05: already marked dropped in the account index.
- Old `raw/briefs/gemini-rewrite/`, `gemini-simple/` and rejected pack iterations: not current briefs. Preserve unique audits/source evidence before deleting duplicated exports.
- Reference-swap batch/provider experiments if no active task needs them; otherwise bring them under the default runner's limits.

### Keep; don't throw away because it is long

- Dated competitor/creative evidence, organic/promoted distinctions and coverage limits.
- The 595-video source index/report and archived evidence.
- Captain-written hooks in exact original form.
- Account master references and final asset manifests.
- Approved/published creative and its provenance.
- The crawler integration, currently backed by 18 passing tests.
- `CLAUDE.md` as a thin AGENTS import.
- Existing `core/`, `accounts/`, `sections/` separation and skill-link tooling.

## Proposed small operating model

Keep the existing architecture and give each item one role:

1. **AGENTS.md:** short navigation, precedence, spend/publication guardrails and completion gates. No campaign script or historical narrative.
2. **core/product.md:** verified product behavior and separately labelled planned/unknown behavior. Put campaign positioning outside it.
3. **core/creative-rules.md:** universal creative permissions, principally exact captain hooks. No batch sizes or current video assignments.
4. **sections/<kind>/:** that deliverable's workflow, rules and active campaign/work index. Add a real-UGC home because that work is already happening; don't create empty sections for hypothetical programs.
5. **accounts/<name>/:** account identity, master references, voice and platform handles. Current account-specific output lives under the relevant section.
6. **research/:** dated evidence; nothing here is an active command. Use a short indexed summary for huge corpora and keep raw records searchable.
7. **history/archive:** superseded plans, old reviews, retired experiments and rejected output. Archive is excluded from skill discovery and default routing.
8. **memory:** short durable factual context or pointers. No duplicate rulebook, current task state or campaign contract.

Each active work item needs only: goal, assigned formats/count, approved exact copy, references, required/flexible parts, status, and source/final/post links. Do not add a heavy schema or mandatory paperwork to every one-off task.

## Recommended order

1. Reconcile active UGC/CTA/image/hook/asset/spend authority first. This stops new wrong work.
2. Promote accepted active sources out of raw; index real UGC and current deck status.
3. Archive the specific superseded plans and abandoned decks above; extract exact hooks.
4. Fix runtime routing, memory ownership and global skill scope. Curate memory records with source checks, not bulk keyword deletion.
5. Repair runner error/spend/output safeguards, dependencies and lint coverage.
6. Reclaim raw media/export space only after provenance and active assets are secured.

Do not start with a huge rewrite or delete every Markdown file. The goal is a small trustworthy active path, with useful history still retrievable.

## Residual limits

No historical external URL was freshly validated over the network. Media files and all 9.4 GB of raw contents were not individually inspected. No all-global-skills semantic audit was performed. Memory flags require individual adjudication before deletion. Third-party source claims and old claimed posting status were not independently re-proven. These limits do not weaken the concrete contradictory instructions identified above; they prevent calling every old file or memory safe to delete.
