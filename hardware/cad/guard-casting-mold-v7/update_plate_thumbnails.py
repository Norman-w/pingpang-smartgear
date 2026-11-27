"""Render real posed STL layouts and replace stale seed thumbnails, never toolpaths."""
from pathlib import Path
import json,subprocess,zipfile,hashlib
ROOT=Path(__file__).resolve().parent.parent/'print-packages/guard-mold-v7-X1C-PETG'
manifest=json.loads((ROOT/'manifest.json').read_text())
for r in manifest['plates']:
 folder=ROOT/Path(r['editable_3mf']).parent
 source=folder/'plate-preview.scad'
 source.write_text('\n'.join(f'translate([{o["bed_min_xy_mm"][0]},{o["bed_min_xy_mm"][1]},0]) import("{o["name"]}.stl");' for o in r['objects'])+'\n')
 for filename,angles in [('plate_1.png','55,0,45'),('top_1.png','0,0,0')]:
  subprocess.run(['/Users/norman/.local/bin/openscad','--render','--projection=o','--imgsize=512,512','--viewall','--autocenter','--camera=0,0,0,'+angles+',550','--colorscheme=Tomorrow','-o',str(folder/filename),str(source)],check=True,capture_output=True)
 for key in ['editable_3mf','sliced_3mf']:
  path=ROOT/r[key]
  with zipfile.ZipFile(path) as z:files={n:z.read(n) for n in z.namelist()}
  for n in ['Metadata/plate_1.png','Metadata/plate_no_light_1.png','Metadata/plate_1_small.png']:
   if n in files:files[n]=(folder/'plate_1.png').read_bytes()
  if 'Metadata/top_1.png' in files:files['Metadata/top_1.png']=(folder/'top_1.png').read_bytes()
  tmp=path.with_suffix('.tmp')
  with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
   for n,data in files.items():z.writestr(n,data)
  tmp.replace(path)
 audit=folder/'package-audit.json'
 if audit.exists():
  a=json.loads(audit.read_text());a['sha256']=hashlib.sha256((ROOT/r['sliced_3mf']).read_bytes()).hexdigest();a['geometry_project_sha256']=hashlib.sha256((ROOT/r['editable_3mf']).read_bytes()).hexdigest();a['thumbnails']='Updated from actual posed STL layout only; G-code bytes unchanged';audit.write_text(json.dumps(a,indent=2)+'\n')
 print('THUMBNAILS_UPDATED',r['plate'],flush=True)
