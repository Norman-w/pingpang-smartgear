#!/usr/bin/env python3
"""Read-only printer-free audit of the generated v1.11 two-object package."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'exports/perpendicular-u-joint-v1.11-fit-21xy-22z/two-piece-x1c'
manifest=json.loads((OUT/'manifest.json').read_text())
package=OUT/manifest['sliced_3mf']
ns={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02',
    'p':'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'}
with zipfile.ZipFile(package) as archive:
    cfg=json.loads(archive.read('Metadata/project_settings.config'))
    root=ET.fromstring(archive.read('3D/3dmodel.model'))
    items=root.findall('c:build/c:item',ns)
    info=ET.fromstring(archive.read('Metadata/slice_info.config'))
    plates=info.findall('plate')
    assert len(items)==2 and len(plates)==1
    objects=plates[0].findall('object')
    assert len(objects)==2 and all(o.get('skipped')=='false' for o in objects)
    metadata={v.get('key'):v.get('value') for v in plates[0].findall('metadata')}
    assert metadata['outside']=='false'
    meshes=[]
    for item in items:
        matrix=[float(v) for v in item.get('transform').split()]
        assert matrix[:9]==[1,0,0,0,1,0,0,0,1]
        ref=root.find(f"c:resources/c:object[@id='{item.get('objectid')}']/c:components/c:component",ns)
        assert [float(v) for v in ref.get('transform').split()]==[1,0,0,0,1,0,0,0,1,0,0,0]
        part=ET.fromstring(archive.read(ref.get('{'+ns['p']+'}path').lstrip('/')))
        verts=[[float(v.get(a))+matrix[9+i] for i,a in enumerate('xyz')]
               for v in part.findall('.//c:vertex',ns)]
        low=[min(v[i] for v in verts) for i in range(3)]
        high=[max(v[i] for v in verts) for i in range(3)]
        size=[high[i]-low[i] for i in range(3)]
        assert all(abs(a-b)<0.001 for a,b in zip(size,[55.8,67,54.5]))
        assert abs(low[2])<0.001 and all(low[i]>5 and high[i]<251 for i in [0,1])
        meshes.append({'object_id':item.get('objectid'),'min_mm':low,'max_mm':high})
    meshes.sort(key=lambda a:a['min_mm'][0])
    assert meshes[1]['min_mm'][0]-meshes[0]['max_mm'][0]>20
    data=archive.read('Metadata/plate_1.gcode')
    md5=archive.read('Metadata/plate_1.gcode.md5').decode().strip()
    assert hashlib.md5(data).hexdigest()==md5.lower()
    for member in ['Metadata/plate_1.png','Metadata/top_1.png']:
        if member in archive.namelist():
            (OUT/Path(member).name).write_bytes(archive.read(member))
assert cfg['printer_settings_id']=='Bambu Lab X1 Carbon 0.4 nozzle'
assert cfg['filament_type']==['PETG'] and cfg['filament_settings_id']==['Generic PETG']
assert len(cfg['filament_self_index'])==len(cfg['filament_extruder_variant'])
assert cfg['curr_bed_type']=='Textured PEI Plate'
assert cfg['wall_loops']=='6' and cfg['sparse_infill_density']=='30%'
assert cfg['xy_hole_compensation']=='0' and cfg['xy_contour_compensation']=='0'
assert cfg['enable_support']=='1' and cfg['support_on_build_plate_only']=='1'
assert hashlib.sha256((HERE/'fit_clearance_guard.scad').read_bytes()).hexdigest()==manifest['source_scad_sha256']
assert hashlib.sha256((HERE.parent/manifest['source_stl']).read_bytes()).hexdigest()==manifest['source_sha256']

roles=defaultdict(list)
xyz=[0.,0.,0.]; role=''; relative_e=True; e_position=0.; absolute_xyz=True
for line in data.decode().splitlines():
    if line.startswith('; FEATURE: '): role=line[len('; FEATURE: '):]
    code=line.split(';')[0].strip()
    if code=='M83': relative_e=True
    elif code=='M82': relative_e=False
    elif code=='G90': absolute_xyz=True
    elif code=='G91': absolute_xyz=False
    elif code.startswith('G92 '):
        match=re.search(r'\bE([-+\d.]+)',code)
        if match: e_position=float(match[1])
    elif re.match(r'^G[0123]\s',code):
        values={k:float(v) for k,v in re.findall(r'([XYZEF])([-+\d.]+)',code)}
        for i,k in enumerate('XYZ'):
            if k in values: xyz[i]=values[k] if absolute_xyz else xyz[i]+values[k]
        e=values.get('E',0) if relative_e else values.get('E',e_position)-e_position
        if 'E' in values: e_position=values['E']
        if e>0 and role.startswith('Support'): roles[role].append((*xyz,e))
support={k:{'extruding_moves':len(v),
            'min_mm':[min(p[i] for p in v) for i in range(3)],
            'max_mm':[max(p[i] for p in v) for i in range(3)]} for k,v in roles.items()}
assert 'Support' in support and 'Support interface' in support
# In this roof-down pose the functional lower pocket starts at print Z=31;
# lips start at Z=53. All ordinary/interface/transition supports must stay
# beneath that zone, not merely appear at a requested ramp in a screenshot.
assert all(v['max_mm'][2]<31 for v in support.values())
report={'package':package.name,'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
        'source_scad_sha256':manifest['source_scad_sha256'],
        'source_stl_sha256':manifest['source_sha256'],
        'object_count':2,'plate_count':1,'objects':meshes,
        'prediction_seconds':int(metadata['prediction']),'weight_g':float(metadata['weight']),
        'support_extrusions':support,'functional_pocket_support_free':True,
        'checks_passed':True,'printer_sent':False,'printer_started':False,
        'physical_fit_and_strength':'not_tested'}
(OUT/'package-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
