#!/usr/bin/env python3
"""Tests for the M6 top-level physical acceptance gate."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_m6_acceptance_bundle import validate


HERE = Path(__file__).resolve().parent
EXAMPLE = HERE.parent / "docs" / "vendor" / "m6-laser-opposed" / "acceptance-bundle.example.json"
CHANNEL_MAP_EXAMPLE = HERE.parent / "docs" / "vendor" / "m6-laser-opposed" / "channel-map.example.json"


class M6AcceptanceBundleTests(unittest.TestCase):
    def write_bundle(self, data: dict[str, object], directory: str) -> Path:
        root = Path(directory)
        path = root / "acceptance.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        (root / "channel-map.example.json").write_text(
            CHANNEL_MAP_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8"
        )
        return path

    def write_evidence(self, directory: str, name: str) -> None:
        evidence_dir = Path(directory) / "evidence"
        evidence_dir.mkdir(exist_ok=True)
        (evidence_dir / name).write_text("test evidence\n", encoding="utf-8")

    def load_example(self) -> dict[str, object]:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_pending_bundle_is_explicitly_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            result = validate(self.write_bundle(self.load_example(), directory))
        self.assertEqual(result["overall_status"], "pending")
        self.assertEqual(result["section_counts"], {"pass": 0, "fail": 0, "pending": 7})

    def test_bundle_binds_the_user_selected_sku(self) -> None:
        data = self.load_example()
        data["sku_id"] = "wrong-sku"
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            with self.assertRaisesRegex(ValueError, "sku_id must be 6122579349941"):
                validate(self.write_bundle(data, directory))

    def test_seller_response_semantics_are_pinned(self) -> None:
        data = self.load_example()
        data["procurement"]["seller_response_semantics"] = "minimum_obstruction_ms"
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            with self.assertRaisesRegex(ValueError, "seller_response_semantics"):
                validate(self.write_bundle(data, directory))

    def test_confirmed_model_cannot_keep_pending_seller_model(self) -> None:
        data = self.load_example()
        data["procurement"]["model_status"] = "pass"
        data["procurement"]["seller_model"] = "pending"
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            with self.assertRaisesRegex(ValueError, "confirmed seller_model"):
                validate(self.write_bundle(data, directory))

    def test_five_ms_is_not_a_continuous_obstruction_gate(self) -> None:
        data = self.load_example()
        data["procurement"]["continuous_obstruction_5ms_required"] = True
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            with self.assertRaisesRegex(ValueError, "must be false"):
                validate(self.write_bundle(data, directory))

    def test_carrier_transport_contract_is_frozen(self) -> None:
        data = self.load_example()
        data["carrier_integration"]["spi_mode"] = 3
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            with self.assertRaisesRegex(ValueError, "spi_mode must be 0"):
                validate(self.write_bundle(data, directory))

    def test_carrier_pass_requires_all_real_gates(self) -> None:
        data = self.load_example()
        data["carrier_integration"]["status"] = "pass"
        data["carrier_integration"]["mcu_model"] = "example-mcu"
        data["carrier_integration"]["pcb_revision"] = "carrier-v0.1"
        data["carrier_integration"]["evidence"] = ["carrier.txt"]
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            self.write_evidence(directory, "carrier.txt")
            with self.assertRaisesRegex(ValueError, "every carrier gate"):
                validate(self.write_bundle(data, directory))

    def test_overall_pass_cannot_hide_pending_sections(self) -> None:
        data = self.load_example()
        data["overall_status"] = "pass"
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            with self.assertRaisesRegex(ValueError, "overall_status=pass"):
                validate(self.write_bundle(data, directory))

    def test_overall_fail_cannot_hide_an_all_pending_bundle(self) -> None:
        data = self.load_example()
        data["overall_status"] = "fail"
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            with self.assertRaisesRegex(ValueError, "overall_status=fail"):
                validate(self.write_bundle(data, directory))

    def test_devices_pass_cannot_use_pending_placeholder_ids(self) -> None:
        data = self.load_example()
        data["devices"]["status"] = "pass"
        data["devices"]["evidence"] = ["devices.txt"]
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            self.write_evidence(directory, "devices.txt")
            with self.assertRaisesRegex(ValueError, "pending placeholder IDs"):
                validate(self.write_bundle(data, directory))

    def test_waveform_width_matrix_is_fixed(self) -> None:
        data = self.load_example()
        data["waveform"] = copy.deepcopy(data["waveform"])
        data["waveform"]["batches"][0]["width_us"] = 1500
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            with self.assertRaisesRegex(ValueError, "cover each target exactly once"):
                validate(self.write_bundle(data, directory))

    def test_sensor_measurements_require_real_dimensions_when_passed(self) -> None:
        data = self.load_example()
        data["mechanical"]["sensor_measurements"]["status"] = "pass"
        data["mechanical"]["sensor_measurements"]["evidence"] = ["measurements.txt"]
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            self.write_evidence(directory, "measurements.txt")
            with self.assertRaisesRegex(ValueError, "requires thread_spec=M6x0.75"):
                validate(self.write_bundle(data, directory))

    def test_mechanical_pass_cannot_hide_pending_sensor_measurements(self) -> None:
        data = self.load_example()
        data["mechanical"]["status"] = "pass"
        data["mechanical"]["evidence"] = ["mechanical.txt"]
        with tempfile.TemporaryDirectory(prefix="smartgear-m6-bundle-") as directory:
            self.write_evidence(directory, "mechanical.txt")
            with self.assertRaisesRegex(ValueError, "requires passing sensor_measurements"):
                validate(self.write_bundle(data, directory))


if __name__ == "__main__":
    unittest.main()
