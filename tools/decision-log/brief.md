# Brief: add new events to the marketing decision log

## Goal
The captain owns ExcerLock, an app that locks the apps a user picks until they walk, hit a step goal or go to the gym. He is building a record of how he directs the marketing work: every task he gives, every decision, every correction he makes to work done by Hermes (his assistant) or its subagents, why he made it, and the rules that come out of it. Corrections of corrections must stay traceable as chains. The record will later be distilled into skills so more of the marketing can be automated. It must be precise about what he said and never invent reasons.

A watcher runs you every 30 minutes on whatever happened since the last run. Your job: turn the new transcript material into events and append them to the log, linked to the events already there.

## Input
- `{{DELTA}}`: new transcript lines since the last run, in time order across all sources. Each line starts with a reference like `[hermes-20260924_094051_9aaaf7#120 2026-09-24T09:45-05:00 user]`. Roles: `user` in a `hermes-…` source is the captain. `user` in a `claude-…` or `pi-…` source is usually the brief Hermes gave that agent, not the captain. `hermes` and `agent` are the assistants; `tool_call` and `tool_result` are actions and their (shortened) output. Lines starting `[IMPORTANT: Background process` are automatic notices, not the captain.
- `{{CONTEXT}}`: the existing rules, open questions and the last 60 events, so you can link to them and continue phases. The full log is `log/events.jsonl` if you need more.
- Tool calls and results in the delta are shortened. The full text is in the archive, which you can't open; work from the delta, and if a cut-off line matters, say so in the summary.

## Output
Write only to `{{OUT}}`: one JSON object per line. Do not touch any other file.

New events use ids from `{{NEXT_ID}}` upward, in time order. Fields:
- `id`, `time` (ISO time from the reference), `type`, `scope`, `phase`, `summary` (one plain sentence), `refs` (the source references it came from, e.g. `hermes-20260924_094051_9aaaf7#120`), `links` (ids of earlier events it answers, corrects, reverses or builds on).
- `captain_quote`: his exact words, typos kept, when the event came from him. Trim to the part that carries the decision if the message is long. Otherwise `null`.
- `why`: the reason he gave, in his words or a close paraphrase. `null` if he gave none. Never infer one.
- `actor`: `captain`, `hermes`, or the agent (e.g. `claude-437265ad`).
- For `correction`: also `was` (what had been done) and `now` (what replaced it).
- For `agent_run`: also `model`, `asked`, `produced`, `accepted` (`yes`, `no`, `partly` or `unknown`, based on what the captain later said).
- For `rule`: also `status` (`active`, `tentative`, `superseded`) and `written_in` (repo file where the rule is now written, or `null`). A rule's `links` are the events that produced it. When a later event changes a rule, write a new rule and supersede the old one with an update.
- For `open_question`: also `status` (`open` or `resolved`).

Types: `task` (he asks for something), `decision` (he picks between options or sets direction), `correction` (he rejects or changes work that was done), `agent_run` (a subagent was launched: what model, what it was asked, what it produced), `artifact` (a significant file or tool made or changed, only when it is an outcome worth finding later), `rule` (a general principle that came out of his decisions or corrections; one rule per principle), `open_question` (something he left unresolved or contradicted).

Updates to existing events: a line `{"update": "E042", "status": "superseded"}`. Allowed keys: `status`, `written_in`, `note`, `summary`, `links_add` (list of ids to add). Use this to supersede rules, resolve open questions and link a later correction back.

## Scope
Tag every event with one scope. The captain wants the main log to be purely about marketing work, with the rest filterable.
- `marketing`: the marketing itself. Research and sources, what counts as a hook or skeleton, tagging and grouping posts, formats, skeletons, scripts, images and styles, accounts and characters, the audience and niche, what gets made or posted, and the review of any of that.
- `workflow`: how marketing work gets done by agents, when it shapes output. Agent briefs and prompting rules, which model or agent does which marketing job, self-review, the review interface, this decision log.
- `tooling`: everything else. Orca tabs and terminals, browsers, model and effort settings, subscriptions and auth, crashes, "how are the agents doing" status checks, questions about how Hermes or other tools work, and the captain's complaints about those. Keep these events, but brief.

## Standards
- Every captain message in the delta that contains a task, decision or correction gets an event. Pure status questions and acknowledgements can be one short `tooling` or `task` event, or folded into a neighbour.
- Hermes's or an agent's own mistakes and fixes, tool failures and retries are not events unless the captain reacted to them; if he did, the event is his correction.
- Link generously but only to real ids. A correction always links to the event or run it corrects.
- Phases are short names for stretches of work ("Tagging TikToks", "Writing skeletons"). Continue the last phase from the context when the work continues.
- Never copy secrets, passwords, keys, emails or account logins; write `[REDACTED]`.
- If the delta has nothing worth logging, leave the output file empty.
- Plain English, short sentences.
