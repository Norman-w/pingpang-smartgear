#!/usr/bin/env python3
"""Verify RX skin, cavity containment, rigid fit and front installation."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from export_receiver_mount import OUTPUT,SOURCES,SOURCE
from validate_laser_micro_mount import component_count,front_skin_sections
from validate_net_stand import _stl_topology,_stl_volume
from validate_scad import find_openscad

def main():
    manifest=json.loads((OUTPUT/'manifest.json').read_text());p=manifest['parameters']
    for source in SOURCES:
        assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_hashes'][source.name],source
    parts=[]
    for part in manifest['parts']:
        path=OUTPUT/part['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==part['sha256']
        assert _stl_topology(path)[0] and _stl_volume(path)>0,part['id']
        components=component_count(path) if part['printable'] else None
        assert components in (1,None),(part['id'],components)
        parts.append(dict(id=part['id'],closed=True,solid_components=components,bounds=part['bounds']))
    sections=front_skin_sections(OUTPUT/'front_cover.stl',p['first_z']+4.5*p['pitch'],p['front_wall'])
    # Shared parts must actually be the same exported geometry on both ends.
    tx=OUTPUT.parent/'laser-micro-mount-v0.1'
    shared=['front_cover','bottom_cover','bottom_gasket','front_hardware']
    for name in shared:
        assert (OUTPUT/f'{name}.stl').read_bytes()==(tx/f'{name}.stl').read_bytes(),name
    checks=[('rigid-fit','receiver_cover_collision();'),('front-containment','receiver_cover_containment();')]
    for distance in [0,2,5,10,20,30,50]:
        checks.append((f'front-install-{distance}',f'intersection(){{translate([-{distance},0,0])laser_micro_front_cover();union(){{receiver_internal_positive();receiver_rear_cover();laser_micro_bottom_cover();}}}}'))
    with tempfile.TemporaryDirectory(prefix='receiver-mount-check-') as directory:
        def check(item):
            name,body=item;path=Path(directory)/f'{name}.scad';path.write_text(f'include <{SOURCE}>\n{body}\n');out=path.with_suffix('.stl')
            result=subprocess.run([find_openscad(),'-o',str(out),'-D','PART="laser_micro_metadata"',str(path)],capture_output=True,text=True)
            log=result.stdout+result.stderr
            assert 'WARNING:' not in log and 'ERROR:' not in log,log
            assert out.exists() or 'top level object is empty' in log,log
            volume=_stl_volume(out) if out.exists() else 0
            assert abs(volume)<1e-6,(name,volume)
            return dict(id=name,interference_mm3=volume)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(check,checks))
    report=dict(source_hashes=manifest['source_hashes'],parts=parts,checks=results,skin_sections=sections,
        shared_with_tx=shared,units='mm',front_cavity_nominal_clearance_mm=.5,
        optical_pitch_mm=p['pitch'],first_installed_axis_z_mm=p['first_z']+p['installed_offset_z'],
        boundaries=['receiver choice not confirmed','existing M6 head and PCB geometry references only',
                    'installation sampled at seven positions','wires and real fastener/tool tolerances not validated'],
        physical_validation='not performed')
    (OUTPUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'RECEIVER_MOUNT_OK: {len(parts)} closed meshes; 5 connected printable parts; {len(sections)} skin sections; {len(results)} fit/containment/installation checks')
if __name__=='__main__':main()
