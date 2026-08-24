#!/usr/bin/env python3
"""Regression tests for the field evidence gate."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_field_record import validate


HERE = Path(__file__).resolve().parent
EXAMPLE = HERE.parent / "docs" / "field-validation-record.example.json"


class FieldRecordValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.record_data = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def write_record(self, directory: Path, data: dict) -> Path:
        path = directory / "record.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_pending_template_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="smartgear-field-record-") as directory:
            self.assertEqual(validate(self.write_record(Path(directory), self.record_data)), (0, 0, 19))

    def test_pass_requires_existing_evidence(self) -> None:
        data = json.loads(json.dumps(self.record_data))
        data["results"]["M-01"] = {"status": "pass", "evidence": []}
        with tempfile.TemporaryDirectory(prefix="smartgear-field-record-") as directory:
            with self.assertRaisesRegex(ValueError, "requires at least one evidence file"):
                validate(self.write_record(Path(directory), data))

    def test_pass_with_evidence_is_counted(self) -> None:
        data = json.loads(json.dumps(self.record_data))
        data["evidence_root"] = "evidence"
        data["results"]["M-01"] = {"status": "pass", "evidence": ["m01.jpg"]}
        with tempfile.TemporaryDirectory(prefix="smartgear-field-record-") as directory:
            root = Path(directory)
            (root / "evidence").mkdir()
            (root / "evidence" / "m01.jpg").write_bytes(b"evidence")
            self.assertEqual(validate(self.write_record(root, data)), (1, 0, 18))

    def test_evidence_cannot_escape_root(self) -> None:
        data = json.loads(json.dumps(self.record_data))
        data["evidence_root"] = "evidence"
        data["results"]["M-01"] = {"status": "pass", "evidence": ["../record.json"]}
        with tempfile.TemporaryDirectory(prefix="smartgear-field-record-") as directory:
            with self.assertRaisesRegex(ValueError, "relative to evidence_root"):
                validate(self.write_record(Path(directory), data))


if __name__ == "__main__":
    unittest.main()
