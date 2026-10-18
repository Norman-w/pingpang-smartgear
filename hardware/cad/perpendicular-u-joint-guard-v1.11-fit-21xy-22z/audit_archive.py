#!/usr/bin/env python3
"""Archive/verify scoped barrier work. No printer/network operations or deletion."""
import argparse
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

CAD=Path(__file__).resolve().parent.parent
PACKAGE=CAD/'print-packages/barrier-clip-v1.11-first-article'
INVENTORY=PACKAGE/'archive-inventory.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def relevant_dirs():
    return sorted([p for p in CAD.iterdir() if p.is_dir() and (
        p.name.startswith('perpendicular-u-joint-guard') or p.name=='rotating-foot-guard')]
        +[p for p in (CAD/'review').iterdir() if p.is_dir() and (
        p.name.startswith('perpendicular-u-joint-') or p.name=='rotating-foot-guard-v0.1')])

def usable(path):
    return path.is_file() and path.name!='.DS_Store' and '__pycache__' not in path.parts

def check_actual():
    editable=PACKAGE/'barrier-clip-v1.11-2x-upright-tree-actual.3mf'
    sliced=PACKAGE/'barrier-clip-v1.11-2x-upright-tree-actual.gcode.3mf'
    with zipfile.ZipFile(editable) as z:
        cfg=json.loads(z.read('Metadata/project_settings.config'))
        root=ET.fromstring(z.read('3D/3dmodel.model'))
        ns={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
        assert len(root.findall('c:build/c:item',ns))==2
        assert cfg['support_type']=='tree(auto)'
        assert cfg['wall_loops']=='6' and cfg['sparse_infill_density']=='30%'
        assert cfg['sparse_infill_pattern']=='gyroid'
        assert cfg['filament_settings_id']==['Generic PETG']
    with zipfile.ZipFile(sliced) as z:
        assert z.testzip() is None
        info=ET.fromstring(z.read('Metadata/slice_info.config'))
        plates=info.findall('plate');assert len(plates)==1
        plate=plates[0]
        meta={m.get('key'):m.get('value') for m in plate.findall('metadata')}
        assert meta['prediction']=='16753' and meta['weight']=='108.87'
        assert meta['outside']=='false' and len(plate.findall('object'))==2
        data=z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(data).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        assert b'; total layer number: 272' in data
        # Exact source mesh parity, separate from the editable build transforms.
        core={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
        footprints=[]
        with zipfile.ZipFile(editable) as project:
            for name in project.namelist():
                if name.startswith('3D/Objects/') and name.endswith('.model'):
                    mesh=ET.fromstring(project.read(name))
                    pts=[[float(v.get(a)) for a in 'xyz'] for v in mesh.findall('.//c:vertex',core)]
                    footprints.append([max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)])
        assert len(footprints)==2
        assert all(all(abs(a-b)<0.001 for a,b in zip(size,[55.8,67,54.5])) for size in footprints)
    return {'prediction_seconds':16753,'weight_g':108.87,'objects':2,'plates':1,
            'layers':272,'support_type':'tree(auto)','printer_started_by_user':True,
            'physical_fit_and_strength':'not_tested'}

def check_dependencies(paths):
    count=0
    for path in paths:
        if path.suffix!='.scad':continue
        for name in re.findall(r'^\s*(?:use|include)\s*<([^>]+)>',path.read_text(),re.M):
            assert (path.parent/name).is_file(),f'Missing SCAD dependency: {path}: {name}'
            count+=1
    return count

def create_zip(files,destination,base):
    entries=[]
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as out:
        for path in sorted(files):
            name=path.relative_to(base).as_posix()
            out.write(path,name)
            entries.append({'path':name,'size':path.stat().st_size,'sha256':digest(path)})
    return entries

def verify(manifest):
    for entry in manifest['files']:
        path=CAD/entry['path']
        assert path.is_file() and digest(path)==entry['sha256'],entry['path']
    for archive in manifest['reference_archives']:
        with zipfile.ZipFile(PACKAGE/archive['file']) as z:
            assert z.testzip() is None
            assert set(z.namelist())=={e['path'] for e in archive['entries']}
            for entry in archive['entries']:
                assert hashlib.sha256(z.read(entry['path'])).hexdigest()==entry['sha256']
    check_actual()
    paths=[CAD/e['path'] for e in manifest['files']]
    return check_dependencies(paths)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify',action='store_true')
    parser.add_argument('--comparison-dir',type=Path)
    args=parser.parse_args()
    if args.verify:
        manifest=json.loads(INVENTORY.read_text())
    else:
        assert args.comparison_dir and args.comparison_dir.is_dir()
        exports=[f for p in (CAD/'exports').iterdir() if p.is_dir() and (
            p.name.startswith('perpendicular-u-joint-') or p.name=='rotating-foot-guard-v0.1')
            for f in p.rglob('*') if usable(f)]
        comparisons=[p for p in args.comparison_dir.rglob('*') if usable(p)
                     and not any(part=='data' for part in p.relative_to(args.comparison_dir).parts)]
        archives=[]
        for name,files,base in [
            ('historical-generated-exports-REFERENCE-ONLY.zip',exports,CAD),
            ('offline-time-comparison-REFERENCE-ONLY.zip',comparisons,args.comparison_dir)]:
            entries=create_zip(files,PACKAGE/name,base)
            archives.append({'file':name,'entries':entries})
        files=[p for folder in relevant_dirs()+[PACKAGE] for p in folder.rglob('*')
               if usable(p) and p!=INVENTORY]
        files+=[CAD/'BARRIER-GUARD-INDEX.zh-CN.md']
        files=sorted(set(files))
        manifest={'schema_version':1,'scope':'barrier guard only; preserved, not deleted',
                  'actual_print':check_actual(),
                  'source_geometry_changed':False,
                  'scad_dependency_references':check_dependencies(files),
                  'files':[{'path':p.relative_to(CAD).as_posix(),'size':p.stat().st_size,
                            'sha256':digest(p)} for p in files],
                  'reference_archives':archives}
        INVENTORY.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    refs=verify(manifest)
    print(json.dumps({'files_verified':len(manifest['files']),'scad_references':refs,
                      'archive_entries':sum(len(a['entries']) for a in manifest['reference_archives']),
                      'actual_print':manifest['actual_print'],'passed':True},ensure_ascii=False))

if __name__=='__main__':main()
