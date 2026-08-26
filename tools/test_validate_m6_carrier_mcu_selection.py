#!/usr/bin/env python3
"""Tests for the M6 carrier MCU selection gate."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_m6_carrier_mcu_selection import validate


HERE = Path(__file__).resolve().parent
EXAMPLE = HERE.parent / "hardware/electronics/m6-capture-carrier-mcu-selection.example.json"


class M6CarrierMcuSelectionTests(unittest.TestCase):
    def load_example(self) -> dict[str, object]:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def write_selection(self, data: dict[str, object], directory: str) -> Path:
        path = Path(directory) / "selection.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_pending_selection_is_explicitly_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="smartgear-mcu-selection-") as directory:
            result = validate(self.write_selection(self.load_example(), directory))
        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["selected_mcu"], "STM32G031K8U6")
        self.assertEqual(result["gate_counts"], {"pass": 0, "fail": 0, "pending": 6})

    def test_input_count_is_fixed_at_ten(self) -> None:
        data = self.load_example()
        data["required_interfaces"] = copy.deepcopy(data["required_interfaces"])
        data["required_interfaces"]["input_channels"] = 8
        with tempfile.TemporaryDirectory(prefix="smartgear-mcu-selection-") as directory:
            with self.assertRaisesRegex(ValueError, "input_channels must be 10"):
                validate(self.write_selection(data, directory))

    def test_pass_requires_selected_mcu_and_all_gates(self) -> None:
        data = self.load_example()
        data["status"] = "pass"
        data["selected_mcu"] = "pending"
        data["selected_package"] = "pending"
        data["evidence"] = ["decision.md"]
        with tempfile.TemporaryDirectory(prefix="smartgear-mcu-selection-") as directory:
            with self.assertRaisesRegex(ValueError, "requires selected_mcu"):
                validate(self.write_selection(data, directory))

    def test_pass_cannot_hide_pending_gate(self) -> None:
        data = self.load_example()
        data["status"] = "pass"
        data["selected_mcu"] = "RP2040"
        data["selected_package"] = "QFN-56"
        data["selection_basis"] = "decision.md"
        data["evidence"] = ["decision.md"]
        data["pin_budget"] = copy.deepcopy(data["pin_budget"])
        data["pin_budget"]["status"] = "pass"
        data["gates"] = copy.deepcopy(data["gates"])
        for gate in data["gates"].values():
            gate["status"] = "pass"
            gate["evidence"] = ["decision.md"]
        data["gates"]["clock_sync_and_drift"]["status"] = "pending"
        data["gates"]["clock_sync_and_drift"]["evidence"] = []
        with tempfile.TemporaryDirectory(prefix="smartgear-mcu-selection-") as directory:
            with self.assertRaisesRegex(ValueError, "requires every gate"):
                validate(self.write_selection(data, directory))


if __name__ == "__main__":
    unittest.main()
