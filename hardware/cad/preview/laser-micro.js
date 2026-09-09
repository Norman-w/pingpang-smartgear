import * as THREE from "three";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import {createCadCamera,resizeCadCamera,configureCadNavigation} from "./cad-navigation.js";

const $ = (id) => document.getElementById(id);
const host = $("viewport");
const scene = new THREE.Scene();
const camera = createCadCamera(THREE,31,2000);
camera.up.set(0,0,1);
const renderer = new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.localClippingEnabled=true;
host.append(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);
configureCadNavigation(controls,camera,host,$("pan-mode"));
scene.add(new THREE.HemisphereLight(0xe5f5ff,0x304453,2));
for(const [position,intensity] of [[[-40,-40,70],3],[[40,20,50],2]]) {
  const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.set(...position);scene.add(light);
}
const root = new THREE.Group(); scene.add(root);
const beam = new THREE.ArrowHelper(new THREE.Vector3(-1,0,0),new THREE.Vector3(-4,0,0),28,0xff6969,2,.7);
const beamRoot=new THREE.Group();beamRoot.add(beam);scene.add(beamRoot);
const meshes=new Map();
let manifest=null;
let serviceMode=true,serviceSign=-1,currentView="iso";
const serviceRoot=new THREE.Group();scene.add(serviceRoot);
const serviceRows=[],serviceCovers=[],serviceTools=new Map();
const clipPlanes=[new THREE.Plane(new THREE.Vector3(0,0,1),30),new THREE.Plane(new THREE.Vector3(0,0,-1),45)];
const directions={iso:[-1,-1.2,.85],front:[-1,0,0],top:[0,0,1],rear:[1,.8,.65]};
function view(name="iso") {
  currentView=name;
  camera.up.set(0,name==="top"?1:0,name==="top"?0:1);
  const withdraw=Number($("withdraw").value),shift=withdraw/(2*Math.sqrt(2));
  const explode=Number($("explode").value)/100;
  controls.target.set(serviceMode?8:0,serviceMode?serviceSign*(12+shift):0,serviceMode?22+shift:6*explode);
  const direction=serviceMode&&name==="iso"?[1,serviceSign*1.4,.65]:directions[name];
  const distance=serviceMode?210+withdraw*1.6:90+explode*45;
  camera.position.copy(new THREE.Vector3(...direction).normalize().multiplyScalar(distance)).add(controls.target);
  const bounds=host.getBoundingClientRect();
  resizeCadCamera(camera,bounds.width,bounds.height,distance*Math.tan(THREE.MathUtils.degToRad(19)),true);
  controls.update();
  document.querySelectorAll("[data-view]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.view===name)));
}
function resize(){const r=host.getBoundingClientRect();if(!r.width||!r.height)return;renderer.setSize(r.width,r.height);resizeCadCamera(camera,r.width,r.height);}
new ResizeObserver(resize).observe(host);
view();resize();
renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera);});
function tip(sign,p,y) {
  const a=[Math.cos(p)*Math.cos(y),Math.cos(p)*Math.sin(y),-Math.sin(p)];
  const l=manifest.parameters.lever,r=manifest.parameters.tail_d/2;
  const b=l*a[0],c=(sign*a[1]+a[2])/Math.sqrt(2),aa=1-c*c,bb=-2*b*c,cc=l*l-b*b-r*r;
  return (-bb+Math.sqrt(bb*bb-4*aa*cc))/(2*aa);
}
function update(){
  if(!manifest)return;
  const pitch=Number($("pitch").value),yaw=Number($("yaw").value),e=Number($("explode").value)/100;
  const p=THREE.MathUtils.degToRad(pitch),y=THREE.MathUtils.degToRad(yaw);
  const rotation=new THREE.Quaternion().setFromEuler(new THREE.Euler(0,p,y,"ZYX"));
  const ta=tip(1,p,y)-manifest.parameters.tail_d/2,tb=tip(-1,p,y)-manifest.parameters.tail_d/2;
  for(const part of manifest.parts){
    const mesh=meshes.get(part.id);if(!mesh)continue;
    mesh.position.set(...part.explosion.map(v=>v*e));mesh.quaternion.identity();mesh.scale.set(1,1,1);
    if(part.moving){mesh.quaternion.copy(rotation);mesh.position.applyQuaternion(rotation);}
    if(part.id==="screw_a"||part.id==="screw_b"){
      const sign=part.id==="screw_a"?1:-1,delta=sign===1?ta:tb;
      mesh.position.add(new THREE.Vector3(0,sign*delta/Math.sqrt(2),delta/Math.sqrt(2)));
    }
    if(part.id==="spring"){
      const h=3.1-manifest.parameters.lever*Math.sin(p),ratio=h/3.1;
      mesh.scale.z=ratio;mesh.position.z=-7.4*(1-ratio);
    }
    if(part.id==="cap"){
      mesh.material.opacity=$("translucent").checked?.24:1;
      mesh.material.transparent=$("translucent").checked;mesh.material.depthWrite=!$("translucent").checked;
    }
  }
  beamRoot.quaternion.copy(rotation);beamRoot.position.set(10*e,-10*e,9*e).applyQuaternion(rotation);
  $("pitch-out").textContent=`${pitch.toFixed(1)}°`;$("yaw-out").textContent=`${yaw.toFixed(1)}°`;$("explode-out").textContent=`${Math.round(e*100)}%`;
  $("screw-readout").textContent=`相对零位：A ${ta.toFixed(2)} mm / B ${tb.toFixed(2)} mm。每转 ${manifest.parameters.screw_pitch} mm；此处演示调节几何。`;
  host.dataset.pitch=String(pitch);host.dataset.yaw=String(yaw);host.dataset.explode=String(e);
}
function numberLabel(number){
  const canvas=document.createElement("canvas");canvas.width=128;canvas.height=64;
  const ctx=canvas.getContext("2d");ctx.fillStyle="#0c171eee";ctx.fillRect(0,0,128,64);
  ctx.font="bold 34px sans-serif";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillStyle="#ffffff";ctx.fillText(`${number} 号`,64,34);
  const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(canvas),depthTest:false}));
  sprite.scale.set(13,6.5,1);sprite.position.set(-10,-23,3);return sprite;
}
function updateService(){
  root.visible=!serviceMode;beamRoot.visible=!serviceMode;serviceRoot.visible=serviceMode;
  $("service-controls").hidden=!serviceMode;$("single-controls").hidden=serviceMode;$("single-parts").hidden=serviceMode;
  $("service-mode").setAttribute("aria-pressed",String(serviceMode));$("single-mode").setAttribute("aria-pressed",String(!serviceMode));
  host.dataset.mode=serviceMode?"service":"single";
  if(!manifest)return;
  const p=manifest.parameters,channel=Number($("channel").value),withdraw=Number($("withdraw").value);
  for(const [index,row] of serviceRows.entries()){
    row.position.z=(index-channel)*p.pitch;row.visible=Math.abs(index-channel)<=1;
    row.children.forEach(mesh=>{if(mesh.isMesh)mesh.material.emissive.set(index===channel?0x182f33:0);});
  }
  for(const mesh of serviceCovers){
    mesh.position.set(-p.origin_x,0,-p.first_z-channel*p.pitch);
    if(["front_cover","rear_cover","bottom_cover"].includes(mesh.name)){
      mesh.material.opacity=$("service-shell").checked?.18:1;
      mesh.material.transparent=$("service-shell").checked;mesh.material.depthWrite=!$("service-shell").checked;
    }
  }
  for(const [sign,tool] of serviceTools){
    tool.visible=sign===serviceSign;tool.position.set(0,sign*withdraw/Math.sqrt(2),withdraw/Math.sqrt(2));
  }
  $("withdraw-out").textContent=`${withdraw} mm`;
  const neighbours=[channel,channel+2].filter(n=>n>=1&&n<=p.count).map(n=>`${n} 号`).join("、");
  const entry=p.shell_top_z-(p.first_z+channel*p.pitch)<p.shell_half_y?"顶部":"侧面";
  const port=`${serviceSign>0?"A":"B"}${channel+1}`;
  $("service-status").textContent=`${channel+1} 号 · ${entry} ${port} 孔。${neighbours}保持安装；后盖和球头固定。孔径 ${p.access_d} mm，工具外径 ${p.tool_d} mm。`;
  $("view-caption").textContent=(serviceMode?"局部剖看：实际头套保持完整，青色为操作工具。":"红线表示出光方向。")+"左键旋转 · 滚轮围绕鼠标缩放 · 中键或右键拖动平移";
  host.dataset.channel=String(channel+1);host.dataset.toolSide=serviceSign>0?"A":"B";host.dataset.withdraw=String(withdraw);
}
$("single-mode").addEventListener("click",()=>{serviceMode=false;updateService();update();view();});
$("service-mode").addEventListener("click",()=>{serviceMode=true;updateService();view();});
$("channel").addEventListener("change",()=>{updateService();view();});
$("service-shell").addEventListener("change",updateService);
$("withdraw").addEventListener("input",()=>{updateService();view();});
for(const [id,sign] of [["tool-a",1],["tool-b",-1]])$(id).addEventListener("click",()=>{
  serviceSign=sign;$("tool-a").setAttribute("aria-pressed",String(sign===1));$("tool-b").setAttribute("aria-pressed",String(sign===-1));updateService();view();
});
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>view(b.dataset.view)));
for(const id of ["pitch","yaw","translucent"])$(id).addEventListener("input",update);
$("explode").addEventListener("input",()=>{update();view(currentView);});
$("reset").addEventListener("click",()=>{for(const id of ["pitch","yaw","explode","withdraw"])$(id).value="0";update();updateService();view();});
document.querySelectorAll("[data-parts]").forEach(button=>button.addEventListener("click",()=>{
  const active=button.getAttribute("aria-pressed")!=="true";
  document.querySelectorAll("[data-parts]").forEach(b=>b.setAttribute("aria-pressed",String(active&&b===button)));
  for(const [id,mesh] of meshes){mesh.material.emissive.set(active&&button.dataset.parts.split(",").includes(id)?0x487b8a:0);}
}));
try{
  const url=new URL("../exports/laser-micro-mount-v0.1/manifest.json",location.href);
  const response=await fetch(url,{cache:"no-store"});if(!response.ok)throw new Error(`清单 HTTP ${response.status}`);
  manifest=await response.json();
  for(const part of manifest.parts.filter(p=>p.printable)) {
    const link=document.createElement("a");link.href=new URL(part.file,url).href;link.download=part.file;
    link.textContent=`${part.name_zh} · ${part.material} · STL`;$("print-files").append(link);
  }
  const loader=new STLLoader();
  await Promise.all(manifest.parts.filter(p=>p.scope==="cassette").map(async part=>{
    const geometry=await loader.loadAsync(new URL(`${part.file}?v=${part.sha256.slice(0,12)}`,url).href);
    geometry.computeVertexNormals();
    const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:part.color,roughness:.52,metalness:part.printable?.03:.5}));
    mesh.name=part.id;root.add(mesh);meshes.set(part.id,mesh);
  }));
  for(let i=0;i<manifest.parameters.count;i++){
    const option=document.createElement("option");option.value=String(i);option.textContent=`${i+1} 号${i===8?" · 上方是 10 号":""}`;$("channel").append(option);
    const row=new THREE.Group();serviceRows.push(row);serviceRoot.add(row);
    for(const [id,original] of meshes){
      const mesh=new THREE.Mesh(original.geometry,original.material.clone());mesh.name=id;row.add(mesh);
    }
    row.add(numberLabel(i+1));
  }
  $("channel").value="8";
  await Promise.all(manifest.parts.filter(p=>p.scope==="array").map(async part=>{
    const geometry=await loader.loadAsync(new URL(`${part.file}?v=${part.sha256.slice(0,12)}`,url).href);geometry.computeVertexNormals();
    const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:part.color,roughness:.6,clippingPlanes:clipPlanes}));
    mesh.name=part.id;serviceCovers.push(mesh);serviceRoot.add(mesh);
  }));
  await Promise.all(manifest.service_assets.map(async asset=>{
    const geometry=await loader.loadAsync(new URL(`${asset.file}?v=${asset.sha256.slice(0,12)}`,url).href);geometry.computeVertexNormals();
    const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0x62e4d1,roughness:.3,metalness:.4}));
    serviceTools.set(asset.sign,mesh);serviceRoot.add(mesh);
  }));
  $("dimension").textContent=`Ø${manifest.parameters.module_d} × ${manifest.parameters.module_length} mm 裸头占位`;
  for(const id of ["pitch","yaw","explode","channel","withdraw"])$(id).disabled=false;
  $("loading").hidden=true;host.dataset.loaded=String(meshes.size);update();updateService();view();
}catch(error){$("loading").textContent=`夹座未能载入：${error.message}。请运行 export_laser_micro_mount.py 后刷新。`;console.error(error);}
