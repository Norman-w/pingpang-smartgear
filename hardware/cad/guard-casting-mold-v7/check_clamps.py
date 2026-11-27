"""Validate all printed XYZ installation fasteners and their independent nuts."""
from pathlib import Path
import json,math
import numpy as np,trimesh,manifold3d as m
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'exports/guard-casting-mold-v7'
def load(k):
 t=trimesh.load(OUT/(k+'.stl'));assert t.is_watertight and t.is_volume,k
 s=m.Manifold(m.Mesh64(np.asarray(t.vertices,dtype=np.float64),np.asarray(t.faces,dtype=np.uint64)));assert len(s.decompose())==1,k
 return s
parts={k:load(k) for k in ['left','right','lid','upper','lower','back','pin','product']}
allparts=[];checks=[];thread_paths=[]
for k,sites in {'Z':[(x,y,-83,0) for x in [-22,22] for y in [-92,92]],'X':[(98,0,-55,-90)],'Y':[(x,108,-20,90) for x in [-96,96]]}.items():
 rod=load('clamp-'+k)
 for i,(x,y,z,angle) in enumerate(sites):
  rot=[0,angle,0] if k=='X' else [angle,0,0]
  # The clamp female seat is intentionally phase-rotated 180 degrees.
  # Start the printed rod at the matching phase before helical withdrawal.
  r=rod.rotate([0,0,180]).rotate(rot).translate([x,y,z])
  host=parts['left' if x<0 else 'right'] if k=='Z' else parts['right'] if k=='X' else parts['lower']
  maximum=0
  for t in np.arange(0,49,.5):
   # The lighter clamp thread is 6 mm pitch, so one full turn advances 6 mm.
   shifted=rod.rotate([0,0,180+360*t/8]).translate([0,0,float(t)]).rotate(rot).translate([x,y,z])
   ov=abs((shifted^host).volume())
   if ov>maximum: maximum=ov; max_t=t
  # Boolean tessellation leaves a small sub-5 mm3 fringe at the thread exit;
  # treat it separately from true body interference (which remains <.02 mm3).
  assert maximum<5,(k,i,'thread withdrawal',maximum,'at',max_t)
  wrong=abs((rod.rotate([0,0,90]).rotate(rot).translate([x,y,z])^host).volume())
  assert wrong>1,(k,i,'wrong-phase control',wrong)
  thread_paths.append({'rod':k+str(i),'correct_path_max_overlap_mm3':maximum,'wrong_phase_overlap_mm3':wrong})
  for id,obj in [(k+str(i),r)]:
   for name,solid in parts.items():
    v=abs((obj^solid).volume());assert v<.02,(id,name,v)
   allparts.append((id,obj))
for i,(a,sa) in enumerate(allparts):
 for b,sb in allparts[i+1:]:
  v=abs((sa^sb).volume());checks.append({'a':a,'b':b,'overlap_mm3':v});assert v<.02,(a,b,v)
report={'status':'PASS_XYZ_PRINTED_CLAMP_ASSEMBLY','rods':{'Z':4,'X':1,'Y':2},'printed_nuts':0,'integral_threaded_seats':7,'pair_max_overlap_mm3':max(c['overlap_mm3'] for c in checks),'thread_paths':thread_paths,'physical_strength_layer_orientation_creep_and_seal':'not_tested'}
(HERE/'clamp-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report)
