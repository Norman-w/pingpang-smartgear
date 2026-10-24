#!/usr/bin/env python3
"""Staged native-CAD export with the SAME octahedral opening as SCAD.

OpenSCAD's CGAL opening asserts on the unified sloping body. Recompute that
operation from its clean raw solid with Manifold64, with 0.00001 mm numerical
tolerance. No hole filling / voxelization / design replacement is performed.
Run: uv run --with manifold3d --with numpy python <this script>
"""
from pathlib import Path
import json
import hashlib
import importlib.metadata
import struct
import subprocess
import numpy as np
import manifold3d as m

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'exports/perpendicular-u-joint-v1.15-tapered-unified'
REVIEW=HERE.parent/'review/perpendicular-u-joint-v1.15-tapered-unified'
OSC='/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
TOL=1e-5

def load_stl(path):
    data=Path(path).read_bytes()
    count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*count, 'Expected staged binary STL'
    points=[]; faces=[]; indices={}
    for i in range(count):
        xyz=struct.unpack_from('<12f',data,84+50*i)[3:]
        face=[]
        for j in (0,3,6):
            p=tuple(xyz[j:j+3])
            if p not in indices:
                indices[p]=len(points);points.append(p)
            face.append(indices[p])
        faces.append(face)
    solid=m.Manifold(m.Mesh64(np.array(points,dtype=np.float64),np.array(faces,dtype=np.uint64)))
    assert solid.status()==m.Error.NoError, str(solid.status())
    return solid

def export_grid(solid):
    # Binary STL is float32. Resolve sub-grid coincidences BEFORE conversion,
    # using a 0.00001 mm coordinate grid; never fill holes or add bridges.
    mesh=solid.to_mesh64()
    points,inverse=np.unique(np.round(mesh.vert_properties[:,:3]/TOL)*TOL,
                            axis=0,return_inverse=True)
    result=m.Manifold(m.Mesh64(np.ascontiguousarray(points),
        np.ascontiguousarray(inverse[mesh.tri_verts],dtype=np.uint64)))
    assert result.status()==m.Error.NoError,str(result.status())
    assert len(result.decompose())==1
    assert abs(result.volume()-solid.volume())<0.02
    return result

def save_stl(path,solid):
    assert solid.status()==m.Error.NoError
    mesh=solid.to_mesh64()
    out=bytearray(b'Native SCAD geometry; Manifold64 staged opening'.ljust(80,b'\0'))
    out.extend(struct.pack('<I',len(mesh.tri_verts)))
    for tri in mesh.tri_verts:
        p=mesh.vert_properties[tri,:3]
        n=np.cross(p[1]-p[0],p[2]-p[0])
        out.extend(struct.pack('<12fH',*n,*p.flatten(),0))
    Path(path).write_bytes(out)

def main():
    OUT.mkdir(parents=True,exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True)
    result=subprocess.run([OSC,'--backend=CGAL','--export-format=binstl',
        '-D','FEATURE="raw"','-o',str(OUT/'raw-solid.stl'),str(HERE/'tapered_guard.scad')],
        capture_output=True,text=True,check=True)
    assert 'ERROR:' not in result.stderr and 'assertion violation' not in result.stderr,result.stderr
    raw=load_stl(OUT/'raw-solid.stl').set_tolerance(TOL)
    kernel=m.Manifold(m.Mesh64(np.array([[.6,0,0],[-.6,0,0],[0,.6,0],
        [0,-.6,0],[0,0,.6],[0,0,-.6]],dtype=np.float64),
        np.array([[0,2,4],[2,1,4],[1,3,4],[3,0,4],
        [2,0,5],[1,2,5],[3,1,5],[0,3,5]],dtype=np.uint64)))
    assert kernel.status()==m.Error.NoError
    print('Opening unified native solid...',flush=True)
    opened=raw.minkowski_difference(kernel).minkowski_sum(kernel)^raw
    band=m.Manifold.cube((120,120,1.5)).translate((-60,-60,-23.5))
    body=export_grid((opened+(raw^band)).simplify(TOL))
    assert body.status()==m.Error.NoError and len(body.decompose())==1
    assert abs((body-raw).volume())<0.01
    save_stl(OUT/'guard-v1.15-body.stl',body)
    lettering=load_stl(HERE.parent/'exports/perpendicular-u-joint-v1.13-edge-safe-label/guard-v1.13-lettering.stl')
    full=export_grid((body+lettering).simplify(TOL))
    assert len(full.decompose())==1
    save_stl(OUT/'guard-v1.15.stl',full)
    report={'method':'native SCAD raw solid; octahedron erosion then dilation, intersect raw, restore lowest 1.5 mm',
        'numerical_tolerance_mm':TOL,'body_components':len(body.decompose()),
        'full_components':len(full.decompose()),'raw_volume_mm3':raw.volume(),
        'body_volume_mm3':body.volume(),'full_volume_mm3':full.volume(),
        'added_outside_raw_mm3':abs((body-raw).volume()),
        'manifold3d_version':importlib.metadata.version('manifold3d'),
        'numpy_version':np.__version__}
    inputs=[HERE/'tapered_guard.scad',HERE/'build_export.py',
        HERE.parent/'perpendicular-u-joint-guard-v1.13-edge-safe-label/edge_safe_guard.scad',
        HERE.parent/'perpendicular-u-joint-guard-v1.12-flush-roof/flush_roof_guard.scad',
        HERE.parent/'perpendicular-u-joint-guard-v1.11-fit-21xy-22z/fit_clearance_guard.scad']
    report['source_sha256']={str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    report['output_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'guard-v1.15-body.stl',OUT/'guard-v1.15.stl']}
    (REVIEW/'build-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
