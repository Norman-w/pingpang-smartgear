"""Check all eight same-source printed screws against actual assembled mold meshes."""
from pathlib import Path
import json,math
import numpy as np,trimesh,manifold3d as m
from preview_manifest import SITES
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'exports/guard-casting-mold-v7'
def load(k):
 t=trimesh.load(OUT/(k+'.stl'));assert t.is_watertight and t.is_volume,k
 return m.Manifold(m.Mesh64(np.asarray(t.vertices,dtype=np.float64),np.asarray(t.faces,dtype=np.uint64)))
solids={k:load(k) for k in ['left','right','lid','upper','lower','back','pin','product']};screw=load('screw');checks=[];placed=[]
for id,parent,pos,rot in SITES:
 part=screw.rotate([r*180/math.pi for r in rot]).translate(pos);placed.append((id,part))
 for k,other in solids.items():
  v=abs((part^other).volume());checks.append({'screw':id,'part':k,'overlap_mm3':v});assert v<.02,(id,k,v)
 # Tip remains at the initial reaction plane while its own mold advances 3mm.
 advanced=screw.rotate([0,0,-135]).translate([0,0,-3]).rotate([r*180/math.pi for r in rot]).translate(pos)
 normal=np.array([0,0,1] if parent=='lid' else [0,1,0] if parent=='lower' else [0,-1,0] if parent=='back' else [1,0,0])
 advanced=advanced.translate(normal*3)
 v=abs((advanced^solids[parent].translate(normal*3)).volume());assert v<.02,(id,'advance',v)
 checks.append({'screw':id,'part':parent+' advanced3mm','overlap_mm3':v})
for i,(a,sa) in enumerate(placed):
 for b,sb in placed[i+1:]:
  v=abs((sa^sb).volume());assert v<.02,(a,b,v)
report={'status':'PASS_SAMPLED_ASSEMBLED_SCREW_GEOMETRY','screw_instances':8,'checks':checks,'maximum_overlap_mm3':max(x['overlap_mm3'] for x in checks),'physical_torque_strength_and_wear':'not_tested'}
(HERE/'screw-assembly-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report['status'],report['maximum_overlap_mm3'])
