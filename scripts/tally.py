#!/usr/bin/env python3
"""
tally.py — promote community-reported numbers into the published blocklist.

Pipeline (runs in GitHub Actions, zero backend):
  1. Read every raw report in reports/*.json. Each report file is one submission:
         {"number": "+33123456789", "reporter": "<anon-uuid>", "ts": "<iso8601>"}
  2. Group reports by E.164 number, counting DISTINCT reporters (Sybil-dampening:
     one reporter can only count once per number).
  3. A number is promoted to data/blocklist.json when its distinct-reporter count
     reaches THRESHOLD, unless it appears in data/allowlist.json (override).
  4. Rewrite data/blocklist.json deterministically (sorted, stable) so diffs are
     clean and the file is auditable in git history.

Design notes:
  - No PII: reporter ids are opaque per-install UUIDs, never phone numbers / emails.
  - Deterministic output: numbers sorted ascending (also what the iOS Call
    Directory extension requires), so re-running with no new data is a no-op diff.
  - Backend-agnostic: this script only reads report files. Whether those files are
    produced by a GitHub Action parsing Issues, or later by a Cloudflare Worker
    committing them, is irrelevant here — the contract is reports/*.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# E.164: leading +, 8..15 digits, first digit non-zero.
E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")


def is_valid_e164(number: str) -> bool:
    return bool(E164_RE.match(number))


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_reports(reports_dir: Path) -> dict[str, set[str]]:
    """Return {number: {distinct reporter ids}} for all valid reports."""
    by_number: dict[str, set[str]] = defaultdict(set)
    if not reports_dir.exists():
        return by_number
    for report_path in sorted(reports_dir.glob("*.json")):
        try:
            data = load_json(report_path, None)
        except json.JSONDecodeError:
            print(f"skip (bad json): {report_path.name}", file=sys.stderr)
            continue
        records = data if isinstance(data, list) else [data]
        for rec in records:
            if not isinstance(rec, dict):
                continue
            number = str(rec.get("number", "")).strip()
            reporter = str(rec.get("reporter", "")).strip()
            if not is_valid_e164(number):
                print(f"skip (bad number): {number!r}", file=sys.stderr)
                continue
            if not reporter:
                print(f"skip (no reporter) for {number}", file=sys.stderr)
                continue
            by_number[number].add(reporter)
    return by_number


def tally(reports_dir: Path, allowlist: list[str], threshold: int) -> list[str]:
    """Return the sorted list of numbers that should be blocked."""
    allow = {n for n in allowlist if is_valid_e164(n)}
    by_number = collect_reports(reports_dir)
    promoted = [
        number
        for number, reporters in by_number.items()
        if number not in allow and len(reporters) >= threshold
    ]
    return sorted(promoted)


def build_blocklist(numbers: list[str], threshold: int) -> dict:
    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "threshold": threshold,
        "count": len(numbers),
        "numbers": numbers,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tally spam reports into the blocklist.")
    parser.add_argument("--root", default=".", help="Project root (contains data/ and reports/).")
    parser.add_argument("--threshold", type=int, default=None,
                        help="Override report threshold (default: value in blocklist.json or 3).")
    parser.add_argument("--check", action="store_true",
                        help="Exit non-zero if the blocklist would change (CI dry-run).")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    data_dir = root / "data"
    reports_dir = root / "reports"

    current = load_json(data_dir / "blocklist.json",
                        {"threshold": 3, "numbers": []})
    threshold = args.threshold or current.get("threshold", 3)
    allowlist = load_json(data_dir / "allowlist.json", {"numbers": []}).get("numbers", [])

    numbers = tally(reports_dir, allowlist, threshold)
    new_blocklist = build_blocklist(numbers, threshold)

    changed = numbers != current.get("numbers", []) or threshold != current.get("threshold")

    if args.check:
        print(f"{'CHANGED' if changed else 'unchanged'}: {len(numbers)} number(s) at threshold {threshold}")
        return 1 if changed else 0

    out_path = data_dir / "blocklist.json"
    # Leave the file alone when nothing changed. Rewriting it would only refresh `generated_at`,
    # which the scheduled workflow would then commit every hour for no reason.
    if not changed and out_path.exists():
        print(f"unchanged: {len(numbers)} number(s) at threshold {threshold}; file left as is")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(new_blocklist, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {len(numbers)} number(s) to {out_path} (threshold {threshold})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
