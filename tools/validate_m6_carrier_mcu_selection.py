#!/usr/bin/env python3
"""Validate the explicitly-pending M6 carrier MCU selection gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCHEMA_VERSION = "m6-carrier-mcu-selection-v0.1"
VALID_STATUSES = {"pending", "pass", "fail"}
CANDIDATES = {"RP2040", "STM32G031K8", "ESP32-C3"}
GATES = (
    "datasheet_and_package",
    "ten_input_edge_capture",
    "spi_slave_tx_preload",
    "irq_reset_waveform",
    "clock_sync_and_drift",
    "bringup_and_production_debug",
)
REQUIRED_SIGNALS = {
    "carrier_in": (10, "input"),
    "spi_sck": (1, "input"),
    "spi_mosi": (1, "input"),
    "spi_miso": (1, "output"),
    "spi_cs_n": (1, "input"),
    "irq_n": (1, "output"),
    "reset_n": (1, "input"),
    "debug": (2, "bidirectional"),
}


def fail(message: str) -> None:
    raise ValueError(message)


def require_object(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        fail(f"{field} must be an object")
    return value


def require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{field} must be a non-empty string")
    return value.strip()


def require_status(value: object, field: str) -> str:
    if value not in VALID_STATUSES:
        fail(f"{field} must be pending, pass, or fail")
    return str(value)


def require_evidence(value: object, field: str, status: str) -> None:
    if not isinstance(value, list):
        fail(f"{field} must be a list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        fail(f"{field} must contain non-empty strings")
    if status in {"pass", "fail"} and not value:
        fail(f"{field}: {status} requires evidence")


def validate(path: Path) -> dict[str, object]:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"invalid JSON: {error}")
    root = require_object(record, "selection")

    if root.get("schema_version") != SCHEMA_VERSION:
        fail(f"schema_version must be {SCHEMA_VERSION}")
    status = require_status(root.get("status"), "status")
    selected_mcu = require_string(root.get("selected_mcu"), "selected_mcu")
    selected_package = require_string(root.get("selected_package"), "selected_package")
    require_string(root.get("selection_basis"), "selection_basis")

    requirements = require_object(root.get("required_interfaces"), "required_interfaces")
    exact_requirements = {
        "logic_voltage_v": 3.3,
        "input_channels": 10,
        "edge_capture": "rising_and_falling",
        "timestamp_resolution_target_us": 1,
        "spi_role": "slave",
        "spi_mode": 0,
        "spi_clock_hz": 1_000_000,
        "max_tx_frame_bytes": 152,
        "irq_polarity": "active_low",
        "reset_polarity": "active_low",
        "watchdog_required": True,
    }
    for field, expected in exact_requirements.items():
        if requirements.get(field) != expected:
            fail(f"required_interfaces.{field} must be {expected!r}")

    candidates = root.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != len(CANDIDATES):
        fail("candidates must contain exactly the three documented candidates")
    candidate_names: set[str] = set()
    for index, candidate in enumerate(candidates):
        data = require_object(candidate, f"candidates[{index}]")
        name = require_string(data.get("name"), f"candidates[{index}].name")
        if name not in CANDIDATES or name in candidate_names:
            fail("candidates must cover RP2040, STM32G031K8, and ESP32-C3 exactly once")
        candidate_names.add(name)
        if data.get("status") != "candidate":
            fail(f"candidates[{index}].status must be candidate")
        require_evidence(data.get("evidence"), f"candidates[{index}].evidence", "pending")

    pin_budget = require_object(root.get("pin_budget"), "pin_budget")
    pin_budget_status = require_status(pin_budget.get("status"), "pin_budget.status")
    if pin_budget.get("mandatory_gpio_count") != 18:
        fail("pin_budget.mandatory_gpio_count must be 18")
    if pin_budget.get("recommended_gpio_count") != 22:
        fail("pin_budget.recommended_gpio_count must be 22")
    signals = pin_budget.get("signals")
    if not isinstance(signals, list):
        fail("pin_budget.signals must be a list")
    seen_signals: set[str] = set()
    for index, signal in enumerate(signals):
        data = require_object(signal, f"pin_budget.signals[{index}]")
        name = require_string(data.get("name"), f"pin_budget.signals[{index}].name")
        if name in seen_signals or name not in REQUIRED_SIGNALS:
            fail("pin_budget.signals must contain each required signal exactly once")
        seen_signals.add(name)
        expected_count, expected_direction = REQUIRED_SIGNALS[name]
        if data.get("count") != expected_count:
            fail(f"pin_budget.signals[{index}].count must be {expected_count}")
        if data.get("direction") != expected_direction:
            fail(f"pin_budget.signals[{index}].direction must be {expected_direction}")
        require_status(data.get("status"), f"pin_budget.signals[{index}].status")
    if seen_signals != set(REQUIRED_SIGNALS):
        fail("pin_budget.signals must cover every required signal")
    optional_signals = pin_budget.get("optional_signals")
    if not isinstance(optional_signals, list):
        fail("pin_budget.optional_signals must be a list")
    for index, signal in enumerate(optional_signals):
        data = require_object(signal, f"pin_budget.optional_signals[{index}]")
        require_string(data.get("name"), f"pin_budget.optional_signals[{index}].name")
        require_status(data.get("status"), f"pin_budget.optional_signals[{index}].status")

    gates = require_object(root.get("gates"), "gates")
    gate_statuses: dict[str, str] = {}
    for gate in GATES:
        gate_data = require_object(gates.get(gate), f"gates.{gate}")
        gate_status = require_status(gate_data.get("status"), f"gates.{gate}.status")
        require_evidence(gate_data.get("evidence"), f"gates.{gate}.evidence", gate_status)
        gate_statuses[gate] = gate_status
    require_evidence(root.get("evidence"), "evidence", status)

    placeholder_values = {"pending", "tbd", "待确认"}
    if status == "pass":
        if selected_mcu.lower() in placeholder_values:
            fail("status=pass requires selected_mcu")
        selected_family = (
            "STM32G031K8" if selected_mcu.startswith("STM32G031K8") else selected_mcu
        )
        if selected_family not in CANDIDATES:
            fail("status=pass selected_mcu must be one of the documented candidates")
        if selected_package.lower() in placeholder_values:
            fail("status=pass requires selected_package")
        if pin_budget_status != "pass":
            fail("status=pass requires pin_budget.pass")
        if any(gate_status != "pass" for gate_status in gate_statuses.values()):
            fail("status=pass requires every gate to pass")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "selected_mcu": selected_mcu,
        "pin_budget_status": pin_budget_status,
        "gate_counts": {
            "pass": sum(value == "pass" for value in gate_statuses.values()),
            "fail": sum(value == "fail" for value in gate_statuses.values()),
            "pending": sum(value == "pending" for value in gate_statuses.values()),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "selection",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "hardware/electronics/m6-capture-carrier-mcu-selection.example.json",
    )
    args = parser.parse_args()
    try:
        result = validate(args.selection)
    except (OSError, TypeError, ValueError) as error:
        print(f"M6_CARRIER_MCU_SELECTION_INVALID: {error}", file=sys.stderr)
        return 1
    counts = result["gate_counts"]
    print(
        "M6_CARRIER_MCU_SELECTION_OK "
        f"(status={result['status']}, mcu={result['selected_mcu']}, "
        f"gates={counts['pass']} pass/{counts['fail']} fail/{counts['pending']} pending)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
