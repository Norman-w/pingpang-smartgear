#!/usr/bin/env python3
"""Create a safe, explicitly-pending M6 physical-acceptance run skeleton."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from validate_m6_acceptance_bundle import (
    EXPECTED_WIDTHS_US,
    validate as validate_bundle,
)


HERE = Path(__file__).resolve().parent
VENDOR_DIR = HERE.parent / "docs" / "vendor" / "m6-laser-opposed"
BUNDLE_TEMPLATE = VENDOR_DIR / "acceptance-bundle.example.json"
CHANNEL_TEMPLATE = VENDOR_DIR / "channel-map.example.json"
TARGET_WIDTHS_US = tuple(EXPECTED_WIDTHS_US)


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def build_run(output_dir: Path) -> dict[str, object]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir()

    bundle = json.loads(BUNDLE_TEMPLATE.read_text(encoding="utf-8"))
    bundle["channel_map"]["path"] = "channel-map.json"
    bundle["run_notes"] = (
        "Skeleton only: replace pending IDs/statuses only after real evidence is copied."
    )
    bundle_path = output_dir / "acceptance-bundle.json"
    _write_json(bundle_path, bundle)

    channel_map = json.loads(CHANNEL_TEMPLATE.read_text(encoding="utf-8"))
    channel_map["notes"] = "首样运行副本；没有真实通道证据时保持 pending。"
    _write_json(output_dir / "channel-map.json", channel_map)

    waveform_header = ["trial_id", "time_us", "reference", "sensor_npn", "mcu"]
    waveform_templates: list[str] = []
    for width_us in TARGET_WIDTHS_US:
        template_name = f"M6-waveform-template-{width_us // 1000}ms.csv"
        waveform_templates.append(template_name)
        with (evidence_dir / template_name).open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.writer(handle)
            writer.writerow(waveform_header)

    (evidence_dir / "README.txt").write_text(
        "把订单/SKU截图、卡尺照片、机械调节记录、载板 MCU/PCB/SPI/IRQ/时钟同步/SmartPaddle 回环记录、原始逻辑分析仪 CSV 和真实球日志放在这里。\n"
        "已按 1/2/3/4/5/6/8/10 ms 目标生成八张空白 CSV 表头；不要把模板 CSV 当作通过证据。\n"
        "每张表填入真实参考快门、传感器 NPN 和 MCU 侧采样后，运行 analyze_m6_response.py 生成对应 JSON，\n"
        "再把 acceptance-bundle.json 中相应批次的 summary_path/status/evidence 补齐。填完后运行：\n"
        "python3 tools/validate_m6_acceptance_bundle.py "
        f"{bundle_path}\n"
        "模板文件：\n"
        + "\n".join(f"- {name}" for name in waveform_templates)
        + "\n",
        encoding="utf-8",
    )

    (evidence_dir / "carrier-integration-template.md").write_text(
        "# 载板与 SmartPaddle 现场记录（模板）\n\n"
        "- carrier MCU：\n"
        "- PCB revision：\n"
        "- GPIO map / 启动日志：\n"
        "- SPI mode 0 / 1 MHz 波形：\n"
        "- IRQ 低有效与 152-byte 帧读取：\n"
        "- 时钟同步交换、offset 和漂移：\n"
        "- 十路同时边沿 / FIFO：\n"
        "- SmartPaddle `/ws` 文本帧回环：\n\n"
        "本文件只是待填写模板；未有原始日志/波形/设备回环证据前，\n"
        "不要把 carrier_integration 或其子门状态改成 pass。\n",
        encoding="utf-8",
    )

    validation = validate_bundle(bundle_path)
    return {
        "output_dir": output_dir,
        "bundle_path": bundle_path,
        "validation": validation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = build_run(args.output_dir)
    counts = result["validation"]["section_counts"]
    print(
        "M6_ACCEPTANCE_RUN_INITIALIZED "
        f"(dir={result['output_dir']}, "
        f"sections={counts['pass']} pass/{counts['fail']} fail/{counts['pending']} pending)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
