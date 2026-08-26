#!/usr/bin/env python3
"""Audit the sibling SmartPaddle checkout before attempting an integration.

This intentionally does not import or copy SmartPaddle into the Pingpang
firmware build.  It verifies the external source contract and reports GPIO
collisions against the provisional Pingpang mapping.  Normal mode is a
read-only report; ``--strict`` exits non-zero when direct pin reuse would be
unsafe.
"""

from __future__ import annotations

import argparse
import re
import runpy
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve()
PINGPANG_ROOT = HERE.parents[1]
DEFAULT_SMARTPADDLE_ROOT = PINGPANG_ROOT.parent / "SmartPaddle"


def _read(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"missing required reference file: {path}")
    return path.read_text(encoding="utf-8")


def _git_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"not a readable git checkout: {root}") from exc


def _require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise ValueError(f"{label}: missing {needle!r}")


def _parse_gpio_array(config_text: str, name: str) -> list[int]:
    match = re.search(
        rf"\b{re.escape(name)}\b\s*=\s*\{{(?P<body>[^}}]*)\}}\s*;",
        config_text,
        re.S,
    )
    if not match:
        raise ValueError(f"Pingpang config is missing {name}")

    def resolve(token: str, seen: set[str]) -> int:
        if re.fullmatch(r"\d+", token):
            return int(token)
        if token in seen:
            raise ValueError(f"cyclic GPIO alias while resolving {name} entry {token!r}")
        seen.add(token)

        # Support both project-local constexpr aliases and preprocessor-style
        # GPIO_NUM_N aliases without depending on a C++ parser.
        direct = re.search(
            rf"\b{re.escape(token)}\b\s*=\s*(?:GPIO_NUM_)?(\d+)\s*;",
            config_text,
        )
        if direct:
            return int(direct.group(1))
        alias = re.search(
            rf"\b{re.escape(token)}\b\s*=\s*([A-Za-z_]\w*)\s*;",
            config_text,
        )
        if alias:
            return resolve(alias.group(1), seen)
        raise ValueError(f"cannot resolve {name} entry {token!r}")

    values: list[int] = []
    for raw in match.group("body").split(","):
        token = raw.strip()
        if token:
            values.append(resolve(token, set()))
    return values


def _load_reference_pinmap(
    path: Path,
) -> tuple[dict[str, int], dict[int, dict[str, str]], dict[int, str]]:
    namespace = runpy.run_path(str(path))
    firmware_gpio = namespace.get("FIRMWARE_GPIO")
    pads = namespace.get("PADS")
    project_bindings = namespace.get("PROJECT_BINDINGS")
    if (
        not isinstance(firmware_gpio, dict)
        or not isinstance(pads, dict)
        or not isinstance(project_bindings, dict)
    ):
        raise ValueError(
            "SmartPaddle pinmap must export FIRMWARE_GPIO, PADS and "
            "PROJECT_BINDINGS"
        )
    return firmware_gpio, pads, project_bindings


def _gpio_from_function(function: str) -> int | None:
    match = re.search(r"GPIO(\d+)(?:/|$)", function)
    return int(match.group(1)) if match else None


