# Architecture

## Layers

```
  Owner request
     |
  Larry (orchestrator) ... routing only, no domain work, no output
     |
  Specialists ............ 15 named members, one competence each, run to completion
     |
  Source of truth ........ what is true; read constantly, written rarely
     |
  Artifacts .............. two kinds: delivered (frozen) and living (kept current)

  Beside the stack:
  Nolan + PAX ............ create a new specialist when no one fits
```

Each layer may read downward. Only an explicit correction step writes to the
source of truth, and nothing writes to a delivered artifact.

See [`routing.md`](routing.md) for who handles what, and
[`integrations.md`](integrations.md) for the external systems the specialists use.

## Why Larry does no work

Larry receives every request and performs none of them. He has one decision to
make: who handles this, or does no one.

This looks like overhead until an agent with broad permissions starts drifting.
An agent that *can* write the document, update the tracking log, and revise the
source of truth will eventually do all three in a single run, and the failure
will be invisible because the output still looks correct. Splitting routing from
execution keeps each specialist's blast radius the size of its actual job.

The second effect is honesty about staffing. When a request arrives that no
existing specialist covers, Larry cannot quietly absorb it. He has to say so.
That surfaces the gap instead of burying it in a mediocre result.

## How the team grows

A gap in coverage is filled by hiring, not by stretching:

1. Larry tells **Nolan** (HR) that a competence is missing.
2. Nolan commissions a **Role Research Report** from **PAX**: what practitioners
   in that field actually do day to day, their tools, what separates junior from
   senior, and the hard parts of the job.
3. Nolan writes the profile from that report: a name, a personality stated as
   judgment, a professional background to reason from, skills, responsibilities,
   and numbered working rules.
4. The new member gets an output folder and a line on the roster, and Larry
   assigns the original request.

The team now covers job applications, LinkedIn, interviews and pay, email,
calendar, health, personal finance, politics, religious studies, vehicles,
business analysis, and translation.

## Why specialists run unattended

A specialist receives a goal, not a procedure. It selects its own steps, uses
whatever tools it needs, and returns a finished result with a written account of
what it could not do.

Approval gates at every step feel safer and are not. They hide the agent's
reasoning behind a series of individually reasonable choices, and they turn
automation back into a conversation. A single review of a completed result,
paired with a mandatory gap report, surfaces more than a dozen mid-run
confirmations. The only permitted stops are genuine ambiguities where a wrong
guess would be expensive: an unclear resume choice, an unclear translation
register, an unclear appointment time.

The gap report is what makes this safe. An agent that must end by writing down
what it failed to cover cannot quietly paper over a shortfall.

## Source of truth

For the job-application members, two files hold everything a specialist may
assert about the Owner:

- **Skills inventory.** Capabilities, tools, depth, and explicit non-capabilities.
- **Work history.** Roles, dates, verified detail, resolved corrections, and open questions.

FORGE owns both. Scout, SPARK, and Remy read them and never contradict them.

Other members keep their own reference files on the same principle: Petra's
glossary of preferred terms, SPARK's record of approved live profile copy,
AXLE's garage file of every vehicle, Mira's tracking workbook for each person.

Three properties matter more than the content:

**Corrections land here, never in a delivered document.** A fact discovered after
delivery updates the source. The artifact that already went out stays as it was.

**Absences are recorded as loudly as strengths.** See `design-principles.md`.

**Resolved questions are marked resolved.** An open question left unmarked gets
re-asked every run, which trains the Owner to stop reading the questions.

## Two kinds of artifact

The system produces documents with opposite lifecycles, and each has its own
rule.

| | Delivered artifact | Living document |
|---|---|---|
| Examples | Resume, cover letter | Mira's doctor-visit guide and health synopsis |
| After handoff | **Frozen.** Never changes without an explicit instruction | **Updated the same day** new information arrives |
| A correction goes | To the source of truth and the tracking note | Into the document, in place |
| History kept by | `_v1`, `_v2` copies when a change is instructed | A dated change log inside the document |
| Why | The recipient already read a specific version | A stale version carried into an appointment is worse than none |

The difference is who reads it next. A resume's next reader is an employer who
already has a copy, so changing it destroys the record of what they saw. A visit
guide's next reader is a clinician at the next appointment, so it must always be
the current truth, and the change log is what makes a document that changes
trustworthy. Superseded wording in a living document is replaced, not struck
through, so no clinician acts on a finding that has since been withdrawn.

## Concurrency

Independent specialists run in parallel. FORGE (resume) and Scout (cover
letter) working the same request share a source of truth but write to separate
outputs, so neither blocks the other.

The constraint is write scope. Two agents may read the same file. Two agents may
not write the same file in the same run. Where both need to record something,
one owns the write and the other reports to it.

## Failure modes this design targets

| Failure | Mechanism |
|---|---|
| Fabricated capability | Confirmed-absence entries; every claim traced to source |
| Inflated match score | Honest ceiling reported with the reason, no padding |
| Silent artifact drift | Delivered files frozen; corrections go to source |
| Stale living document | Same-day updates, dated change log, in-place correction |
| Over-read constraint | Restrictions applied at stated scope only |
| Scope creep across agents | Larry routes; each specialist holds one competence |
| Coverage gap absorbed badly | No-fit requests go to Nolan and PAX, not to the nearest member |
| Anchoring on a first explanation | Alternatives listed before the leading one (Mira, Vera, Grant) |
| Misfiled important mail | Unmatched mail stays visible; human replies tested before bulk |
| Repeated settled questions | Resolved items marked resolved in the source |
