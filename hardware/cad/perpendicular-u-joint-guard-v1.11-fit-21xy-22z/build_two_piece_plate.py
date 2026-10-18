#!/usr/bin/env python3
"""Build/slice two v1.11 clips. Never send a printer command.

Only rigidly rotate the source STL roof-down; no scaling or mesh edits.
An existing editable X1C project supplies a full native setting envelope;
current installed official profiles replace machine/process/filament values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAD = HERE.parent
sys.path.insert(0, str(CAD))
from build_print_platter import (load_binary_stl, rotation_matrix_xyz,
    transform_bounds, transform_triangles, write_binary_stl)

BAMBU = Path('/Applications/BambuStudio.app/Contents/MacOS/BambuStudio')
PROFILES = BAMBU.parents[1] / 'Resources/profiles/BBL'
OUT = CAD / 'exports/perpendicular-u-joint-v1.11-fit-21xy-22z/two-piece-x1c'
SOURCE = OUT.parent / 'perpendicular-double-u-guard-v1.11.stl'

def run(args: list[str], log: Path) -> None:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, check=False)
    log.write_text(result.stdout)
    if result.returncode:
        raise RuntimeError(f'{log.name}: exit {result.returncode}\n{result.stdout[-5000:]}')

def profile(category: str, name: str) -> dict:
    data = json.loads((PROFILES / category / f'{name}.json').read_text())
    merged = profile(category, data['inherits']) if data.get('inherits') else {}
    for include in data.get('include', []):
        merged.update(profile(category, include))
    merged.update({k:v for k,v in data.items() if k not in {
        'type','name','inherits','include','from','instantiation','setting_id',
        'description','compatible_printers','compatible_printers_condition'}})
    return merged

def build(template: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source_mesh = load_binary_stl(SOURCE)
    rotation = rotation_matrix_xyz(180,0,0)
    lower, _ = transform_bounds(source_mesh.bounds, rotation)
    translation = tuple(-v for v in lower)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    names = ['barrier-clip-v1.11-A.stl','barrier-clip-v1.11-B.stl']
    for name in names:
        write_binary_stl(OUT / name,
            transform_triangles(source_mesh.triangles, rotation, translation),
            'v1.11 roof-down rigid transform, mm')
    with zipfile.ZipFile(template) as archive:
        cfg = json.loads(archive.read('Metadata/project_settings.config'))
    cfg.update(profile('machine','Bambu Lab X1 Carbon 0.4 nozzle'))
    cfg.update(profile('process','0.20mm Standard @BBL X1C'))
    cfg.update(profile('filament','Generic PETG'))
    cfg.update({
        'printer_settings_id':'Bambu Lab X1 Carbon 0.4 nozzle',
        'print_settings_id':'Barrier clip v1.11 PETG 0.20mm 6 walls',
        'filament_settings_id':['Generic PETG'],
        'filament_ids':['GFG99'], 'filament_colour':['#A0A0A0'],
        # Official Generic PETG defines one Standard variant, unlike the
        # template's Standard+High Flow pair. GUI requires a matching index.
        'filament_self_index':['1'],
        'curr_bed_type':'Textured PEI Plate',
        'layer_height':'0.2', 'initial_layer_print_height':'0.2',
        'wall_loops':'6', 'top_shell_layers':'5', 'bottom_shell_layers':'5',
        'sparse_infill_density':'30%', 'sparse_infill_pattern':'gyroid',
        'outer_wall_speed':['80','80'], 'inner_wall_speed':['120','120'],
        'sparse_infill_speed':['120','120'], 'top_surface_speed':['60','60'],
        'initial_layer_speed':['30','30'], 'initial_layer_infill_speed':['50','50'],
        'enable_prime_tower':'0', 'print_sequence':'by layer',
        'enable_support':'1', 'support_type':'normal(auto)',
        'support_style':'default', 'support_on_build_plate_only':'1',
        'support_threshold_angle':'45', 'support_top_z_distance':'0.24',
        'support_bottom_z_distance':'0.24',
        'support_interface_top_layers':'3', 'support_interface_spacing':'0.5',
        'support_object_xy_distance':'0.4', 'support_speed':['80','80'],
        'support_interface_speed':['60','60'],
        'brim_type':'outer_only', 'brim_width':'5', 'brim_object_gap':'0.15',
        'xy_hole_compensation':'0', 'xy_contour_compensation':'0',
        'elefant_foot_compensation':'0.15',
    })
    editable = OUT / 'barrier-clip-v1.11-2x-X1C-PETG.3mf'
    sliced = OUT / 'barrier-clip-v1.11-2x-X1C-PETG.gcode.3mf'
    with tempfile.TemporaryDirectory(prefix='barrier-v111-2x-') as tmp:
        work = Path(tmp)
        seed = work / 'seed.3mf'
        run([str(BAMBU),'--datadir',str(work/'seed-data'),'--arrange','1',
             '--orient','0','--avoid-extrusion-cali-region','--export-3mf',
             str(seed),*(str(OUT/name) for name in names)], OUT/'seed.log')
        with zipfile.ZipFile(seed) as archive:
            root = ET.fromstring(archive.read('3D/3dmodel.model'))
        core='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
        ET.register_namespace('',core)
        ET.register_namespace('p','http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
        items=root.findall(f'{{{core}}}build/{{{core}}}item')
        if len(items)!=2:
            raise RuntimeError(f'Expected 2 independent items, got {len(items)}')
        for item,cx in zip(items,[90,166]):
            pose=item.attrib['transform'].split()
            # Bambu seed meshes keep normalized XY coordinates but centre Z.
            pose[9]=str(cx-(source_mesh.bounds[1][0]-source_mesh.bounds[0][0])/2)
            pose[10]=str(128-(source_mesh.bounds[1][1]-source_mesh.bounds[0][1])/2)
            item.set('transform',' '.join(pose))
        with zipfile.ZipFile(seed) as archive, zipfile.ZipFile(
            editable,'w',zipfile.ZIP_DEFLATED) as output:
            for item in archive.infolist():
                if item.filename in {'Metadata/project_settings.config',
                    'Metadata/filament_sequence.json','Metadata/slice_info.config',
                    '3D/3dmodel.model'}:
                    continue
                output.writestr(item,archive.read(item.filename))
            output.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
            output.writestr('Metadata/project_settings.config',json.dumps(cfg))
            output.writestr('Metadata/filament_sequence.json',json.dumps({
                'plate_1':{'nozzle_sequence':[0],'optimal_assignment':[0],
                           'sequence':[1]}}))
        (OUT/'resolved-settings.json').write_text(json.dumps(cfg,indent=2))
        run([str(BAMBU),'--datadir',str(work/'slice-data'),'--arrange','0',
             '--orient','0','--slice','0','--export-3mf',str(sliced),
             str(editable)],OUT/'slice.log')
    with zipfile.ZipFile(sliced) as archive:
        gcodes = [n for n in archive.namelist() if n.endswith('.gcode')]
        if len(gcodes)!=1:
            raise RuntimeError(f'Expected exactly one sliced plate, got {gcodes}')
        (OUT/'plate_1.gcode').write_bytes(archive.read(gcodes[0]))
        for member in ['Metadata/plate_1.png','Metadata/top_1.png']:
            if member in archive.namelist():
                (OUT/Path(member).name).write_bytes(archive.read(member))
    manifest = {
        'source_stl':str(SOURCE.relative_to(CAD)), 'source_sha256':source_hash,
        'source_scad_sha256':hashlib.sha256((HERE/'fit_clearance_guard.scad').read_bytes()).hexdigest(),
        'quantity':2, 'plate_count':1, 'unit':'mm',
        'centres_xy_mm':[[90,128],[166,128]], 'object_gap_x_mm':20.2,
        'rotation_xyz_deg':[180,0,0], 'normalization_translation_mm':translation,
        'scale':1, 'printer':'X1 Carbon 0.4 nozzle',
        'material':'Generic PETG', 'plate':'Textured PEI Plate',
        'editable_3mf':editable.name, 'sliced_3mf':sliced.name,
        'printer_sent':False, 'printer_started':False,
        'warning':'Physical fit/bed clearance and PETG snap flexibility require first articles.'
    }
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--settings-template',type=Path,required=True)
    build(parser.parse_args().settings_template)
