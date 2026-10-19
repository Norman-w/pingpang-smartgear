#!/usr/bin/env python3
"""Build from native SCAD in robust stages; no slicing or printer commands."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'exports/perpendicular-u-joint-v1.13-edge-safe-label'
OPENSCAD='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

def export(backend,destination,source,feature=None):
    cmd=[OPENSCAD,f'--backend={backend}','--export-format=binstl']
    if feature:cmd+=['-D',f'FEATURE="{feature}"']
    cmd+=['-o',str(destination),str(source)]
    subprocess.run(cmd,check=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(export,'CGAL',OUT/'guard-v1.13-body.stl',HERE/'edge_safe_guard.scad','body'),
              pool.submit(export,'Manifold',OUT/'guard-v1.13-lettering.stl',HERE/'edge_safe_guard.scad','label')]
        for job in jobs:job.result()
    export('Manifold',OUT/'guard-v1.13.stl',HERE/'assemble_export.scad')

if __name__=='__main__':main()
