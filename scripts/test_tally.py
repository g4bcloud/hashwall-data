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


def _blocklist(root: Path):
    return json.loads((root / "data" / "blocklist.json").read_text(encoding="utf-8"))


def test_main_does_not_rewrite_an_unchanged_blocklist(tmp_path):
    # Regression: every scheduled run used to refresh `generated_at`, so the workflow committed
    # a timestamp-only change every hour.
    _write(tmp_path / "data" / "blocklist.json",
           {"version": 1, "generated_at": "1970-01-01T00:00:00Z", "threshold": 3, "count": 0, "numbers": []})
    before = (tmp_path / "data" / "blocklist.json").read_bytes()
    assert tally.main(["--root", str(tmp_path)]) == 0
    assert (tmp_path / "data" / "blocklist.json").read_bytes() == before


def test_main_writes_when_a_number_is_promoted(tmp_path):
    _write(tmp_path / "data" / "blocklist.json",
           {"version": 1, "generated_at": "1970-01-01T00:00:00Z", "threshold": 3, "count": 0, "numbers": []})
    for i in range(3):
        _write(tmp_path / "reports" / f"{i}.json", _report("+33123456789", f"u{i}"))
    assert tally.main(["--root", str(tmp_path)]) == 0
    result = _blocklist(tmp_path)
    assert result["numbers"] == ["+33123456789"] and result["count"] == 1
    assert result["generated_at"] != "1970-01-01T00:00:00Z"


def test_main_is_a_no_op_on_the_second_run(tmp_path):
    _write(tmp_path / "data" / "blocklist.json",
           {"version": 1, "generated_at": "1970-01-01T00:00:00Z", "threshold": 3, "count": 0, "numbers": []})
    for i in range(3):
        _write(tmp_path / "reports" / f"{i}.json", _report("+33123456789", f"u{i}"))
    tally.main(["--root", str(tmp_path)])
    after_first = (tmp_path / "data" / "blocklist.json").read_bytes()
    tally.main(["--root", str(tmp_path)])
    assert (tmp_path / "data" / "blocklist.json").read_bytes() == after_first


def test_main_creates_the_blocklist_when_missing(tmp_path):
    assert tally.main(["--root", str(tmp_path)]) == 0
    assert _blocklist(tmp_path)["numbers"] == []


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
