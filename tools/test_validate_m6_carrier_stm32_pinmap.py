#!/usr/bin/env python3
"""Tests for the pending STM32G031K8U6 carrier pin-map validator."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_m6_carrier_stm32_pinmap import validate


HERE = Path(__file__).resolve().parent
EXAMPLE = HERE.parent / "hardware/electronics/m6-capture-carrier-stm32g031k8-pinmap.example.json"


class M6CarrierStm32PinmapTests(unittest.TestCase):
    def load_example(self) -> dict[str, object]:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def write_data(self, data: dict[str, object], directory: str) -> Path:
        path = Path(directory) / "pinmap.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_example_has_ten_unique_exti_inputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="smartgear-stm32-pinmap-") as directory:
            result = validate(self.write_data(self.load_example(), directory))
        self.assertEqual(result["input_count"], 10)
        self.assertEqual(result["unique_exti_lines"], 10)
        data = self.load_example()
        cs = next(signal for signal in data["signals"] if signal["name"] == "spi_cs_n")
        self.assertEqual(cs["alternate_function"], "SPI1_NSS/AF0+EXTI0")

    def test_duplicate_exti_line_is_rejected(self) -> None:
        data = self.load_example()
        data["signals"] = copy.deepcopy(data["signals"])
        data["signals"][1]["exti_line"] = 0
        with tempfile.TemporaryDirectory(prefix="smartgear-stm32-pinmap-") as directory:
            with self.assertRaisesRegex(ValueError, "pin/EXTI assignment"):
                validate(self.write_data(data, directory))

    def test_spi_pin_drift_is_rejected(self) -> None:
        data = self.load_example()
        data["signals"] = copy.deepcopy(data["signals"])
        data["signals"][11]["mcu_pin"] = "PB2"
        with tempfile.TemporaryDirectory(prefix="smartgear-stm32-pinmap-") as directory:
            with self.assertRaisesRegex(ValueError, "spi_sck fixed assignment"):
                validate(self.write_data(data, directory))


if __name__ == "__main__":
    unittest.main()
