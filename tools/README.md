# inbox_sort.py

A rule-based IMAP inbox sorter. Reads headers only, classifies each message
against an ordered rule set, and files it.

## Why rules and not a model

The classification is deterministic and auditable. Every message that moves has
a stated reason, printed in the dry run and written to the log. When it files
something wrong you can point at the rule and fix it, which is not true of a
classifier that returns a confidence score.

The rules were derived from hand-classifying 136 real messages in one sitting.
That is the part that actually matters. Rules written from imagination cover the
cases you can picture, and an inbox is mostly cases you cannot.

## Safety properties

These are design commitments, not incidental behavior:

- **Unmatched mail stays in the inbox.** The sorter never guesses. Rule 11 is a
  deliberate destination, not a fallthrough.
- **Flagged mail is never moved.** A human marked it; that outranks every rule.
- **Nothing is permanently deleted.** The lowest-value bucket is Trash, which
  the provider retains on its own schedule.
- **Dry run is the default.** `--apply` is required before anything changes.
- **Security review runs first.** A message impersonating a known brand from an
  unrelated domain is quarantined for human review before any rule can file it
  as legitimate.

## Usage

```bash
python3 inbox_sort.py                  # dry run, shows the plan, moves nothing
python3 inbox_sort.py --apply          # execute
python3 inbox_sort.py --apply --quiet  # scheduled runs
```

## Configuration

Copy `config.example.ini` somewhere outside the repo, fill it in, and export
`INBOX_SORT_CONFIG` pointing at it. Credentials never live in the repository.

The contact tuples at the top of the script are intentionally empty. They hold
real names and vendor domains, which is personal data. Populate them locally.
Every rule that references them degrades to a no-op when the tuple is empty, so
the sorter runs correctly out of the box with reduced precision.

## The interesting rule

Rule 8, and rule ordering generally.

An applicant tracking system sends two very different things from the same
domain: automated acknowledgments, and messages typed by a human being. Filing
both into an "applications" folder buries the ones that need a reply.

So the sorter checks the subject for acknowledgment language first. Failing
that, it checks whether the subject reads like correspondence. Failing that, it
checks whether the sender's *display name* reads like a person rather than an
organization, using a marker list that catches "Acme Hiring Team" and
"no-reply" but not "Firstname Lastname".

A human writing through a tracking platform reaches the folder a human reads.

Rule order carries the same weight. Correspondence is checked *after*
applications, so an auto-acknowledgment beginning "Re:" does not trip the
human-reply test. It is checked *before* marketing, so a real reply is never
filed as bulk. Reordering those three rules silently changes the behavior of all
three.
