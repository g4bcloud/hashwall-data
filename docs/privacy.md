---
title: Privacy Policy
---

# Privacy Policy

> **DRAFT / PLACEHOLDER.** This text describes how Hashwall is designed to work. It has not
> been reviewed by a lawyer and must be reviewed and completed (controller identity, contact
> address, legal basis, retention) before the app is published.

_Last updated: 2026-10-11_

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

**Reporting a spam number (planned).** When you report a number, the app sends:

- the reported phone number,
- a random identifier generated on your device when you first use the app (it is not linked to
  you, your Apple ID or your phone number), and
- the time of the report.

Reports are published in a public repository, so what is stored there is reduced first: only
a one-way hash of the random identifier (it lets the project count how many different people
reported a number, and can't be turned back into the identifier) and the **day** of the report,
not the time. The reported phone number itself is published. **Do not report numbers that belong
to people you know.** A number is only added to the community list after several different
people report it.

> _Open: before reports go live, decide how people can ask for a number to be removed, and how
> the project handles phone numbers that belong to private individuals. Phone numbers linked to a
> person can count as personal data under the GDPR. This needs legal review._

## Purchases

Plans are bought through the App Store. Apple processes payment; Hashwall never sees your
payment details. The app receives only a signed confirmation that a purchase happened.

## Your choices

- Delete the app to remove all data stored on your device.
- Because reports are tied to a random identifier and not to you, the project cannot tell
  which reports are yours. [Contact placeholder: add address] to ask about removing a specific
  number from the public list.

## Children

Hashwall is not directed at children.

## Changes

Changes to this policy will be published on this page with a new date.

## Contact

[Contact placeholder: add email address]
