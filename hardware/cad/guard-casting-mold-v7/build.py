"""Export the SCAD mold contract, validate solids and sampled extraction paths."""
from pathlib import Path
import json,subprocess,shutil,importlib.util,hashlib,re
import numpy as np
HERE=Path(__file__).resolve().parent; CAD=HERE.parent
OUT=CAD/'exports/guard-casting-mold-v7'; OUT.mkdir(parents=True,exist_ok=True)
WEB=CAD/'preview/guard-mold-v7'; (WEB/'models').mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('mesh_io',CAD/'perpendicular-u-joint-guard-v1.17-load-path/build.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
text=(HERE/'mold.scad').read_text()
def param(name): return float(re.search(r'\b'+name+r'=([-\d.]+);',text)[1])
BX=param('BX');BY=param('BY');Z0=param('Z0');Z1=param('Z1');DROP=param('CORE_DROP')
NAMES={'left':'① 左外模 · −X','right':'② 右外模 · +X','lid':'③ 顶盖与圆孔芯 · +Z','upper':'④ 上梁芯 · 快插销定位','lower':'⑤ 组合芯 · 宽肩止挡 / 防反插','back':'⑥ 后端芯 · 宽肩止挡 / 防反插','pin':'⑦ 快插定位销 · 先拔出','product':'PU成品 · v1.19阴刻版'}
COLORS={'left':'#48a8dd','right':'#6383ed','lid':'#a877df','upper':'#eeb750','lower':'#4dbda6','back':'#f08eae','pin':'#c9e65b','product':'#ec7956'}
def write_ascii(s,path):
    mesh=s.to_mesh64();v=mesh.vert_properties[:,:3];f=mesh.tri_verts
    with path.open('w') as out:
        out.write('solid mold_mm\n')
        for face in f:
            pts=v[face];n=np.cross(pts[1]-pts[0],pts[2]-pts[0]);n/=max(np.linalg.norm(n),1e-30)
            out.write('facet normal '+' '.join(format(x,'.17g') for x in n)+'\nouter loop\n')
            for p in pts:out.write('vertex '+' '.join(format(x,'.17g') for x in p)+'\n')
            out.write('endloop\nendfacet\n')
        out.write('endsolid mold_mm\n')
def main():
    solids={};records=[]
    for key in NAMES:
        path=OUT/f'{key}.stl'
        subprocess.run([shutil.which('openscad'),'--backend=Manifold','--export-format=binstl','-D',f'FEATURE="{key}"','-o',str(path),str(HERE/'mold.scad')],check=True,stdout=subprocess.DEVNULL)
        s=b.load(path)
        if key not in ('product','upper','pin'):
            # Repeat the same cavity subtraction in double precision: OpenSCAD's
            # single-precision mesh export can retain coplanar sliver wedges.
            source=b.load(CAD/'exports/perpendicular-u-joint-v1.19-engraved-logo/guard-v1.19.stl')
            s=(s-source).set_tolerance(.00001).simplify(.00001)
        pieces=[p for p in s.decompose() if abs(p.volume())>1e-6]
        assert len(pieces)==1,(key,len(pieces))
        s=pieces[0]
        s=b.export_precision(s)
        solids[key]=s
        write_ascii(s,path)
        shutil.copy2(path,WEB/'models'/path.name)
        records.append({'id':key,'volume_mm3':s.volume(),'bounds_mm':s.bounding_box(),'components':len(s.decompose()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    overlaps=[]
    keys=list(solids)
    for i,a in enumerate(keys):
        for c in keys[i+1:]:
            volume=abs((solids[a]^solids[c]).volume())
            if volume>.02:overlaps.append({'a':a,'b':c,'mm3':volume})
    # Validate actual path order with the casting kept rigid; elastomer flex is NOT used to hide interference.
    pos={k:np.zeros(3) for k in keys};paths=[]
    sequence=[('pin',[0,0,30]),('pin',[40,0,0]),('lid',[0,0,90]),('lower',[0,160,0]),('back',[0,-110,0]),('left',[-90,0,0]),('right',[270,0,0]),('upper',[0,0,-DROP]),('upper',[120,0,0])]
    for moving,delta in sequence:
        delta=np.array(delta,dtype=float);length=np.linalg.norm(delta)
        distances=sorted(set([0,*np.arange(.05,min(2,length)+.001,.05),*np.arange(2.5,length,.5),length]))
        peak=0;pair=None;at=0
        for dist in distances:
            shifted=solids[moving].translate(pos[moving]+delta*dist/length)
            for other in keys:
                if other==moving:continue
                # AABB test avoids unnecessary mesh Booleans after disengagement.
                aa=np.array(shifted.bounding_box());bb=np.array(solids[other].bounding_box())+np.tile(pos[other],2)
                if np.any(aa[:3]>=bb[3:]-1e-7) or np.any(bb[:3]>=aa[3:]-1e-7):continue
                v=abs((shifted^solids[other].translate(pos[other])).volume())
                if v>peak:peak,pair,at=v,other,dist
        paths.append({'part':moving,'delta_mm':delta.tolist(),'max_overlap_mm3':peak,'with':pair,'at_distance_mm':at,'samples':len(distances)})
        print('PATH',paths[-1],flush=True);pos[moving]+=delta
    report={'source':'mold.scad','source_sha256':hashlib.sha256((HERE/'mold.scad').read_bytes()).hexdigest(),'original_product_sha256':hashlib.sha256((CAD/'exports/perpendicular-u-joint-v1.19-engraved-logo/guard-v1.19.stl').read_bytes()).hexdigest(),'product_sha256':records[-1]['sha256'],'units':'mm','nominal_clearance_mm':0,'material_shrinkage_compensation':'not_established','stock_size_mm':[BX,BY,Z1-Z0],'parts':records,'closed_overlaps':overlaps,'sampled_paths':paths,'sample_step_near_start_mm':.05,'sample_step_after_2mm':.5,'continuous_sweep_proven':False,'physical_release_and_sealing':'not_tested','elastic_strip_required':{'parts':['left','right'],'feature':'lower-arm convex end chamfers','maximum_nominal_radial_undercut_mm':.6,'material':'flexible cast PU only; not suitable for rigid resin without redesign'}}
    (HERE/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    shutil.copy2(HERE/'validation.json',WEB/'validation.json')
    create_manifest(records)
    assert not overlaps,overlaps
    rigid_clear=[x for x in paths if x['part'] not in ('left','right')]
    assert max(x['max_overlap_mm3'] for x in rigid_clear)<.02,'Core extraction collision; repair mold before delivery'
    # Existing lower-arm convex end bevels need up to 0.6mm elastic stripping.
    # This is deliberately NOT labelled a collision-free rigid demold.
    assert max(x['max_overlap_mm3'] for x in paths if x['part'] in ('left','right'))<25
def create_manifest(records):
    import sys
    sys.path.insert(0,str(HERE))
    from preview_manifest import main as preview
    preview()
if __name__=='__main__':main()
