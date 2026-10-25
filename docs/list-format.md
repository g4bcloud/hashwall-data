---
title: List format
---

# Publishing a Hashwall list

Anyone can publish a list of spam numbers for Hashwall users to follow. A list is just a file
at an `https://` address, for example a file in a GitHub repository. People paste the address
into **Community → Add a list**. A normal GitHub file link
(`https://github.com/you/repo/blob/main/list.txt`) works.

Lists can only **block** numbers. They cannot allow numbers or set caller names, and a user's own
Allow list always wins.

## Text format

One entry per line. Lines that start with `+` are entries. `//` lines can carry optional details.
Anything else is ignored.

```text
// name: French telemarketing ranges
// description: Prefixes used for unsolicited calls
// maintainer: your-github-name

+33162000000        // one number
+3316212####        // a range: 10,000 numbers
```

## JSON format

```json
{
  "version": 1,
  "name": "French telemarketing ranges",
  "description": "Prefixes used for unsolicited calls",
  "maintainer": "your-github-name",
  "numbers": ["+33162000000"],
  "ranges": ["+3316212####"]
}
```

Hashwall's own `blocklist.json` is a valid list in this format.

## Begone files

Hashwall also reads the property-list (`.xml`/`.plist`) files used by the Begone app, so existing
Begone lists work as they are. Only entries with category `0` (block) are used. Titles and other
categories are ignored, because lists in Hashwall can't name callers.

## Rules

- Numbers are in international format with the country code: `+33162000000`.
- `#` is a wildcard digit and must come at the end. Up to 6 per entry (1,000,000 numbers).
- A list may contain up to 250,000 entries, be at most 8 MB, and cover at most 25 million numbers
  once overlapping entries are merged. Larger lists are rejected. (French lists are big: one
  telemarketing prefix such as `+33162######` alone is a million numbers.)
- Invalid entries are skipped, and the user is told how many.
- Names and descriptions are trimmed to 80 characters; control characters are removed.

## Be a good maintainer

- Only list numbers you have good reason to believe are unwanted. Wrongly blocking someone's real
  number has a cost, and users can unfollow lists that cause it.
- Say who you are and how people can report mistakes, for example in the repository README.
- Keep the address stable. Moving or deleting the file stops updates for everyone who follows it.
