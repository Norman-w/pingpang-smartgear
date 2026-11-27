// Isolated browser regression test for this local preview; never attaches to user Chrome.
import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
const base=process.argv[2]||'http://192.168.7.187:8791/';
const dir=await fs.mkdtemp(os.tmpdir()+'/guard-mold-v7-ui-');
const browser=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless','--no-first-run','--no-default-browser-check','--remote-debugging-port=9402',`--user-data-dir=${dir}`,'--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows','--window-size=1600,1100','about:blank'],{stdio:'ignore'});
let ws;const checks=[];const errors=[];
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const check=(ok,label)=>{if(!ok)throw Error(label+' '+JSON.stringify(errors));checks.push(label);};
try{
 let targets;
 for(let i=0;i<100;i++){try{targets=await (await fetch('http://127.0.0.1:9402/json')).json();break;}catch{await delay(100);}}
 if(!targets)throw Error('Chrome debug endpoint unavailable');
 ws=new WebSocket(targets.find(x=>x.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener('open',r,{once:true}));
 let n=0;const pending=new Map();
 ws.addEventListener('message',e=>{const d=JSON.parse(e.data);if(d.id){const p=pending.get(d.id);pending.delete(d.id);d.error?p.reject(Error(JSON.stringify(d.error))):p.resolve(d.result);}if(d.method==='Runtime.exceptionThrown')errors.push(d.params.exceptionDetails.text+' '+d.params.exceptionDetails.exception?.description);});
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++n;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:base});
 await evaluate(`new Promise((resolve,reject)=>{let n=0;const t=setInterval(()=>{if(document.body?.dataset.ready==='true'){clearInterval(t);resolve(true);}else if(n++>200){clearInterval(t);reject(Error(document.querySelector('#status')?.textContent||'timeout'));}},50);})`);
 check(await evaluate('document.querySelectorAll("select").length===0'),'flat controls; no dropdowns');
 check(await evaluate('moldSnapshot().instances.length===23'),'23 reference instances, including alternative J locations');
 check(await evaluate('document.querySelectorAll("#stage button").length===18'),'18 ordered unclamp/screw/backoff/extraction stages');
 for(let i=0;i<18;i++){
   await evaluate(`document.querySelectorAll('#stage button')[${i}].click()`);
   const snap=await evaluate('moldSnapshot()');
   if(i===0)check(snap.instances.filter(x=>/^[XYZ]-/.test(x.id)).length===7&&snap.instances.filter(x=>/^[XYZ]-/.test(x.id)).every(x=>x.visible),'all 7 installation rods present; integral seats, no nuts');
   if(i===1)check(snap.instances.filter(x=>x.visible&&x.id.endsWith('-screw')).length===2,'two J screws installed for first demolding step');
   if(i===1)check(snap.instances.filter(x=>/^[XYZ]-/.test(x.id)).every(x=>!x.visible),'clamps removed before ejectors operate');
   check(snap.instances.filter(x=>x.visible&&x.id.endsWith('-screw')).length<=2,'stage '+i+': at most two J screws');
   check(snap.instances.find(x=>x.id==='product-instance').world.every(x=>Math.abs(x)<1e-6),'stage '+i+': PU reference stays fixed');
 }
 check(await evaluate("JSON.stringify(moldSnapshot().instances.find(x=>x.id==='upper-instance').world)==='[120,0,-1]'"),'upper follows original -Z then +X extraction');
 await evaluate(`document.querySelector('#reset').click();document.querySelector('#play').click()`);
 for(let i=0;i<300;i++){if(await evaluate("moldSnapshot().motion['pin-lift']>0"))break;await delay(200);}
 check(await evaluate("moldSnapshot().motion['pin-lift']>0"),'animated extraction updates real frame positions');
 await evaluate(`document.querySelector('#play').click();document.querySelector('#reset').click()`);
 await delay(150);
 const screenshot=async name=>{const x=await send('Page.captureScreenshot',{format:'png'});await fs.writeFile(new URL(name,import.meta.url),Buffer.from(x.data,'base64'));};
 await evaluate(`document.querySelectorAll('#mold-modes button')[1].click()`);
 check(await evaluate("moldSnapshot().instances.filter(x=>x.visible&&x.id.endsWith('-screw')).length<=2"),'only two J demolding screws used at a time');
 await screenshot('preview-closed.png');
 await evaluate(`document.querySelectorAll('#stage button')[4].click()`);
 await screenshot('preview-jack.png');
 await evaluate(`document.querySelectorAll('#band-controls button')[0].click()`);
 await screenshot('preview-thread-detail.png');
 await evaluate(`document.querySelectorAll('#stage button')[17].click()`);
 await screenshot('preview-separated.png');
 check(errors.length===0,'no browser runtime errors');
 await fs.writeFile(new URL('ui-validation.json',import.meta.url),JSON.stringify({checks,errors},null,2));
 console.log(JSON.stringify({checks,errors},null,2));
}finally{ws?.close();const stopped=new Promise(resolve=>browser.once('exit',resolve));browser.kill();await stopped;await fs.rm(dir,{recursive:true,force:true,maxRetries:8,retryDelay:200});}
