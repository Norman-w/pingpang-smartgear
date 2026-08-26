#!/usr/bin/env python3
"""Validate the pending STM32G031K8U6 carrier pin-map contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCHEMA_VERSION = "m6-carrier-stm32g031k8-pinmap-v0.1"
EXPECTED_INPUTS = [
    ("carrier_in_00", "PA1", 8, 1),
    ("carrier_in_01", "PA2", 9, 2),
    ("carrier_in_02", "PA3", 10, 3),
    ("carrier_in_03", "PA4", 11, 4),
    ("carrier_in_04", "PA5", 12, 5),
    ("carrier_in_05", "PA6", 13, 6),
    ("carrier_in_06", "PA7", 14, 7),
    ("carrier_in_07", "PA9", 19, 9),
    ("carrier_in_08", "PA10", 21, 10),
    ("carrier_in_09", "PA15", 26, 15),
]
EXPECTED_FIXED = {
    "spi_cs_n": ("PB0", 15, "input", "SPI1_NSS/AF0+EXTI0"),
    "spi_sck": ("PB3", 27, "input", "SPI1_SCK/AF0"),
    "spi_miso": ("PB4", 28, "output", "SPI1_MISO/AF0"),
    "spi_mosi": ("PB5", 29, "input", "SPI1_MOSI/AF0"),
    "irq_n": ("PB8", 32, "output", "GPIO"),
    "reset_n": ("PF2-NRST", 6, "reset_input", "NRST"),
    "swdio": ("PA13", 24, "bidirectional", "SWDIO"),
    "swclk": ("PA14", 25, "input", "SWCLK"),
}
EXPECTED_HOST_GPIO = {"sck": 10, "mosi": 11, "miso": 12, "cs_n": 13, "irq_n": 14, "reset_n": 5}


def fail(message: str) -> None:
    raise ValueError(message)


def validate(path: Path) -> dict[str, object]:
    try:
        root = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"invalid JSON: {error}")
    if not isinstance(root, dict):
        fail("root must be an object")
    if root.get("schema_version") != SCHEMA_VERSION:
        fail(f"schema_version must be {SCHEMA_VERSION}")
    if root.get("status") not in {"pending", "pass", "fail"}:
        fail("status must be pending, pass, or fail")
    if root.get("mcu") != "STM32G031K8U6":
        fail("mcu must be STM32G031K8U6")
    if root.get("package") != "UFQFPN32":
        fail("package must be UFQFPN32")
    source_urls = root.get("source_urls")
    if not isinstance(source_urls, list) or len(source_urls) < 2 or any(
        not isinstance(value, str) or not value.startswith("https://")
        for value in source_urls
    ):
        fail("source_urls must contain official HTTPS sources")
    if root.get("host_gpio") != EXPECTED_HOST_GPIO:
        fail("host_gpio must match SmartPaddle carrier candidate mapping")

    signals = root.get("signals")
    if not isinstance(signals, list) or len(signals) != len(EXPECTED_INPUTS) + len(EXPECTED_FIXED):
        fail("signals must contain exactly ten inputs and eight fixed signals")
    by_name: dict[str, dict[str, object]] = {}
    for index, signal in enumerate(signals):
        if not isinstance(signal, dict):
            fail(f"signals[{index}] must be an object")
        name = signal.get("name")
        if not isinstance(name, str) or not name or name in by_name:
            fail("signal names must be unique non-empty strings")
        by_name[name] = signal

    exti_lines: list[int] = []
    for name, mcu_pin, package_pin, exti_line in EXPECTED_INPUTS:
        signal = by_name.get(name)
        if signal is None:
            fail(f"missing {name}")
        if (
            signal.get("mcu_pin") != mcu_pin
            or signal.get("package_pin") != package_pin
            or signal.get("direction") != "input"
            or signal.get("exti_line") != exti_line
        ):
            fail(f"{name} pin/EXTI assignment is incorrect")
        exti_lines.append(exti_line)
    if len(set(exti_lines)) != 10:
        fail("ten carrier inputs must use unique EXTI lines")

    for name, (mcu_pin, package_pin, direction, alternate_function) in EXPECTED_FIXED.items():
        signal = by_name.get(name)
        if signal is None:
            fail(f"missing {name}")
        if (
            signal.get("mcu_pin") != mcu_pin
            or signal.get("package_pin") != package_pin
            or signal.get("direction") != direction
            or signal.get("alternate_function") != alternate_function
        ):
            fail(f"{name} fixed assignment is incorrect")

    package_pins = [signal.get("package_pin") for signal in by_name.values()]
    if len(set(package_pins)) != len(package_pins):
        fail("signal package pins must be unique")
    return {
        "status": root["status"],
        "mcu": root["mcu"],
        "package": root["package"],
        "input_count": len(EXPECTED_INPUTS),
        "unique_exti_lines": len(set(exti_lines)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pinmap",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "hardware/electronics/m6-capture-carrier-stm32g031k8-pinmap.example.json",
    )
    args = parser.parse_args()
    try:
        result = validate(args.pinmap)
    except (OSError, TypeError, ValueError) as error:
        print(f"M6_CARRIER_STM32_PINMAP_INVALID: {error}", file=sys.stderr)
        return 1
    print(
        "M6_CARRIER_STM32_PINMAP_OK "
        f"(status={result['status']}, mcu={result['mcu']}, "
        f"package={result['package']}, inputs={result['input_count']}, "
        f"unique_exti={result['unique_exti_lines']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
