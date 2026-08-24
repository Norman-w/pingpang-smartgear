#!/usr/bin/env python3
"""Correlate NetEvent timestamps with external replay markers.

This tool deliberately performs timestamp bookkeeping only. It does not read
video frames, infer ball height, or turn an external marker into a referee
decision.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TextIO


@dataclass(frozen=True)
class ExternalMarker:
    record_id: str
    timestamp_us: int
    source: str


def _parse_integer(value: object, label: str, *, nonnegative: bool) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be an integer")
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be an integer: {value!r}") from exc
    if nonnegative and parsed < 0:
        raise ValueError(f"{label} must be non-negative: {parsed}")
    return parsed


def _event_json_from_line(line: str, line_number: int) -> dict[str, object]:
    payload = line.strip()
    if payload.startswith("JSON_EVENT "):
        payload = payload.removeprefix("JSON_EVENT ")
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"events line {line_number} is not JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"events line {line_number} must contain a JSON object")
    if value.get("type") != "net_event":
        raise ValueError(f"events line {line_number} has an unexpected type")
    event_id = value.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        raise ValueError(f"events line {line_number} has no event_id")
    timestamp = _parse_integer(
        value.get("timestamp_us"),
        f"events line {line_number} timestamp_us",
        nonnegative=True,
    )
    value["timestamp_us"] = timestamp
    return value


def load_events(stream: TextIO) -> list[dict[str, object]]:
    """Load raw NetEvent JSONL or lines prefixed with ``JSON_EVENT``."""

    events: list[dict[str, object]] = []
    for line_number, line in enumerate(stream, start=1):
        if not line.strip():
            continue
        events.append(_event_json_from_line(line, line_number))
    return events


def load_external_markers(stream: TextIO) -> list[ExternalMarker]:
    """Load CSV rows with ``external_timestamp_us`` and optional metadata."""

    reader = csv.DictReader(stream)
    if reader.fieldnames is None or "external_timestamp_us" not in reader.fieldnames:
        raise ValueError("external CSV must contain external_timestamp_us")

    markers: list[ExternalMarker] = []
    for row_number, row in enumerate(reader, start=2):
        raw_timestamp = row.get("external_timestamp_us")
        timestamp = _parse_integer(
            raw_timestamp,
            f"external CSV row {row_number} external_timestamp_us",
            nonnegative=True,
        )
        record_id = (row.get("record_id") or f"row-{row_number}").strip()
        source = (row.get("source") or "external").strip()
        if not record_id:
            raise ValueError(f"external CSV row {row_number} has an empty record_id")
        markers.append(ExternalMarker(record_id, timestamp, source))
    return markers


def correlate(
    events: Iterable[dict[str, object]],
    markers: Iterable[ExternalMarker],
    *,
    external_offset_us: int = 0,
    window_us: int = 50_000,
) -> list[dict[str, object]]:
    """Return one correlation result per event.

    ``aligned_external_timestamp_us = external_timestamp_us +
    external_offset_us`` and ``delta_us = aligned - event``. A marker is a
    match when ``abs(delta_us) <= window_us``. Matches are deterministic:
    nearest delta first, then aligned timestamp and record ID.
    """

    offset = _parse_integer(
        external_offset_us, "external_offset_us", nonnegative=False
    )
    window = _parse_integer(window_us, "window_us", nonnegative=True)
    prepared = [
        (marker, marker.timestamp_us + offset) for marker in markers
    ]
    results: list[dict[str, object]] = []
    for event in events:
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event has no event_id")
        event_timestamp = _parse_integer(
            event.get("timestamp_us"),
            f"event {event_id} timestamp_us",
            nonnegative=True,
        )
        matches: list[dict[str, object]] = []
        for marker, aligned_timestamp in prepared:
            delta = aligned_timestamp - event_timestamp
            if abs(delta) <= window:
                matches.append(
                    {
                        "record_id": marker.record_id,
                        "source": marker.source,
                        "external_timestamp_us": marker.timestamp_us,
                        "aligned_external_timestamp_us": aligned_timestamp,
                        "delta_us": delta,
                    }
                )
        matches.sort(
            key=lambda item: (
                abs(int(item["delta_us"])),
                int(item["aligned_external_timestamp_us"]),
                str(item["record_id"]),
            )
        )
        results.append(
            {
                "event_id": event_id,
                "event_timestamp_us": event_timestamp,
                "external_offset_us": offset,
                "window_us": window,
                "matches": matches,
            }
        )
    return results


def _open_input(path: str) -> TextIO:
    if path == "-":
        return sys.stdin
    return Path(path).open("r", encoding="utf-8", newline="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Match NetEvent timestamps to external replay markers."
    )
    parser.add_argument("--events", required=True, help="NetEvent JSONL file, or -")
    parser.add_argument("--external", required=True, help="external marker CSV file")
    parser.add_argument(
        "--offset-us",
        type=int,
        default=0,
        help="add this offset to every external timestamp (default: 0)",
    )
    parser.add_argument(
        "--window-us",
        type=int,
        default=50_000,
        help="inclusive absolute matching window in microseconds (default: 50000)",
    )
    args = parser.parse_args(argv)

    try:
        with _open_input(args.events) as events_stream:
            events = load_events(events_stream)
        with _open_input(args.external) as external_stream:
            markers = load_external_markers(external_stream)
        results = correlate(
            events,
            markers,
            external_offset_us=args.offset_us,
            window_us=args.window_us,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for result in results:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
