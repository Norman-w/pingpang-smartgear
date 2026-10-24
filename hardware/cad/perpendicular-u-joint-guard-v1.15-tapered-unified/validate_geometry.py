#!/usr/bin/env python3
"""Probe unified seams, clearances and the bottom edge on the exported solid."""
import json
import numpy as np
import manifold3d as m
from build_export import HERE,OUT,REVIEW,load_stl

def box(lo,hi):
    return m.Manifold.cube(tuple(b-a for a,b in zip(lo,hi))).translate(lo)

body=load_stl(OUT/'guard-v1.15-body.stl')
full=load_stl(OUT/'guard-v1.15.stl')
assert len(body.decompose())==len(full.decompose())==1
report={}
# Four mirrored probes at each joint. None is a designed external bevel.
joints={
    'old_arm_to_added_thickness':((15.7,12,-19),(16.1,32,-2)),
    'ramp_to_arm':((11.7,23,-.1),(17.1,32,.1)),
    'rib_to_arm':((17.8,12,-12),(18,22,-8)),
    'rib_to_roof':((22,13,22.9),(24,19,23.1)),
    'upper_wall_to_arm':((11.7,12,-.1),(15,20,.1)),
    'old_upper_wall_to_tapered_rib_pocket':((15.8,12,.2),(16.3,20,1.8)),
}
for name,(lo,hi) in joints.items():
    missing=[]
    for sx in (-1,1):
        for sy in (-1,1):
            probe=box(lo,hi).scale((sx,sy,1))
            missing.append(abs((probe-body).volume()))
    report[name+'_missing_mm3']=max(missing)
    assert max(missing)<1e-6,(name,missing)

clearances={
    'upper_tube_entry':box((-60,-10.499,-60),(60,10.499,22.999)),
    'lower_foot':box((-10.899,-60,-21.999),(10.899,60,-.001)),
    'screw_bore':m.Manifold.cylinder(120,7.99,7.99,64).translate((0,0,-60)),
}
for name,probe in clearances.items():
    volume=abs((body^probe).volume())
    report[name+'_intrusion_mm3']=volume
    assert volume<1e-6,(name,volume)

mesh=body.to_mesh64()
vertices=mesh.vert_properties[:,:3]
bottom=vertices[np.abs(vertices[:,2]+23.5)<1e-5]
report['bottom_max_abs_x_mm']=float(np.max(np.abs(bottom[:,0])))
assert abs(report['bottom_max_abs_x_mm']-17.9)<1e-5
report['bottom_edge_y_intervals_mm']=[[-33.5,-10.5],[10.5,33.5]]
# Verify each designed bottom edge endpoint is present in the mesh.
for sx in (-1,1):
    for sy in (-1,1):
        for y in (10.5,33.5):
            p=np.array([sx*17.9,sy*y,-23.5])
            assert np.min(np.linalg.norm(bottom-p,axis=1))<2e-5
old=load_stl(HERE.parent/'exports/perpendicular-u-joint-v1.13-edge-safe-label/guard-v1.13-body.stl')
# Highest roof region is invariant, including the existing top chamfers.
top=box((-60,-60,24),(60,60,60))
report['upper_roof_change_mm3']=abs(((body-old)^top).volume())+abs(((old-body)^top).volume())
assert report['upper_roof_change_mm3']<.01
report['body_components']=len(body.decompose())
report['full_components']=len(full.decompose())
(REVIEW/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
