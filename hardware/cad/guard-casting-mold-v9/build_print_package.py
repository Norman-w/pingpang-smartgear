"""Five explicit X1C/PETG plates: 7 integral-seat clamp rods, exactly 2 J screws."""
from pathlib import Path
import json,hashlib,tempfile,subprocess,zipfile,shutil,sys,importlib.util
import xml.etree.ElementTree as ET
import numpy as np,trimesh
from print_aids import add_print_aid
HERE=Path(__file__).resolve().parent;CAD=HERE.parent
SRC=CAD/'exports/guard-casting-mold-v7';OUT=CAD/'print-packages/guard-mold-v9-HOLD-X1C-PETG';OUT.mkdir(parents=True,exist_ok=True)
BAMBU='/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
TEMPLATE=CAD/'print-packages/guard-mold-v2-X1C-PETG/guard-mold-v2-7parts-X1C-PETG.3mf'
sys.path.insert(0,str(CAD));spec=importlib.util.spec_from_file_location('old',CAD/'guard-casting-mold-v2/build_print_package.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
C=old.C;P=old.P
# Angles apply Rx then Ry then Rz. XY is rotated bbox lower-left, millimeters.
PLAN=[
 [('screw',(180,0,0),(24,24),'J1'),('screw',(180,0,0),(96,24),'J2'),('clamp-Z',(180,0,0),(168,24),'Z1'),('clamp-Z',(180,0,0),(24,96),'Z2'),('clamp-Z',(180,0,0),(96,96),'Z3'),('clamp-Z',(180,0,0),(168,96),'Z4'),('clamp-X',(180,0,0),(24,168),'X1'),('clamp-Y',(180,0,0),(96,168),'Y1'),('clamp-Y',(180,0,0),(168,168),'Y2')],
 [('left',(0,0,90),(12,34),'A'),('right',(0,0,90),(12,126),'B')],
 [('lower',(0,0,0),(10,34),'E')],
 [('back',(0,0,0),(10,34),'F'),('upper',(0,0,0),(24,138),'D'),('pin',(180,0,0),(170,138),'G')],
 [('lid',(0,0,0),(24,19),'C')]
]
LABELS=['upright-fasteners-9','upright-shells-AB','flat-core-E','flat-core-F-D-G','flat-lid-C']

def run(args,log):
 r=subprocess.run(args,capture_output=True,text=True);log.write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise RuntimeError(str(log)+' exit '+str(r.returncode)+'\n'+r.stdout[-1200:]+r.stderr[-1200:])
def main():
 counts={};selected=int(sys.argv[1]) if len(sys.argv)>1 else None;plates=[]
 if selected and (OUT/'manifest.json').exists():
  plates=[p for p in json.loads((OUT/'manifest.json').read_text())['plates'] if p['plate']!=selected]
  for p in plates:
   for r in p['objects']:counts[r['id']]=counts.get(r['id'],0)+1
 with zipfile.ZipFile(TEMPLATE) as z:basecfg=json.loads(z.read('Metadata/project_settings.config'))
 expected={x['id']:x['sha256'] for x in json.loads((CAD/'guard-casting-mold-v7/validation.json').read_text())['parts']}
 for pi,plan in enumerate(PLAN,1):
  if selected and pi!=selected:continue
  plateout=OUT/f'plate-{pi:02d}-{LABELS[pi-1]}';plateout.mkdir(exist_ok=True);records=[];posed=[]
  cfg=dict(basecfg);cfg.update({'print_settings_id':'Guard mold v9 HOLD anti-tip X1C PETG','filament_colour':['#000000'],'layer_height':'0.2','initial_layer_print_height':'0.2','wall_loops':'5','top_shell_layers':'6','bottom_shell_layers':'6','sparse_infill_density':'20%','sparse_infill_pattern':'gyroid','wall_generator':'arachne','enable_support':'1','support_type':'normal(auto)','support_style':'snug','support_on_build_plate_only':'0','support_threshold_angle':'40','support_top_z_distance':'0.24','support_bottom_z_distance':'0.24','support_object_xy_distance':'0.4','support_remove_small_overhang':'1','brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.15','enable_prime_tower':'0'})
  for k,angles,xy,name in plan:
   counts[k]=counts.get(k,0)+1;source=SRC/(k+'.stl');sha=hashlib.sha256(source.read_bytes()).hexdigest()
   if k in expected:assert sha==expected[k],k
   t=trimesh.load(source);assert t.is_watertight and t.is_volume,k
   matrix=trimesh.transformations.euler_matrix(*np.radians(angles));t.apply_transform(matrix);shift=-t.bounds[0];t.apply_translation(shift)
   aid=None
   if k in ('left','right','lid','lower','back','screw') or k.startswith('clamp-'):
    t,aid,aid_shift=add_print_aid(t,k);shift+=aid_shift
   size=t.extents.tolist()
   path=plateout/(name+'.stl');t.export(path);posed.append(path)
   if aid:
    aid.pop('_aid_mesh').export(plateout/(name+'-removable-aid.stl'))
    original=trimesh.load(source);original.apply_transform(matrix);original.apply_translation(shift);original.export(plateout/(name+'-body.stl'))
   assert min(xy)>=8 and xy[0]+size[0]<=252.01 and xy[1]+size[1]<=252.01,(name,size,xy)
   records.append({'id':k,'name':name,'source_sha256':sha,'rotation_xyz_deg':angles,'normalized_translation_mm':shift.tolist(),'size_mm':size,'bed_min_xy_mm':xy,'scale':1,'support_blockers':[],'print_aid':aid})
  for i,a in enumerate(records):
   for b in records[i+1:]:
    gap=max(max(a['bed_min_xy_mm'][j]-b['bed_min_xy_mm'][j]-b['size_mm'][j],b['bed_min_xy_mm'][j]-a['bed_min_xy_mm'][j]-a['size_mm'][j]) for j in (0,1))
    assert gap>=7.5,(a['name'],b['name'],gap)
  stem=f'guard-mold-v9-HOLD-plate-{pi:02d}-X1C-black-PETG';editable=plateout/(stem+'.3mf');sliced=plateout/(stem+'.gcode.3mf')
  with tempfile.TemporaryDirectory(prefix='mold-v7-plate-') as tmp:
   tmp=Path(tmp);seed=tmp/'seed.3mf'
   run([BAMBU,'--datadir',str(tmp/'seed-data'),'--arrange','0','--orient','0','--export-3mf',str(seed),*map(str,posed)],plateout/'seed.log')
   with zipfile.ZipFile(seed) as z:files={n:z.read(n) for n in z.namelist()}
   root=ET.fromstring(files['3D/3dmodel.model']);model=ET.fromstring(files['Metadata/model_settings.config']);ET.register_namespace('',C);ET.register_namespace('p',P)
   items=root.findall(f'{{{C}}}build/{{{C}}}item');assert len(items)==len(records);assert len(model.findall('plate'))==1
   block_id=1000
   for item,r in zip(items,records):
    obj=root.find(f"{{{C}}}resources/{{{C}}}object[@id='{item.get('objectid')}']");comp=obj.find(f'{{{C}}}components/{{{C}}}component');cm=list(map(float,comp.get('transform').split()));assert cm[:9]==[1,0,0,0,1,0,0,0,1]
    body=ET.fromstring(files[comp.get('{'+P+'}path').lstrip('/')]);verts=[[float(v.get(a)) for a in 'xyz'] for v in body.findall('.//{'+C+'}vertex')];lo=[min(v[j] for v in verts)+cm[9+j] for j in range(3)]
    tf=item.get('transform').split();assert list(map(float,tf[:9]))==[1,0,0,0,1,0,0,0,1];tf[9:]=[str(r['bed_min_xy_mm'][0]-lo[0]),str(r['bed_min_xy_mm'][1]-lo[1]),str(-lo[2])];item.set('transform',' '.join(tf));r['object_id']=item.get('objectid')
    mc=model.find(f"object[@id='{item.get('objectid')}']")
    settings={}
    if r['id']=='right':settings.update({'support_type':'tree(auto)','support_style':'default','support_on_build_plate_only':'1'})
    if r['id']=='screw':
     settings={'wall_loops':'6','sparse_infill_density':'100%','sparse_infill_pattern':'cubic','top_shell_layers':'6','bottom_shell_layers':'6'}
    elif r['id'].startswith('clamp-'):
     # Smaller installation rods: perimeter carries the printed thread and
     # root load; moderate infill is sufficient, unlike the demolding J rods.
     settings={'wall_loops':'4','sparse_infill_density':'50%','sparse_infill_pattern':'cubic','top_shell_layers':'6','bottom_shell_layers':'6'}
    if r['id'] in ('pin','upper','screw') or r['id'].startswith('clamp-'):settings['enable_support']='0'
    for key,val in settings.items():ET.SubElement(mc,'metadata',{'key':key,'value':val})
    if r['id'] in ('left','right','lid','lower','back'):
     r['support_blockers']=[] if r['id']=='lid' else old.protected_regions(r['id'])
     for region in r['support_blockers']:
      if r['id']=='right' and region['label']=='pull-pin alignment bore':
       region['source_min_mm'][2]=-80;region['source_max_mm'][2]=44
      block_id+=1;old.add_blocker(root,model,files,item,region,r,block_id)
   for a in list(model.findall('assemble')):model.remove(a)
   pl=model.find('plate');next(e for e in pl.findall('metadata') if e.get('key')=='plater_name').set('value',f'v9-HOLD-{pi}-{LABELS[pi-1]}')
   files['3D/3dmodel.model']=ET.tostring(root,encoding='utf-8',xml_declaration=True);files['Metadata/model_settings.config']=ET.tostring(model,encoding='utf-8',xml_declaration=True);files['Metadata/project_settings.config']=json.dumps(cfg).encode();files['Metadata/filament_sequence.json']=json.dumps({'plate_1':{'nozzle_sequence':[0],'optimal_assignment':[0],'sequence':[1]}}).encode()
   with zipfile.ZipFile(editable,'w',zipfile.ZIP_DEFLATED) as z:
    for n,data in files.items():
     if n!='Metadata/slice_info.config':z.writestr(n,data)
   run([BAMBU,'--datadir',str(tmp/'slice-data'),'--arrange','0','--orient','0','--slice','0','--mstpp','1800','--export-3mf',str(sliced),str(editable)],plateout/'slice.log')
  with zipfile.ZipFile(sliced) as z:
   gc=z.read('Metadata/plate_1.gcode').decode();info=ET.fromstring(z.read('Metadata/slice_info.config')).find('plate');meta={x.get('key'):x.get('value') for x in info.findall('metadata')}
   for image in ['plate_1.png','top_1.png']:
    if 'Metadata/'+image in z.namelist():(plateout/image).write_bytes(z.read('Metadata/'+image))
   estimate={k:meta.get(k) for k in ['prediction','weight','outside','support_used']}
  rec={'plate':pi,'name':LABELS[pi-1],'editable_3mf':str(editable.relative_to(OUT)),'sliced_3mf':str(sliced.relative_to(OUT)),'objects':records,'estimate':estimate,'sent':False,'started':False};plates.append(rec)
  (OUT/'manifest.json').write_text(json.dumps({'revision':'v9-print-orientation','do_not_print':True,'release_status':'HOLD_USER_REQUEST','printer':'X1 Carbon 0.4mm','material':'black PETG','total_quantity':sum(counts.values()),'counts_so_far':counts,'planned_counts':json.loads((CAD/'guard-casting-mold-v7/print-quantities.json').read_text()),'plates':plates},ensure_ascii=False,indent=2)+'\n')
  print('PLATE_READY',pi,estimate,flush=True)
 expected_counts={Path(x['file']).stem:x['copies'] for x in json.loads((CAD/'guard-casting-mold-v7/print-quantities.json').read_text())}
 if counts==expected_counts:print('COMPLETE_16_PIECES_5_PLATES',flush=True)
 else:print('PARTIAL_REBUILD_COUNTS',counts,flush=True)
if __name__=='__main__':main()
