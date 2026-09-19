#!/usr/bin/env python3
"""Build an explicit Bambu Studio package for the split C-scheme clamp/post interface.

The C-clamp is split at y=0 into an operator-side half and an opponent-side
half.  The active connection is the SKP C-scheme: a green integrated base on
the upright slides into a clearance pocket in the fixed body, then two M4
fasteners and a spring-ball detent retain it.  Nine transverse M5 joints clamp
the two C-clamp halves.  This helper selects the four print objects, normalises
their OpenSCAD world coordinates, and produces an editable Bambu project with
all object names preserved.

The generated 3MF is an editable Bambu project.  The four source objects are kept
together as complete source objects, but they are deliberately not claimed to
be one-plate G-code: the fixed body and the tilted carrier cannot both fit beside
each other on one X1C plate.  Open the project in Bambu Studio and arrange the
parts on separate plates before slicing.  The source STL files and the
machine/process settings remain separate evidence; this script does not claim
that a printed part has passed a fit test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from build_print_platter import (
    load_binary_stl,
    rotation_matrix_xyz,
    transform_bounds,
    transform_triangles,
    write_binary_stl,
)


HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE_DIR = HERE / "exports" / "desktop-clamp-one-side-x1c-v0.7-split-c-scheme"
DEFAULT_OUTPUT_DIR = HERE / "exports" / "desktop-clamp-one-side-x1c-v0.7-split-c-scheme-3mf"
DEFAULT_TEMPLATE = (
    HERE
    / "exports"
    / "desktop-clamp-one-side-x1c-v0.5-net-structure"
    / "right-net-structure-X1C-PETG.gcode.3mf"
)
IDENTITY = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def find_bambu(explicit: Path | None) -> Path:
    if explicit:
        candidate = explicit.expanduser().resolve()
        if candidate.is_file():
            return candidate
        raise SystemExit(f"Bambu Studio executable not found: {candidate}")
    candidates = [
        os.environ.get("BAMBUSTUDIO"),
        "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
    ]
    for raw in candidates:
        if raw:
            candidate = Path(raw).expanduser()
            if candidate.is_file():
                return candidate
    raise SystemExit(
        "找不到 Bambu Studio；请用 --bambu 指定其 Contents/MacOS/BambuStudio 路径"
    )


def run(command: list[str], label: str, *, cwd: Path | None = None) -> None:
    result = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd,
    )
    if result.returncode != 0:
        tail = result.stdout[-4000:]
        raise RuntimeError(f"{label} 失败（退出码 {result.returncode}）:\n{tail}")


def normalise_stl(source: Path, destination: Path, matrix=IDENTITY) -> None:
    mesh = load_binary_stl(source)
    rotated_bounds = transform_bounds(mesh.bounds, matrix)
    lo = rotated_bounds[0]
    rotated = transform_triangles(mesh.triangles, matrix, (0.0, 0.0, 0.0))
    translated = transform_triangles(rotated, IDENTITY, (-lo[0], -lo[1], -lo[2]))
    write_binary_stl(destination, translated, f"SmartGear normalised {source.name}")


def copy_template_settings(seed: Path, template: Path, destination: Path) -> None:
    """Add the known-good X1C/PETG settings to an unsliced Bambu project."""

    with zipfile.ZipFile(seed) as source_zip, zipfile.ZipFile(template) as template_zip:
        settings = template_zip.read("Metadata/project_settings.config")
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as output_zip:
            for info in source_zip.infolist():
                if info.filename in {
                    "Metadata/project_settings.config",
                    "Metadata/filament_sequence.json",
                    "Metadata/slice_info.config",
                }:
                    continue
                output_zip.writestr(info, source_zip.read(info.filename))
            output_zip.writestr("Metadata/project_settings.config", settings)
            output_zip.writestr(
                "Metadata/filament_sequence.json",
                json.dumps(
                    {
                        "plate_1": {
                            "nozzle_sequence": [0],
                            "optimal_assignment": [0],
                            "sequence": [1],
                        }
                    },
                    separators=(",", ":"),
                ).encode("utf-8"),
            )


def verify_3mf(path: Path, required_names: set[str], *, require_gcode: bool) -> list[str]:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"3MF 未生成: {path}")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        model_settings = archive.read("Metadata/model_settings.config").decode(
            "utf-8", errors="replace"
        )
        missing = sorted(name for name in required_names if name not in model_settings)
        if missing:
            raise RuntimeError(f"3MF 缺少对象名: {missing} ({path})")
        if require_gcode and not any(name.endswith(".gcode") for name in names):
            raise RuntimeError(f"3MF 没有切片 G-code: {path}")
        return sorted(
            name
            for name in required_names
            if name in model_settings
        )


def build_side(
    side: str,
    *,
    source_dir: Path,
    output_dir: Path,
    template: Path,
    bambu: Path,
    no_slice: bool,
) -> dict[str, object]:
    carrier_name = f"{side}-post-clamp-carrier.stl"
    body_user_name = f"{side}-clamp-body-half-user.stl"
    body_opponent_name = f"{side}-clamp-body-half-opponent.stl"
    clip_name = f"{side}-net-clamp-clip.stl"
    source_files = [
        source_dir / body_user_name,
        source_dir / body_opponent_name,
        source_dir / carrier_name,
        source_dir / clip_name,
    ]
    for path in source_files:
        if not path.is_file():
            raise SystemExit(f"当前打印包缺少必要零件: {path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    # Keep all three source meshes next to the generated project so opening the
    # package never requires recovering them from an older directory.
    for path in source_files:
        shutil.copy2(path, output_dir / path.name)

    project_name = f"{side}-split-c-scheme-X1C-PETG"
    final_path = (
        output_dir / f"{project_name}.3mf"
        if no_slice
        else output_dir / f"{project_name}.gcode.3mf"
    )
    with tempfile.TemporaryDirectory(prefix=f"smartgear-{side}-") as temp_name:
        temp_dir = Path(temp_name)
        normalised = []
        for source in source_files:
            target = temp_dir / source.name
            matrix = (
                rotation_matrix_xyz(0.0, 51.0, 45.0)
                if source.name == carrier_name
                else IDENTITY
            )
            normalise_stl(source, target, matrix)
            normalised.append(target)

        seed = temp_dir / "seed.3mf"
        run(
            [
                str(bambu),
                "--datadir",
                str(temp_dir / "export-datadir"),
                "--allow-rotations",
                "--arrange",
                "0" if no_slice else "1",
                "--orient",
                "0",
                "--export-3mf",
                str(seed),
                *(str(path) for path in normalised),
            ],
            f"Bambu {side} 项目导出",
            cwd=temp_dir,
        )

        seeded = temp_dir / "seed-with-settings.3mf"
        copy_template_settings(seed, template, seeded)
        if no_slice:
            shutil.copy2(seeded, final_path)
        else:
            raise RuntimeError(
                "当前接口换版包包含 C 夹前后半体、C 方案黄绿立柱和网夹四件，不能诚实地作为一张 X1C 底板切片；"
                "请省略 --slice（默认生成可编辑 3MF），在 Bambu Studio 中分盘排版后再切片。"
            )

    required_names = {
        body_user_name,
        body_opponent_name,
        carrier_name,
        clip_name,
    }
    names = verify_3mf(final_path, required_names, require_gcode=not no_slice)
    manifest = {
        "schema_version": "0.1",
        "package": "desktop-clamp-one-side-x1c-v0.7-split-c-scheme",
        "side": side,
        "source_manifest": "../desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json",
        "source_files": [
            {
                "file": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "role": "可打印源 STL",
            }
            for path in source_files
        ],
        "project": final_path.name,
        "project_objects": names,
        "sliced": not no_slice,
        "notes": [
            "这是 C 方案分型接口换版包：操作者侧/对手侧两件 C 夹半体、带绿色整体底座的整根立柱和全高 U 形滑入网夹是四类独立打印对象。",
            "两件 C 夹半体在 y=0 合拢；前半圆头沉孔朝外，后半防转六角螺母窝朝外，9 个横向 M5 连接位把两半锁成一体；只有贴到电子腔空腔边界的连接位带承力 boss，实心夹臂里的连接位只保留孔位，避免外壳凸起。左下角孔向外侧移动，电子仓左下角和右下斜加强边沿各增加连接点。",
            "分型后的 C 夹必须与带让位腔的立柱配套换版；旧的完整整件夹体不能继续使用。",
            "绿色整体底座沿 x 方向推入灰色让位腔，两个 M4 穿孔锁紧，4 mm 钢珠只负责终点定位。",
            "本 3MF 保留四件完整模型但不包含 G-code；两件 C 夹半体和斜放立柱不能同时放在一张 X1C 底板内，请在 Bambu Studio 中分盘排版后切片。",
            "当前方案没有独立圆柱 net_clamp_rod；旧名称只是兼容诊断入口。",
            "切片/导出通过不等于实物推入配合、网布夹持和承力验收。",
        ],
    }
    (output_dir / f"{side}-c-scheme-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--bambu", type=Path)
    parser.add_argument("--side", choices=("right", "left", "both"), default="both")
    parser.add_argument(
        "--no-slice",
        action="store_true",
        default=True,
        help="只导出带 X1C/PETG 设置的 3MF 项目，不生成 G-code",
    )
    parser.add_argument(
        "--slice",
        dest="no_slice",
        action="store_false",
        help="已禁用：三件不能诚实地在一张 X1C 底板切片；请在 Bambu Studio 中分盘后切片",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="清理本脚本生成的补打印包文件",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = args.source_dir.resolve()
    output_dir = args.output_dir.resolve()
    if args.clean and output_dir == source_dir:
        raise SystemExit(
            "--clean 的 3MF 输出目录不能与 STL 源目录相同；请使用独立的 -3mf 目录"
        )
    template = args.template.resolve()
    if not (source_dir / "manifest.json").is_file():
        raise SystemExit(f"找不到源打印件 manifest: {source_dir / 'manifest.json'}")
    if not template.is_file():
        raise SystemExit(f"找不到 X1C/PETG 设置模板: {template}")
    if not args.no_slice:
        raise SystemExit(
            "当前换版包包含 C 夹前后半体、C 方案黄绿立柱和网夹四件，不能作为一张 X1C 底板切片；"
            "请直接运行本脚本生成可编辑 3MF，再在 Bambu Studio 中分盘排版。"
        )
    if args.clean and output_dir.is_dir():
        for path in output_dir.glob("*-net-structure*"):
            if path.is_file():
                path.unlink()
        for path in output_dir.glob("*-c-scheme*"):
            if path.is_file():
                path.unlink()
        for path in output_dir.glob("*.gcode.3mf"):
            path.unlink()
        for path in output_dir.glob("*-post-clamp-carrier.stl"):
            path.unlink()
        for path in output_dir.glob("*-clamp-body-segment.stl"):
            path.unlink()
        for path in output_dir.glob("*-clamp-body-half-user.stl"):
            path.unlink()
        for path in output_dir.glob("*-clamp-body-half-opponent.stl"):
            path.unlink()
        for path in output_dir.glob("*-net-clamp-clip.stl"):
            path.unlink()

    bambu = find_bambu(args.bambu)
    sides = ("right", "left") if args.side == "both" else (args.side,)
    results = [
        build_side(
            side,
            source_dir=source_dir,
            output_dir=output_dir,
            template=template,
            bambu=bambu,
            no_slice=args.no_slice,
        )
        for side in sides
    ]
    print(
        f"NET_CLAMP_BAMBU_PACKAGE_OK (sides={','.join(sides)}, "
        f"sliced={not args.no_slice}, output={output_dir})"
    )
    for result in results:
        print(f"{result['side']}: {result['project']} -> {result['project_objects']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
