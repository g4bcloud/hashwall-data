---
title: Privacy Policy
---

# Privacy Policy

> **DRAFT / PLACEHOLDER.** This text describes how Hashwall is designed to work. It has not
> been reviewed by a lawyer and must be reviewed and completed (controller identity, contact
> address, legal basis, retention) before the app is published.

_Last updated: 2026-11-07_

## The short version

Hashwall has no accounts and no analytics. Your block, allow and name lists stay on your
iPhone. Hashwall does not read your contacts or your call history.

## What stays on your device

- The numbers and ranges you block, allow or name.
- The community spam list once it has been downloaded.

iOS, not Hashwall, performs the call blocking. Hashwall gives iOS a list of numbers; it never
sees your incoming calls.

## What leaves your device

**Downloading lists.** The app downloads the community list, and any other list you choose to
follow, from the web address of that list. The community list comes from the jsDelivr content
delivery network, which serves it from this project's public GitHub repository. Lists you add
come from whoever hosts them. Like any web request, this exposes your IP address to the host.
Hashwall sends no identifier with it. Lists are published by third parties; follow only lists
from people you trust.

**Reporting a spam number.** Reporting opens a pre-filled GitHub Issue on this project's public
repository; you tap "Submit new issue" there yourself to finish sending it. This is a deliberate
stopgap: Hashwall has no server of its own, and a token that could file Issues on your behalf
cannot safely live inside the app.

The pre-filled Issue contains:

- the reported phone number,
- a one-way hash of a random identifier generated on your device when you first use the app
  (hashed on your device before anything is sent; it cannot be turned back into the identifier),
  and
- the time of the report.

**This is not anonymous to GitHub.** Filing the Issue through your own GitHub account links that
submission to your account, the way any GitHub Issue does. Hashwall only controls what goes into
the Issue body, not what GitHub itself records about who filed it.

Once filed, a GitHub Action validates the Issue, writes a reduced record to this public
repository, and closes the Issue. What is kept there is deliberately minimal: the one-way hash
above and the **day** of the report, not the time, and not the Issue itself. The reported phone
number is published once enough different people report it. **Do not report numbers that belong
to people you know.**

> _Open: a planned second phase replaces this with a small server, so reporting no longer needs
> a GitHub account and is no longer tied to it. Also decide how people can ask for a number to be
> removed, and how the project handles phone numbers that belong to private individuals. Phone
> numbers linked to a person can count as personal data under the GDPR. This needs legal review._

## Purchases

The unlock is bought through the App Store. Apple processes payment; Hashwall never sees your
payment details. The app receives only a signed confirmation that a purchase happened.

To run the 30-day free trial, the app stores the date you first opened it on your device (in the
iOS Keychain, so reinstalling doesn't restart the trial) and reads the date you first downloaded
it from Apple's signed record. Neither leaves your device.

## Your choices

- Delete the app to remove all data stored on your device.
- Because what the project stores (a one-way hash and a day) can't be reversed, the project
  cannot tell which stored reports are yours from that data alone. If you reported through
  GitHub, the Issue you filed stays visible in your own GitHub account's history, like any
  GitHub Issue.
- [Contact placeholder: add address] to ask about removing a specific number from the public list.

## Children

Hashwall is not directed at children.

## Changes

Changes to this policy will be published on this page with a new date.

## Contact

[Contact placeholder: add email address]
