"""Verify actual 3MF transforms and G-code, including manual support blockers."""
from pathlib import Path
import zipfile,json,hashlib,xml.etree.ElementTree as ET,re,math
from collections import defaultdict
import sys
HERE=Path(__file__).resolve().parent;OUT=Path(sys.argv[1]).resolve()
BORE=json.loads((HERE/'pin-bore-wall-probe.json').read_text())
C='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';P='http://schemas.microsoft.com/3dmanufacturing/production/2015/06';ns={'c':C}
def main():
 manifest=json.loads((OUT/'manifest.json').read_text());records={r['name']+'.stl':r for r in manifest['objects']}
 package=OUT/manifest['sliced_3mf'];objects=[]
 with zipfile.ZipFile(package) as gz, zipfile.ZipFile(OUT/manifest['editable_3mf']) as z:
  # Native GUI slice exports are toolpath-only archives; editable project owns meshes.
  root=ET.fromstring(z.read('3D/3dmodel.model'));model=ET.fromstring(z.read('Metadata/model_settings.config'));cfg=json.loads(z.read('Metadata/project_settings.config'));plates=ET.fromstring(gz.read('Metadata/slice_info.config')).findall('plate');assert len(plates)==1
  plate=plates[0];meta={e.get('key'):e.get('value') for e in plate.findall('metadata')};labels={int(e.get('identify_id')):e.get('name') for e in plate.findall('object')}
  assert len(labels)==manifest['quantity'] and all(e.get('skipped')=='false' for e in plate.findall('object')) and meta['outside']=='false'
  assert cfg['printer_model']=='Bambu Lab X1 Carbon' and cfg['filament_type']==['PETG'] and cfg['nozzle_diameter']==['0.4']
  assert cfg['wall_loops']=='5' and cfg['layer_height']=='0.2' and cfg['sparse_infill_density']=='20%'
  for item in root.findall('c:build/c:item',ns):
   oid=item.get('objectid');mc=model.find(f"object[@id='{oid}']");name=next(e.get('value') for e in mc.findall('metadata') if e.get('key')=='name');r=records[name]
   tf=[float(v) for v in item.get('transform').split()];assert tf[:9]==[1,0,0,0,1,0,0,0,1]
   obj=root.find(f"c:resources/c:object[@id='{oid}']",ns);vertices=[];blockers=0
   for comp in obj.findall('c:components/c:component',ns):
    part=mc.find(f"part[@id='{comp.get('objectid')}']");assert part is not None
    subtype=part.get('subtype')
    if subtype=='support_blocker':blockers+=1;continue
    assert subtype=='normal_part'
    stats=part.find('mesh_stat');assert all(int(stats.get(k,'0'))==0 for k in ['edges_fixed','degenerate_facets','facets_removed','facets_reversed','backwards_edges'])
    cm=[float(v) for v in comp.get('transform').split()];assert cm[:9]==[1,0,0,0,1,0,0,0,1]
    f=ET.fromstring(z.read(comp.get('{'+P+'}path').lstrip('/')));mesh=f.find(f"c:resources/c:object[@id='{comp.get('objectid')}']/c:mesh",ns)
    for v in mesh.findall('c:vertices/c:vertex',ns):vertices.append([float(v.get(a))+cm[9+j]+tf[9+j] for j,a in enumerate('xyz')])
   assert blockers==len(r['support_blockers'])
   low=[min(v[j] for v in vertices) for j in range(3)];high=[max(v[j] for v in vertices) for j in range(3)]
   assert abs(low[2])<.001 and all(abs(high[j]-low[j]-r['size_mm'][j])<.001 for j in range(3))
   assert all(abs(low[j]-r['bed_min_xy_mm'][j])<.001 for j in (0,1))
   objects.append({'name':name,'min_mm':low,'max_mm':high,'support_blocker_count':blockers,'mesh_repairs':0})
  assert len(objects)==manifest['quantity']
  data=gz.read('Metadata/plate_1.gcode');assert hashlib.md5(data).hexdigest()==gz.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
 xyz=[0.,0.,0.];relative=True;absolute=True;epos=0.;active=False;current=None;role='';layer=0
 groups=defaultdict(lambda:{'moves':0,'filament_mm':0.,'min':[math.inf]*3,'max':[-math.inf]*3})
 forbidden=defaultdict(int);nearby_pin=[];bounds=[math.inf,math.inf,-math.inf,-math.inf];segments=[];excluded_hits=[]
 for line in data.decode().splitlines():
  if line.startswith('; CHANGE_LAYER'):active=True;layer+=1
  if line.startswith('; OBJECT_ID:'):current=int(line.rsplit(':',1)[1]);role=''
  if line.startswith('; start printing object, unique label id:'):current=int(line.rsplit(':',1)[1]);role=''
  if line.startswith('; stop printing object, unique label id:'):current=None;role=''
  if line.startswith('; FEATURE: '):role=line[11:]
  code=line.split(';',1)[0].strip()
  if code=='M83':relative=True
  elif code=='M82':relative=False
  elif code=='G90':absolute=True
  elif code=='G91':absolute=False
  elif code.startswith('G92 '):
   v=re.search(r'\bE([-+\d.]+)',code)
   if v:epos=float(v[1])
  elif re.match(r'^G[0123]\s',code):
   values={k:float(v) for k,v in re.findall(r'([XYZEF])([-+\d.]+)',code)};old=list(xyz)
   for j,k in enumerate('XYZ'):
    if k in values:xyz[j]=values[k] if absolute else xyz[j]+values[k]
   extrusion=(values.get('E',0) if relative else values.get('E',epos)-epos)
   if 'E' in values:epos=values['E']
   if not active or current not in labels or extrusion<=0 or math.dist(old,xyz)<1e-7:continue
   name=labels[current];g=groups[(name,role)]
   if min(old[0],xyz[0])<18 and min(old[1],xyz[1])<28:excluded_hits.append({'object':name,'from':old,'to':list(xyz),'role':role})
   g['moves']+=1;g['filament_mm']+=extrusion
   for j in range(3):g['min'][j]=min(g['min'][j],old[j],xyz[j]);g['max'][j]=max(g['max'][j],old[j],xyz[j])
   bounds=[min(bounds[0],old[0],xyz[0]),min(bounds[1],old[1],xyz[1]),max(bounds[2],old[0],xyz[0]),max(bounds[3],old[1],xyz[1])]
   if role.startswith('Support'):
    # Conservative segment samples in the intentionally protected bounding volumes.
    r=records[name]
    for reg in r['support_blockers']:
     lo=[reg['normalized_min_mm'][j]+(r['bed_min_xy_mm'][j] if j<2 else 0) for j in range(3)];hi=[reg['normalized_max_mm'][j]+(r['bed_min_xy_mm'][j] if j<2 else 0) for j in range(3)]
     count=max(1,math.ceil(math.dist(old,xyz)/.4))
     points=[[old[j]+(xyz[j]-old[j])*i/count for j in range(3)] for i in range(count+1)]
     inside=[p for p in points if all(lo[j]+.001<p[j]<hi[j]-.001 for j in range(3))]
     if inside:
      if reg['label']=='pull-pin alignment bore':
       # Pin bore is a vertical source-space cylinder, diameter 5.4mm.
       angles=[v*math.pi/180 for v in r['rotation_xyz_deg']];cx,sx=math.cos(angles[0]),math.sin(angles[0]);cy,sy=math.cos(angles[1]),math.sin(angles[1]);cz,sz=math.cos(angles[2]),math.sin(angles[2])
       R=[[cy*cz,cz*sx*sy-cx*sz,sx*sz+cx*cz*sy],[cy*sz,cx*cz+sx*sy*sz,cx*sy*sz-cz*sx],[-sy,cy*sx,cx*cy]]
       actual=[]
       for p in inside:
        q=[p[j]-(r['bed_min_xy_mm'][j] if j<2 else 0)-r['normalized_translation_mm'][j] for j in range(3)];source=[sum(R[j][i]*q[j] for j in range(3)) for i in range(3)]
        assert r['source_sha256']==BORE['source_sha256']
        if math.hypot(source[0]-BORE['center_xy_mm'][0],source[1]-BORE['center_xy_mm'][1])<BORE['hole_radius_mm']-.001:
         if BORE['actual_bore_wall_interval_mm'][0]+.001<source[2]<BORE['actual_bore_wall_interval_mm'][1]-.001:actual.append(source)
         elif source[2]<BORE['actual_bore_wall_interval_mm'][0]:nearby_pin.append(source[2])
       if not actual:continue
      forbidden[(name,role,reg['label'])]+=1
 # Every object has actual non-support model extrusion, not just a metadata item.
 assert all(any(n==name and not role.startswith('Support') and g['moves']>0 for (n,role),g in groups.items()) for name in records)
 assert bounds[0]>=0 and bounds[1]>=0 and bounds[2]<=256 and bounds[3]<=256,bounds
 support={name:{role:g for (n,role),g in groups.items() if n==name and role.startswith('Support')} for name in records}
 grams=sum(g['filament_mm'] for (n,r),g in groups.items() if r.startswith('Support'))*math.pi*(1.75/2)**2*1.27/1000
 report={'package':package.name,'geometry_project':manifest['editable_3mf'],'geometry_project_sha256':hashlib.sha256((OUT/manifest['editable_3mf']).read_bytes()).hexdigest(),'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'plate_count':1,'object_count':len(objects),'objects':objects,'prediction_seconds':int(meta['prediction']),'weight_g':float(meta['weight']),'support_estimated_g_from_extrusions':grams,'extruding_xy_bounds_mm':bounds,'support_extrusions':support,'pin_bore_actual_wall_interval_mm':BORE['actual_bore_wall_interval_mm'],'pin_bore_cavity_support_below_wall_z_range_mm':[min(nearby_pin),max(nearby_pin)] if nearby_pin else None,'excluded_corner_hits':excluded_hits,'protected_region_support_hits':[{'name':k[0],'role':k[1],'region':k[2],'moves':v} for k,v in forbidden.items()],'source_print_rotation_verified':True,'gcode_md5_verified':True,'printer_sent':False}
 (OUT/'package-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['object_count','prediction_seconds','weight_g','support_estimated_g_from_extrusions','extruding_xy_bounds_mm','protected_region_support_hits']},indent=2))
 assert not forbidden,'Support entered intentionally protected regions; inspect before release'
 assert not excluded_hits,'Extrusions entered X1C excluded corner'
if __name__=='__main__':main()
