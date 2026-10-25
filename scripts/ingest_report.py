#!/usr/bin/env python3
"""
ingest_report.py: turn a 'spam-report' GitHub Issue body into a reports/ file.

Reads the issue body from the ISSUE_BODY env var (set by the workflow). The body
must be JSON: {"number": "+E164", "reporter": "<uuid>", "ts": "<iso8601>"}.

Privacy: this repository is PUBLIC, so what is written to reports/ is deliberately minimal.
  - the raw install id is never stored; only a one-way hash of it (enough to count
    distinct reporters, not enough to recover the id);
  - the time of the report is reduced to the day.
A stored report looks like: {"number": "+33...", "reporter": "<hash>", "day": "YYYY-MM-DD"}.

Validation:
  - number must be valid E.164 (reuses tally.is_valid_e164)
  - reporter must be present
One file per (number, reporter-hash) pair means a reporter re-reporting the same number is
naturally idempotent, which keeps the distinct-reporter tally honest.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tally  # noqa: E402

SAFE = re.compile(r"[^A-Za-z0-9_.+-]")
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}")


def sanitize(part: str) -> str:
    return SAFE.sub("_", part)


def pseudonymize(reporter: str) -> str:
    """One-way, stable id for a reporter. Truncated: it only has to distinguish reporters."""
    return hashlib.sha256(reporter.encode("utf-8")).hexdigest()[:32]


def to_day(ts: str) -> str:
    """Keep only the date part of a client-supplied timestamp; fall back to today (UTC)."""
    if DAY.match(ts):
        return ts[:10]
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def main() -> int:
    raw = os.environ.get("ISSUE_BODY", "").strip()
    # Issue templates may wrap the JSON in a code fence: strip it.
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[raw.find("{"): raw.rfind("}") + 1]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"invalid report JSON: {e}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("invalid report: expected a JSON object", file=sys.stderr)
        return 1

    number = str(data.get("number", "")).strip()
    reporter = str(data.get("reporter", "")).strip()
    day = to_day(str(data.get("ts", "")).strip())

    if not tally.is_valid_e164(number):
        print(f"rejected: bad E.164 number {number!r}", file=sys.stderr)
        return 1
    if not reporter:
        print("rejected: missing reporter id", file=sys.stderr)
        return 1

    hashed = pseudonymize(reporter)
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    out = reports_dir / f"{sanitize(number)}-{hashed}.json"
    out.write_text(
        json.dumps({"number": number, "reporter": hashed, "day": day}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"stored {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
