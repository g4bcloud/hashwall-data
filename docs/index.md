---
title: Hashwall
---

# Hashwall

An iPhone call blocker built around an open, auditable community spam list.

Hashwall blocks and identifies callers using lists you control: your own block, allow and
caller-name entries, plus any list you choose to follow. The built-in community list, and the
pipeline that decides which numbers go on it, are entirely public — in this repository, not
hidden inside the app.

The Hashwall app itself is closed source. Everything that affects which numbers the community
list blocks lives here instead, so anyone can check how a number got there.

## Why it's different

- **Nothing is blocked on a whim.** A number only joins the community list once several
  different people have reported it.
- **No black box.** The report-counting rules, the list itself, and every change to it are
  public git history — not a hidden server decision.
- **Your Allow list always wins.** Lists can only add numbers to block; nothing a list says can
  override a number you've allowed.

## Status

Hashwall is early in development and not yet on the App Store. The community list is empty, and
it stays empty until reports can come from the public. Reporting opens a pre-filled GitHub Issue,
but that only works for people with write access to the repository today. See the
[repository README](https://github.com/g4bcloud/hashwall-data#reporting) for the fix in progress.

## Price

Hashwall costs €1.99, paid once through the App Store. There is no subscription. Every new
install gets a 30-day free trial of the full app first. Blocking your own numbers and ranges is
free, with or without the purchase.

## Learn more

- [Privacy Policy](privacy)
- [Terms of Use](terms)
- [Publish your own list](list-format) for others to follow
- [The pipeline and public lists, on GitHub](https://github.com/g4bcloud/hashwall-data)
