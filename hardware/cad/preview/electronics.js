import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";

const MANIFEST_URL = new URL("../exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json", import.meta.url);
const MODEL_ROOT = new URL("../../../electronics/3d/v0.2/", MANIFEST_URL);
const PREVIEW_CACHE_BUSTER = "electronics-v39";
const COLORS = Object.freeze({
  shellUser: "#65727b",
  shellOpponent: "#8898a1",
  mainBoard: "#2f80ed",
  emitterBoard: "#c94b63",
  uiBoard: "#48a0e8",
  uiBezel: "#222f38",
  uiFrame: "#f2a33b",
});

const D = Object.freeze({
  cavityXMin: 777.5,
  cavityXMax: 894.3,
  cavityYHalf: 20,
  boardXMin: 792.9,
  boardXMax: 878.9,
  boardYMin: -16,
  boardBottomZ: -36.4912,
  emitterBoardXMin: 802.9,
  emitterBoardXMax: 870.9,
  emitterBoardYMin: -16,
  emitterBoardBottomZ: -35.8912,
  uiBoardXMin: 806.9,
  // UI PCB is the interference datum behind the positive-Y wall window; the
  // printed insert panel is installed from y- and finishes at the wall outer
  // face. The KiCad board remains at the same world plane.
  // The PCB stays at y=19.2 inside the cavity; the printed USB land reaches
  // inward to the KiCad housing front without moving the complete board.
  uiSideBoardPlaneY: 19.2,
  // ui-panel-v0.2.stl has a raw KiCad component envelope down to z=-2.51.
  // normalizeGeometry() removes that minimum, so put it back here; otherwise
  // the browser moves the whole board 2.51 mm toward the panel and exposes
  // the connector's far interior beyond the printed bowl datum.
  uiBoardModelMinZ: -2.51,
  uiSideZMin: -40,
  uiBoardWidth: 28,
  // Bounds of PART="clamp_electronics_ui_physical_items" exported from the
  // SCAD off-board component library (screen + speaker only). The STL is
  // normalized at load time; this is its world-space minimum in the same
  // assembly datum.
  uiPhysicalItemsMin: [823.4, 25.8, -33.0],
  // World-axis reference is translated into the active cavity so it stays
  // visible while retaining the shared global x/y/z directions.
  axisOriginX: (777.5 + 894.3) / 2,
  axisOriginZ: -35,
  axisLength: 35,
});

const refs = {
  host: document.querySelector("#model-host"),
  placeholder: document.querySelector("#model-placeholder"),
  hover: document.querySelector("#hover-label"),
  status: document.querySelector("#load-status"),
  statusDot: document.querySelector("#status-dot"),
  error: document.querySelector("#error-banner"),
  title: document.querySelector("#model-title"),
  caption: document.querySelector("#model-caption"),
  selectionTitle: document.querySelector("#selection-title"),
  selectionDetail: document.querySelector("#selection-detail"),
  objectCount: document.querySelector("#object-count"),
  manifestLink: document.querySelector("#source-manifest-link"),
  explode: document.querySelector("#explode-range"),
  explodeOutput: document.querySelector("#explode-output"),
  shellOpacity: document.querySelector("#shell-opacity"),
  shellOpacityOutput: document.querySelector("#shell-opacity-output"),
};

const state = {
  manifest: null,
  items: [],
  itemById: new Map(),
  side: "right",
  explode: 0,
  shellOpacity: 0.22,
  showUserShell: false,
  showOpponentShell: true,
  showMainBoard: true,
  showEmitterBoard: true,
  showUi: true,
  view: "iso",
  loaded: false,
  scene: null,
  camera: null,
  renderer: null,
  controls: null,
  root: null,
  axes: null,
  raycaster: new THREE.Raycaster(),
  pointer: new THREE.Vector2(),
  selectedId: null,
  focus: null,
  // STL files arrive asynchronously. Once the user starts orbiting, the
  // eventual load completion must never re-apply the initial ISO fit.
  cameraInteracted: false,
  initialViewApplied: false,
  cameraProgrammatic: false,
};

function makeAxisLabel(text, color) {
  const canvas = document.createElement("canvas");
  canvas.width = 320;
  canvas.height = 72;
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.font = "700 30px -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.lineWidth = 8;
  context.strokeStyle = "rgba(5, 16, 21, .92)";
  context.strokeText(text, canvas.width / 2, canvas.height / 2);
  context.fillStyle = color;
  context.fillText(text, canvas.width / 2, canvas.height / 2);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.minFilter = THREE.LinearFilter;
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthTest: false,
    depthWrite: false,
  });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(20, 4.5, 1);
  sprite.renderOrder = 30;
  return sprite;
}

