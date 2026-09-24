# New section

A section is one kind of marketing work (slideshows today; AI UGC, real UGC, clipping or influencer marketing later). Each one is a folder under `sections/` that can be deleted without breaking anything else.

1. **Create `sections/<name>/`** with a `README.md`: what the section makes, its files, which core skills it uses.
2. **Rules.** `sections/<name>/rules.md` for that section's house rules, each with an ID and a `Why:`. Don't copy rules from another section; if two sections truly share a rule, move it into `core/` and link it from both.
3. **Skills.** `sections/<name>/skills/<skill>/SKILL.md` for work only this section does. If a skill is useful to every section, put it in `core/skills/` instead and keep it free of section and account details.
4. **Workflows.** `sections/<name>/workflows/<workflow>.md`: the ordered steps, naming the skill for each step.
5. **Accounts.** `sections/<name>/accounts/<account>/README.md` for each account that posts here: overrides of this section's rules and the list of its work. Who the account is stays in `accounts/<account>/account.md`.
6. **Register the skills.** Run `scripts/link-skills` so Claude Code and Pi load them.
7. **Run `scripts/lint`.** The section may use `core/`, `accounts/`, `library/` and `research/`, but must never name another section, and `core/` must never name it.
