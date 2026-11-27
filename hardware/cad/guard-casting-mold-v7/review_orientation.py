from pathlib import Path
import trimesh,numpy as np,json
from shapely.geometry import Polygon,Point
HERE=Path(__file__).resolve().parent
out=[]
for k in ['left','right','lid','lower','back','upper','screw','clamp-Y']:
 t=trimesh.load(HERE.parent/'exports/guard-casting-mold-v7'/(k+'.stl'))
 for r in [(0,0,0),(180,0,0),(90,0,0),(-90,0,0),(0,90,0),(0,-90,0)]:
  m=t.copy();m.apply_transform(trimesh.transformations.euler_matrix(*np.radians(r)));m.apply_translation(-m.bounds[0]);sec=m.section([0,0,1],[0,0,.12]);poly=Polygon()
  if sec:
   for p in sec.discrete:
    if len(p)>3:poly=poly.symmetric_difference(Polygon(p[:,:2]).buffer(0))
  cm=m.center_mass[:2];hull=poly.convex_hull;inside=hull.contains(Point(cm));margin=hull.boundary.distance(Point(cm))*(1 if inside else -1) if not hull.is_empty else -999
  mask=(m.face_normals[:,2]<-.7)&(m.triangles_center[:,2]>1)
  down=float(m.area_faces[mask].sum());entry={'part':k,'r':r,'size':m.extents.round(1).tolist(),'bed_area_mm2':round(poly.area,1),'COM_margin_mm':round(margin,1),'downward_area_proxy_mm2':round(down,1)};out.append(entry);print(entry,flush=True)
(HERE/'orientation-review.json').write_text(json.dumps(out,indent=2)+'\n')
