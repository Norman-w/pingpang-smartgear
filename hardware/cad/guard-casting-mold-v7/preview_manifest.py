import json,math,subprocess,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;CAD=HERE.parent;OUT=CAD/'exports/guard-casting-mold-v7';WEB=CAD/'preview/guard-mold-v7'
IDENT={'position':[0,0,0],'rotation':[0,0,0]}
# One source for preview attachment coordinates, parsed by validation too.
SITES=[*(('lid-'+str(s),'lid',[s*53,30,30.2],[0,0,0]) for s in [-1,1]),*(('lower-'+str(s),'lower',[s*50,51,-12],[-math.pi/2,0,0]) for s in [-1,1]),*(('back-'+str(s),'back',[s*50,-51,-12],[math.pi/2,0,0]) for s in [-1,1]),*(('side-'+str(s),'right',[0,s*48,-57],[0,math.pi/2,0]) for s in [-1,1])]
def main():
 m=json.loads((CAD/'preview/guard-mold-v2/manifest.json').read_text());m['title']='围挡卡 · XYZ全打印紧固与编号 v7'
 m['extensions'].update(bands=[],inspections=[],jack_note='X/Y/Z均使用打印粗牙杆直接拧入模具一体母牙；安装杆全部保留，J拆模杆仅2颗轮换。A—G为零件阴刻字母。先卸所有紧固杆再拆模。',mechanical_status='all_printed_xyz_clamp_draft_not_load_tested')
 for f in m['assembly']['frames']:
  if f['id']=='right':f['range']=[0,270]
 for p in m['parts']:p['source']['file']='../../guard-casting-mold-v7/mold.scad'
 frames=m['assembly']['frames'];inst=[]
 for id,parent,pos,rot in SITES:
  frames.append({'id':id+'-mount','label':id+' 螺杆座','parentFrameId':parent,'kind':'fixed','localTransform':{'position':pos,'rotation':rot}})
  frames.append({'id':id+'-slide','label':id+' 顶进','parentFrameId':id+'-mount','kind':'prismatic','axis':[0,0,1],'range':[-3,0],'defaultValue':0,'localTransform':IDENT})
  frames.append({'id':id+'-turn','label':id+' 旋转','parentFrameId':id+'-slide','kind':'revolute','axis':[0,0,1],'range':[-3*2*math.pi/8,0],'defaultValue':0,'localTransform':IDENT})
  inst.append({'id':id+'-screw','name':{'lid':'顶盖','lower':'绿芯','back':'粉芯','right':'外模'}[parent]+' PETG粗牙螺杆 '+str(pos[0] if parent!='right' else pos[1]),'parentFrameId':id+'-turn','localTransform':IDENT,'explosion':[0,0,0]})
 for k in ['screw','male-test','female-test','clamp-X','clamp-Y','clamp-Z']:
  p=OUT/(k+'.stl');subprocess.run([shutil.which('openscad'),'--backend=Manifold','--export-format=binstl','-D',f'FEATURE="{k}"','-o',str(p),str(HERE/'mold.scad')],check=True,stdout=subprocess.DEVNULL)
  shutil.copy2(p,WEB/'models'/p.name)
 m['parts'].append({'id':'screw','name':'J拆模螺杆 · 仅打印2颗（图中换位）','source':{'kind':'scad','file':'../../guard-casting-mold-v7/mold.scad','selector':'FEATURE="screw"'},'file':'models/screw.stl','geometrySpace':'local','role':'printed','color':'#ffad39','opacity':1,'instances':inst})
 # Independent printed installation hardware: seven rods into integral threaded seats.
 rod_sites={'Z':[(f'Z-{x}-{y}',[x,y,-83],[0,0,0]) for x in [-22,22] for y in [-92,92]],'X':[('X-0',[98,0,-55],[0,-math.pi/2,0])],'Y':[(f'Y-{x}',[x,108,-20],[math.pi/2,0,0]) for x in [-96,96]]}
 nuts=[]
 for k,sites in rod_sites.items():
  ins=[]
  for id,pos,rot in sites:
   ins.append({'id':id,'name':k+'安装杆','parentFrameId':'world','localTransform':{'position':pos,'rotation':rot},'explosion':[0,0,0]})
  m['parts'].append({'id':'clamp-'+k,'name':k+'安装紧固杆 ×'+str(len(sites)),'source':{'kind':'scad','file':'../../guard-casting-mold-v7/mold.scad','selector':'FEATURE="clamp-'+k+'"'},'file':'models/clamp-'+k+'.stl','geometrySpace':'local','role':'printed','color':'#dfcf9f','opacity':1,'instances':ins})
 labels={'left':'A 左外模','right':'B 右外模','lid':'C 顶盖','upper':'D 上梁芯','lower':'E 绿芯','back':'F 后芯','pin':'G 定位销'}
 for p in m['parts']:
  if p['id'] in labels:
   p['name']=labels[p['id']]
   for instance in p['instances']:instance['name']=p['name']
 values={f['id']:0 for f in frames if f['kind']!='fixed'};stages=[]
 def add(id,label,**update):values.update(update);stages.append({'id':id,'label':label,'values':dict(values)})
 def jacks(parent,d):
  for id,p,_,_ in SITES:
   if p==parent:values[id+'-slide']=-d;values[id+'-turn']=-d*2*math.pi/8
 add('closed','▣ X/Y/Z打印紧固杆全部装好')
 add('unclamped','① 卸X/Y/Z安装杆')
 add('pin-lifted','① 拔销',**{'pin-lift':30});add('pin-out','② 移开销',pin=40)
 for parent,label,axisdist in [('lid','顶盖',90),('lower','绿芯',160),('back','粉芯',110),('right','外模',270)]:
  jacks(parent,3);add(parent+'-jack','↻ '+label+' 双螺杆顶开3mm（约⅜圈）',**{parent:3})
  jacks(parent,0);add(parent+'-backoff','↺ '+label+' 退回螺杆',**{parent:3})
  update={parent:axisdist}
  if parent=='right':update['left']=90
  add(parent+'-off','↗ '+label+' 退出',**update)
 add('upper-lowered','↓ 黄色芯下降1mm',**{'upper-drop':1});add('released','→ 黄色芯手动抽出',upper=120)
 m['stages']=stages;m['playback']['sequence']=[s['id'] for s in stages]
 m['extensions']['thread']={'major_mm':22,'core_mm':19,'pitch_mm':8,'root_mm':5.6,'crest_mm':1.6,'radial_clearance_mm':.3,'axial_clearance_mm':.25,'female_length_mm':32,'initial_engagement_mm':30,'physical_fit':'not_tested'}
 m['extensions']['print_quantities']=[{'file':k+'.stl','copies':q} for k,q in [('left',1),('right',1),('lid',1),('upper',1),('lower',1),('back',1),('pin',1),('screw',2),('clamp-Z',4),('clamp-X',1),('clamp-Y',2)]]
 (HERE/'print-quantities.json').write_text(json.dumps(m['extensions']['print_quantities'],ensure_ascii=False,indent=2)+'\n')
 (WEB/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