function createWorldAxes() {
  const group = new THREE.Group();
  group.name = "world-coordinate-axes";
  const helper = new THREE.AxesHelper(D.axisLength);
  helper.name = "world-coordinate-axes-lines";
  helper.renderOrder = 20;
  const axisMaterials = Array.isArray(helper.material) ? helper.material : [helper.material];
  axisMaterials.forEach((material) => {
    material.transparent = true;
    material.opacity = 0.92;
    material.depthTest = false;
    material.depthWrite = false;
    material.needsUpdate = true;
  });
  group.add(helper);

  const length = D.axisLength;
  const labels = [
    ["X+ 右", "#ff6b6b", [length + 3, 0, 0]],
    ["X− 左", "#ff6b6b", [-length - 3, 0, 0]],
    ["Y+ UI侧", "#68e0b4", [0, length + 4, 0]],
    ["Y− 操作者侧", "#68e0b4", [0, -length - 5, 0]],
    ["Z+ 上", "#6ea8ff", [0, 0, length + 3]],
    ["Z− 下", "#6ea8ff", [0, 0, -length - 3]],
  ];
  for (const [text, color, position] of labels) {
    const label = makeAxisLabel(text, color);
    label.position.set(...position);
    label.userData.axisLabel = true;
    group.add(label);
  }
  state.axes = group;
  state.scene.add(group);
  updateWorldAxesOrigin();
}

function updateWorldAxesOrigin() {
  if (!state.axes) return;
  const sign = state.side === "left" ? -1 : 1;
  state.axes.position.set(sign * D.axisOriginX, 0, D.axisOriginZ);
}

function setStatus(text, kind = "loading") {
  refs.status.textContent = text;
  refs.statusDot.className = `status-dot ${kind === "ready" ? "ready" : kind === "error" ? "error" : ""}`;
}

function number(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function sourceEntry(file) {
  return state.manifest?.parts?.find((entry) => entry.file === file) || null;
}

function geometryUrl(file) {
  // Electronics STLs live beside the KiCad exports under hardware/electronics.
  // Keep optional guide parts in this list too; otherwise a new part is
  // resolved relative to the print-package manifest and makes Promise.all()
  // reject the complete view with a misleading 404.
  const base = /^(esp32-control|emitter-power|ui-panel|ui-physical-items|ui-led-light-pipes|m6-receiver)/.test(file) ? MODEL_ROOT : MANIFEST_URL;
  const url = file.startsWith("http") ? new URL(file) : new URL(file, base);
  if (state.manifest?.source_sha256) url.searchParams.set("v", state.manifest.source_sha256.slice(0, 16));
  return url.href;
}

function sideVisible(side) {
  // Keep the electronics page single-sided.  The two mirrored assemblies are
  // large enough that placing them in one canvas makes a cavity/PCB easy to
  // misidentify; switch between the dedicated right and left views instead.
  return state.side === side;
}

function createMaterial(color, opacity = 1, options = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness: options.roughness ?? 0.66,
    metalness: options.metalness ?? 0.04,
    transparent: opacity < 0.999,
    opacity,
    depthWrite: opacity > 0.5,
    side: options.side || THREE.FrontSide,
  });
}

function normalizeGeometry(geometry) {
  geometry.computeBoundingBox();
  const min = geometry.boundingBox.min;
  geometry.translate(-min.x, -min.y, -min.z);
  geometry.computeBoundingBox();
  geometry.computeVertexNormals();
  return geometry;
}

async function loadGeometry(url) {
  return new Promise((resolve, reject) => {
    new STLLoader().load(url, resolve, undefined, reject);
  });
}

function makeItem(id, name, category, basePosition, explosion = [0, 0, 0], options = {}) {
  const item = {
    id,
    name,
    category,
    object: new THREE.Group(),
    basePosition: basePosition.map(number),
    explosion: explosion.map(number),
    side: options.side || 0,
    role: options.role || category,
    visibleWhen: options.visibleWhen || (() => true),
    detail: options.detail || "来源模型",
    meshes: [],
  };
  item.object.userData.previewId = id;
  item.object.userData.previewItem = item;
  state.itemById.set(id, item);
  state.items.push(item);
  state.root.add(item.object);
  return item;
}

