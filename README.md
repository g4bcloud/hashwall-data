# hashwall-data

The open side of **Hashwall**, an iPhone call blocker: the public spam lists, the pipeline that
builds them from community reports, and the legal pages. The Hashwall app itself is closed source.

Everything that decides which numbers end up on the community list is in this repository, so
anyone can check how a number got there.

## Status

Early development, not yet on the App Store. The community list is currently empty: it only
fills once the reporting path below actually accepts reports from the general public, which it
doesn't yet.

## What's here

| Path | What it is |
|---|---|
| `data/blocklist.json` | The community list the app downloads (built by the tally workflow) |
| `data/allowlist.json` | Numbers that are never added, however many reports they get |
| `data/catalog.json` | The "recommended lists" shown in the app |
| `data/lists/` | Lists maintained here |
| `reports/` | Spam reports, one small file per report (see *Privacy*) |
| `scripts/` | The intake and tally scripts, with tests |
| `.github/workflows/` | The automation that runs them |
| `docs/` | Privacy Policy, Terms, and the list format (published with GitHub Pages) |

## How a number joins the community list

1. A report arrives (see *Reporting*) and is validated by `scripts/ingest_report.py`.
2. `scripts/tally.py` counts **distinct reporters** per number. At **3 distinct reporters** the
   number is added to `data/blocklist.json`, unless it is in `data/allowlist.json`.
3. The app downloads `data/blocklist.json` through the jsDelivr CDN.

A reporter counts once per number, however many times they report it. Numbers on the allow list
are never added. This is not abuse-proof: someone can fake reporter ids. The threshold and the
allow list limit the damage, and the whole process is visible here.

## Publish your own list

Anyone can publish a list for Hashwall users to follow: a text or JSON file at an `https://`
address. See [docs/list-format.md](docs/list-format.md). Lists can only block numbers, and a
user's own Allow list always overrides them.

To suggest a list for the in-app catalog, open an issue or a pull request that edits
`data/catalog.json`. Describe any risk of blocking legitimate callers in the `caution` field.

## Reporting

The app opens a pre-filled GitHub Issue (labelled `spam-report`) instead of holding a GitHub
token itself. **This only works for people with write access to this repository today.** GitHub
requires permission to add a label before its `labels` URL query parameter takes effect, and
returns a 404 for the whole request otherwise ([GitHub's docs](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue#creating-an-issue-from-a-url-query)).
Because `ingest.yml` only processes Issues that already carry that label, an outside
contributor's attempt never reaches it, so this still doesn't accept public submissions. Fixing
that needs either a trigger that doesn't depend on a label, or the planned small server that
files reports on the person's behalf.

## Privacy

This repository is public, so reports are stored in a reduced form: the reported number, a
**one-way hash** of the reporter's random install id (never the id itself), and the **day** of the
report, not the time. See [docs/privacy.md](docs/privacy.md).

Do not report numbers that belong to people you know. To ask for a number to be removed or
protected, open an issue; allow-list entries are never added to the community list.

## Development

```bash
python3 scripts/test_tally.py     # list promotion rules
python3 scripts/test_ingest.py    # report intake and privacy rules
python3 scripts/tally.py --root . --check   # would the blocklist change?
```

Only the Python standard library is used, so the scripts run on a bare GitHub Actions runner.

## Licence

- Lists and other data (`data/`, `reports/`): [CC0 1.0](LICENSE-DATA), public domain dedication.
- Scripts, workflows and documentation: [MIT](LICENSE).

The legal pages in `docs/` are drafts and are not legal advice.
