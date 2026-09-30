#!/usr/bin/env python3
"""
Rule-based inbox sorter for an IMAP mailbox.

Reads the inbox, classifies each message against an ordered rule set, and files
it. Anything that does not match a rule stays in the inbox, visible.

Usage:
    python3 inbox_sort.py                  # DRY RUN - shows the plan, moves nothing
    python3 inbox_sort.py --apply          # executes the moves
    python3 inbox_sort.py --apply --quiet  # for scheduled runs

The rules below were derived from hand-classifying 136 real inbox messages in a
single sitting, then reviewed. That matters more than it sounds: rules written
from imagination cover the cases you can picture, and inboxes are mostly cases
you cannot.

Safety properties, in order of importance:
  - Unmatched mail STAYS IN THE INBOX. The sorter never guesses.
  - Flagged/starred mail is never moved.
  - Nothing is permanently deleted. The lowest-value bucket is Trash, which the
    provider retains on its own schedule.
  - Dry run is the default. --apply is required before anything changes.

CONFIGURATION
    Copy config.example.ini, fill it in, and point INBOX_SORT_CONFIG at it.
    The contact lists below are intentionally empty. Populate them locally;
    they are personal data and do not belong in version control.
"""
import imaplib, ssl, email, re, sys, os, collections
from datetime import datetime
from email.utils import parsedate_to_datetime, parseaddr
from email.header import decode_header, make_header

# --- paths -----------------------------------------------------------------
# Credentials live outside the repo. Never inline them here.
CFG = os.environ.get('INBOX_SORT_CONFIG',
                     os.path.expanduser('~/.config/inbox_sort/connection.txt'))
LOG = os.environ.get('INBOX_SORT_LOG',
                     os.path.expanduser('~/.local/share/inbox_sort/sort.log'))

APPLY = '--apply' in sys.argv
QUIET = '--quiet' in sys.argv

# --- destination folders ---------------------------------------------------
# IMAP modified UTF-7: a literal '&' must be written '&-'
U      = 'Folders/Utilities &- Home'
ACTION = 'Folders/Job Search/Action Needed'
APPS   = 'Folders/Job Search/Applications'
RECR   = 'Folders/Job Search/Recruiters'
NEWS   = 'Folders/Newsletters'
PERS   = 'Folders/Personal'
VERIFY = 'Folders/Verify Before Acting'
UTIL_A, UTIL_B, UTIL_C = f'{U}/Provider A', f'{U}/Provider B', f'{U}/Provider C'
TRASH  = 'Trash'
STAY   = None   # sentinel: leave in inbox

# --- local personalization (populate these yourself) -----------------------
# Lowercase substrings matched against the sender display name or domain.
#
# Deliberately empty in the published version. These are real people and real
# vendors, which makes them personal data. The rules referencing them degrade
# gracefully to no-ops when the tuples are empty, so the sorter still runs.

NAMED_CONTACTS    = ()   # e.g. ('firstname lastname', 'firstname')
RECRUITER_NAMES   = ()   # e.g. ('firstname lastname',)
RECRUITER_DOMAINS = ()   # e.g. ('agencydomain.com',)
PRIORITY_DOMAINS  = ()   # senders routed to ACTION rather than RECRUITERS
SELF_ADDRESSES    = ()   # your own addresses, for self-sent notes
UTILITY_A_MATCH   = ()   # e.g. ('providerdomain.com', 'provider name')
UTILITY_B_MATCH   = ()
UTILITY_C_MATCH   = ()

# Domains whose branding is impersonated in phishing sent to this mailbox.
# A message claiming to be a known brand from an unrelated domain is not filed
# as legitimate; it is quarantined for human review.
SPOOFED_BRAND_DOMAINS = ()   # e.g. ('lookalike-domain.com',)

# --- classification data (safe to publish; these are public platforms) -----
ATS_DOMAINS = ('icims.com', 'greenhouse-mail.io', 'greenhouse.io', 'ashbyhq.com',
               'lever.co', 'myworkday.com', 'workday', 'smartrecruiters', 'jobvite',
               'taleo', 'workable', 'successfactors', 'jobs2web', 'applytojob',
               'recruiting.', 'bamboohr', 'jazzhr', 'paylocity')

APP_SUBJ = re.compile(
    r'thank you for (applying|your (recent )?(job )?application|your interest)'
    r'|application (received|submitted|confirmation|update)'
    r"|you'?ve started your job application|security code for your application"
    r'|sign-in link for your application|one-time password|finish your .* application'
    r'|your application to|candidate account verification|submittal confirmation'
    r'|received your application|update on your application'
    r'|please provide feedback on your application', re.I)

HUMAN_SUBJ = re.compile(
    r'^re:|^fwd:|^fw:|interview|next steps|phone conversation|phone screen'
    r'|process review|invitation:|updated invitation'
    r'|schedule|availability|offer letter|call with', re.I)