function entryBounds(file) {
  const entry = sourceEntry(file);
  if (!entry?.bounds?.min) throw new Error(`manifest 中找不到 ${file} 的 bounds`);
  return entry.bounds;
}

async function addStlItem({ id, name, category, file, basePosition, color, side, role, explosion, detail, mirrorX = false, rotation = null, opacity = 1, visibleWhen }) {
  const item = makeItem(id, name, category, basePosition, explosion, { side, role, detail, visibleWhen });
  const geometry = normalizeGeometry(await loadGeometry(geometryUrl(file)));
  const material = createMaterial(color, opacity, { side: mirrorX ? THREE.DoubleSide : THREE.FrontSide });
  const mesh = new THREE.Mesh(geometry, material);
  if (rotation) mesh.rotation.set(...rotation);
  if (mirrorX) mesh.scale.x = -1;
  mesh.userData.previewId = id;
  item.object.add(mesh);
  item.meshes.push(mesh);
  item.object.userData.bounds = sourceEntry(file)?.bounds || null;
  return item;
}

function addShellItem(file, sideName, half, basePosition) {
  const color = half === "user" ? COLORS.shellUser : COLORS.shellOpponent;
  const id = `shell:${sideName}:${half}`;
  return addStlItem({
    id,
    name: `${sideName === "right" ? "右侧" : "左侧"} C 夹${half === "user" ? "操作者侧半体（y−）" : "对手侧半体（y＋）"}`,
    category: "shell",
    file,
    basePosition,
    color,
    side: sideName === "right" ? 1 : -1,
    role: "shell",
    explosion: half === "user" ? [0, -22, 0] : [0, 22, 0],
    opacity: state.shellOpacity,
    detail: `当前正式分型壳体 STL；${half === "user" ? "y− 操作者侧" : "y＋ 对手侧"}。透明度仅用于看内部，不代表材料透明。`,
    visibleWhen: () => sideVisible(sideName) && (half === "user" ? state.showUserShell : state.showOpponentShell),
  });
}

function addMainBoard() {
  return addStlItem({
    id: "electronics:main-board:right",
    name: "ESP32-S3 主控板（真实 KiCad STL）",
    category: "board",
    file: "esp32-control-v0.1.stl",
    basePosition: [D.boardXMin, D.boardYMin, D.boardBottomZ],
    color: COLORS.mainBoard,
    side: 1,
    role: "main-board",
    explosion: [0, 0, 24],
    detail: "真实 KiCad 板级模型；板框 86 × 32 mm，沿 y=0 腔体中线居中，左右墙各留约 4 mm，包含板上器件的 3D 包络。",
    visibleWhen: () => sideVisible("right") && state.showMainBoard,
  });
}

function addEmitterBoard() {
  return addStlItem({
    id: "electronics:emitter-board:left",
    name: "发射端电源子板（真实 KiCad STL）",
    category: "emitter",
    file: "emitter-power-v0.2.stl",
    basePosition: [-D.emitterBoardXMin, D.emitterBoardYMin, D.emitterBoardBottomZ],
    color: COLORS.emitterBoard,
    side: -1,
    role: "emitter-board",
    explosion: [0, 0, 24],
    mirrorX: true,
    detail: "真实 KiCad 板级模型；在左侧腔体按 x 镜像放置，安装方向以现场接线和实物孔位复核。",
    visibleWhen: () => sideVisible("left") && state.showEmitterBoard,
  });
}

async function addUiBoard() {
  const item = await addStlItem({
    id: "electronics:ui-board:right",
    name: "UI 子板（真实 KiCad STL）",
    category: "ui",
    file: "ui-panel-v0.2.stl",
    basePosition: [
      D.uiBoardXMin,
      D.uiSideBoardPlaneY + D.uiBoardModelMinZ,
      D.uiSideZMin + D.uiBoardWidth,
    ],
    color: COLORS.uiBoard,
    side: 1,
    role: "ui",
    explosion: [0, 34, 0],
    detail: "真实 KiCad 板级 STL；包含 PCB、板侧线束连接器，以及 KiCad 封装中的按键、LED、USB-C 3D 模型。",
    visibleWhen: () => sideVisible("right") && state.showUi,
  });
  // STLLoader normalizes the raw KiCad y=-28..0 range to 0..28. Reflect it
  // back into the shared side datum before the -90° X rotation: KiCad y=8
  // must land at the faceplate's local y=8, not at y=20.
  const boardMesh = item.meshes[0];
  boardMesh.scale.y = -1;
  boardMesh.position.y = D.uiBoardWidth;
  // Rotate the KiCad board so its 58 x 28 face becomes an x/z panel on the
  // positive-Y wall. The normalized STL is top-anchored in z; board/component
  // material ends at the side opening and the service face projects to y+.
  item.object.rotation.x = -Math.PI / 2;
  return item;
}

