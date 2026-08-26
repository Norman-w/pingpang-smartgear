#!/usr/bin/env python3
"""Regression tests for the M6 physical channel-map validator."""

from __future__ import annotations

import copy
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from validate_m6_channel_map import main, validate


def pending_map() -> dict[str, object]:
    return {
        "schema_version": "m6-channel-map-v0.1",
        "calibration_id": "pending-calibration",
        "evidence_root": "evidence",
        "channels": [
            {
                "index": index,
                "height_mm": 10 + index * 10,
                "transmitter_id": f"TX-PENDING-{index:02d}",
                "receiver_id": f"RX-PENDING-{index:02d}",
                "output_bit": index,
                "status": "pending",
                "evidence": [],
            }
            for index in range(10)
        ],
    }


class M6ChannelMapTests(unittest.TestCase):
    def _write(self, record: dict[str, object], evidence: bool = False) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        if evidence:
            (root / "evidence").mkdir()
            (root / "evidence" / "channel-map.jpg").write_bytes(b"evidence")
        path = root / "channel-map.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def test_pending_ten_channel_map_passes(self) -> None:
        path = self._write(pending_map())
        self.assertEqual(validate(path), (0, 0, 10))

    def test_height_and_bit_bijection_are_required(self) -> None:
        record = pending_map()
        record["channels"] = copy.deepcopy(record["channels"])
        record["channels"][3]["height_mm"] = 50
        with self.assertRaisesRegex(ValueError, "height"):
            validate(self._write(record))

        record = pending_map()
        record["channels"] = copy.deepcopy(record["channels"])
        record["channels"][3]["output_bit"] = 4
        with self.assertRaisesRegex(ValueError, "duplicate output_bit"):
            validate(self._write(record))

    def test_pass_requires_existing_evidence(self) -> None:
        record = pending_map()
        record["channels"] = copy.deepcopy(record["channels"])
        record["channels"][0]["status"] = "pass"
        with self.assertRaisesRegex(ValueError, "requires evidence"):
            validate(self._write(record))

        record["channels"][0]["evidence"] = ["channel-map.jpg"]
        path = self._write(record, evidence=True)
        self.assertEqual(validate(path), (1, 0, 9))

    def test_cli_reports_invalid_map_without_throwing(self) -> None:
        path = self._write(pending_map())
        output = io.StringIO()
        with redirect_stdout(output):
            with patch.object(sys, "argv", ["validate_m6_channel_map.py", str(path)]):
                self.assertEqual(main(), 0)
        self.assertIn("M6_CHANNEL_MAP_OK", output.getvalue())


if __name__ == "__main__":
    unittest.main()
