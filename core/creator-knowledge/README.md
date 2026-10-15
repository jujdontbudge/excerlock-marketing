# Creator knowledge base

Everything an agent needs to answer creators, and later to grade and edit their videos, without asking the captain again. It grows every time the captain answers a new question.

## Files
| File | What | Used for |
|---|---|---|
| `program.md` | The facts of the creator program: deal, pay, formats, accounts, warm-up, posting, rights, ending. Each fact has its source and date. | Any agent that talks to creators or writes creator docs |
| `faq.md` | Questions creators ask, with the captain-approved answer written to the creator. Each entry is `auto` (agents may send it) or `captain` (agents must escalate). | The inbox automation, DMs, emails |
| `quality.md` | What a good video looks like for each format, and the common mistakes. | Reviewing creator videos, giving feedback, future auto-grading and editing |

Voice for anything a creator reads: `core/writing-to-creators.md`.

## Authority
1. The captain's newest instruction wins.
2. Then the documents creators actually receive: the Google Docs and the signed contract, listed in `program.md` under "Sources".
3. Then this knowledge base.

Where a source disagrees with this base, the fact is marked **Open** in `program.md` and stays out of automatic replies until the captain settles it. Never pick a side yourself.

## Answering a creator
1. Split her message into separate questions.
2. Find each one in `faq.md`. A question is covered only if an entry clearly matches it and its status is `auto`.
3. **All questions covered:** reply using only those approved answers. You may join them and shorten them, and add a greeting and sign-off in the creator voice, but you must not add any new fact, number, promise or date.
4. **Anything not covered, `captain` status, Open, or about money or contract terms not answered in `faq.md`:** escalate to the captain with a suggested reply built from `program.md`, and mark which questions are new.

## Learning (keep this base growing)
Whenever the captain answers a creator's question, changes a term, or corrects an agent's reply:
1. Add or update the entry in `faq.md`: the question as creators phrase it (plus 1–3 other ways they might ask), his answer written to the creator, status `auto` unless he said to always check with him, the date, and where it came from.
2. If it changes a program fact, update `program.md` too, and add the old version to the entry's history line.
3. If the same answer is also an automatic-reply rule somewhere, keep the wording identical in both places.
Do this in the same session, before you finish. Why: the captain wants the automation to answer more questions every time he answers one, and an answer that isn't written down here is lost (2026-10-14).