async function addUiPhysicalItems() {
  return addStlItem({
    id: "electronics:ui-physical-items:right",
    name: "UI 线束实体件（SCAD）",
    category: "ui-components",
    file: "ui-physical-items-v0.2.stl",
    basePosition: D.uiPhysicalItemsMin,
    color: "#7be0c0",
    side: 1,
    role: "ui-components",
    explosion: [0, 34, 0],
    detail: "来自 net_stand.scad 的 clamp_electronics_ui_physical_items：仅挂载通过线束连接的屏幕和扬声器；PCB 按键、LED、USB-C 已由 KiCad 板 STL 提供。",
    visibleWhen: () => sideVisible("right") && state.showUi,
  });
}

async function addUiPanelMount() {
  const bounds = entryBounds("right-clamp-electronics-ui-panel-mount.stl");
  return addStlItem({
    id: "electronics:ui-panel-mount:right",
    name: "右侧 y+ UI 填平固定板（一体打印 STL）",
    category: "ui-panel-mount",
    file: "right-clamp-electronics-ui-panel-mount.stl",
    basePosition: bounds.min,
    color: COLORS.uiBezel,
    side: 1,
    role: "ui-panel-mount",
    explosion: [0, 34, 0],
    detail: "当前打印包中的正式一体式 UI 填平固定板 STL；从电子腔 y- 侧穿入窗口，外侧齐平，腔内侧固定法兰、捕获环和 8 个螺钉孔与面板融合。按键导向柱、LED 直孔、屏幕窗、扬声器窗和 Type-C 圆角碗槽均以 KiCad UI 板为同一干涉基准，外围碗槽保留 0.60 mm 环形底，中心 KiCad-fit 通孔贯穿，由 Type-C 模型负责中心显示。",
    visibleWhen: () => sideVisible("right") && state.showUi,
  });
}

async function addUiLightPipes() {
  // Optional transparent-print guide part generated from the same SCAD datum.
  // It is intentionally a separate object so a clear resin/PETG guide can be
  // printed without turning the opaque UI insert panel into a fake LED body.
  const id = "electronics:ui-led-light-pipes:right";
  try {
    return await addStlItem({
      id,
      name: "UI LED 导光柱（可选透明件）",
      category: "ui-components",
      file: "ui-led-light-pipes-v0.2.stl",
      basePosition: [834.9, 25.4, -38.0],
      color: "#b8f6dc",
      side: 1,
      role: "ui-components",
      explosion: [0, 34, 0],
      detail: "由 net_stand.scad 的 LED 中心生成的独立透明导光柱；不重复创建 0603 LED，直线穿过内装封口板的 LED 孔。",
      visibleWhen: () => sideVisible("right") && state.showUi,
    });
  } catch (error) {
    // A transparent guide is optional.  If an older checkout has not yet
    // received this STL, remove the half-created item and keep the real shell,
    // KiCad boards and UI insert usable instead of failing the whole view.
    const item = state.itemById.get(id);
    if (item) {
      state.root.remove(item.object);
      state.itemById.delete(id);
      state.items = state.items.filter((candidate) => candidate !== item);
    }
    console.warn("optional UI LED light pipes unavailable", error);
    return null;
  }
}

function updateItemTransform(item) {
  item.object.position.set(
    item.basePosition[0] + item.explosion[0] * state.explode,
    item.basePosition[1] + item.explosion[1] * state.explode,
    item.basePosition[2] + item.explosion[2] * state.explode,
  );
}

