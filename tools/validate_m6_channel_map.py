#!/usr/bin/env python3
"""Validate the physical-to-firmware map for the ten M6 beam channels.

The map is deliberately separate from the firmware schema: it records which
physical transmitter/receiver pair and which MCU bit produced each height.
It can contain pending rows before the hardware arrives, but a pass/fail row
must point at evidence that exists under the declared evidence root.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn


EXPECTED_CHANNELS = tuple(range(10))
EXPECTED_HEIGHTS = {index: 10 + index * 10 for index in EXPECTED_CHANNELS}
VALID_STATUSES = {"pending", "pass", "fail"}


def fail(message: str) -> NoReturn:
    raise ValueError(message)


def _non_empty_string(value: object, field: str, row: int) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"channel {row}: {field} must be a non-empty string")
    return value.strip()


def _evidence_path(map_path: Path, root_value: object, relative: object) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        fail("evidence entries must be non-empty relative paths")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        fail(f"evidence path must stay relative to evidence_root: {relative!r}")
    root = (map_path.parent / str(root_value)).resolve()
    evidence = (root / candidate).resolve()
    try:
        evidence.relative_to(root)
    except ValueError as error:
        raise ValueError(f"evidence path escapes evidence_root: {relative!r}") from error
    return evidence


def validate(map_path: Path) -> tuple[int, int, int]:
    """Return (pass_count, fail_count, pending_count) after validation."""

    try:
        record = json.loads(map_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"invalid JSON: {error}")
    if not isinstance(record, dict):
        fail("map root must be an object")
    if record.get("schema_version") != "m6-channel-map-v0.1":
        fail("schema_version must be m6-channel-map-v0.1")
    _non_empty_string(record.get("calibration_id"), "calibration_id", 0)
    evidence_root = record.get("evidence_root", "evidence")
    if not isinstance(evidence_root, str) or not evidence_root.strip():
        fail("evidence_root must be a non-empty relative directory")
    evidence_root_path = Path(evidence_root)
    if evidence_root_path.is_absolute() or ".." in evidence_root_path.parts:
        fail("evidence_root must stay relative to the map file")

    channels = record.get("channels")
    if not isinstance(channels, list) or len(channels) != len(EXPECTED_CHANNELS):
        fail("channels must contain exactly ten rows")

    seen_indices: set[int] = set()
    seen_bits: set[int] = set()
    seen_transmitters: set[str] = set()
    seen_receivers: set[str] = set()
    passed = failed = pending = 0

    for row_number, channel in enumerate(channels, start=1):
        if not isinstance(channel, dict):
            fail(f"channel {row_number}: row must be an object")
        index = channel.get("index")
        if not isinstance(index, int) or index not in EXPECTED_HEIGHTS:
            fail(f"channel {row_number}: index must be one of 0..9")
        if index in seen_indices:
            fail(f"channel {row_number}: duplicate index {index}")
        seen_indices.add(index)

        if channel.get("height_mm") != EXPECTED_HEIGHTS[index]:
            fail(
                f"channel {row_number}: index {index} must map to "
                f"height {EXPECTED_HEIGHTS[index]} mm"
            )

        output_bit = channel.get("output_bit")
        if not isinstance(output_bit, int) or not 0 <= output_bit < 10:
            fail(f"channel {row_number}: output_bit must be an integer from 0 to 9")
        if output_bit in seen_bits:
            fail(f"channel {row_number}: duplicate output_bit {output_bit}")
        seen_bits.add(output_bit)

        transmitter_id = _non_empty_string(
            channel.get("transmitter_id"), "transmitter_id", row_number
        )
        receiver_id = _non_empty_string(
            channel.get("receiver_id"), "receiver_id", row_number
        )
        if transmitter_id in seen_transmitters:
            fail(f"channel {row_number}: duplicate transmitter_id {transmitter_id!r}")
        if receiver_id in seen_receivers:
            fail(f"channel {row_number}: duplicate receiver_id {receiver_id!r}")
        seen_transmitters.add(transmitter_id)
        seen_receivers.add(receiver_id)

        status = channel.get("status", "pending")
        if status not in VALID_STATUSES:
            fail(f"channel {row_number}: status must be pending, pass, or fail")
        evidence = channel.get("evidence", [])
        if not isinstance(evidence, list):
            fail(f"channel {row_number}: evidence must be a list")
        if status in {"pass", "fail"}:
            if not evidence:
                fail(f"channel {row_number}={status} requires evidence")
            for relative in evidence:
                path = _evidence_path(map_path, evidence_root, relative)
                if not path.is_file():
                    fail(f"channel {row_number}: evidence file does not exist: {path}")

        if status == "pass":
            passed += 1
        elif status == "fail":
            failed += 1
        else:
            pending += 1

    if seen_indices != set(EXPECTED_CHANNELS) or seen_bits != set(EXPECTED_CHANNELS):
        fail("channels must cover every index and output bit exactly once")
    return passed, failed, pending


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("map", type=Path, help="M6 channel map JSON")
    args = parser.parse_args()
    try:
        passed, failed, pending = validate(args.map)
    except (OSError, ValueError, TypeError) as error:
        print(f"M6_CHANNEL_MAP_INVALID: {error}", file=sys.stderr)
        return 1
    print(
        "M6_CHANNEL_MAP_OK (10 channels, "
        f"pass={passed}, fail={failed}, pending={pending})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
