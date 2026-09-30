# Agentic Orchestration

A 16-member agent team built on Claude Code. An orchestrator, Larry, routes every request to a named specialist with a defined scope, its own working rules, and a shared source of truth it is not permitted to contradict. The team covers job applications end to end (resume, cover letter, LinkedIn, interview prep, inbox triage, scheduling) plus health, finance, translation, and research work.

The interesting problem here is not generating documents. It is generating documents that are **verifiably true**.

## The problem

Give a language model a job description and a resume and ask it to tailor one to the other, and it will do it well. It will also, reliably, close the gaps. A posting asks for regression analysis, the candidate has statistics adjacent to it, and the model writes something that sounds close enough. Nobody instructed it to lie. It optimized for match score, which is what it was asked to do.

That output is worse than useless. It fails at the interview, where a candidate is asked to expand on a claim they cannot defend.

This system is built around that failure mode.

## The core idea: confirmed absence

Most systems track what a person **can** do. This one also tracks what they **cannot**, explicitly, as first-class data:

```markdown
**Not held, confirmed 2026-08-30: formal experiment design.**
No Design of Experiments, no ANOVA, no two-sample hypothesis testing.
The statistical quality control work listed above is control-chart and
process-capability methodology, which is real and fully claimable; it is
not experiment design. Never claim DoE, ANOVA, two-sample hypothesis
testing, or A/B test design. This is a confirmed absence, not a pending
question, so it does not need to be asked again.
```

A skills inventory that lists only strengths gives an agent no way to distinguish "not mentioned" from "does not exist," so it fills the silence. A confirmed absence makes the gap loud. It also records what *is* true nearby, so the agent has somewhere honest to go instead.

The last sentence matters as much as the rest. Without it, every run re-asks a question that was already settled.

## Architecture

```
                         Owner request
                              |
                            LARRY
                   routes, never executes
                              |
     +-----------+-----------+-----------+-----------+
     |           |           |           |           |
   SCOUT       FORGE       SPARK       REMY      REED, CLAIRE
   cover       tailored    LinkedIn    interview  inbox and
   letter +    resume +    copy        prep +     calendar
   intake      ATS check               pay        handoffs
     |           |           |           |
     +-----------+-----+-----+-----------+
                       |
                SOURCE OF TRUTH
       skills inventory + master work history
          (FORGE owns it; others read it)

   Other specialists: Mira (health), Grant (finance), Vera (politics),
   Solon (religious studies), AXLE (automotive), Alex (business
   analysis), Petra (translation)

   No specialist fits?  Larry -> NOLAN -> PAX researches the role
                        -> NOLAN writes the profile -> new hire
```

Larry holds no domain skill and produces no output. His only job is deciding who handles a request, and saying so. That constraint is what keeps specialist scope from blurring: an agent that can do everything gradually does everything badly.

When nobody on the team fits, Larry does not stretch someone. He tells Nolan (HR), who commissions a role research report from PAX and writes a new profile from it.

Specialists run to completion without mid-process check-ins. They are given a goal and the authority to choose their own steps, which is the line between an agent and an assistant. One FORGE run independently read the target requirements, scored a draft against them, revised, rescored, and stopped at 85% with a written explanation of why the remaining 15% could not be closed without fabricating. Nobody scripted those steps.

## The team