function updateVisibility() {
  for (const item of state.items) {
    item.object.visible = Boolean(item.visibleWhen());
    updateItemTransform(item);
    if (item.role === "shell") {
      item.meshes.forEach((mesh) => {
        const material = mesh.material;
        if (!material) return;
        material.opacity = state.shellOpacity;
        material.transparent = state.shellOpacity < 0.999;
        material.depthWrite = state.shellOpacity > 0.5;
      });
    }
  }
  const visible = state.items.filter((item) => item.object.visible).length;
  refs.objectCount.textContent = String(visible);
  const sideText = state.side === "right" ? "右侧主控电子腔" : "左侧发射电子腔";
  refs.title.textContent = `${sideText} · ${state.explode ? `维护展开 ${Math.round(state.explode * 100)}%` : "开放腔体"}`;
}

function visibleBounds() {
  const box = new THREE.Box3();
  let hasMesh = false;
  for (const item of state.items) {
    if (!item.object.visible) continue;
    item.object.updateMatrixWorld(true);
    item.object.traverse((child) => {
      if (child.isMesh || child.isLineSegments) {
        box.expandByObject(child);
        hasMesh = true;
      }
    });
  }
  if (!hasMesh || box.isEmpty()) box.set(new THREE.Vector3(770, -30, -80), new THREE.Vector3(910, 30, 10));
  return box;
}

function focusBounds(role) {
  const box = new THREE.Box3();
  let hasMesh = false;
  for (const item of state.items) {
    if (!item.object.visible) continue;
    const match = role === "cavity" ? ["shell", "main-board", "emitter-board", "ui", "ui-components", "ui-panel-mount"].includes(item.role)
      : role === "board" ? ["main-board", "emitter-board"].includes(item.role)
        : role === "ui" ? ["ui", "ui-components", "ui-panel-mount"].includes(item.role)
            : true;
    if (!match) continue;
    item.object.updateMatrixWorld(true);
    item.object.traverse((child) => {
      if (child.isMesh || child.isLineSegments) { box.expandByObject(child); hasMesh = true; }
    });
  }
  return hasMesh && !box.isEmpty() ? box : visibleBounds();
}

function setCameraView(view = state.view, focus = state.focus, options = {}) {
  const force = Boolean(options.force);
  // A completed STL request or a visibility refresh must never overwrite a
  // camera that the user has already touched.  Only an explicit view/fit/
  // reset action passes force:true.
  if (state.initialViewApplied && state.cameraInteracted && !force) return false;
  state.view = view;
  const box = focusBounds(focus);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  if (![center.x, center.y, center.z, size.x, size.y, size.z].every(Number.isFinite)) {
    center.set((D.cavityXMin + D.cavityXMax) / 2, 0, -35);
    size.set(D.cavityXMax - D.cavityXMin, D.cavityYHalf * 2, 80);
  }
  const radius = Math.max(size.length() * 0.56, 60);
  const directions = {
    iso: new THREE.Vector3(1.18, -1.35, 0.92),
    split: new THREE.Vector3(0, -1.75, 0.04),
    side: new THREE.Vector3(0, 1.75, 0.12),
    top: new THREE.Vector3(0.08, -0.2, 1.8),
    bottom: new THREE.Vector3(-0.08, 0.2, -1.8),
  };
  const direction = (directions[view] || directions.iso).clone().normalize();
  state.cameraProgrammatic = true;
  try {
    state.camera.position.copy(center).addScaledVector(direction, radius * 1.62);
    state.camera.near = Math.max(0.1, radius / 1000);
    state.camera.far = Math.max(3000, radius * 10);
    state.camera.updateProjectionMatrix();
    state.controls.target.copy(center);
    state.camera.lookAt(center);
    state.camera.updateMatrixWorld(true);
    state.controls.update();
    state.camera.lookAt(center);
    state.camera.updateMatrixWorld(true);
  } finally {
    state.cameraProgrammatic = false;
  }
  document.querySelectorAll("[data-view]").forEach((button) => button.classList.toggle("active", button.dataset.view === view));
  return true;
}

function applySelection(item) {
  state.selectedId = item?.id || null;
  if (!item) {
    refs.selectionTitle.textContent = "未选择对象";
    refs.selectionDetail.textContent = "鼠标移动到模型上查看名称；点击后固定说明。";
    return;
  }
  refs.selectionTitle.textContent = item.name;
  refs.selectionDetail.textContent = item.detail;
}

function hoveredItem(event) {
  const rect = refs.host.getBoundingClientRect();
  state.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  state.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  state.raycaster.setFromCamera(state.pointer, state.camera);
  const roots = state.items.filter((item) => item.object.visible).map((item) => item.object);
  const hits = state.raycaster.intersectObjects(roots, true);
  for (const hit of hits) {
    const id = hit.object.userData.previewId;
    if (id && state.itemById.has(id)) return state.itemById.get(id);
  }
  return null;
}