MARKETING_DOMAINS = ('linkedin.com', 'substack', 'mailchimp', 'canva',
                     'coursera', 'udemy')


def load_cfg(path):
    """Read a connection file exporting LABEL on one line and its value on the next."""
    lines = [l.strip() for l in open(path).read().splitlines() if l.strip()]
    keys = {'HOSTNAME', 'PORT', 'USERNAME', 'PASSWORD', 'SECURITY', 'IMAP', 'SMTP'}
    cfg, i = {}, 0
    while i < len(lines):
        k = lines[i].upper().rstrip(':=')
        if k in keys and i + 1 < len(lines) and lines[i + 1].upper().rstrip(':=') not in keys:
            cfg[k] = lines[i + 1]; i += 2
        else:
            i += 1
    return cfg


def dec(v):
    """Decode an RFC 2047 encoded header, falling back to the raw value."""
    try: return str(make_header(decode_header(v or '')))
    except Exception: return v or ''


# Organizational senders read like "Company @ platform", "Acme Hiring Team", or
# "no-reply". A real person reads like "Firstname Lastname". When someone writes
# THROUGH an applicant tracking system, the display name is the only signal that
# a human is on the other end, so this test decides whether their message gets
# buried in the applications pile or surfaced for a reply.
ORG_MARKERS = ('team', 'careers', 'recruiting', 'recruitment', 'talent', 'hiring',
               'no-reply', 'noreply', 'do not reply', 'notification', 'support',
               'inc', 'llc', 'corp', 'ltd', 'group', 'systems', 'solutions',
               'technologies', 'health', 'services', '@', 'via ')


def looks_like_person(name):
    """True when a display name reads like a personal name rather than an organization."""
    n = (name or '').strip()
    if not n or any(mark in n.lower() for mark in ORG_MARKERS):
        return False
    parts = [p for p in re.split(r'\s+', n) if p]
    if not 2 <= len(parts) <= 3:
        return False
    return all(p[:1].isupper() and p.replace('.', '').replace('-', '').isalpha()
               for p in parts)


def route(m):
    """Return (destination, reason). A None destination means leave it in the inbox.

    Order is load-bearing. Each rule assumes the ones above it already ran.
    """
    nm, addr, dom, subj = m['name'].lower(), m['addr'], m['dom'], m['subj']

    # 1. Never touch flagged mail. The user marked it; that outranks every rule.
    if m['flagged']:
        return STAY, 'flagged, left alone'

    # 2. Security review runs before anything can file a message as legitimate.
    if any(d in dom for d in SPOOFED_BRAND_DOMAINS):
        return VERIFY, 'known brand impersonation, unrelated domain'
    if re.search(r'recover|access to your', subj, re.I) and 'account' in subj.lower():
        return VERIFY, 'account recovery notice'

    # 3. Known people. Named senders always reach a human-visible folder.
    if any(r in nm for r in RECRUITER_NAMES):
        return RECR, 'known recruiter'
    if any(d in dom for d in PRIORITY_DOMAINS) or any(d in dom for d in RECRUITER_DOMAINS):
        return ACTION, 'known agency contact'
    if any(h in nm for h in NAMED_CONTACTS):
        return ACTION, 'known contact'

    # 4. Automated job alerts are noise, by explicit user ruling.
    if 'jobalerts-noreply@linkedin.com' in addr or 'job alert' in subj.lower():
        return TRASH, 'job alert'

    # 5. Utilities and household accounts, by sender.
    if any(x in dom or x in nm for x in UTILITY_A_MATCH):
        return UTIL_A, 'utility provider A'
    if any(x in dom or x in nm for x in UTILITY_B_MATCH):
        return UTIL_B, 'utility provider B'
    if any(x in dom or x in nm for x in UTILITY_C_MATCH):
        return UTIL_C, 'utility provider C'

    # 6. Self-sent notes.
    if addr in SELF_ADDRESSES:
        return PERS, 'self-sent'

    # 7. Recruiter outreach through a social platform.
    if 'inmail-hit-reply@linkedin' in addr or 'messages-noreply@linkedin' in addr:
        return RECR, 'recruiter outreach'

    # 8. Applications: tracking-system domains and acknowledgment language.
    #    A real person often writes THROUGH an applicant tracking system. If the
    #    subject reads as correspondence rather than an acknowledgment, treat it
    #    as a human reply so it is never buried in the applications pile.
    if any(x in dom or x in addr for x in ATS_DOMAINS) or APP_SUBJ.search(subj):
        if not APP_SUBJ.search(subj):
            if HUMAN_SUBJ.search(subj):
                return ACTION, 'correspondence via tracking platform'
            if looks_like_person(m['name']):
                return ACTION, 'named person writing via tracking platform'
        return APPS, 'application acknowledgment'

    # 9. Real correspondence. Checked AFTER applications so an auto-acknowledgment
    #    does not trip the "Re:" test, but BEFORE marketing so a human reply is
    #    never filed as bulk.
    if HUMAN_SUBJ.search(subj):
        return ACTION, 'human-reply pattern'

    # 10. Bulk mail.
    if m['bulk'] or any(x in dom for x in MARKETING_DOMAINS):
        return NEWS, 'bulk / marketing'

    # 11. Unknown stays visible. This is deliberate, not a fallthrough.
    return STAY, 'no rule matched'


