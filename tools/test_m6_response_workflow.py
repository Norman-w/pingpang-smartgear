#!/usr/bin/env python3
"""End-to-end regression for the synthetic M6 waveform acceptance flow."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from analyze_m6_response import analyze_file
from validate_m6_response_batch import validate as validate_batch


class M6ResponseWorkflowTests(unittest.TestCase):
    def test_thirty_trial_csv_to_batch_gate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m6-response-workflow-") as directory:
            root = Path(directory)
            trace_path = root / "synthetic-5ms.csv"
            summary_path = root / "synthetic-5ms-summary.json"
            with trace_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["trial_id", "time_us", "reference", "sensor_npn"],
                )
                writer.writeheader()
                for trial_index in range(30):
                    trial_id = f"synthetic-{trial_index:02d}"
                    # Reference obstruction: 1000..6000 us (5000 us wide).
                    # Sensor response: rising edge 5000 us late, recovery 1000 us late.
                    writer.writerows(
                        [
                            {"trial_id": trial_id, "time_us": 0, "reference": 0, "sensor_npn": 0},
                            {"trial_id": trial_id, "time_us": 1000, "reference": 1, "sensor_npn": 0},
                            {"trial_id": trial_id, "time_us": 6000, "reference": 0, "sensor_npn": 1},
                            {"trial_id": trial_id, "time_us": 7000, "reference": 0, "sensor_npn": 0},
                        ]
                    )

            summary = analyze_file(trace_path, max_latency_us=10_000)
            summary_path.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result = validate_batch(
                summary_path,
                target_width_us=5_000,
                min_trials=30,
                max_latency_us=10_000,
            )

            self.assertEqual(summary["trial_count"], 30)
            self.assertEqual(summary["detected_count"], 30)
            self.assertEqual(result["trial_count"], 30)
            self.assertEqual(result["latency_us"], {"min": 1000, "median": 3000, "max": 5000})


if __name__ == "__main__":
    unittest.main()
