---
name: wa-lessons-learned
description: Hard-won gotchas from working on the World Ablaze HOI4 mod — the mistakes that already cost someone a debugging session, and the protocol for recording new ones. Covers puppet/subject scope traps, file-scoped constants that are duplicated across files, the `# Fix NN:` changelog convention in railway code, doc drift, and the diagnose-before-fixing rule. Read this before debugging any AI misbehaviour or making a change whose correctness depends on who controls what, and append to it whenever a bug turns out to have a non-obvious cause. Most of these look like redundant or wrong code until you know the case they encode — check here before "simplifying" anything.
---

# Lessons learned

The catalogue lives in `references/lessons-log.md`. Read it when debugging; append to it when you learn something.

## Consulting the log without reading it — the `wa-lessons-reviewer` subagent

The log is ~1800 lines and grows with every fix. Reading it inline to check one decision spends
main-agent context on entries that do not apply. Instead, **before committing to a fix design, a
change to an existing system, or an analysis conclusion**, send the decision to the
`wa-lessons-reviewer` subagent (`.claude/agents/wa-lessons-reviewer.md`, read-only). Give it:

- the decision itself in 3–10 lines (what changes, where, why), including any claim you are
  making about the residual ("bounded", "rare", "self-heals") and any alternative you rejected;
- the names involved (system, effects/triggers, buildings, variables, `Fix NN`).

It returns a ≤40-line verdict: the lessons that apply with COMPLIES/CONFLICTS per entry, the
AGENTS.md (f)/(g) checks (bound-without-timeline, replaced proposal without refutation), the
two-states-of-one-object check, and the concrete actions required. Treat CONFLICT as blocking —
either change the design or write down why the lesson does not apply this time. Other agents
(Codex, non-Claude tools) do the same by reading that agent file as a checklist and running it
in whatever isolated context they have.

This is a **pre-commit** check, not a replacement for reading the log while diagnosing — when you
are debugging, you still read the entries the reviewer names.

## The five that come up most

**1. Puppet territory is not yours.** `every_controlled_state` iterates only states the country controls *directly* — subject/puppet land is controlled by the puppet. Any system that should cover an overlord's whole sphere must also walk `every_subject_country`. This is the single most repeated bug in the railway system.

**2. `@` constants are file-scoped, and some are deliberately duplicated.** `WA_AI_misc_on_actions.txt` redeclares the railway eligibility constants with a `# must match ...` comment. Changing one declaration and not the other is a silent behaviour split. Grep the constant name before editing it.

**3. `# Fix NN:` comments are a changelog, and later fixes revoke earlier ones.** `Fix 27` revokes `Fix 25`. Code that looks redundant is usually encoding a case that broke. Read the surrounding Fix comments before removing anything.

**4. Run a diagnostic before implementing a fix.** In this codebase the first hypothesis about an AI misbehaviour is usually wrong — control vs ownership, landmass boundaries, and subject scoping are subtler than they read. Confirm what the AI actually sees before changing what it does.

**5. Documentation drifts.** Docs here are authoritative for *design intent* but can be stale on *facts*. Verify version numbers, line references, and file lists against the source (`descriptor.mod`, the actual file) before relying on them.

## Recording a new lesson

Add an entry when the cause was **non-obvious** — something a careful reader of the diff would not have predicted. Skip it for ordinary bugs, typos, and anything already stated in `AGENTS.md` or `documentation/`.

Append to the end of `references/lessons-log.md` using this shape:

```markdown
### <short imperative title>

- **Date:** YYYY-MM-DD
- **Symptom:** what was observed
- **Cause:** what was actually happening
- **Rule:** what to do differently, stated so it applies beyond this one case
- **Evidence:** file:line, commit, or Fix number
```

Two things that make an entry worth having:

- **State the rule generally.** "Check `every_subject_country` when a system must cover an overlord's sphere" survives; "add subjects to the port search in railway_helpers line 593" does not.
- **Cite evidence.** An unsourced claim is unverifiable later, and the codebase moves. A `file:line` or a Fix number lets the next reader confirm it still holds.

If the lesson belongs to a system that has a doc in `documentation/`, put the durable rule in that doc **and** the incident here — the doc is what the next author reads, the log is what explains why.

If the lesson invalidates an existing entry, edit that entry rather than adding a contradicting one, and note the supersession.
