#!/usr/bin/env python3
"""Tests for the non-destructive M6 acceptance-run initializer."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from init_m6_acceptance_run import build_run
from validate_m6_acceptance_bundle import validate as validate_bundle


class M6AcceptanceRunInitializerTests(unittest.TestCase):
    def test_creates_pending_bundle_and_channel_map(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m6-acceptance-run-") as directory:
            output_dir = Path(directory) / "run-01"
            result = build_run(output_dir)
            bundle_path = result["bundle_path"]

            self.assertTrue((output_dir / "channel-map.json").is_file())
            self.assertTrue(
                (output_dir / "evidence" / "carrier-integration-template.md").is_file()
            )
            expected_templates = {
                f"M6-waveform-template-{width_ms}ms.csv"
                for width_ms in (1, 2, 3, 4, 5, 6, 8, 10)
            }
            actual_templates = {
                path.name
                for path in (output_dir / "evidence").glob(
                    "M6-waveform-template-*.csv"
                )
            }
            self.assertEqual(actual_templates, expected_templates)
            for template in actual_templates:
                self.assertEqual(
                    (output_dir / "evidence" / template).read_text(encoding="utf-8"),
                    "trial_id,time_us,reference,sensor_npn,mcu\n",
                )
            readme = (output_dir / "evidence" / "README.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("八张空白 CSV 表头", readme)
            self.assertEqual(result["validation"]["overall_status"], "pending")
            self.assertEqual(
                result["validation"]["section_counts"],
                {"pass": 0, "fail": 0, "pending": 7},
            )
            self.assertEqual(validate_bundle(bundle_path)["overall_status"], "pending")

    def test_refuses_to_overwrite_non_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m6-acceptance-run-") as directory:
            output_dir = Path(directory) / "run-01"
            output_dir.mkdir()
            (output_dir / "keep.txt").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not empty"):
                build_run(output_dir)


if __name__ == "__main__":
    unittest.main()
