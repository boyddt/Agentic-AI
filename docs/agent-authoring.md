# Authoring an Agent

## When a new agent is warranted

Add one when a request needs a competence no current specialist holds, and that
competence will recur. A one-off does not justify a profile.

Do not add an agent for a task an existing one already covers. Two agents with
overlapping scope will diverge, and the Owner will not know which produced a
given result.

## How agents are actually created here

Profiles are not written from general knowledge. The process runs through two
members (see [`routing.md`](routing.md#hiring)):

1. **PAX** writes a Role Research Report: what practitioners in the field do day
   to day, core hard and soft skills, tools and methods, what separates junior
   from senior, and the recurring hard parts of the job.
2. **Nolan** writes the profile from that report, files it, creates the output
   folder, and adds the member to the roster.

The research step is the one that matters. A profile written without it
describes the job as outsiders imagine it, and the agent reasons like an
outsider.

## Why every agent has a name

Each member has a name and a personality: Scout, FORGE, Mira, AXLE. This is
deliberate, not decoration.

- **The Owner addresses members directly.** "Send it to FORGE" is unambiguous;
  "send it to the document agent" is not, once there are sixteen.
- **Rules refer to members by name.** "Every job description goes to Scout and
  FORGE" and "FORGE owns the work history; SPARK never edits it" are routing
  rules that only work with stable names.
- **A persona carries judgment.** "Thinks like an interviewer who switched
  sides" and "constitutionally sceptical of anyone who profits from the
  recommendation" set how a member weighs evidence far more reliably than a
  list of adjectives.

## Profile structure

Every profile carries the same sections. The order matters; agents read top down
and the early sections set the frame for the rest.

```markdown
# NAME: Role

## Identity
Name, role, and a personality description written in terms of judgment,
not adjectives. "Unflinching about gaps" is actionable. "Detail-oriented"
is not.

## Background
The professional frame the agent reasons from. This is the section that
does the most work. An agent told to think like a senior technical
screener reads requirements differently than one told to be helpful.

## Core Skills
Specific competences, each with enough detail to be a decision rule.

## Responsibilities
The ordered workflow. What it receives, what it does, what it delivers.

## Working Rules
Numbered, absolute, and each one traceable to a real failure. This is
the section that gets consulted mid-run.

## Output Contract
Format, destination, naming convention, and what must accompany the
deliverable (gap report, score, format check).
```

## Writing rules that hold

**State the failure, not just the rule.** "No em dashes" gets rationalized away.
"No em dashes; they are a strong AI-writing signal, and the letters are scored by
AI detectors" does not.

**Make prohibitions enumerate their terms.** Agents match phrasing. List the
actual banned strings.

**Give every prohibition an alternative.** A rule that closes a door without
opening another produces either a refusal or a workaround. Neither is what you
wanted.

**Mark settled questions settled.** Otherwise they resurface every run.

## The output contract is not optional

Every specialist ends by delivering the artifact *and* a report of what it could
not do. An agent that may finish silently will finish silently, and a shortfall
that is never written down is a shortfall nobody sees.

Minimum contents:

- What is well covered
- What is inferred from adjacent evidence rather than stated directly
- What is genuinely absent and could not be closed honestly
- The score, and if below target, why the remainder is unreachable

## Testing a new agent

Run it against a case where the correct answer is "I cannot do this honestly."

Any agent will perform well on a request that matches its subject well. The
question is what it does when the honest answer is unflattering. An agent that
manufactures coverage under pressure will do the same thing on every run after,
and the failures will be harder to spot because the outputs look fine.
