#!/usr/bin/env python3
"""Validate one repeated M6 shutter-width batch after waveform analysis.

This is intentionally a second gate after analyze_m6_response.py.  The
analyzer proves edge pairing for each trial; this tool proves that a chosen
target obstruction width was repeated enough times without misses or extra
edges.  It does not declare that the chosen width is the sensor's universal
minimum pulse width.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import NoReturn


def fail(message: str) -> NoReturn:
    raise ValueError(message)


def validate(
    summary_path: Path,
    *,
    target_width_us: int,
    width_tolerance_us: int = 250,
    min_trials: int = 30,
    max_latency_us: int | None = None,
) -> dict[str, object]:
    if target_width_us <= 0:
        fail("target_width_us must be positive")
    if width_tolerance_us < 0:
        fail("width_tolerance_us must be non-negative")
    if min_trials <= 0:
        fail("min_trials must be positive")
    if max_latency_us is not None and max_latency_us <= 0:
        fail("max_latency_us must be positive when supplied")

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"invalid analyzer JSON: {error}")
    if not isinstance(summary, dict):
        fail("analyzer summary root must be an object")
    if summary.get("schema_version") != "m6-response-v0.1":
        fail("unexpected analyzer schema_version")
    trials = summary.get("trials")
    if not isinstance(trials, list):
        fail("analyzer summary must contain a trials list")
    if len(trials) < min_trials:
        fail(f"expected at least {min_trials} trials, got {len(trials)}")

    latencies: list[int] = []
    for number, trial in enumerate(trials, start=1):
        if not isinstance(trial, dict):
            fail(f"trial {number}: row must be an object")
        width = trial.get("reference_width_us")
        if not isinstance(width, int) or abs(width - target_width_us) > width_tolerance_us:
            fail(
                f"trial {number}: reference width {width!r} is outside "
                f"{target_width_us}±{width_tolerance_us} us"
            )
        if trial.get("detected") is not True:
            fail(f"trial {number}: detected must be true")
        if trial.get("missed_edge_count") != 0:
            fail(f"trial {number}: missed_edge_count must be zero")
        if trial.get("extra_output_edge_count") != 0:
            fail(f"trial {number}: extra_output_edge_count must be zero")
        trial_latencies = trial.get("latencies_us")
        if not isinstance(trial_latencies, list) or not trial_latencies:
            fail(f"trial {number}: latencies_us must be a non-empty list")
        if not all(isinstance(value, int) and value >= 0 for value in trial_latencies):
            fail(f"trial {number}: latencies_us must contain non-negative integers")
        latencies.extend(trial_latencies)

    if max_latency_us is not None and any(value > max_latency_us for value in latencies):
        fail(f"latency exceeds configured limit {max_latency_us} us")

    result = {
        "schema_version": "m6-response-batch-v0.1",
        "summary_file": str(summary_path),
        "target_width_us": target_width_us,
        "width_tolerance_us": width_tolerance_us,
        "min_trials": min_trials,
        "trial_count": len(trials),
        "latency_us": {
            "min": min(latencies),
            "median": int(statistics.median(latencies)),
            "max": max(latencies),
        },
    }
    if max_latency_us is not None:
        result["max_latency_us"] = max_latency_us
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path, help="JSON from analyze_m6_response.py")
    parser.add_argument("--target-width-us", type=int, required=True)
    parser.add_argument("--width-tolerance-us", type=int, default=250)
    parser.add_argument("--min-trials", type=int, default=30)
    parser.add_argument("--max-latency-us", type=int)
    args = parser.parse_args()
    try:
        result = validate(
            args.summary,
            target_width_us=args.target_width_us,
            width_tolerance_us=args.width_tolerance_us,
            min_trials=args.min_trials,
            max_latency_us=args.max_latency_us,
        )
    except (OSError, ValueError, TypeError) as error:
        print(f"M6_RESPONSE_BATCH_INVALID: {error}", file=sys.stderr)
        return 1
    print(
        f"M6_RESPONSE_BATCH_OK (width={result['target_width_us']}us, "
        f"trials={result['trial_count']}, "
        f"latency_us={result['latency_us']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