function wirePointerEvents() {
  refs.host.addEventListener("pointermove", (event) => {
    const item = hoveredItem(event);
    if (!item) { refs.hover.hidden = true; return; }
    refs.hover.textContent = item.name;
    const rect = refs.host.getBoundingClientRect();
    refs.hover.style.left = `${Math.min(rect.width - refs.hover.offsetWidth - 10, Math.max(8, event.clientX - rect.left + 12))}px`;
    refs.hover.style.top = `${Math.min(rect.height - 32, Math.max(8, event.clientY - rect.top + 12))}px`;
    refs.hover.hidden = false;
  });
  refs.host.addEventListener("pointerleave", () => { refs.hover.hidden = true; });
  refs.host.addEventListener("click", (event) => applySelection(hoveredItem(event)));
}

function bindControls() {
  document.querySelectorAll("[data-side]").forEach((button) => button.addEventListener("click", () => {
    state.side = button.dataset.side;
    document.querySelectorAll("[data-side]").forEach((other) => other.classList.toggle("active", other === button));
    updateWorldAxesOrigin();
    updateVisibility();
    setCameraView(state.view, state.focus, {force: true});
  }));
  document.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => { state.focus = null; setCameraView(button.dataset.view, state.focus, {force: true}); }));
  document.querySelectorAll("[data-focus]").forEach((button) => button.addEventListener("click", () => {
    state.focus = button.dataset.focus;
    // The UI hardware faces y+.  Jumping to the y+ camera when the user asks
    // for the UI focus prevents the default y- isometric view from showing
    // only the back edge of the small daughter board.
    const focusView = state.focus === "ui" ? "side" : state.view;
    setCameraView(focusView, state.focus, {force: true});
  }));
  refs.explode.addEventListener("input", () => { state.explode = number(refs.explode.value) / 100; refs.explodeOutput.textContent = String(Math.round(state.explode * 100)); updateVisibility(); });
  refs.shellOpacity.addEventListener("input", () => { state.shellOpacity = number(refs.shellOpacity.value) / 100; refs.shellOpacityOutput.textContent = String(Math.round(state.shellOpacity * 100)); updateVisibility(); });
  const checks = {
    "show-user-shell": "showUserShell", "show-opponent-shell": "showOpponentShell",
    "show-main-board": "showMainBoard", "show-emitter-board": "showEmitterBoard",
    "show-ui": "showUi",
  };
  Object.entries(checks).forEach(([id, key]) => document.querySelector(`#${id}`).addEventListener("change", (event) => { state[key] = event.target.checked; updateVisibility(); }));
  refs.host.addEventListener("dblclick", () => { state.focus = null; setCameraView(state.view, state.focus, {force: true}); });
  document.querySelector("#fit-button").addEventListener("click", () => setCameraView(state.view, state.focus, {force: true}));
  document.querySelector("#reset-button").addEventListener("click", () => { state.explode = 0; refs.explode.value = "0"; refs.explodeOutput.textContent = "0"; state.focus = null; updateVisibility(); setCameraView("iso", state.focus, {force: true}); });
}

