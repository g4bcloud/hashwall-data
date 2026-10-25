#!/usr/bin/env python3
"""Unit tests for the tally pipeline. Run: python3 -m pytest scripts/test_tally.py -q"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tally  # noqa: E402


def _write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def _report(number, reporter, ts="2026-01-01T00:00:00Z"):
    return {"number": number, "reporter": reporter, "ts": ts}


def test_valid_e164():
    assert tally.is_valid_e164("+33123456789")
    assert tally.is_valid_e164("+1202555018")
    assert not tally.is_valid_e164("0123456789")   # no +
    assert not tally.is_valid_e164("+0123456789")  # leading zero after +
    assert not tally.is_valid_e164("+33 1 23")     # spaces
    assert not tally.is_valid_e164("")


def test_promotes_at_threshold(tmp_path):
    r = tmp_path / "reports"
    _write(r / "a.json", _report("+33123456789", "u1"))
    _write(r / "b.json", _report("+33123456789", "u2"))
    _write(r / "c.json", _report("+33123456789", "u3"))
    assert tally.tally(r, allowlist=[], threshold=3) == ["+33123456789"]


def test_below_threshold_not_promoted(tmp_path):
    r = tmp_path / "reports"
    _write(r / "a.json", _report("+33123456789", "u1"))
    _write(r / "b.json", _report("+33123456789", "u2"))
    assert tally.tally(r, allowlist=[], threshold=3) == []


def test_distinct_reporters_only(tmp_path):
    # same reporter 5 times must NOT reach threshold 3
    r = tmp_path / "reports"
    for i in range(5):
        _write(r / f"{i}.json", _report("+33123456789", "same-user"))
    assert tally.tally(r, allowlist=[], threshold=3) == []


def test_allowlist_override(tmp_path):
    r = tmp_path / "reports"
    for i in range(5):
        _write(r / f"{i}.json", _report("+33123456789", f"u{i}"))
    assert tally.tally(r, allowlist=["+33123456789"], threshold=3) == []


def test_output_sorted(tmp_path):
    r = tmp_path / "reports"
    for n in ("+33999999999", "+33100000000", "+33555555555"):
        for i in range(3):
            _write(r / f"{n}-{i}.json", _report(n, f"u{i}"))
    assert tally.tally(r, allowlist=[], threshold=3) == [
        "+33100000000", "+33555555555", "+33999999999",
    ]


def test_batched_report_file(tmp_path):
    # a single file may contain a list of reports (Action may batch)
    r = tmp_path / "reports"
    _write(r / "batch.json", [
        _report("+33123456789", "u1"),
        _report("+33123456789", "u2"),
        _report("+33123456789", "u3"),
    ])
    assert tally.tally(r, allowlist=[], threshold=3) == ["+33123456789"]


def test_bad_number_skipped(tmp_path):
    r = tmp_path / "reports"
    _write(r / "a.json", _report("not-a-number", "u1"))
    _write(r / "b.json", _report("+33123456789", "u1"))
    _write(r / "c.json", _report("+33123456789", "u2"))
    _write(r / "d.json", _report("+33123456789", "u3"))
    assert tally.tally(r, allowlist=[], threshold=3) == ["+33123456789"]


def test_build_blocklist_shape():
    bl = tally.build_blocklist(["+33123456789"], threshold=3)
    assert bl["count"] == 1
    assert bl["threshold"] == 3
    assert bl["numbers"] == ["+33123456789"]
    assert bl["generated_at"].endswith("Z")


# ---------------------------------------------------------------------------
# Stdlib fallback: run `python3 scripts/test_tally.py` with no pytest installed.
# pytest, if present, ignores everything below and uses its own tmp_path fixture.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import inspect
    import tempfile
    import traceback

    tests = [obj for name, obj in sorted(globals().items())
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for fn in tests:
        try:
            if "tmp_path" in inspect.signature(fn).parameters:
                with tempfile.TemporaryDirectory() as d:
                    fn(Path(d))
            else:
                fn()
            passed += 1
            print(f"PASS {fn.__name__}")
        except Exception:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
