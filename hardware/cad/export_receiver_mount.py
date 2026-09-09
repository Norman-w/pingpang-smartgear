#!/usr/bin/env python3
"""Export the RX enclosure using the same front cover and floor as the TX."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import re
from export_laser_micro_mount import HERE, SOURCE, LIBRARY, scad
from validate_scad import find_openscad, stl_bounds
from validate_net_stand import _stl_topology, _stl_volume

OUTPUT=HERE/'exports/receiver-mount-v0.1'
SOURCES=(SOURCE,LIBRARY,HERE/'receiver_mount.scad')
PARTS=[
    ('rail','接收端承载条（配加大前盖）','PETG','#526f89',True),
    ('front_cover','接收端加大光学前盖','PETG','#728394',True),
    ('rear_cover','接收端后盖（端部固定孔）','PETG','#728394',True),
    ('bottom_cover','接收端配套加大底盖','PETG','#526f89',True),
    ('bottom_gasket','接收端底部柔性垫','TPU','#dc9850',True),
    ('front_hardware','接收端前盖 M3×30 螺钉与螺母','钢','#b8c6cf',False),
    ('pcb','原 M6 接收子板（接口参考）','电路板','#338878',False),
]
def main():
    OUTPUT.mkdir(parents=True,exist_ok=True);openscad=find_openscad()
    metadata=scad([openscad,'-o',str(OUTPUT/'metadata.csg'),'-D','PART="laser_micro_metadata"',str(SOURCE)])
    params={k:float(v) for k,v in re.findall(r'LASER_PARAM (\w+)=([-\d.eE+]+)',metadata)}
    def build(spec):
        key,name,material,color,printed=spec;path=OUTPUT/f'{key}.stl'
        scad([openscad,'-o',str(path),'-D',f'PART="receiver_{key}"',str(SOURCE)])
        closed,topology=_stl_topology(path);volume=_stl_volume(path)
        assert closed and volume>0,(key,topology,volume)
        b=stl_bounds(path);lo=[b[0],b[2],b[4]];hi=[b[1],b[3],b[5]]
        print(f'{key}: closed, {volume:.1f} mm3',flush=True)
        return dict(id=key,file=path.name,name_zh=name,material=material,color=color,printable=printed,
            bounds=dict(min=lo,max=hi,size=[y-x for x,y in zip(lo,hi)]),volume_mm3=volume,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),watertight=closed,topology=topology)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:parts=list(pool.map(build,PARTS))
    manifest=dict(schema_version='receiver-mount-0.1',units='mm',parameters=params,parts=parts,
        source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},
        scope='右侧接收端外壳与安装接口升级；内部接收头和电路保留原M6接口参考，选型未确认',
        physical_validation='未完成')
    (OUTPUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
