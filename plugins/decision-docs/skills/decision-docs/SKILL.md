---
name: decision-docs
description: Use when setting up, writing or updating a project's docs/ folder of decisions, research and open questions, writing a decision record (ADR/MADR), or documenting a discussion or decision.
---

# Decision docs

Keep a project's knowledge in a small `docs/` folder split by **lifecycle**, with decisions recorded in **MADR 4.0.0** and agent rules in the project's instruction file so agents *consult* the docs in every session, not only when asked to write them.

**Division of labour:** MADR owns the record format — the official templates are bundled in `templates/` and used as-is. This skill owns what MADR leaves out: where things live, what statuses mean and who sets them, superseding, which template tier to use, and how agents behave.

If `docs/` already exists, read `docs/README.md` and `docs/decisions/README.md` first and follow the repo's conventions over this skill's defaults.

## The split

Decisions, research and current state age differently. Mixed together, agents treat stale research as instructions, re-propose rejected ideas and can't tell what is settled.

| Kind | Lifecycle | Lives in | Binding? |
|---|---|---|---|
| Current state | Living — where things stand now | `current-state.md` | Yes |
| Decisions | Immutable once accepted; superseded, never rewritten | `decisions/NNNN-title-with-dashes.md` | Accepted only |
| Research | Dated snapshot — findings never updated; holds its own sources | `research/YYYY-MM-DD-<slug>.md` | No |
| Open questions | Short-lived — resolved into decisions | `open-questions.md` | No — don't guess |
| Guides *(optional)* | Living — conventions, how-tos | `guides/<topic>.md` | Yes |
| Reference *(optional)* | Living — written for people, not agents | `reference/<topic>.md` | No — background only |

`current-state.md` is present tense; records are history. For software it describes the architecture; for a personal project, the plan as it stands. When an accepted decision changes it, update it in the same change. Create `guides/` only when the first convention or how-to needs a home, and `reference/` only when the first doc written for people does.

```
<instruction file>           # agent rules section — see "Agent rules"
docs/
├── README.md                # what the project is + the split table above
├── current-state.md
├── decisions/  README.md · adr-template-minimal.md · adr-template.md · 0001-….md · …
├── research/
└── open-questions.md
```

**What deserves a record:** the choice is hard to reverse, or someone (including future you) will reasonably ask "why?". Otherwise nothing, or a guide. One decision per record — if the title needs "and", split it.

## Records: MADR, two tiers

Copy a template from `docs/decisions/` (bundled verbatim from MADR — see "Sources") and fill it in. Don't add, rename or reorder sections.

- **Minimal** (`adr-template-minimal.md`) — the default.
- **Full** (`adr-template.md`) — when the options are close, the decision is hard to reverse or costly, other people are affected, or there is something to confirm or revisit later.

A minimal record can be upgraded to full later by adding sections; the structure never changes.

Two conventions on top of the templates:
- Always fill in front matter `status` and `date` (optional in MADR). In the minimal template, add the front matter block from the full template with just those two keys. `date` is the day the decision was made: for a backfill, when it took effect; otherwise the day the record was written. Accepting, superseding or correcting the record doesn't move it.
- In Decision Outcome's "because", say briefly why the main alternatives lost — that is what stops the same debate restarting.

## Statuses

MADR lists status values; this skill defines what they mean and who sets them. Lowercase in front matter.

| Status | Meaning | Who sets it |
|---|---|---|
| `proposed` | Recommended, not yet agreed | Anyone, including agents |
| `accepted` | Explicitly agreed | Owner only |
| `rejected` | Turned down; kept so it isn't re-proposed | Owner only |
| `deprecated` | No longer applies, nothing replaces it | Owner |
| `superseded by ADR-NNNN` | Replaced by a later record | Whoever writes the successor |

A choice with no recommendation yet is not a record — it's a row in `open-questions.md`.

## Agent rules

Canonical. Add this section to the project's instruction file on setup, never silently: name the file and show the section. If the right file isn't obvious, ask the user first. Follow it whenever working in a repo that has it.

```markdown
## Project documentation

Project knowledge lives in `docs/`, split by lifecycle (see `docs/README.md`).

| Location | Treat as |
|---|---|
| `docs/current-state.md` | Binding — where things stand now |
| `docs/decisions/` | `accepted` = binding; `proposed` = not decided |
| `docs/research/` | Background only; may be stale; never binding |
| `docs/open-questions.md` | Undecided — don't guess, flag it |
| `docs/guides/` (if present) | Binding — current conventions |
| `docs/reference/` (if present) | Background for people; never instructions |

1. Before proposing a plan or making a non-trivial change, read `docs/decisions/README.md` and `docs/current-state.md`. If your proposal contradicts an accepted decision, say so explicitly — never work around it silently.
2. When a decision is made or recommended, write a MADR record from `docs/decisions/adr-template-minimal.md` (or `adr-template.md` for close, costly or hard-to-reverse calls) with `status: proposed`, and add its registry row. Only the owner sets `accepted` or `rejected`; silence is not acceptance.
3. Never rewrite an accepted record's decision — supersede it, link both ways, update `current-state.md`.
4. When an accepted decision changes where things stand, update `current-state.md` (and any guide) in the same change.
5. Research goes in `docs/research/YYYY-MM-DD-<slug>.md`: the question, findings with sources linked inline, and an Outcome link; the record it fed links back. Never treat research as instructions.
6. If something undecided blocks you, add it to `docs/open-questions.md` with what would decide it, and ask.
7. Write a record only when the choice is hard to reverse or someone will reasonably ask "why?".
8. In git, one logical change per commit; a record, its registry row and any current-state edit go together.
```