def fetch_messages(M):
    """Return header-only dicts for every message in the inbox."""
    typ, d = M.uid('SEARCH', None, 'ALL')
    uids = d[0].split()
    if not uids:
        return []

    typ, data = M.uid('FETCH', b','.join(uids),
                      '(FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE LIST-UNSUBSCRIBE)])')
    msgs, i = [], 0
    while i < len(data):
        part = data[i]
        if not isinstance(part, tuple):
            i += 1
            continue
        uid = None
        if i + 1 < len(data) and isinstance(data[i + 1], (bytes, bytearray)):
            mm = re.search(rb'UID (\d+)', data[i + 1])
            uid = mm.group(1).decode() if mm else None
        fl = re.search(rb'FLAGS \(([^)]*)\)', part[0])
        flags = fl.group(1).decode() if fl else ''
        i += 1
        if not uid:
            continue
        e = email.message_from_bytes(part[1])
        nm, addr = parseaddr(e.get('From') or '')
        try: dt = parsedate_to_datetime(e.get('Date'))
        except Exception: dt = None
        msgs.append({'uid': uid, 'dt': dt, 'name': dec(nm),
                     'addr': (addr or '').lower(),
                     'dom': (addr or '').split('@')[-1].lower(),
                     'subj': dec(e.get('Subject')),
                     'bulk': bool(e.get('List-Unsubscribe')),
                     'flagged': '\\Flagged' in flags})
    return msgs


def print_plan(msgs, plan):
    mode = "APPLY" if APPLY else "DRY RUN"
    print(f"=== inbox sort [{mode}] - {len(msgs)} messages ===")
    for dest in sorted(plan, key=lambda x: (x is None, x or '')):
        label = dest.replace('&-', '&') if dest else 'STAY IN INBOX'
        print(f"\n  {len(plan[dest]):>3} -> {label}")
        for m, why in sorted(plan[dest], key=lambda r: r[0]['dt'] or datetime.min,
                             reverse=True)[:5]:
            dt = f"{m['dt']:%m-%d}" if m['dt'] else '??'
            print(f"      {dt} {m['name'][:26]:<26} {m['subj'][:44]}")
        if len(plan[dest]) > 5:
            print(f"      ... {len(plan[dest]) - 5} more")


def main():
    try:
        cfg = load_cfg(CFG)
    except FileNotFoundError:
        print(f"No connection config at {CFG}. "
              f"Copy config.example.ini and set INBOX_SORT_CONFIG.")
        return

    ctx = ssl.create_default_context()
    # A local mail bridge presents a self-signed certificate on loopback.
    # Only disable verification when the host is genuinely local.
    if cfg.get('HOSTNAME', '') in ('127.0.0.1', 'localhost', '::1'):
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    try:
        M = imaplib.IMAP4(cfg['HOSTNAME'], int(cfg['PORT']), timeout=15)
        M.starttls(ssl_context=ctx)
        M.login(cfg['USERNAME'], cfg['PASSWORD'])
    except (ConnectionRefusedError, OSError, imaplib.IMAP4.error, KeyError) as e:
        # The bridge is closed or the machine is asleep. Expected, not an error.
        if not QUIET:
            print(f"Mail server unreachable ({e}). Nothing done.")
        return

    M.select('INBOX', readonly=not APPLY)
    msgs = fetch_messages(M)
    if not msgs:
        if not QUIET: print("INBOX empty, nothing to sort.")
        M.logout(); return

    plan = collections.defaultdict(list)
    for m in msgs:
        dest, why = route(m)
        plan[dest].append((m, why))

    if not QUIET:
        print_plan(msgs, plan)

    if not APPLY:
        print("\nDRY RUN - nothing moved. Re-run with --apply to execute.")
        M.logout(); return

    moved = 0
    lines = [f"\n=== {datetime.now():%Y-%m-%d %H:%M} ==="]
    for dest, items in plan.items():
        if dest is STAY:
            continue
        ids = ','.join(m['uid'] for m, _ in items)
        typ, r = M.uid('MOVE', ids, f'"{dest}"')
        ok = (typ == 'OK')
        moved += len(items) if ok else 0
        line = f"  {'OK ' if ok else 'FAIL'} {len(items):>3} -> {dest.replace('&-','&')}"
        lines.append(line)
        if not QUIET: print(line)
    M.expunge()
    lines.append(f"  left in INBOX: {len(plan.get(STAY, []))}")
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a') as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass
    if not QUIET:
        print(f"\nmoved {moved}, left in INBOX {len(plan.get(STAY, []))}")

    M.logout()


if __name__ == '__main__':
    main()