function setupThree() {
  state.scene = new THREE.Scene();
  state.scene.background = new THREE.Color("#071319");
  state.camera = new THREE.PerspectiveCamera(34, 1, 0.1, 5000);
  state.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  state.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  state.renderer.outputColorSpace = THREE.SRGBColorSpace;
  state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
  state.renderer.toneMappingExposure = 1.12;
  refs.host.appendChild(state.renderer.domElement);
  state.controls = new OrbitControls(state.camera, state.renderer.domElement);
  state.controls.enableDamping = true;
  state.controls.dampingFactor = 0.08;
  state.controls.screenSpacePanning = true;
  state.controls.minDistance = 20;
  state.controls.maxDistance = 2500;
  const markCameraInteraction = () => {
    if (!state.cameraProgrammatic) state.cameraInteracted = true;
  };
  state.controls.addEventListener("start", markCameraInteraction);
  state.controls.addEventListener("end", markCameraInteraction);
  // Cover browsers where a pointerdown is delivered before OrbitControls'
  // start event, and treat wheel zoom as camera interaction too.
  state.renderer.domElement.addEventListener("pointerdown", markCameraInteraction, {capture: true});
  state.renderer.domElement.addEventListener("wheel", markCameraInteraction, {capture: true, passive: true});
  state.root = new THREE.Group();
  state.scene.add(state.root);
  createWorldAxes();
  state.scene.add(new THREE.HemisphereLight("#d7ffff", "#142029", 2.0));
  state.scene.add(new THREE.AmbientLight("#ffffff", 0.8));
  const key = new THREE.DirectionalLight("#ffffff", 2.8); key.position.set(200, -250, 360); state.scene.add(key);
  const fill = new THREE.DirectionalLight("#7ab7ff", 1.35); fill.position.set(-260, 160, 180); state.scene.add(fill);
  const rim = new THREE.DirectionalLight("#f6bd67", 0.8); rim.position.set(0, 260, -160); state.scene.add(rim);
  wirePointerEvents();
  const resize = () => { const rect = refs.host.getBoundingClientRect(); state.camera.aspect = rect.width / Math.max(1, rect.height); state.camera.updateProjectionMatrix(); state.renderer.setSize(rect.width, rect.height, false); };
  window.addEventListener("resize", resize);
  resize();
  const animate = () => { requestAnimationFrame(animate); state.controls.update(); state.renderer.render(state.scene, state.camera); };
  animate();
}

async function buildScene() {
  const manifestUrl = new URL(MANIFEST_URL.href);
  manifestUrl.searchParams.set("preview", "electronics");
  manifestUrl.searchParams.set("v", PREVIEW_CACHE_BUSTER);
  const response = await fetch(manifestUrl.href, {cache: "no-store"});
  if (!response.ok) throw new Error(`manifest HTTP ${response.status}`);
  state.manifest = await response.json();
  refs.manifestLink.href = MANIFEST_URL.href;
  refs.manifestLink.textContent = `当前源 manifest · ${String(state.manifest.source_sha256 || "").slice(0, 12)} ↗`;
  const shellJobs = [];
  for (const sideName of ["right", "left"]) {
    for (const half of ["user", "opponent"]) {
      const file = `${sideName}-clamp-body-half-${half}.stl`;
      const bounds = entryBounds(file);
      shellJobs.push(addShellItem(file, sideName, half, bounds.min));
    }
  }
  await Promise.all(shellJobs);
  await Promise.all([addMainBoard(), addEmitterBoard()]);
  await Promise.all([addUiBoard(), addUiPhysicalItems(), addUiPanelMount(), addUiLightPipes()]);
  state.loaded = true;
  refs.placeholder.hidden = true;
  setStatus(`当前源 ${String(state.manifest.source_sha256 || "").slice(0, 12)} · 电子对象已载入`, "ready");
      refs.caption.textContent = "当前载入正式壳体、一体式外侧齐平 UI 填平固定板（含 72×42 mm 腔内固定法兰、捕获环和 8 个通孔）、包含 PCB 直装器件模型的 KiCad 板级 STL，以及来自 electronics_components.scad 的屏幕/扬声器线束实体。2 mm 蘑菇头自攻钉从腔内穿过一体件上的 Ø2.3 通孔，直接进入 C 夹实心内壁 Ø1.6 盲导孔，孔边至少保留 1.2 mm 实体边；网页检查仍不替代切片、实物装配、绝缘与受力验证。";
  updateVisibility();
  // The first STL load used to unconditionally snap the camera back to ISO.
  // Keep the fit only for a load that completed before any user orbit/pan/
  // zoom. After that point the controls own the camera until an explicit view
  // button, fit button, or reset button is pressed.
  if (!state.cameraInteracted || !state.initialViewApplied) {
    if (!state.cameraInteracted) setCameraView("iso");
    state.initialViewApplied = true;
  }
  // Render once immediately after the async STL loads.  The animation loop
  // continues afterwards, but this removes a blank first frame on browsers
  // that delay requestAnimationFrame while the tab is being restored.
  state.renderer.render(state.scene, state.camera);
}

function reportError(error) {
  console.error(error);
  refs.error.hidden = false;
  refs.error.textContent = `电子腔视图载入失败：${error?.message || error}。请确认 8000 服务仍指向当前仓库，并检查浏览器是否能访问 electronics/3d/v0.2 下的 STL。`;
  setStatus("载入失败，请检查服务或缓存", "error");
}

setupThree();
bindControls();
buildScene().catch(reportError);
