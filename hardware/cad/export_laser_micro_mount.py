#!/usr/bin/env python3
"""Export the adjustable laser cassette from the same SCAD used by the assembly.

This is a separate first-article package, not the historical M6 print platter.
Both its geometry and installation datums are read from OpenSCAD.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
from pathlib import Path

from validate_net_stand import _stl_topology, _stl_volume
from validate_scad import find_openscad, stl_bounds

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_stand.scad"
LIBRARY = HERE / "laser_micro_mount.scad"
OUTPUT = HERE / "exports" / "laser-micro-mount-v0.1"
# id, name, material, color, printable, moving, exploded displacement (mm)
PARTS = [
    ("base", "下夹座 / 弹簧承力座", "PETG", "#647d96", True, False, [0,0,0]),
    ("cap", "上夹座 / A、B 调节座", "PETG", "#86a9c4", True, False, [0,0,20]),
    ("liner_lower", "球面衬垫下半", "TPU", "#46cfb2", True, False, [0,0,0]),
    ("liner_upper", "球面衬垫上半", "TPU", "#46cfb2", True, False, [0,0,14]),
    ("carrier", "球面激光夹筒", "PETG", "#ec934b", True, True, [-14,-10,9]),
    ("laser", "裸激光头（尺寸待实测）", "外购铜壳激光头", "#d4b567", False, True, [10,-10,9]),
    ("screw_a", "A 微调螺钉 / M2×8", "钢", "#eceff1", False, False, [0,0,20]),
    ("screw_b", "B 微调螺钉 / M2×8", "钢", "#eceff1", False, False, [0,0,20]),
    ("nuts", "A、B 捕获调节螺母", "钢", "#b8c6cf", False, False, [0,0,20]),
    ("lock_a", "A 锁紧螺母", "钢", "#b8c6cf", False, False, [0,0,20]),
    ("lock_b", "B 锁紧螺母", "钢", "#b8c6cf", False, False, [0,0,20]),
    ("spring", "底部压缩弹簧", "弹簧钢", "#c4d2d9", False, False, [0,0,0]),
    ("cap_bolt_a", "夹座合拢螺钉 A / M2×14", "钢", "#b8c6cf", False, False, [0,0,20]),
    ("cap_bolt_b", "夹座合拢螺钉 B / M2×14", "钢", "#b8c6cf", False, False, [0,0,20]),
    ("cap_nuts", "下夹座捕获螺母", "钢", "#b8c6cf", False, False, [0,0,0]),
    ("retention_screw", "激光头限位顶丝", "钢", "#b8c6cf", False, True, [-14,-10,9]),
    ("retention_nut", "激光头限位捕获螺母", "钢", "#b8c6cf", False, True, [-14,-10,9]),
    ("rear_pusher_screw", "激光头后段径向防退顶丝 / M3×3", "钢（平头机米螺丝）", "#aebbc4", False, True, [-14,-10,9]),
    ("mount_hardware", "通道安装螺钉与螺母", "钢", "#b8c6cf", False, False, [0,0,0]),
    ("rail", "十路小夹座承载条", "PETG", "#526f89", True, False, [0,0,0]),
    ("front_cover", "裸激光光学前盖（端部固定孔）", "PETG", "#728394", True, False, [-24,0,0]),
    ("rear_cover", "裸激光后盖（带编号调节孔）", "PETG", "#728394", True, False, [24,0,0]),
    ("bottom_cover", "加大前腔配套底盖", "PETG", "#526f89", True, False, [0,0,-20]),
    ("bottom_gasket", "加大底盖柔性垫", "TPU", "#dc9850", True, False, [0,0,-10]),
    ("front_bolts", "前盖 M3×30 沉头螺钉", "钢", "#b8c6cf", False, False, [-34,45,0]),
    ("front_nuts", "前盖捕获螺母", "钢", "#b8c6cf", False, False, [0,0,0]),
]
ARRAY_PARTS={"rail","front_cover","rear_cover","bottom_cover","bottom_gasket","front_bolts","front_nuts"}

def read_motion(metadata, label):
    return [dict(progress=float(e),values=json.loads(values))
            for e,values in re.findall(rf'{label} ([\d.eE+-]+) (\[.*\])"',metadata)]

def scad(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout + result.stderr
    if result.returncode or "ERROR:" in output or "WARNING:" in output:
        raise RuntimeError(output)
    return output

def export(output_dir=OUTPUT, jobs=3):
    output_dir.mkdir(parents=True, exist_ok=True)
    openscad = find_openscad()
    metadata = scad([openscad,"-o",str(output_dir/"metadata.csg"),"-D",
                     'PART="laser_micro_metadata"',str(SOURCE)])
    params = {name:float(value) for name,value in re.findall(r"LASER_PARAM (\w+)=([-\d.eE+]+)",metadata)}
    if not params:
        raise RuntimeError("OpenSCAD metadata is missing")
    source_hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,LIBRARY)}
    def build(spec):
        key,name,material,color,printed,moving,explosion = spec
        path = output_dir / f"{key}.stl"
        scad([openscad,"-o",str(path),"-D",f'PART="laser_micro_{key}"',str(SOURCE)])
        closed, topology = _stl_topology(path)
        volume = _stl_volume(path)
        if not closed or volume <= 0:
            raise RuntimeError(f"{key}: {topology}, volume {volume}")
        b = stl_bounds(path)
        low,high = [b[0],b[2],b[4]],[b[1],b[3],b[5]]
        entry = dict(id=key,file=path.name,name_zh=name,material=material,color=color,
                     printable=printed,moving=moving,explosion=explosion,
                     quantity=1 if key in ARRAY_PARTS else int(params["count"]),
                     scope="array" if key in ARRAY_PARTS else "cassette",
                     bounds=dict(min=low,max=high,size=[hi-lo for lo,hi in zip(low,high)]),
                     volume_mm3=round(volume,4),watertight=True,topology=topology,
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        print(f"{key}: closed, {volume:.1f} mm3",flush=True)
        return entry
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        parts = list(pool.map(build,PARTS))
    service_assets=[]
    for sign,side in [(1,"a"),(-1,"b")]:
        path=output_dir/f"service_tool_{side}.stl"
        scad([openscad,"-o",str(path),"-D",'PART="laser_micro_service_tool"',
              "-D",f"laser_micro_service_sign={sign}",str(SOURCE)])
        closed,topology=_stl_topology(path)
        assert closed and _stl_volume(path)>0,topology
        service_assets.append(dict(id=f"tool_{side}",file=path.name,sign=sign,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),printable=False))
    manifest = dict(schema_version="laser-micro-mount-0.2",units="mm",parameters=params,
                    source_hashes=source_hashes,parts=parts,service_assets=service_assets,
                    bench_motion=read_motion(metadata,"LASER_MOTION"),
                    cover_motion=read_motion(metadata,"COVER_MOTION"),
                    scope="左侧裸激光发射端；接收器与驱动电路待单独选型",
                    physical_validation="未完成：裸头尺寸、TPU预紧、弹簧参数、锁紧漂移")
    (output_dir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    return manifest

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=OUTPUT)
    parser.add_argument("--jobs",type=int,default=3)
    args=parser.parse_args()
    export(args.output,args.jobs)