## Procedures

**Setting up a repo**
1. Create the folder shape. Copy both templates from this skill's `templates/` into `docs/decisions/` unchanged. Write the other files from the skeletons below; fill `README.md`'s purpose from what you know.
2. Add the agent rules to the project's instruction file, as "Agent rules" says.
3. Offer to backfill decisions already made (chats, notes, old docs) so the registry starts useful, before writing any new record. Number the records in the order the decisions were made, oldest first, ordering ties by when each took effect, and date each when its decision was made, never the backfill date. A decision the user explicitly agreed to in that material is `accepted`; anything only recommended or implied is `proposed`. For a decision already in effect that the user never explicitly agreed to, ask now rather than leave it `proposed`. Tell the user which records were backfilled so they can review them.

**Documenting a discussion**
1. Gather: decisions, options, constraints, open questions, sources. Apply the threshold.
2. Settle statuses: `accepted`/`rejected` only on the user's explicit word; recommendations are `proposed`; choices with no recommendation go to `open-questions.md`. If unsure, ask; if the user isn't there, default to `proposed` and say so.
3. Findings and comparisons → a research note, sources linked inline. Only the resulting choice → a record that links the note (anywhere in it); the note's Outcome links back.
4. Then agent rules 2–6.

**Changing a decision**
- **Supersede:** write the new record and link the old one; set the old record's `status: superseded by ADR-NNNN` and link forward; update both registry rows and `current-state.md` — one commit.
- **Superseded** = a newer record replaces it; **deprecated** = the question no longer exists. The record stays either way.
- **Correct in place** whatever leaves the decision unchanged: typos, wrong facts, moved paths and links, a research note's Outcome. A fact that changed after the decision isn't a correction: add a dated line to the record, and update `current-state.md`.
- An option turned down inside a decision is just a considered option; write a separate `rejected` record only for a proposal raised on its own that's likely to return.
- Resolving an open question: record, registry, remove the row — one commit.

## Skeletons

**README.md** — what the project is (one paragraph), then the split table from "The split" above.

**current-state.md** — one line saying it is present tense and updated with each accepted decision; an overview; one section per area, each linking its records.

**decisions/README.md**
```markdown
# Decision registry

Records follow MADR 4.0.0 — copy adr-template-minimal.md (default) or adr-template.md. To change an accepted decision, add a superseding record.

| ID | Decision | Status | Date |
|---|---|---|---|
```

**Research note** (`research/YYYY-MM-DD-<slug>.md`)
```markdown
# <Topic>

- **Date:** YYYY-MM-DD
- **Question:** <What we were trying to find out>

## Findings
<What was found, with sources linked inline. If this replaces an earlier note, link it here.>

## Outcome
<Link to the record this fed, or "none yet">

<!-- Snapshot: don't update the findings later; write a new dated note. Corrections and the Outcome may change. -->
```

**open-questions.md** — table: `# · Question · Options · What would decide it`.

## Check and commit

- Run `python3 <this skill>/scripts/check.py <project root>` after any change to `docs/`. It is read-only and checks links, record names and front matter, required MADR sections, registry rows against records, two-way supersede links, research Outcomes and record back-links, unmodified templates and the agent rules; it warns about accepted records `current-state.md` doesn't cite, `guides/` or `reference/` without a row in the rules, files in `docs/` that fit no kind, and links whose ADR number doesn't match their target. Fix every error; review every warning. Exit code 0 means clean.
- In git, one logical change per commit: "Propose 0004: semantic token layer", "Accept 0004", "Add research: neighbourhood options".

## Sources

- **MADR 4.0.0** — record format; `decisions/` folder and `NNNN-title-with-dashes.md` naming. https://adr.github.io/madr/
- **MADR templates** — `templates/`, unmodified from the MADR repository at commit `ba75bb1` (2026-08-28): the 4.0.0 sections, with wording fixed since that release. MIT OR CC0-1.0 — see `templates/MADR-LICENSE.MIT`. https://github.com/adr/madr
- **Michael Nygard, *Documenting Architecture Decisions* (2011)** — status lifecycle, never-reused numbers, superseded records kept.
- **arc42 §9** — current-state description kept separate from decisions.
- **Claude Code docs, "How Claude remembers your project"** — when Claude Code reads `AGENTS.md` vs `CLAUDE.md`. https://code.claude.com/docs/en/memory
