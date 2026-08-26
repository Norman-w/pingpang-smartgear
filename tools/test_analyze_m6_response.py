#!/usr/bin/env python3
"""Tests for the M6 waveform response analyzer."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from analyze_m6_response import analyze_file


class M6ResponseAnalyzerTests(unittest.TestCase):
    def _write_trace(self, rows: list[dict[str, object]]) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "trace.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["trial_id", "time_us", "reference", "sensor_npn"],
            )
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_detects_two_edges_and_reports_latency(self) -> None:
        path = self._write_trace(
            [
                {"trial_id": "pass", "time_us": 0, "reference": 0, "sensor_npn": 0},
                {"trial_id": "pass", "time_us": 1_000, "reference": 1, "sensor_npn": 0},
                {"trial_id": "pass", "time_us": 3_000, "reference": 1, "sensor_npn": 0},
                {"trial_id": "pass", "time_us": 6_000, "reference": 1, "sensor_npn": 1},
                {"trial_id": "pass", "time_us": 8_000, "reference": 0, "sensor_npn": 1},
                {"trial_id": "pass", "time_us": 9_000, "reference": 0, "sensor_npn": 0},
            ]
        )
        summary = analyze_file(path, max_latency_us=10_000)
        self.assertEqual(summary["trial_count"], 1)
        self.assertEqual(summary["detected_count"], 1)
        result = summary["trials"][0]
        self.assertTrue(result["detected"])
        self.assertEqual(result["reference_width_us"], 7_000)
        self.assertEqual(result["output_width_us"], 3_000)
        self.assertEqual(result["latencies_us"], [5_000, 1_000])

    def test_missing_edge_is_a_miss_not_a_zero_latency_pass(self) -> None:
        path = self._write_trace(
            [
                {"trial_id": "miss", "time_us": 0, "reference": 0, "sensor_npn": 0},
                {"trial_id": "miss", "time_us": 1_000, "reference": 1, "sensor_npn": 0},
                {"trial_id": "miss", "time_us": 2_000, "reference": 0, "sensor_npn": 0},
            ]
        )
        summary = analyze_file(path, max_latency_us=5_000)
        result = summary["trials"][0]
        self.assertEqual(summary["detected_count"], 0)
        self.assertFalse(result["detected"])
        self.assertEqual(result["missed_edge_count"], 2)
        self.assertIsNone(summary["latency_us"])

    def test_latency_limit_controls_pairing(self) -> None:
        path = self._write_trace(
            [
                {"trial_id": "slow", "time_us": 0, "reference": 0, "sensor_npn": 0},
                {"trial_id": "slow", "time_us": 1_000, "reference": 1, "sensor_npn": 0},
                {"trial_id": "slow", "time_us": 2_000, "reference": 0, "sensor_npn": 0},
                {"trial_id": "slow", "time_us": 7_000, "reference": 0, "sensor_npn": 1},
                {"trial_id": "slow", "time_us": 8_000, "reference": 0, "sensor_npn": 0},
            ]
        )
        summary = analyze_file(path, max_latency_us=2_000)
        self.assertEqual(summary["detected_count"], 0)
        self.assertEqual(summary["trials"][0]["missed_edge_count"], 2)

    def test_extra_output_edge_is_not_a_clean_detection(self) -> None:
        path = self._write_trace(
            [
                {"trial_id": "glitch", "time_us": 0, "reference": 0, "sensor_npn": 0},
                {"trial_id": "glitch", "time_us": 1_000, "reference": 1, "sensor_npn": 1},
                {"trial_id": "glitch", "time_us": 1_500, "reference": 1, "sensor_npn": 0},
                {"trial_id": "glitch", "time_us": 2_000, "reference": 0, "sensor_npn": 0},
                {"trial_id": "glitch", "time_us": 2_100, "reference": 0, "sensor_npn": 1},
            ]
        )
        summary = analyze_file(path, max_latency_us=5_000)
        result = summary["trials"][0]
        self.assertFalse(result["detected"])
        self.assertEqual(result["extra_output_edge_count"], 2)
        self.assertEqual(result["missed_edge_count"], 1)

    def test_active_low_output_requires_explicit_inversion(self) -> None:
        path = self._write_trace(
            [
                {"trial_id": "active-low", "time_us": 0, "reference": 0, "sensor_npn": 1},
                {"trial_id": "active-low", "time_us": 1_000, "reference": 1, "sensor_npn": 0},
                {"trial_id": "active-low", "time_us": 2_000, "reference": 0, "sensor_npn": 1},
            ]
        )
        raw_summary = analyze_file(path, max_latency_us=5_000)
        self.assertEqual(raw_summary["detected_count"], 0)
        self.assertFalse(raw_summary["trials"][0]["detected"])

        inverted_summary = analyze_file(
            path,
            max_latency_us=5_000,
            output_inverted=True,
        )
        self.assertEqual(inverted_summary["detected_count"], 1)
        self.assertTrue(inverted_summary["output_inverted"])

    def test_cli_writes_machine_readable_summary(self) -> None:
        path = self._write_trace(
            [
                {"trial_id": "cli", "time_us": 0, "reference": 0, "sensor_npn": 0},
                {"trial_id": "cli", "time_us": 1_000, "reference": 1, "sensor_npn": 1},
                {"trial_id": "cli", "time_us": 2_000, "reference": 0, "sensor_npn": 0},
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "summary.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("analyze_m6_response.py")),
                    "--input",
                    str(path),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("M6_RESPONSE_ANALYSIS_OK", result.stdout)
            summary = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(summary["schema_version"], "m6-response-v0.1")
            self.assertEqual(summary["detected_count"], 1)


if __name__ == "__main__":
    unittest.main()
