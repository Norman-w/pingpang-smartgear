#!/usr/bin/env python3
"""Regression tests for repeated M6 response-batch acceptance."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_m6_response_batch import validate


def summary(*, trials: int = 30, width_us: int = 5_000) -> dict[str, object]:
    return {
        "schema_version": "m6-response-v0.1",
        "trials": [
            {
                "trial_id": str(index),
                "reference_width_us": width_us,
                "detected": True,
                "missed_edge_count": 0,
                "extra_output_edge_count": 0,
                "latencies_us": [5_000, 1_000],
            }
            for index in range(trials)
        ],
    }


class M6ResponseBatchTests(unittest.TestCase):
    def _write(self, value: dict[str, object]) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "summary.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_repeated_target_width_passes(self) -> None:
        result = validate(
            self._write(summary()),
            target_width_us=5_000,
            max_latency_us=5_000,
        )
        self.assertEqual(result["trial_count"], 30)
        self.assertEqual(result["latency_us"]["median"], 3_000)
        self.assertEqual(result["latency_us"]["max"], 5_000)

    def test_missing_trial_fails_the_batch(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 30 trials"):
            validate(self._write(summary(trials=29)), target_width_us=5_000)

    def test_missed_edge_fails_the_batch(self) -> None:
        value = summary()
        value["trials"][7]["detected"] = False
        with self.assertRaisesRegex(ValueError, "detected must be true"):
            validate(self._write(value), target_width_us=5_000)

    def test_width_and_latency_limits_are_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside"):
            validate(self._write(summary(width_us=4_000)), target_width_us=5_000)
        with self.assertRaisesRegex(ValueError, "latency exceeds"):
            validate(
                self._write(summary()),
                target_width_us=5_000,
                max_latency_us=4_999,
            )


if __name__ == "__main__":
    unittest.main()
