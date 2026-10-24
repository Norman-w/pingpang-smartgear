#!/usr/bin/env python3
"""Offline audit of six-object upright package; never contacts a printer."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

CAD = Path(__file__).resolve().parent.parent
OUT = CAD / 'print-packages/barrier-clip-v1.15-6x-black-PETG'
manifest = json.loads((OUT / 'manifest.json').read_text())
ns = {'c': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02',
      'p': 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'}
package = OUT / manifest['sliced_3mf']
with zipfile.ZipFile(package) as z:
    cfg = json.loads(z.read('Metadata/project_settings.config'))
    root = ET.fromstring(z.read('3D/3dmodel.model'))
    items = root.findall('c:build/c:item', ns)
    plates = ET.fromstring(z.read('Metadata/slice_info.config')).findall('plate')
    assert len(items) == 6 and len(plates) == 1
    objects = plates[0].findall('object')
    assert len(objects) == 6 and all(o.get('skipped') == 'false' for o in objects)
    metadata = {e.get('key'): e.get('value') for e in plates[0].findall('metadata')}
    assert metadata['outside'] == 'false'
    meshes = []
    for item in items:
        matrix = [float(v) for v in item.get('transform').split()]
        assert matrix[:9] == [1,0,0,0,1,0,0,0,1]
        ref = root.find(f"c:resources/c:object[@id='{item.get('objectid')}']/c:components/c:component", ns)
        assert [float(v) for v in ref.get('transform').split()] == [1,0,0,0,1,0,0,0,1,0,0,0]
        part = ET.fromstring(z.read(ref.get('{'+ns['p']+'}path').lstrip('/')))
        verts = [[float(v.get(a)) + matrix[9+i] for i,a in enumerate('xyz')]
                 for v in part.findall('.//c:vertex', ns)]
        low = [min(v[i] for v in verts) for i in range(3)]
        high = [max(v[i] for v in verts) for i in range(3)]
        assert all(abs(high[i]-low[i]-s)<.001 for i,s in enumerate((55.8,67,55.1)))
        assert abs(low[2]) < .001 and all(low[i]>5 and high[i]<251 for i in (0,1))
        meshes.append({'object_id': item.get('objectid'), 'min_mm': low, 'max_mm': high})
    for i,a in enumerate(meshes):
        for b in meshes[i+1:]:
            assert any(max(a['min_mm'][j]-b['max_mm'][j], b['min_mm'][j]-a['max_mm'][j])>10 for j in (0,1))
    data = z.read('Metadata/plate_1.gcode')
    assert hashlib.md5(data).hexdigest() == z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()

with zipfile.ZipFile(CAD/'print-packages/barrier-clip-v1.11-first-article/barrier-clip-v1.11-2x-upright-tree-actual.3mf') as z:
    previous = json.loads(z.read('Metadata/project_settings.config'))
keys = ('printer_settings_id','curr_bed_type','layer_height','wall_loops',
        'sparse_infill_density','sparse_infill_pattern','top_shell_layers','bottom_shell_layers',
        'enable_support','support_type','support_on_build_plate_only','support_top_z_distance',
        'support_bottom_z_distance','support_interface_top_layers','support_interface_spacing',
        'support_object_xy_distance','brim_type','brim_width','brim_object_gap',
        'filament_type','filament_settings_id','nozzle_temperature','nozzle_temperature_initial_layer',
        'textured_plate_temp','textured_plate_temp_initial_layer',
        'xy_hole_compensation','xy_contour_compensation')
assert all(cfg[k] == previous[k] for k in keys)
assert cfg['filament_colour'] == ['#000000']
assert hashlib.sha256((OUT/'guard-v1.15.stl').read_bytes()).hexdigest() == manifest['source_sha256']

roles = defaultdict(list)
xyz = [0.,0.,0.]; role = ''; relative_e = True; e_position = 0.; absolute_xyz = True
for line in data.decode().splitlines():
    if line.startswith('; FEATURE: '): role = line[len('; FEATURE: '):]
    code = line.split(';')[0].strip()
    if code == 'M83': relative_e = True
    elif code == 'M82': relative_e = False
    elif code == 'G90': absolute_xyz = True
    elif code == 'G91': absolute_xyz = False
    elif code.startswith('G92 '):
        match = re.search(r'\bE([-+\d.]+)', code)
        if match: e_position = float(match[1])
    elif re.match(r'^G[0123]\s', code):
        values = {k:float(v) for k,v in re.findall(r'([XYZEF])([-+\d.]+)', code)}
        for i,k in enumerate('XYZ'):
            if k in values: xyz[i] = values[k] if absolute_xyz else xyz[i]+values[k]
        e = values.get('E',0) if relative_e else values.get('E',e_position)-e_position
        if 'E' in values: e_position = values['E']
        if e>0 and role.startswith('Support'): roles[role].append((*xyz,e))
support = {k:{'extruding_moves':len(v), 'min_mm':[min(p[i] for p in v) for i in range(3)],
              'max_mm':[max(p[i] for p in v) for i in range(3)]} for k,v in roles.items()}
assert 'Support' in support and 'Support interface' in support
assert all(v['min_mm'][2] >= .19 and v['max_mm'][2] < 47 for v in support.values())
report = {'package':package.name,'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
          'source_sha256':manifest['source_sha256'],'objects':meshes,'object_count':6,'plate_count':1,
          'prediction_seconds':int(metadata['prediction']),'weight_g':float(metadata['weight']),
          'matched_actual_recipe_keys':list(keys),'support_extrusions':support,
          'checks_passed':True,'physical_fit_and_strength':'not_tested'}
(OUT/'package-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