| Member | Role | Profile |
|---|---|---|
| Larry | Chief Orchestrator: routing, coordination, team-wide standards | [LARRY.md](agents/LARRY.md) |
| Nolan | HR Director: writes new member profiles | [NOLAN.md](agents/NOLAN.md) |
| PAX | Senior Researcher: role research for new hires | [PAX.md](agents/PAX.md) |
| Scout | Job Search Assistant: intake, cover letters, application tracking | [SCOUT.md](agents/SCOUT.md) |
| FORGE | Technical CV Specialist: tailored resumes, ATS checks, owns the work history | [FORGE.md](agents/FORGE.md) |
| SPARK | LinkedIn Presence Architect | [SPARK.md](agents/SPARK.md) |
| Remy | Interview Coach and Compensation Strategist | [REMY.md](agents/REMY.md) |
| REED | Email Manager: rule-based inbox triage | [REED.md](agents/REED.md) |
| Claire | Calendar Manager: events and RFC 5545 `.ics` generation | [CLAIRE.md](agents/CLAIRE.md) |
| Mira | Personal Health Advisor: living doctor-visit guides | [MIRA.md](agents/MIRA.md) |
| Grant | Personal Financial Analyst | [GRANT.md](agents/GRANT.md) |
| Vera | Political Analyst | [VERA.md](agents/VERA.md) |
| Solon | Religious Studies Scholar | [SOLON.md](agents/SOLON.md) |
| AXLE | Automotive Technical Representative | [AXLE.md](agents/AXLE.md) |
| Alex | Business Analyst (social enterprise) | [ALEX.md](agents/ALEX.md) |
| Petra | Language Translator | [PETRA.md](agents/PETRA.md) |

Every member has a name and a personality on purpose. A named member is easier to address directly and easier to hold to a scope, and the profiles are written in terms of judgment ("unflinching about gaps"), not adjectives ("detail-oriented").

## Design principles

Six of the core rules, each written after something went wrong. The full set of eleven, including the rules shared by the health, finance, politics, and automotive members, is in [`docs/design-principles.md`](docs/design-principles.md).

### 1. Never fabricate. Flag instead.

Missing data becomes a marked placeholder, not an invention:

```
Analyzed [INSERT: approximate record count] records across
[INSERT: environment] in a [INSERT: regulated/mission-critical] context.
```

The sentence is structurally complete and grammatically sound, so the document reads as finished. The bracket is unmissable. The agent never substitutes a plausible number for a real one.

### 2. Report the real score

FORGE targets 88-92% requirement match. When the honest ceiling is lower, it stops and says so, with the reason. A padded score is a lie that surfaces later, in a room, in front of a person who asks a follow-up question.

### 3. Delivered files are immutable

Once a document is handed over, it never changes without an explicit instruction. Not to fix a typo, not to close a gap discovered afterward, not to apply a style rule learned later.

This is counterintuitive and it is the rule agents most want to break. But the person may have already sent that document. A corrected copy that silently replaces it destroys their ability to know what the recipient actually read. Corrections flow to the source of truth and to the tracking log. The artifact stays frozen.

### 4. Read restrictions at their stated scope

A requirement that says "no AI tools during interviews" is a rule about interview conduct. It is not a signal that the organization dislikes AI, and it is not a reason to strip a genuine skill from the entire application.

This rule exists because the system did exactly that once, over-read a narrow constraint into a general stance, and quietly deleted a real and marketable qualification.

### 5. Verify factual claims against the primary source

Agents citing regulations, standards, or specifications check the actual text. A confidently wrong regulatory citation in a document is worse than no citation.

### 6. Every claim must survive a follow-up question

The final filter. If the subject could not answer "tell me more about that," the sentence does not belong in the document, regardless of how well it scores.

## Repository layout

| Path | Contents |
|---|---|
| `agents/` | All 16 team member profiles: identity, scope, working rules, output contract |
| `schemas/` | Every member's reference-file format, with illustrative data and an index |
| `docs/` | Architecture, routing between members, external integrations, design principles, and how a new agent is created |
| `examples/` | A worked requirement-intake document and gap report |
| `tools/` | REED's inbox sorter, with an example config |

## Status and scope

This is a working system, running daily. What is published here is the architecture and every agent's contract, with all personal data removed: no names of real people, no employers, no contact details, no credentials, and no health or financial specifics. The source-of-truth files are replaced by illustrative examples.

The design is domain-neutral. The problem it solves, generating tailored documents from a source of truth without drifting past what the source supports, is not specific to any one use case.

## License

MIT. See `LICENSE`.