def audit(smartpaddle_root: Path, strict: bool = False) -> int:
    firmware_root = smartpaddle_root / "firmware" / "main"
    web_root = smartpaddle_root / "web"
    server_root = smartpaddle_root / "server"
    pinmap_path = smartpaddle_root / "pcb" / "lib" / "esp32s3wroom1" / "pinmap.py"

    ws_header = _read(firmware_root / "ws_data_server.h")
    ws_source = _read(firmware_root / "ws_data_server.cpp")
    config_text = _read(PINGPANG_ROOT / "firmware" / "main" / "net_sensor_config.h")
    carrier_config_text = _read(
        PINGPANG_ROOT / "firmware" / "main" / "m6_carrier_config.h"
    )
    device_protocol = _read(web_root / "src" / "lib" / "deviceImuProtocol.ts")
    vite_config = _read(web_root / "vite.config.ts")
    server_main = _read(server_root / "main.go")
    reference_config = _read(firmware_root / "config.h")

    _require(ws_header, "ws_data_has_client", "SmartPaddle ws header")
    _require(ws_header, "ws_data_send_text", "SmartPaddle ws header")
    _require(ws_source, '.uri = "/ws"', "SmartPaddle device websocket")
    _require(ws_source, "httpd_ws_send_frame_async", "SmartPaddle device websocket")
    _require(ws_source, ".is_websocket = true", "SmartPaddle device websocket")
    _require(device_protocol, "'/ws'", "SmartPaddle web device path")
    _require(device_protocol, "/device/ws", "SmartPaddle dev proxy path")
    _require(vite_config, "'/device'", "SmartPaddle Vite device proxy")
    _require(server_main, '"/ws/paddle"', "SmartPaddle Go server path")
    _require(reference_config, "PIEZO_PIN_1", "SmartPaddle board config")

    firmware_gpio, pads, project_bindings = _load_reference_pinmap(pinmap_path)
    reference_used = {int(value) for value in firmware_gpio.values()}
    exposed = {
        gpio
        for entry in pads.values()
        if isinstance(entry, dict)
        and isinstance(entry.get("function"), str)
        for gpio in [_gpio_from_function(entry["function"])]
        if gpio is not None
    }

    # FIRMWARE_GPIO intentionally omits board-level USB/UART bindings.  Add
    # every electrically bound module GPIO from the same PCB truth source so
    # the spare-pin report cannot advertise USB/UART pins as free.
    reference_name_by_gpio: dict[int, list[str]] = {}
    for name, value in firmware_gpio.items():
        reference_name_by_gpio.setdefault(int(value), []).append(name)
    for pad, binding in project_bindings.items():
        pad_entry = pads.get(pad)
        if not isinstance(pad_entry, dict):
            continue
        function = pad_entry.get("function")
        if not isinstance(function, str):
            continue
        gpio = _gpio_from_function(function)
        if gpio is None:
            continue
        reference_used.add(gpio)
        reference_name_by_gpio.setdefault(gpio, []).append(str(binding))

    pingpang_groups = {
        "beam": _parse_gpio_array(config_text, "kBeamGpioPins"),
        "pvdf_comparator": _parse_gpio_array(
            config_text, "kPiezoComparatorGpioPins"
        ),
        "pvdf_adc": _parse_gpio_array(config_text, "kPiezoAdcGpioPins"),
        "feedback": _parse_gpio_array(config_text, "kFeedbackGpioPins"),
    }
    carrier_pins = _parse_gpio_array(
        carrier_config_text, "kSmartPaddleCarrierGpioPins"
    )
    conflicts = {
        name: sorted(set(values) & reference_used)
        for name, values in pingpang_groups.items()
    }
    conflict_count = sum(len(values) for values in conflicts.values())

    # These pins are not ordinary spare GPIOs on the selected module even if
    # they are visible in the package pin table.
    protected = {
        0,
        3,
        19,
        20,
        35,
        36,
        37,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
    }
    carrier_conflicts = sorted(set(carrier_pins) & (reference_used | protected))
    ordinary_free = sorted(exposed - reference_used - protected)

    print(f"SMARTPADDLE_REFERENCE_OK (head={_git_head(smartpaddle_root)})")
    print("device_ws=/ws; dev_proxy=/device/ws; go_server_ws=/ws/paddle")
    print(
        "reference_used_gpio="
        + ",".join(str(gpio) for gpio in sorted(reference_used))
    )
    print(
        "ordinary_free_gpio="
        + (",".join(str(gpio) for gpio in ordinary_free) or "none")
    )
    print("carrier_candidate_gpio=" + ",".join(map(str, carrier_pins)))
    if carrier_conflicts:
        print(
            "CARRIER_PIN_RESERVED: GPIO"
            + ",".join(map(str, carrier_conflicts))
        )
    else:
        print("CARRIER_PIN_RESERVED: none")
    for name, values in conflicts.items():
        if values:
            roles = "; ".join(
                f"GPIO{gpio}=" + "/".join(reference_name_by_gpio.get(gpio, []))
                for gpio in values
            )
            print(f"CONFLICT {name}: GPIO{','.join(map(str, values))} ({roles})")
        else:
            print(f"CONFLICT {name}: none")

    if strict and (conflict_count or carrier_conflicts):
        print(
            "STRICT_FAIL: current Pingpang provisional pins cannot be wired "
            "directly to the SmartPaddle reference board",
            file=sys.stderr,
        )
        return 1
    if conflict_count:
        print(
            "DIRECT_PIN_REUSE=UNSAFE; use a dedicated sensor carrier or a "
            "newly audited expansion/latch architecture"
        )
    else:
        print("DIRECT_PIN_REUSE=NO_CONFLICT_DETECTED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smartpaddle-root",
        type=Path,
        default=DEFAULT_SMARTPADDLE_ROOT,
        help="sibling SmartPaddle checkout (default: ../SmartPaddle)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail when direct reuse of the current provisional pins conflicts",
    )
    args = parser.parse_args()
    try:
        return audit(args.smartpaddle_root.resolve(), strict=args.strict)
    except ValueError as exc:
        print(f"SMARTPADDLE_REFERENCE_FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
