#!/usr/bin/env python3
"""Build/run the pure C++ business layer and validate emitted NetEvent JSON."""

from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BUILD = HERE / "build"
SCHEMA = REPO / "docs" / "net-event-v0.1.schema.json"
TRACE = HERE / "fixtures" / "net_trace_v0.1.csv"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(command))
    return subprocess.run(command, cwd=HERE, check=True, text=True)


def main() -> None:
    run(["cmake", "-S", ".", "-B", str(BUILD), "-DCMAKE_BUILD_TYPE=Debug"])
    run(["cmake", "--build", str(BUILD), "--parallel"])
    result = subprocess.run(
        [str(BUILD / "net_event_tests")],
        cwd=HERE,
        check=True,
        text=True,
        capture_output=True,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    events = []
    for line in result.stdout.splitlines():
        if not line.startswith("JSON_EVENT "):
            continue
        event = json.loads(line.removeprefix("JSON_EVENT "))
        validator.validate(event)
        events.append(event)
    if len(events) != 2:
        raise AssertionError(f"expected 2 schema events, got {len(events)}")
    invalid_height = dict(events[0])
    invalid_height["beam_mask"] = 0
    invalid_height["beam_height_mm"] = [10, 10]
    if validator.is_valid(invalid_height):
        raise AssertionError("schema must reject a nonzero height interval without beams")
    invalid_state = dict(events[1])
    invalid_state["state"] = "clean_over"
    if validator.is_valid(invalid_state):
        raise AssertionError("schema must reject clean_over without a beam hit")
    print(f"JSON_SCHEMA_OK ({len(events)} events)")

    trace_result = subprocess.run(
        [str(BUILD / "net_event_trace"), str(TRACE)],
        cwd=HERE,
        check=True,
        text=True,
        capture_output=True,
    )
    trace_events = []
    for line in trace_result.stdout.splitlines():
        if line.startswith("TRACE_EVENT "):
            event = json.loads(line.removeprefix("TRACE_EVENT "))
            validator.validate(event)
            trace_events.append(event)
    expected_states = ["clean_over", "touch_over", "touch_no_cross"]
    if [event["state"] for event in trace_events] != expected_states:
        raise AssertionError(
            "trace states mismatch: "
            f"{[event['state'] for event in trace_events]}"
        )
    if not trace_events[1]["net_touch"]["waveform_ref"].startswith("trace-wave-"):
        raise AssertionError("trace touch_over must retain an actual waveform reference")
    if trace_events[1]["net_touch"]["duration_us"] == 0:
        raise AssertionError("trace touch_over must retain waveform duration")
    invalid_touch_state = deepcopy(trace_events[1])
    invalid_touch_state["net_touch"]["triggered"] = False
    invalid_touch_state["net_touch"]["sensor_mask"] = 0
    if validator.is_valid(invalid_touch_state):
        raise AssertionError("schema must reject touch_over without touch evidence")
    invalid_height_step = deepcopy(trace_events[0])
    invalid_height_step["beam_height_mm"] = [15, 20]
    if validator.is_valid(invalid_height_step):
        raise AssertionError("schema must reject a height outside the 10 mm grid")
    invalid_height_order = deepcopy(trace_events[0])
    invalid_height_order["beam_height_mm"] = [40, 10]
    if validator.is_valid(invalid_height_order):
        raise AssertionError("schema must reject a descending height interval")
    invalid_gap = deepcopy(trace_events[0])
    invalid_gap["ball_bottom_gap_mm"] = [0, 20]
    if validator.is_valid(invalid_gap):
        raise AssertionError("schema must reject a gap outside the adjacent 10 mm interval")
    for lowest_height in range(10, 101, 10):
        valid_relation = deepcopy(trace_events[0])
        valid_relation["beam_height_mm"] = [lowest_height, 100]
        valid_relation["ball_bottom_gap_mm"] = [lowest_height - 10, lowest_height]
        validator.validate(valid_relation)
        invalid_relation = deepcopy(valid_relation)
        invalid_relation["ball_bottom_gap_mm"] = (
            [10, 20] if lowest_height == 10 else [0, 10]
        )
        if validator.is_valid(invalid_relation):
            raise AssertionError(
                "schema must tie ball_bottom_gap_mm to the lowest beam height"
            )
    invalid_touch_mask = deepcopy(trace_events[2])
    invalid_touch_mask["net_touch"]["triggered"] = False
    invalid_touch_mask["net_touch"]["sensor_mask"] = 1
    if validator.is_valid(invalid_touch_mask):
        raise AssertionError("schema must reject a false trigger with a nonzero sensor mask")
    invalid_touch_no_cross = deepcopy(trace_events[1])
    invalid_touch_no_cross["state"] = "touch_no_cross"
    if validator.is_valid(invalid_touch_no_cross):
        raise AssertionError("schema must reject touch_no_cross with a beam hit")
    invalid_event_id = deepcopy(trace_events[0])
    invalid_event_id["event_id"] = "not-a-uuid"
    if validator.is_valid(invalid_event_id):
        raise AssertionError("schema must reject a non-UUID event ID")
    print(f"TRACE_SCHEMA_OK ({len(trace_events)} events)")


if __name__ == "__main__":
    main()
