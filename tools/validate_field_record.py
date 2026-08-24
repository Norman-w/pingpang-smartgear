#!/usr/bin/env python3
"""Validate a field-validation record without turning missing hardware into a pass."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


REQUIRED_TEST_IDS = (
    "M-01", "M-02", "M-03",
    "B-01", "B-02", "B-03", "B-04", "B-05", "B-06", "B-07", "B-08", "B-09",
    "S-01", "S-02", "S-03",
    "T-01", "T-02", "T-03",
    "E-01",
)
SCHEMA = Path(__file__).resolve().parents[1] / "docs" / "field-validation-record-v0.1.schema.json"


def fail(message: str) -> "NoReturn":
    raise ValueError(message)


def validate_evidence_path(record_path: Path, evidence_root: str, relative: str) -> None:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        fail(f"evidence path must stay relative to evidence_root: {relative!r}")
    root = (record_path.parent / evidence_root).resolve()
    evidence = (root / candidate).resolve()
    try:
        evidence.relative_to(root)
    except ValueError as error:
        raise ValueError(f"evidence path escapes evidence_root: {relative!r}") from error
    if not evidence.is_file():
        fail(f"evidence file does not exist: {evidence}")


def validate(record_path: Path) -> tuple[int, int, int]:
    record = json.loads(record_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(record), key=str)
    if errors:
        fail("schema validation failed: " + "; ".join(error.message for error in errors))

    results = record["results"]
    if set(results) != set(REQUIRED_TEST_IDS):
        fail("results must contain exactly the M/B/S/T/E validation matrix IDs")

    passed = failed = pending = 0
    for test_id in REQUIRED_TEST_IDS:
        result = results[test_id]
        status = result["status"]
        evidence = result["evidence"]
        if status in {"pass", "fail"}:
            if not evidence:
                fail(f"{test_id}={status} requires at least one evidence file")
            for path in evidence:
                validate_evidence_path(record_path, record["evidence_root"], path)
        elif status == "not_applicable" and not result.get("notes", "").strip():
            fail(f"{test_id}=not_applicable requires notes")
        elif status == "pending":
            pending += 1

        if status == "pass":
            passed += 1
        elif status == "fail":
            failed += 1

    return passed, failed, pending


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        passed, failed, pending = validate(args.record)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FIELD_RECORD_INVALID: {error}", file=sys.stderr)
        return 1
    print(
        f"FIELD_RECORD_OK ({len(REQUIRED_TEST_IDS)} cases, "
        f"pass={passed}, fail={failed}, pending={pending})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
