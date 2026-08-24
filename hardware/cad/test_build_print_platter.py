#!/usr/bin/env python3
"""Regression tests for the net-stand print-platter manifest and layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_print_platter import DEFAULT_OUTPUT, load_binary_stl


def _overlap_gap(left: dict[str, object], right: dict[str, object]) -> float:
    left_lo, left_hi = left["placed_bounds"]
    right_lo, right_hi = right["placed_bounds"]
    x_gap = max(float(right_lo[0]) - float(left_hi[0]), float(left_lo[0]) - float(right_hi[0]))
    y_gap = max(float(right_lo[1]) - float(left_hi[1]), float(left_lo[1]) - float(right_hi[1]))
    # Rectangles can be diagonally separated: the row boundary may provide
    # the required clearance even if the adjacent row's X gap is smaller.
    if x_gap > 0 or y_gap > 0:
        return max(x_gap, y_gap)
    return 0.0


def _assert_source_file(manifest_path: Path, entry: dict[str, object]) -> None:
    source_path = entry.get("source_path")
    if not source_path:
        raise AssertionError(f"拼盘条目缺少 source_path: {entry.get('file')}")
    resolved = (manifest_path.parent / str(source_path)).resolve()
    if not resolved.is_file():
        raise AssertionError(f"拼盘条目的源 STL 不存在: {resolved}")


def validate_manifest(path: Path, source_manifest_path: Path | None = None) -> None:
    if not path.is_file():
        raise AssertionError(f"拼盘 manifest 不存在: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "0.1":
        raise AssertionError("拼盘 manifest schema 版本错误")
    bed = data.get("print_bed")
    if not isinstance(bed, dict):
        raise AssertionError("缺少 print_bed")
    width = float(bed["width_mm"])
    depth = float(bed["depth_mm"])
    height = float(bed["height_mm"])
    margin = float(bed["edge_margin_mm"])
    gap = float(bed["part_gap_mm"])
    if min(width, depth, height, margin, gap) <= 0:
        raise AssertionError("打印床参数必须为正数")

    source_manifest = source_manifest_path or path.parent.parent / "manifest.json"
    if not source_manifest.is_file():
        raise AssertionError(f"源打印件 manifest 不存在: {source_manifest}")
    source = json.loads(source_manifest.read_text(encoding="utf-8"))
    expected_files = {str(item["file"]) for item in source["parts"]}
    entries = data.get("parts")
    if not isinstance(entries, list) or {str(item["file"]) for item in entries} != expected_files:
        raise AssertionError("拼盘 parts 与 50 件源清单不一致")
    components = data.get("assembly_components")
    if not isinstance(components, list) or not components:
        raise AssertionError("拼盘 manifest 缺少装配物料清单")

    plates = data.get("plates")
    if not isinstance(plates, list) or not plates:
        raise AssertionError("至少应生成一张拼盘")
    placed_files: set[str] = set()
    for plate in plates:
        plate_file = path.parent / str(plate["file"])
        mesh = load_binary_stl(plate_file)
        size = tuple(mesh.bounds[1][axis] - mesh.bounds[0][axis] for axis in range(3))
        if size[0] > width + 1e-3 or size[1] > depth + 1e-3 or size[2] > height + 1e-3:
            raise AssertionError(f"{plate_file.name} 超出打印床: {size}")
        parts = plate.get("parts")
        if not isinstance(parts, list) or not parts:
            raise AssertionError(f"{plate['id']} 没有排版零件")
        for item in parts:
            filename = str(item["file"])
            if not item.get("name_zh"):
                raise AssertionError(f"拼盘条目缺少中文名称: {filename}")
            _assert_source_file(path, item)
            if filename in placed_files:
                raise AssertionError(f"零件重复排版: {filename}")
            placed_files.add(filename)
            lo, hi = item["placed_bounds"]
            if (
                float(lo[0]) < margin - 1e-3
                or float(lo[1]) < margin - 1e-3
                or float(hi[0]) > width - margin + 1e-3
                or float(hi[1]) > depth - margin + 1e-3
                or float(lo[2]) < -1e-3
                or float(hi[2]) > height + 1e-3
            ):
                raise AssertionError(f"{filename} 超出安全排版区域: {item['placed_bounds']}")
        for index, left in enumerate(parts):
            for right in parts[index + 1:]:
                if _overlap_gap(left, right) < gap - 1e-3:
                    raise AssertionError(
                        f"{plate['id']} 零件间隔不足: {left['file']} / {right['file']}"
                    )

    oversized = data.get("oversized")
    oversized_files = {str(item["file"]) for item in oversized}
    if placed_files & oversized_files:
        raise AssertionError("同一零件同时 placed 和 oversized")
    if placed_files | oversized_files != expected_files:
        raise AssertionError("不是所有源零件都得到 placed/oversized 结论")
    for item in oversized:
        if not item.get("name_zh"):
            raise AssertionError(f"超尺寸条目缺少中文名称: {item.get('file')}")
        _assert_source_file(path, item)
        if item.get("status") != "oversized":
            raise AssertionError(f"超尺寸条目缺少 oversized 状态: {item}")


def validate_default(path: Path, source_manifest_path: Path | None = None) -> None:
    validate_manifest(path, source_manifest_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data["print_bed"]["width_mm"] != 256.0 or data["print_bed"]["depth_mm"] != 256.0:
        raise AssertionError("默认拼盘必须是 256 × 256 mm")
    if len(data["plates"]) != 2 or sum(p["part_count"] for p in data["plates"]) != 47:
        raise AssertionError("默认拼盘的板数/已排版数量发生变化")
    oversized = {item["file"] for item in data["oversized"]}
    if oversized != {f"net-rail-segment-{index}.stl" for index in range(3)}:
        raise AssertionError(f"默认超尺寸清单发生变化: {oversized}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_OUTPUT / "manifest.json")
    parser.add_argument("--source-manifest", type=Path, help="源打印件清单路径（输出目录不在默认 exports 时使用）")
    parser.add_argument("--default", action="store_true", help="额外检查默认 256 mm 清单")
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    source_manifest_path = args.source_manifest.resolve() if args.source_manifest else None
    validate_manifest(manifest_path, source_manifest_path)
    if args.default:
        validate_default(manifest_path, source_manifest_path)
    print(
        f"PRINT_PLATTER_TEST_OK ({len(json.loads(manifest_path.read_text(encoding='utf-8'))['plates'])} plates)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
