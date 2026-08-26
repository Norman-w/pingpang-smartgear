#!/usr/bin/env python3
"""Validate the single evidence bundle for the M6 optical-array gate.

The bundle is intentionally allowed to be ``pending`` before the hardware
arrives.  Once a section is marked ``pass`` or ``fail``, it must reference
real evidence.  Passing waveform batches and the channel map are delegated to
their existing validators so a top-level bundle cannot hide a weak lower-level
result.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import NoReturn

from validate_m6_channel_map import validate as validate_channel_map
from validate_m6_response_batch import validate as validate_response_batch


SCHEMA_VERSION = "m6-acceptance-bundle-v0.1"
ITEM_ID = "1071628886139"
SKU_ID = "6122579349941"
EXPECTED_HEIGHTS = list(range(10, 101, 10))
EXPECTED_WIDTHS_US = [1000, 2000, 3000, 4000, 5000, 6000, 8000, 10000]
AXES = ("yaw", "pitch", "roll")
CARRIER_GATES = (
    "gpio_map",
    "spi_irq_waveform",
    "clock_sync",
    "ten_channel_edge_burst",
    "smartpaddle_ws",
)
VALID_STATUSES = {"pending", "pass", "fail"}
SELLER_RESPONSE_SEMANTICS = "input_state_change_to_output_change_complete"
SENSOR_MEASUREMENT_FIELDS = (
    "thread_effective_length_mm",
    "head_length_x_mm",
    "head_width_y_mm",
    "head_height_z_mm",
    "mount_stem_length_mm",
    "lock_nut_af_mm",
    "optical_axis_to_thread_offset_x_mm",
    "cable_min_bend_radius_mm",
)


def fail(message: str) -> NoReturn:
    raise ValueError(message)


def require_object(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        fail(f"{field} must be an object")
    return value


def require_string(value: object, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        fail(f"{field} must be a non-empty string")
    return value.strip()


def require_status(value: object, field: str) -> str:
    if value not in VALID_STATUSES:
        fail(f"{field} must be pending, pass, or fail")
    return str(value)


def require_evidence_list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        fail(f"{field} must be a list")
    return value


def resolve_relative_file(
    bundle_path: Path,
    root: Path,
    relative: object,
    field: str,
    *,
    require_exists: bool = True,
) -> Path:
    value = require_string(relative, field)
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        fail(f"{field} must stay relative to its root: {value!r}")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"{field} escapes its root: {value!r}") from error
    if require_exists and not resolved.is_file():
        fail(f"{field} does not exist: {resolved}")
    return resolved


def validate_evidence(
    bundle_path: Path,
    evidence_root: Path,
    evidence: object,
    field: str,
    status: str,
) -> list[Path]:
    entries = require_evidence_list(evidence, field)
    resolved = [
        resolve_relative_file(bundle_path, evidence_root, entry, f"{field}[{index}]")
        for index, entry in enumerate(entries)
    ]
    if status in {"pass", "fail"} and not resolved:
        fail(f"{field}: {status} requires at least one evidence file")
    return resolved


def validate_section(
    bundle_path: Path,
    evidence_root: Path,
    section: object,
    field: str,
) -> tuple[dict[str, object], str, list[Path]]:
    data = require_object(section, field)
    status = require_status(data.get("status"), f"{field}.status")
    evidence = validate_evidence(
        bundle_path, evidence_root, data.get("evidence", []), f"{field}.evidence", status
    )
    return data, status, evidence


def validate(bundle_path: Path) -> dict[str, object]:
    try:
        record = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"invalid JSON: {error}")
    root = require_object(record, "bundle")

    if root.get("schema_version") != SCHEMA_VERSION:
        fail(f"schema_version must be {SCHEMA_VERSION}")
    if root.get("item_id") != ITEM_ID:
        fail(f"item_id must be {ITEM_ID}")
    if root.get("sku_id") != SKU_ID:
        fail(f"sku_id must be {SKU_ID}")
    require_string(root.get("selected_variant"), "selected_variant")

    evidence_root_value = require_string(root.get("evidence_root"), "evidence_root")
    evidence_root_relative = Path(evidence_root_value)
    if evidence_root_relative.is_absolute() or ".." in evidence_root_relative.parts:
        fail("evidence_root must be a relative directory")
    evidence_root = (bundle_path.parent / evidence_root_relative).resolve()

    procurement, procurement_status, _ = validate_section(
        bundle_path, evidence_root, root.get("procurement"), "procurement"
    )
    model_status = require_status(
        procurement.get("model_status"), "procurement.model_status"
    )
    seller_model = require_string(
        procurement.get("seller_model"), "procurement.seller_model"
    )
    if model_status == "pass" and seller_model.strip().lower() in {
        "pending",
        "tbd",
        "待确认",
    }:
        fail("procurement.model_status=pass requires a confirmed seller_model")
    polarity = procurement.get("output_polarity")
    if polarity not in {"pending", "NPN_NO", "NPN_NC"}:
        fail("procurement.output_polarity must be pending, NPN_NO, or NPN_NC")
    receiver_count = procurement.get("receiver_output_count")
    if receiver_count is not None and (
        not isinstance(receiver_count, int) or not 0 <= receiver_count <= 10
    ):
        fail("procurement.receiver_output_count must be null or an integer from 0 to 10")
    response_time = procurement.get("seller_response_time_ms")
    if (
        not isinstance(response_time, (int, float))
        or isinstance(response_time, bool)
        or not math.isfinite(float(response_time))
        or float(response_time) != 5
    ):
        fail("procurement.seller_response_time_ms must be exactly 5")
    if procurement.get("seller_response_semantics") != SELLER_RESPONSE_SEMANTICS:
        fail(
            "procurement.seller_response_semantics must describe "
            "input-state change to output-change completion"
        )
    if procurement.get("continuous_obstruction_5ms_required") is not False:
        fail("procurement.continuous_obstruction_5ms_required must be false")
    minimum_input_pulse = procurement.get("minimum_input_pulse_ms")
    if minimum_input_pulse is not None and (
        not isinstance(minimum_input_pulse, (int, float))
        or isinstance(minimum_input_pulse, bool)
        or not math.isfinite(float(minimum_input_pulse))
        or float(minimum_input_pulse) <= 0
    ):
        fail("procurement.minimum_input_pulse_ms must be null or positive")
    require_string(procurement.get("seller_response_source"), "procurement.seller_response_source")
    if procurement_status == "pass" and not (
        model_status == "pass"
        and polarity in {"NPN_NO", "NPN_NC"}
        and receiver_count == 10
    ):
        fail("procurement.pass requires confirmed model, polarity, and ten outputs")

    devices, devices_status, _ = validate_section(
        bundle_path, evidence_root, root.get("devices"), "devices"
    )
    for key in ("transmitter_count", "receiver_count"):
        if devices.get(key) != 10:
            fail(f"devices.{key} must be 10")
    for key in ("transmitter_ids", "receiver_ids"):
        values = devices.get(key)
        if not isinstance(values, list) or len(values) != 10:
            fail(f"devices.{key} must contain exactly ten IDs")
        if any(not isinstance(value, str) or not value.strip() for value in values):
            fail(f"devices.{key} must contain non-empty strings")
        if len(set(values)) != 10:
            fail(f"devices.{key} must contain unique IDs")
        if devices_status == "pass" and any(
            "PENDING" in value.upper() for value in values
        ):
            fail(f"devices.{key}.pass cannot use pending placeholder IDs")

    carrier, carrier_status, _ = validate_section(
        bundle_path, evidence_root, root.get("carrier_integration"),
        "carrier_integration"
    )
    carrier_mcu_model = require_string(
        carrier.get("mcu_model"), "carrier_integration.mcu_model"
    )
    carrier_pcb_revision = require_string(
        carrier.get("pcb_revision"), "carrier_integration.pcb_revision"
    )
    if carrier.get("spi_mode") != 0:
        fail("carrier_integration.spi_mode must be 0")
    if carrier.get("spi_clock_hz") != 1_000_000:
        fail("carrier_integration.spi_clock_hz must be 1000000")
    if carrier.get("max_frame_bytes") != 152:
        fail("carrier_integration.max_frame_bytes must be 152")
    carrier_gate_statuses: dict[str, str] = {}
    for gate in CARRIER_GATES:
        _, gate_status, _ = validate_section(
            bundle_path, evidence_root, carrier.get(gate),
            f"carrier_integration.{gate}"
        )
        carrier_gate_statuses[gate] = gate_status
    if carrier_status == "pass":
        if carrier_mcu_model.strip().lower() in {"pending", "tbd", "待确认"}:
            fail("carrier_integration.pass requires a selected carrier MCU")
        if carrier_pcb_revision.strip().lower() in {"pending", "tbd", "待确认"}:
            fail("carrier_integration.pass requires a PCB revision")
        if any(status != "pass" for status in carrier_gate_statuses.values()):
            fail("carrier_integration.pass requires every carrier gate to pass")

    mechanical, mechanical_status, _ = validate_section(
        bundle_path, evidence_root, root.get("mechanical"), "mechanical"
    )
    if mechanical.get("channel_heights_mm") != EXPECTED_HEIGHTS:
        fail("mechanical.channel_heights_mm must be 10,20,...,100")
    measurements, measurement_status, _ = validate_section(
        bundle_path,
        evidence_root,
        mechanical.get("sensor_measurements"),
        "mechanical.sensor_measurements",
    )
    thread_spec = measurements.get("thread_spec")
    if not isinstance(thread_spec, str) or not thread_spec.strip():
        fail("mechanical.sensor_measurements.thread_spec must be a non-empty string")
    for field in SENSOR_MEASUREMENT_FIELDS:
        value = measurements.get(field)
        if value is not None and (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
            or float(value) <= 0
        ):
            fail(f"mechanical.sensor_measurements.{field} must be null or a positive finite number")
    cable_direction = measurements.get("cable_exit_direction")
    if not isinstance(cable_direction, str) or not cable_direction.strip():
        fail("mechanical.sensor_measurements.cable_exit_direction must be a non-empty string")
    if measurement_status == "pass":
        if thread_spec.strip() != "M6x0.75":
            fail("mechanical.sensor_measurements.pass requires thread_spec=M6x0.75")
        if any(measurements.get(field) is None for field in SENSOR_MEASUREMENT_FIELDS):
            fail("mechanical.sensor_measurements.pass requires every physical dimension")
        if cable_direction.strip().lower() == "pending":
            fail("mechanical.sensor_measurements.pass requires a measured cable_exit_direction")
    if mechanical_status == "pass" and measurement_status != "pass":
        fail("mechanical.pass requires passing sensor_measurements")
    axes = require_object(mechanical.get("axis_adjustment"), "mechanical.axis_adjustment")
    axis_statuses: dict[str, str] = {}
    for axis in AXES:
        axis_data, axis_status, _ = validate_section(
            bundle_path, evidence_root, axes.get(axis), f"mechanical.axis_adjustment.{axis}"
        )
        axis_statuses[axis] = axis_status
        if axis_data.get("range_deg") != 4:
            fail(f"mechanical.axis_adjustment.{axis}.range_deg must be 4")
        angle = axis_data.get("final_angle_deg")
        if angle is not None and (
            not isinstance(angle, (int, float))
            or isinstance(angle, bool)
            or not math.isfinite(float(angle))
            or abs(float(angle)) > 4
        ):
            fail(f"mechanical.axis_adjustment.{axis}.final_angle_deg must be null or within ±4°")

    waveform, waveform_status, _ = validate_section(
        bundle_path, evidence_root, root.get("waveform"), "waveform"
    )
    if waveform.get("target_widths_us") != EXPECTED_WIDTHS_US:
        fail("waveform.target_widths_us must be 1000,2000,3000,4000,5000,6000,8000,10000")
    batches = waveform.get("batches")
    if not isinstance(batches, list) or len(batches) != len(EXPECTED_WIDTHS_US):
        fail("waveform.batches must contain exactly eight widths")
    seen_widths: set[int] = set()
    batch_statuses: list[str] = []
    for index, batch in enumerate(batches):
        batch_data, batch_status, _ = validate_section(
            bundle_path, evidence_root, batch, f"waveform.batches[{index}]"
        )
        width = batch_data.get("width_us")
        if width not in EXPECTED_WIDTHS_US or width in seen_widths:
            fail(f"waveform.batches[{index}].width_us must cover each target exactly once")
        seen_widths.add(width)
        batch_statuses.append(batch_status)
        summary_path_value = batch_data.get("summary_path", "")
        if not isinstance(summary_path_value, str):
            fail(f"waveform.batches[{index}].summary_path must be a string")
        if batch_status == "pass":
            summary_path = resolve_relative_file(
                bundle_path,
                evidence_root,
                summary_path_value,
                f"waveform.batches[{index}].summary_path",
            )
            try:
                validate_response_batch(
                    summary_path,
                    target_width_us=width,
                    min_trials=30,
                )
            except (OSError, TypeError, ValueError) as error:
                raise ValueError(
                    f"waveform.batches[{index}] failed response-batch validation: {error}"
                ) from error
    if seen_widths != set(EXPECTED_WIDTHS_US):
        fail("waveform.batches must cover every required target width")

    channel_map, channel_map_status, _ = validate_section(
        bundle_path, evidence_root, root.get("channel_map"), "channel_map"
    )
    channel_map_path_value = channel_map.get("path", "")
    if not isinstance(channel_map_path_value, str):
        fail("channel_map.path must be a string")
    if channel_map_path_value:
        channel_map_path = resolve_relative_file(
            bundle_path,
            bundle_path.parent,
            channel_map_path_value,
            "channel_map.path",
        )
        try:
            map_counts = validate_channel_map(channel_map_path)
        except (OSError, TypeError, ValueError) as error:
            raise ValueError(f"channel_map failed validation: {error}") from error
        if channel_map_status == "pass" and map_counts != (10, 0, 0):
            fail("channel_map.pass requires ten passing channels and no pending/fail rows")
    elif channel_map_status == "pass":
        fail("channel_map.pass requires a path")

    ball_test, ball_status, _ = validate_section(
        bundle_path, evidence_root, root.get("real_ball_test"), "real_ball_test"
    )
    cases = ball_test.get("cases")
    expected_cases = {"center", "edge", "diagonal", "height_sweep"}
    if not isinstance(cases, list) or len(cases) != len(expected_cases):
        fail("real_ball_test.cases must contain four cases")
    case_statuses: dict[str, str] = {}
    for index, case in enumerate(cases):
        case_data, case_status, _ = validate_section(
            bundle_path, evidence_root, case, f"real_ball_test.cases[{index}]"
        )
        name = case_data.get("name")
        if name not in expected_cases or name in case_statuses:
            fail("real_ball_test.cases must cover center, edge, diagonal, and height_sweep")
        case_statuses[name] = case_status
    if set(case_statuses) != expected_cases:
        fail("real_ball_test.cases must cover center, edge, diagonal, and height_sweep")

    section_statuses = {
        "procurement": procurement_status,
        "devices": devices_status,
        "carrier_integration": carrier_status,
        "mechanical": mechanical_status,
        "waveform": waveform_status,
        "channel_map": channel_map_status,
        "real_ball_test": ball_status,
    }
    declared_overall = require_status(root.get("overall_status"), "overall_status")
    if declared_overall == "pass" and (
        any(status != "pass" for status in section_statuses.values())
        or any(status != "pass" for status in axis_statuses.values())
        or any(status != "pass" for status in batch_statuses)
        or any(status != "pass" for status in case_statuses.values())
        or any(status != "pass" for status in carrier_gate_statuses.values())
    ):
        fail("overall_status=pass requires every section, axis, waveform batch, and ball case to pass")
    all_statuses = [
        *section_statuses.values(),
        *axis_statuses.values(),
        *batch_statuses,
        *case_statuses.values(),
        *carrier_gate_statuses.values(),
    ]
    if declared_overall == "fail" and "fail" not in all_statuses:
        fail("overall_status=fail requires at least one failed section or case")

    counts = {
        "pass": sum(status == "pass" for status in section_statuses.values()),
        "fail": sum(status == "fail" for status in section_statuses.values()),
        "pending": sum(status == "pending" for status in section_statuses.values()),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "overall_status": declared_overall,
        "section_counts": counts,
        "pending_sections": [
            name for name, status in section_statuses.items() if status == "pending"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.bundle)
    except (OSError, TypeError, ValueError) as error:
        print(f"M6_ACCEPTANCE_BUNDLE_INVALID: {error}", file=sys.stderr)
        return 1
    counts = result["section_counts"]
    print(
        "M6_ACCEPTANCE_BUNDLE_OK "
        f"(overall={result['overall_status']}, "
        f"sections={counts['pass']} pass/{counts['fail']} fail/{counts['pending']} pending)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
