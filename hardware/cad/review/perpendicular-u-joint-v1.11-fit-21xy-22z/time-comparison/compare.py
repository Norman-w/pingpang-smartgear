import argparse,concurrent.futures,json,subprocess,tempfile,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
cad=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser(description='Offline diagnostics only; never sends printer commands.')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
root=args.output or Path(tempfile.mkdtemp(prefix='barrier-print-time-'))
root.mkdir(parents=True,exist_ok=True)
source=cad/'print-packages/barrier-clip-v1.11-first-article/reference-roof-down-prepared-NOT-ACTUAL.3mf'
exe='/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
cases=[('6w-30-gyroid',6,'30%','gyroid'),('6w-15-gyroid',6,'15%','gyroid'),('8w-15-gyroid',8,'15%','gyroid'),('6w-15-lines',6,'15%','rectilinear'),('8w-15-lines',8,'15%','rectilinear')]
def run(case):
    name,walls,density,pattern=case
    folder=root/name;folder.mkdir(exist_ok=True)
    project=folder/'input.3mf';out=folder/'sliced.3mf'
    with zipfile.ZipFile(source) as z:
        cfg=json.loads(z.read('Metadata/project_settings.config'))
        cfg.update(wall_loops=str(walls),sparse_infill_density=density,sparse_infill_pattern=pattern,support_type='tree(auto)')
        with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as dest:
            for info in z.infolist():
                data=json.dumps(cfg).encode() if info.filename=='Metadata/project_settings.config' else z.read(info.filename)
                dest.writestr(info,data)
    command=[exe,'--datadir',str(folder/'data'),'--rotate-x','180','--ensure-on-bed','--arrange','0','--orient','0','--slice','0','--export-3mf',str(out),str(project)]
    p=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (folder/'slice.log').write_text(p.stdout)
    if p.returncode:return {'name':name,'error':p.stdout[-1200:]}
    with zipfile.ZipFile(out) as z:
        info=ET.fromstring(z.read('Metadata/slice_info.config'))
        plate=info.find('plate');m={x.get('key'):x.get('value') for x in plate.findall('metadata')}
        assert m['outside']=='false'
        result={'name':name,'seconds':int(m['prediction']),'grams':float(m['weight'])}
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(run,cases))
(root/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
