# Integrations

The agents do real work against real systems. This page records each
integration, how it is wired, and the specific failures that shaped it.
Credentials, hosts, and account details never appear in the repository; every
integration reads them from local configuration at runtime.

| System | Member | Access | Direction |
|---|---|---|---|
| Mailbox (encrypted provider) | REED | IMAP through a local bridge | Read, move, flag |
| Google Calendar | Claire | Calendar API | Create, edit, list |
| Job-search calendar | Claire | None available; `.ics` import | Write via file |
| Note-taking app | Scout | Local REST API | Create folders and notes, update status |
| Word and Excel files | All | `python-docx`, `openpyxl` | Generate and update |
| Web pages | Scout, Mira | Browser automation, fetch | Read only |
| Public reference databases | Mira | HTTP APIs (e.g. NCBI dbSNP) | Read only |

---

## Mail: IMAP through a local bridge (REED)

Some encrypted mail providers offer no public IMAP server. A bridge application
runs on the local machine, decrypts mail, and exposes ordinary IMAP on the
loopback interface.

- **TLS:** the bridge presents a self-signed certificate. The client TLS context
  must disable hostname checking and certificate verification for the loopback
  connection, or the handshake fails.
- **Sequence order is not date order.** Fetching "the last 15 by sequence number"
  returns arbitrary dates. Parse the `Date` header and sort explicitly.
- **The UID arrives after the tuple.** In a `UID FETCH` response the UID element
  follows each `(header, body)` tuple instead of sitting inside it. Parse by
  looking ahead.
- **Ampersands break folder names.** IMAP folder names use modified UTF-7, where
  `&` is an escape character. A folder name containing `&` fails to create.
- **Scheduling:** the sorter runs from cron every 30 minutes and exits silently
  when the bridge is unreachable (closed, or the machine asleep), so a stopped
  bridge produces no noise.
- **Headers only.** The sorter never downloads message bodies.

See [`tools/`](../tools/) for the sorter itself.

## Calendar: API where possible, `.ics` where not (Claire)

General events go through the Google Calendar API. Job-search events live in a
calendar with no write API and no CalDAV, so the only route is a generated `.ics`
file the Owner imports. Getting RFC 5545 exactly right matters, because a
malformed file often fails silently or renders badly:

1. CRLF line endings.
2. Lines folded at 75 **octets**, not characters, continued with one leading space.
   Counting characters breaks on any non-ASCII text.
3. TEXT values escaped in order: backslash, semicolon, comma, newline. One
   unescaped comma truncates a description.
4. UTC (`Z`) timestamps, converted from local time with daylight saving applied,
   to avoid shipping VTIMEZONE blocks.
5. `TRANSP:TRANSPARENT`, so a reminder does not show the day as busy.
6. Reminders as `VALARM` blocks.

**Validate by reading the file back in binary mode.** Text mode converts CRLF to
LF on read and makes a correct file look broken.

## Application tracking: a local REST API (Scout)

Each application becomes one note, filed in a weekly folder.

- **The API token is read from the app's settings file at runtime**, never
  hardcoded. The app rotates it, and the same code runs on more than one
  machine (including under WSL, where the settings file lives on the Windows
  side and the host is found from the default route).
- **Folder lookup must paginate.** The folders endpoint returns pages. Checking
  only the first page misses the existing weekly folder, and the code then
  creates a duplicate. This happened several times before the lookup was fixed
  to follow `has_more` to the end.
- **Check before create, every time.** A folder is created only after a full
  paginated search finds nothing.

## Office documents (all members)

Owner-facing output is `.docx` and `.xlsx`, generated with `python-docx` and
`openpyxl`.

- **Scripts are written to a file and executed**, not piped through a shell
  heredoc. Python dict syntax inside a heredoc trips shell safety heuristics.
- **Page numbers are live fields.** Long living documents carry a "Page X of Y"
  footer built from `PAGE` and `NUMPAGES` field codes, so the count stays right
  as the document grows. Spreadsheets carry the equivalent `&P of &N` print
  footer on every sheet.
- **Rendered to PDF to verify.** A headless office suite renders the file, and
  the text is extracted to confirm the footer and layout, because `python-docx`
  alone cannot compute pagination.
- **Files open elsewhere are not written.** Before editing, check for the
  office suite's lock file. Writing a file the Owner has open means the Owner's
  next save silently discards the change.
- **Backup before bulk edits.** Every multi-file change is preceded by a copy
  of the originals.

## Web and reference data (read only)

- **Browser automation** reads pages the Owner is already signed in to (for
  example, a genetic-screening dashboard). It reads; it does not start paid
  reports, submit forms, or change settings without an explicit instruction.
- **Primary databases over summaries.** Mira checks a consumer report's variant
  identifiers against NCBI's public variation API before recording them, and
  records any place the report over-calls a finding.
