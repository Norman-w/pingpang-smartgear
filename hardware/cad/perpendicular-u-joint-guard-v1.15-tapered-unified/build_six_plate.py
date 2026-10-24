#!/usr/bin/env python3
"""Prepare six upright clips using the user's archived actual PETG recipe.
Offline only: no printer/network commands. The current black A4 mapping is
verified separately in Bambu Studio at dispatch, not inferred from this file.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile,zipfile
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
CAD=HERE.parent
sys.path.insert(0,str(CAD))
from build_print_platter import load_binary_stl,transform_triangles,write_binary_stl

SOURCE=CAD/'exports/perpendicular-u-joint-v1.15-tapered-unified/guard-v1.15.stl'
TEMPLATE=CAD/'print-packages/barrier-clip-v1.11-first-article/barrier-clip-v1.11-2x-upright-tree-actual.3mf'
OUT=CAD/'print-packages/barrier-clip-v1.15-6x-black-PETG'
BAMBU='/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
STEM='barrier-clip-v1.15-6x-upright-black-PETG'
CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
IDENTITY=((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))
CENTRES=[(x,y) for y in (76.,172.) for x in (55.,128.,201.)]

def run(args,log):
    result=subprocess.run(args,capture_output=True,text=True)
    log.write_text(result.stdout+result.stderr)
    if result.returncode:
        raise RuntimeError(f'{log}: exit {result.returncode}\n{result.stdout[-3000:]}\n{result.stderr[-1000:]}')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    expected=json.loads((CAD/'review/perpendicular-u-joint-v1.15-tapered-unified/build-validation.json').read_text())['output_sha256']['guard-v1.15.stl']
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert sha==expected,'Source differs from validated v1.15'
    mesh=load_binary_stl(SOURCE)
    low,high=mesh.bounds
    size=[b-a for a,b in zip(low,high)]
    assert all(abs(a-b)<.001 for a,b in zip(size,(55.8,67,55.1)))
    with zipfile.ZipFile(TEMPLATE) as z:
        cfg=json.loads(z.read('Metadata/project_settings.config'))
    assert cfg['support_type']=='tree(auto)' and cfg['wall_loops']=='6'
    assert cfg['sparse_infill_density']=='30%' and cfg['filament_type']==['PETG']
    # Preserve the actual prior recipe; change only display ID and color.
    cfg['filament_colour']=['#000000']
    cfg['print_settings_id']='Barrier clip v1.15 6x upright PETG 0.20mm 6 walls'
    shutil.copy2(SOURCE,OUT/'guard-v1.15.stl')
    editable=OUT/f'{STEM}.3mf'
    sliced=OUT/f'{STEM}.gcode.3mf'
    with tempfile.TemporaryDirectory(prefix='barrier-v115-six-') as tmp:
        work=Path(tmp)
        objects=[]
        for i in range(6):
            target=work/f'guard-v1.15-{i+1:02}.stl'
            write_binary_stl(target,transform_triangles(mesh.triangles,IDENTITY,tuple(-v for v in low)),
                             'v1.15 upright at 1:1 mm; translation only')
            objects.append(target)
        seed=work/'seed.3mf'
        run([BAMBU,'--datadir',str(work/'seed-data'),'--arrange','1','--orient','0',
             '--avoid-extrusion-cali-region','--export-3mf',str(seed),*map(str,objects)],OUT/'seed.log')
        with zipfile.ZipFile(seed) as z:
            root=ET.fromstring(z.read('3D/3dmodel.model'))
            model_cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        ET.register_namespace('',CORE);ET.register_namespace('p',PROD)
        items=root.findall(f'{{{CORE}}}build/{{{CORE}}}item')
        assert len(items)==6
        for item,(cx,cy) in zip(items,CENTRES):
            pose=item.attrib['transform'].split()
            assert [float(v) for v in pose[:9]]==[1,0,0,0,1,0,0,0,1]
            pose[9]=str(cx-size[0]/2);pose[10]=str(cy-size[1]/2)
            item.set('transform',' '.join(pose))
        # Remove stale seed assemble positions: project loads the build items.
        for element in list(model_cfg.findall('assemble')):
            model_cfg.remove(element)
        plates=model_cfg.findall('plate')
        assert len(plates)==1,'Seed unexpectedly spans multiple plates'
        assert len(plates[0].findall('model_instance'))==6
        with zipfile.ZipFile(seed) as z,zipfile.ZipFile(editable,'w',zipfile.ZIP_DEFLATED) as output:
            replaced={'3D/3dmodel.model','Metadata/model_settings.config','Metadata/project_settings.config',
                      'Metadata/filament_sequence.json','Metadata/slice_info.config'}
            for info in z.infolist():
                if info.filename not in replaced:output.writestr(info,z.read(info.filename))
            output.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
            output.writestr('Metadata/model_settings.config',ET.tostring(model_cfg,encoding='utf-8',xml_declaration=True))
            output.writestr('Metadata/project_settings.config',json.dumps(cfg))
            output.writestr('Metadata/filament_sequence.json',json.dumps({'plate_1':{
                'nozzle_sequence':[0],'optimal_assignment':[0],'sequence':[1]}}))
        run([BAMBU,'--datadir',str(work/'slice-data'),'--arrange','0','--orient','0',
             '--slice','0','--export-3mf',str(sliced),str(editable)],OUT/'slice.log')
    with zipfile.ZipFile(sliced) as z:
        assert [n for n in z.namelist() if n.endswith('.gcode')]==['Metadata/plate_1.gcode']
        for name in ('Metadata/plate_1.png','Metadata/top_1.png'):
            if name in z.namelist():(OUT/Path(name).name).write_bytes(z.read(name))
    report={'source_sha256':sha,'template_sha256':hashlib.sha256(TEMPLATE.read_bytes()).hexdigest(),
        'quantity':6,'plate_count':1,'centres_xy_mm':CENTRES,'rotation_xyz_deg':[0,0,0],
        'scale':1,'source_normalization_translation_mm':[-v for v in low],
        'orientation':'roof up; hooks on bed; automatic tree supports',
        'printer':'X1 Carbon 0.4 nozzle','material':'Generic PETG','colour':'black',
        'expected_mapping':'AMS A4; verify in live send dialog',
        'editable_3mf':editable.name,'sliced_3mf':sliced.name,
        'printer_sent':False,'printer_started':False}
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
