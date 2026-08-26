#!/usr/bin/env python3
"""Analyze reference-shutter and M6 NPN waveforms from a sampled CSV trace.

The tool intentionally reports hardware behavior; it does not turn a missed
edge into a pass and does not infer a minimum pulse width from a 5 ms response
claim.  Input CSV columns are: trial_id, time_us, reference, and the selected
output column (default: sensor_npn).  Boolean columns accept 0/1, true/false,
low/high.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_OUTPUT_COLUMN = "sensor_npn"


@dataclass(frozen=True)
class Sample:
    timestamp_us: int
    state: bool


@dataclass(frozen=True)
class Edge:
    timestamp_us: int
    previous: bool
    current: bool

    @property
    def direction(self) -> str:
        return "rising" if self.current else "falling"


def _parse_bool(value: str, *, row_number: int, column: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "high", "on"}:
        return True
    if normalized in {"0", "false", "low", "off"}:
        return False
    raise ValueError(
        f"row {row_number}: {column} must be 0/1 or true/false, got {value!r}"
    )


def read_trace(
    path: Path, *, reference_column: str, output_column: str
) -> dict[str, dict[str, list[Sample]]]:
    """Read a trace into trial -> signal -> samples, enforcing timestamps."""

    trials: dict[str, dict[str, list[Sample]]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")
        required = {"trial_id", "time_us", reference_column, output_column}
        missing = sorted(required - set(reader.fieldnames))
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(missing)}")
        for row_number, row in enumerate(reader, start=2):
            trial_id = (row.get("trial_id") or "").strip()
            if not trial_id:
                raise ValueError(f"row {row_number}: trial_id is empty")
            try:
                timestamp_us = int((row.get("time_us") or "").strip())
            except ValueError as error:
                raise ValueError(f"row {row_number}: time_us must be an integer") from error
            if timestamp_us < 0:
                raise ValueError(f"row {row_number}: time_us must be non-negative")
            trial = trials.setdefault(
                trial_id,
                {reference_column: [], output_column: []},
            )
            trial[reference_column].append(
                Sample(
                    timestamp_us,
                    _parse_bool(
                        row.get(reference_column) or "",
                        row_number=row_number,
                        column=reference_column,
                    ),
                )
            )
            trial[output_column].append(
                Sample(
                    timestamp_us,
                    _parse_bool(
                        row.get(output_column) or "",
                        row_number=row_number,
                        column=output_column,
                    ),
                )
            )

    if not trials:
        raise ValueError("CSV contains no data rows")
    for trial_id, signals in trials.items():
        for column, samples in signals.items():
            samples.sort(key=lambda sample: sample.timestamp_us)
            if any(
                left.timestamp_us == right.timestamp_us
                for left, right in zip(samples, samples[1:])
            ):
                raise ValueError(
                    f"trial {trial_id!r}, column {column!r}: duplicate timestamps"
                )
    return trials


def detect_edges(samples: Iterable[Sample]) -> list[Edge]:
    ordered = list(samples)
    if not ordered:
        return []
    edges: list[Edge] = []
    previous = ordered[0]
    for sample in ordered[1:]:
        if sample.state != previous.state:
            edges.append(Edge(sample.timestamp_us, previous.state, sample.state))
        previous = sample
    return edges


def _pair_edges(
    reference_edges: list[Edge], output_edges: list[Edge], max_latency_us: int
) -> tuple[list[dict[str, object]], set[int]]:
    output_index = 0
    pairs: list[dict[str, object]] = []
    used_output_indices: set[int] = set()
    for reference in reference_edges:
        while (
            output_index < len(output_edges)
            and output_edges[output_index].timestamp_us < reference.timestamp_us
        ):
            output_index += 1
        output: Edge | None = None
        matched_index: int | None = None
        candidate_index = output_index
        while candidate_index < len(output_edges):
            candidate = output_edges[candidate_index]
            latency_us = candidate.timestamp_us - reference.timestamp_us
            if latency_us > max_latency_us:
                break
            # A rising reference edge must pair with a rising output edge,
            # and likewise for falling edges.  Raw NPN signals are often
            # active-low; callers must opt into --invert-output instead of
            # allowing an opposite-polarity edge to look like a pass.
            if candidate.direction == reference.direction:
                output = candidate
                matched_index = candidate_index
                break
            candidate_index += 1
        if output is not None and matched_index is not None:
            used_output_indices.add(matched_index)
            output_index = matched_index + 1
        pairs.append(
            {
                "reference_time_us": reference.timestamp_us,
                "reference_direction": reference.direction,
                "output_time_us": output.timestamp_us if output else None,
                "output_direction": output.direction if output else None,
                "latency_us": (
                    output.timestamp_us - reference.timestamp_us if output else None
                ),
            }
        )
    return pairs, used_output_indices


def _width(edges: list[Edge]) -> int | None:
    if len(edges) < 2:
        return None
    return edges[1].timestamp_us - edges[0].timestamp_us


def analyze_trial(
    trial_id: str,
    signals: dict[str, list[Sample]],
    *,
    reference_column: str,
    output_column: str,
    max_latency_us: int,
    output_inverted: bool,
) -> dict[str, object]:
    reference_edges = detect_edges(signals[reference_column])
    output_samples = signals[output_column]
    if output_inverted:
        output_samples = [
            Sample(sample.timestamp_us, not sample.state)
            for sample in output_samples
        ]
    output_edges = detect_edges(output_samples)
    pairs, used_output_indices = _pair_edges(
        reference_edges, output_edges, max_latency_us
    )
    latencies = [
        int(pair["latency_us"])
        for pair in pairs
        if pair["latency_us"] is not None
    ]
    extra_output_edge_count = len(output_edges) - len(used_output_indices)
    detected = (
        bool(reference_edges)
        and len(latencies) == len(reference_edges)
        and extra_output_edge_count == 0
    )
    return {
        "trial_id": trial_id,
        "reference_edge_count": len(reference_edges),
        "output_edge_count": len(output_edges),
        "reference_width_us": _width(reference_edges),
        "output_width_us": _width(output_edges),
        "detected": detected,
        "missed_edge_count": len(reference_edges) - len(latencies),
        "extra_output_edge_count": extra_output_edge_count,
        "edge_pairs": pairs,
        "latencies_us": latencies,
    }


def _statistics(values: list[int]) -> dict[str, int] | None:
    if not values:
        return None
    return {
        "min": min(values),
        "median": int(statistics.median(values)),
        "max": max(values),
    }


def analyze_file(
    path: Path,
    *,
    reference_column: str = "reference",
    output_column: str = DEFAULT_OUTPUT_COLUMN,
    max_latency_us: int = 20_000,
    output_inverted: bool = False,
) -> dict[str, object]:
    if max_latency_us <= 0:
        raise ValueError("max_latency_us must be positive")
    trials = read_trace(
        path,
        reference_column=reference_column,
        output_column=output_column,
    )
    results = [
        analyze_trial(
            trial_id,
            signals,
            reference_column=reference_column,
            output_column=output_column,
            max_latency_us=max_latency_us,
            output_inverted=output_inverted,
        )
        for trial_id, signals in sorted(trials.items())
    ]
    latencies = [latency for result in results for latency in result["latencies_us"]]
    detected_count = sum(bool(result["detected"]) for result in results)
    return {
        "schema_version": "m6-response-v0.1",
        "input_file": str(path),
        "reference_column": reference_column,
        "output_column": output_column,
        "output_inverted": output_inverted,
        "max_latency_us": max_latency_us,
        "trial_count": len(results),
        "detected_count": detected_count,
        "missed_trial_count": len(results) - detected_count,
        "detection_rate": detected_count / len(results),
        "latency_us": _statistics(latencies),
        "trials": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="sampled waveform CSV")
    parser.add_argument("--output", type=Path, help="write JSON summary to this path")
    parser.add_argument("--reference-column", default="reference")
    parser.add_argument("--output-column", default=DEFAULT_OUTPUT_COLUMN)
    parser.add_argument(
        "--invert-output",
        action="store_true",
        help="invert a raw active-low NPN output before edge pairing",
    )
    parser.add_argument(
        "--max-latency-us",
        type=int,
        default=20_000,
        help="maximum allowed reference-to-output edge latency",
    )
    args = parser.parse_args()
    summary = analyze_file(
        args.input,
        reference_column=args.reference_column,
        output_column=args.output_column,
        max_latency_us=args.max_latency_us,
        output_inverted=args.invert_output,
    )
    rendered = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(
        f"M6_RESPONSE_ANALYSIS_OK ({summary['trial_count']} trials, "
        f"detected={summary['detected_count']}, "
        f"rate={summary['detection_rate']:.3f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
