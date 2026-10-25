#!/usr/bin/env python3
"""Tests for the report intake. Run: python3 scripts/test_ingest.py (or pytest)."""

import contextlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ingest_report  # noqa: E402
import tally  # noqa: E402

RAW_ID = "0b1f6c3e-aaaa-bbbb-cccc-123456789abc"


def _run(body, workdir):
    """Run ingest_report.main() against ISSUE_BODY inside workdir; return (exit_code, stderr)."""
    old_cwd = os.getcwd()
    os.chdir(workdir)
    os.environ["ISSUE_BODY"] = body
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = ingest_report.main()
    finally:
        os.chdir(old_cwd)
    return code, err.getvalue()


def _stored(workdir):
    return [json.loads(p.read_text()) for p in sorted((Path(workdir) / "reports").glob("*.json"))]


def test_raw_install_id_is_never_stored():
    with tempfile.TemporaryDirectory() as d:
        body = json.dumps({"number": "+33123456789", "reporter": RAW_ID, "ts": "2026-10-25T13:51:06Z"})
        assert _run(body, d)[0] == 0
        files = sorted((Path(d) / "reports").glob("*.json"))
        assert len(files) == 1
        text = files[0].name + files[0].read_text()
        assert RAW_ID not in text and RAW_ID.replace("-", "") not in text


def test_time_of_day_is_dropped():
    with tempfile.TemporaryDirectory() as d:
        body = json.dumps({"number": "+33123456789", "reporter": RAW_ID, "ts": "2026-10-25T13:51:06Z"})
        _run(body, d)
        report = _stored(d)[0]
        assert report["day"] == "2026-10-25"
        assert "ts" not in report and "13:51" not in json.dumps(report)


def test_same_reporter_is_idempotent_and_distinct_reporters_count():
    with tempfile.TemporaryDirectory() as d:
        for rid in (RAW_ID, RAW_ID, "another-install-id", "third-install-id"):
            _run(json.dumps({"number": "+33123456789", "reporter": rid}), d)
        assert len(_stored(d)) == 3  # the repeated reporter did not add a file
        # and the tally promotes the number at the default threshold of 3 distinct reporters
        assert tally.tally(Path(d) / "reports", allowlist=[], threshold=3) == ["+33123456789"]


def test_hash_is_stable_and_not_the_input():
    assert ingest_report.pseudonymize(RAW_ID) == ingest_report.pseudonymize(RAW_ID)
    assert ingest_report.pseudonymize(RAW_ID) != RAW_ID
    assert len(ingest_report.pseudonymize(RAW_ID)) == 32


def test_rejects_bad_input():
    with tempfile.TemporaryDirectory() as d:
        assert _run("not json", d)[0] == 1
        assert _run("[1, 2]", d)[0] == 1
        assert _run(json.dumps({"number": "0123", "reporter": "x"}), d)[0] == 1
        assert _run(json.dumps({"number": "+33123456789"}), d)[0] == 1
        assert not (Path(d) / "reports").exists() or _stored(d) == []


def test_accepts_code_fenced_json():
    with tempfile.TemporaryDirectory() as d:
        body = "```json\n" + json.dumps({"number": "+33123456789", "reporter": RAW_ID}) + "\n```"
        assert _run(body, d)[0] == 0


def test_missing_timestamp_falls_back_to_today():
    with tempfile.TemporaryDirectory() as d:
        _run(json.dumps({"number": "+33123456789", "reporter": RAW_ID}), d)
        day = _stored(d)[0]["day"]
        assert len(day) == 10 and day[4] == "-" and day[7] == "-"


if __name__ == "__main__":
    import inspect
    import traceback

    tests = [f for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
