// Orthographic CAD navigation keeps the orbit distance independent of zoom.
// Panning is measured in screen pixels at every scale, including close-ups.
export function createCadCamera(THREE, halfHeight=100, far=10000) {
  const camera=new THREE.OrthographicCamera(-halfHeight,halfHeight,halfHeight,-halfHeight,.05,far);
  camera.userData.halfHeight=halfHeight;
  camera.up.set(0,0,1);
  return camera;
}

export function resizeCadCamera(camera,width,height,halfHeight=camera.userData.halfHeight,resetZoom=false) {
  const aspect=Math.max(width,1)/Math.max(height,1);
  camera.userData.halfHeight=halfHeight;
  camera.left=-halfHeight*aspect;camera.right=halfHeight*aspect;
  camera.top=halfHeight;camera.bottom=-halfHeight;
  if(resetZoom)camera.zoom=1;
  camera.updateProjectionMatrix();
}

export function configureCadNavigation(controls,camera,host,panButton=null) {
  controls.enableDamping=true;
  controls.dampingFactor=.12;
  controls.zoomToCursor=true;
  controls.zoomSpeed=1.65;
  controls.screenSpacePanning=true;
  controls.panSpeed=1;
  controls.minZoom=.02;
  controls.maxZoom=2000;
  controls.mouseButtons.MIDDLE=controls.mouseButtons.RIGHT;
  if(panButton){
    const rotateButton=controls.mouseButtons.LEFT;
    panButton.addEventListener("click",()=>{
      const enabled=panButton.getAttribute("aria-pressed")!=="true";
      panButton.setAttribute("aria-pressed",String(enabled));
      controls.mouseButtons.LEFT=enabled?controls.mouseButtons.RIGHT:rotateButton;
    });
  }
  let published="";
  const publish=()=>{
    const zoom=camera.zoom.toFixed(6);
    const span=((camera.top-camera.bottom)/camera.zoom).toFixed(6);
    const target=controls.target.toArray().map(x=>x.toFixed(6)).join(",");
    const state=`${zoom}|${span}|${target}`;
    if(state===published)return;
    published=state;
    host.dataset.cameraProjection="orthographic";
    host.dataset.cameraZoom=zoom;
    host.dataset.cameraSpan=span;
    host.dataset.cameraTarget=target;
  };
  controls.addEventListener("change",publish);
  publish();
}
