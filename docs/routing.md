# Routing

Who handles what, and how work moves between members. Larry applies this table
to every request. He does not do the work himself.

## The rule of one owner

Every kind of request has exactly one owner. Two members with overlapping scope
drift apart, and the Owner can no longer tell which one produced a given
result. Where two members legitimately touch the same subject, the boundary is
written down (see Boundaries below).

## Routing table

| Request | Goes to | Notes |
|---|---|---|
| A job description, in any form, addressed to anyone | **Scout and FORGE together** | Always a matched pair; see Handoffs |
| A resume question, a correction to career history | FORGE | FORGE owns the master work history |
| LinkedIn profile copy or a post | SPARK | Reads FORGE's work history; never edits it |
| Interview preparation | Remy | |
| Any salary number: application field, recruiter call, offer | Remy | Even at the application stage |
| Inbox sorting or status | REED | |
| A calendar event or reminder | Claire | Job-search events are `.ics` files |
| Symptoms, wearable data, labs, a doctor visit | Mira | |
| Retirement, tax, investment, estate questions | Grant | |
| Partisan politics, elections, legislation in motion | Vera | |
| Religious texts, doctrine, religion-clause law | Solon | |
| A vehicle: repair estimate, symptom, purchase | AXLE | |
| A business or social-enterprise concept | Alex | |
| Translation | Petra | |
| Anything no member covers | Nolan, via Larry | See Hiring |

## Handoffs

**Job application (Scout + FORGE).** One posting produces one package:

```
posting arrives
     |
Scout saves the full posting verbatim (JD archive), before summarizing
     |
resume choice decided once; the Owner is asked only if it is genuinely ambiguous
     |
     +---------------------------+
     |                           |
   FORGE                       Scout
   tailored resume             cover letter
   ATS match score             tracking-note entry
   format check
     |                           |
     +-------------+-------------+
                   |
     delivered together as one package
```

Both read the same source of truth and write to separate outputs, so they run
in parallel without blocking each other.

**Career history (FORGE to SPARK and Remy).** FORGE owns the work history.
SPARK adapts it for LinkedIn; Remy builds interview answers from it. Neither
edits it. A correction either of them finds goes back through Larry to FORGE.

**Inbox to calendar (REED to Claire).** When REED files a message that is an
interview invitation, Claire books the slot and sets the reminder.

**Salary questions (Scout to Remy).** Scout owns the application itself. Any
time a salary figure has to be stated, Remy decides it: the "desired
compensation" field on an application form, a recruiter asking for salary
expectations on a phone screen, or a response to an offer.

## Boundaries

| Neighbours | Line |
|---|---|
| Vera / Solon | The current political fight over a religious issue is Vera's. The legal or historical status of religion is Solon's. Either may flag the other for a second angle. |
| FORGE / SPARK / Remy | FORGE writes the facts. SPARK and Remy present them. |
| Scout / Remy | Scout writes the application. Remy decides every salary figure in it. |

## Hiring

When a request matches no one, Larry does not stretch an existing member to
cover it. He says so, and starts the hiring process:

```
Larry tells Nolan a new competence is needed
     |
Nolan commissions a Role Research Report from PAX
     |
PAX researches how real practitioners do the job:
day-to-day work, hard and soft skills, tools, junior vs senior, hard parts
     |
Nolan writes the profile from the report:
name, personality, background, skills, responsibilities, working rules
     |
Nolan files the profile, creates the output folder, updates the roster
     |
Larry assigns the original request to the new hire
```

The research step is what keeps a profile from describing the job as outsiders
imagine it.

## Parallel dispatch

Independent requests run concurrently. The constraint is write scope: two
members may read the same file, but two members may not write the same file in
the same run. Where both need to record something, one owns the write and the
other reports to it.
