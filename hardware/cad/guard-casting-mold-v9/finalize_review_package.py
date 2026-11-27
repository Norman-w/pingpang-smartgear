"""Collect only audited, active editable 3MFs; keep the user's print hold."""
from pathlib import Path
from collections import Counter
import json,hashlib,zipfile,shutil
HERE=Path(__file__).resolve().parent;CAD=HERE.parent;ROOT=CAD/'print-packages/guard-mold-v9-HOLD-X1C-PETG'
m=json.loads((ROOT/'manifest.json').read_text());m['plates'].sort(key=lambda p:p['plate']);assert len(m['plates'])==5
expected={Path(r['file']).stem:r['copies'] for r in json.loads((CAD/'guard-casting-mold-v7/print-quantities.json').read_text())};counts=Counter();summaries=[];aids=[]
validation=json.loads((CAD/'guard-casting-mold-v7/validation.json').read_text());assert validation['source_sha256']==hashlib.sha256((CAD/'guard-casting-mold-v7/mold.scad').read_bytes()).hexdigest()
for p in m['plates']:
 folder=ROOT/Path(p['editable_3mf']).parent;a=json.loads((folder/'package-audit.json').read_text())
 assert a['object_count']==len(p['objects']);assert not a['excluded_corner_hits'] and not a['protected_region_support_hits'];assert a['gcode_md5_verified'];assert a['extruding_xy_bounds_mm'][1]>=14
 # Thumbnail refresh changes only package image bytes; always bind this summary to current packages.
 assert a['sha256']==hashlib.sha256((ROOT/p['sliced_3mf']).read_bytes()).hexdigest(),p['plate']
 assert a['geometry_project_sha256']==hashlib.sha256((ROOT/p['editable_3mf']).read_bytes()).hexdigest(),p['plate']
 for r in p['objects']:
  counts[r['id']]+=1
  if r['id']=='screw' or r['id'].startswith('clamp-'):
   assert p['plate']==1 and r['rotation_xyz_deg']==[180,0,0] and r['print_aid']['kind']=='removable_annular_knob_collar'
  assert hashlib.sha256((CAD/'exports/guard-casting-mold-v7'/(r['id']+'.stl')).read_bytes()).hexdigest()==r['source_sha256']
  if r['print_aid']:
   assert r['print_aid']['functional_body_removed_mm3']<1e-6 and r['print_aid']['COM_inside_bed_hull_after'];aids.append({'name':r['name'],**r['print_aid']})
 support=a['support_extrusions']
 if p['plate']==1:assert all(not any(g['moves'] for g in roles.values()) for roles in support.values())
 support_objects=[name for name,roles in support.items() if any(g['moves'] for g in roles.values())]
 summaries.append({'plate':p['plate'],'objects':[r['name'] for r in p['objects']],'seconds':a['prediction_seconds'],'weight_g':a['weight_g'],'support_path_weight_g':a['support_estimated_g_from_extrusions'],'objects_with_support':support_objects,'support_moves':sum(g['moves'] for roles in support.values() for g in roles.values()),'extrusion_bounds_xy_mm':a['extruding_xy_bounds_mm'],'outside_exclusion':True,'protected_support_hits':[]})
assert counts==expected and sum(counts.values())==16 and counts['screw']==2
report={'status':'DIGITAL_CHECKS_PASS_PRINT_HELD_BY_USER','do_not_print':True,'sent':False,'started':False,'plates':summaries,'counts':dict(counts),'service_pieces':16,'plate_count':5,'total_weight_g':sum(p['weight_g'] for p in summaries),'total_seconds':sum(p['seconds'] for p in summaries),'print_aids':aids,'thread_and_assembly_validation':'v7 geometry unchanged; correct screw paths, wrong-phase control, full assembly geometry inherited from v7 validation files','support_statement':'All nine rods upright head-down, zero support G-code on fastener plate. Mold plates retain necessary supports; remove aids before assembly.','physical_adhesion_fit_layer_strength_and_cast_release':'not_tested','previous_v7_attempt':'Transferred, then printer idle with no heating/printing observed; no resend after user hold'}
(ROOT/'review-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');shutil.copy2(HERE/'README.zh-CN.md',ROOT/'README.zh-CN.md')
m.update(do_not_print=True,release_status='DIGITAL_CHECKS_PASS_PRINT_HELD_BY_USER',sent=False,started=False,total_quantity=16,plate_count=5);(ROOT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

print(json.dumps({'direct_3mf':[str(ROOT/p['editable_3mf']) for p in m['plates']],'counts':dict(counts),'weight_g':report['total_weight_g'],'hours':report['total_seconds']/3600,'support_g':sum(p['support_path_weight_g'] for p in summaries),'sent':False},ensure_ascii=False,indent=2))
