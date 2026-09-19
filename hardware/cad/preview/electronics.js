import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";

const MANIFEST_URL = new URL("../exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json", import.meta.url);
const MODEL_ROOT = new URL("../../../electronics/3d/v0.2/", MANIFEST_URL);
const COLORS = Object.freeze({
  shellUser: "#65727b",
  shellOpponent: "#8898a1",
  mainBoard: "#2f80ed",
  emitterBoard: "#c94b63",
  battery: "#e89b3a",
  uiBoard: "#48a0e8",
  faceplate: "#222f38",
  screen: "#20d6ed",
  button: "#f6bd67",
  led: "#64df85",
  speaker: "#9975d2",
  usb: "#e7ba5d",
  fastener: "#5bd0ad",
  wiring: "#437de7",
  cavity: "#f2c76b",
});

const D = Object.freeze({
  cavityXMin: 777.5,
  cavityXMax: 894.3,
  cavityYHalf: 20,
  cavityTopZ: 0.5,
  reinforcementStartX: 759.5,
  reinforcementEndX: 918.3,
  reinforcementBottomStartZ: -75,
  reinforcementBottomEndZ: -49,
  boardXMin: 792.9,
  boardXMax: 878.9,
  boardYMin: -13.5,
  boardBottomZ: -46.4912,
  batteryXMin: 803.4,
  batteryXMax: 868.4,
  batteryYMin: -15,
  batteryBottomZ: -34.2912,
  emitterBoardXMin: 802.9,
  emitterBoardXMax: 870.9,
  emitterBoardYMin: -16,
  emitterBoardBottomZ: -48.0912,
  uiBoardXMin: 806.9,
  // UI is mounted through the positive-Y side wall: the PCB plane is just
  // inside the wall and the faceplate/components project out to y+.
  uiSideBoardPlaneY: 23.2,
  uiSideZMin: -50,
  uiBoardLength: 58,
  uiBoardWidth: 28,
  uiBoardT: 1.6,
  screenLength: 28,
  screenWidth: 14,
  buttonDiameter: 10,
  ledDiameter: 4,
  speakerDiameter: 16,
  buttonCenters: [[8, 9], [8, 20]],
  ledCenters: [[29, 4], [29, 24]],
  speakerCenter: [52.2, 8],
  usbCenter: [52, 24],
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
  showCavity: true,
  showMainBoard: true,
  showEmitterBoard: true,
  showBattery: true,
  showUi: true,
  showBosses: true,
  showWiring: true,
  view: "iso",
  loaded: false,
  scene: null,
  camera: null,
  renderer: null,
  controls: null,
  root: null,
  raycaster: new THREE.Raycaster(),
  pointer: new THREE.Vector2(),
  selectedId: null,
  focus: null,
};

function setStatus(text, kind = "loading") {
  refs.status.textContent = text;
  refs.statusDot.className = `status-dot ${kind === "ready" ? "ready" : kind === "error" ? "error" : ""}`;
}

function escapeText(value) {
  return String(value || "").replace(/[&<>\"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[char]));
}

function number(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function sourceEntry(file) {
  return state.manifest?.parts?.find((entry) => entry.file === file) || null;
}

function sourceUrl(file) {
  return new URL(file, MANIFEST_URL);
}

function geometryUrl(file) {
  const base = /^(esp32-control|emitter-power|ui-panel|m6-receiver)/.test(file) ? MODEL_ROOT : MANIFEST_URL;
  const url = file.startsWith("http") ? new URL(file) : new URL(file, base);
  if (state.manifest?.source_sha256) url.searchParams.set("v", state.manifest.source_sha256.slice(0, 16));
  return url.href;
}

function floorAt(x) {
  return D.reinforcementBottomStartZ + ((x - D.reinforcementStartX) / (D.reinforcementEndX - D.reinforcementStartX)) * (D.reinforcementBottomEndZ - D.reinforcementBottomStartZ);
}

function sideVisible(side) {
  return state.side === "both" || state.side === side;
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
    detail: options.detail || "网页显示参考",
    meshes: [],
  };
  item.object.userData.previewId = id;
  item.object.userData.previewItem = item;
  state.itemById.set(id, item);
  state.items.push(item);
  state.root.add(item.object);
  return item;
}

function addMesh(item, mesh, localPosition = [0, 0, 0], options = {}) {
  mesh.position.set(...localPosition.map(number));
  if (options.rotation) mesh.rotation.set(...options.rotation.map(number));
  if (options.scale) mesh.scale.set(...options.scale.map(number));
  mesh.userData.previewId = item.id;
  item.object.add(mesh);
  item.meshes.push(mesh);
  return mesh;
}

function addBox(item, size, localPosition, color, options = {}) {
  const geometry = new THREE.BoxGeometry(...size.map(number));
  const material = createMaterial(color, options.opacity ?? 1, options);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(localPosition[0] + size[0] / 2, localPosition[1] + size[1] / 2, localPosition[2] + size[2] / 2);
  mesh.userData.previewId = item.id;
  item.object.add(mesh);
  item.meshes.push(mesh);
  return mesh;
}

function addCylinder(item, diameter, height, center, color, options = {}) {
  const geometry = new THREE.CylinderGeometry(diameter / 2, diameter / 2, height, options.segments || 32);
  const material = createMaterial(color, options.opacity ?? 1, options);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(...center.map(number));
  if (options.rotation) mesh.rotation.set(...options.rotation.map(number));
  mesh.userData.previewId = item.id;
  item.object.add(mesh);
  item.meshes.push(mesh);
  return mesh;
}

function addTube(item, a, b, diameter, color, options = {}) {
  const start = new THREE.Vector3(...a);
  const end = new THREE.Vector3(...b);
  const delta = new THREE.Vector3().subVectors(end, start);
  const length = delta.length();
  const geometry = new THREE.CylinderGeometry(diameter / 2, diameter / 2, length, 16);
  const material = createMaterial(color, options.opacity ?? 0.88, options);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.copy(start).add(end).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), delta.normalize());
  mesh.userData.previewId = item.id;
  item.object.add(mesh);
  item.meshes.push(mesh);
  return mesh;
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

function addCavityReference() {
  const width = D.cavityXMax - D.cavityXMin;
  const height = D.cavityTopZ - floorAt((D.cavityXMin + D.cavityXMax) / 2);
  const center = [(D.cavityXMin + D.cavityXMax) / 2, -D.cavityYHalf, floorAt((D.cavityXMin + D.cavityXMax) / 2) + height / 2];
  const item = makeItem("reference:cavity", "电子腔有效边界（参考）", "cavity", [0, 0, 0], [0, 0, 0], {
    role: "cavity",
    detail: "按当前 SCAD 的 116.8 × 40 mm 腔体范围绘制。底面实际为斜面，这个线框用于快速观察包络。",
    visibleWhen: () => state.showCavity && sideVisible("right"),
  });
  const geometry = new THREE.BoxGeometry(width, D.cavityYHalf * 2, height);
  const edges = new THREE.EdgesGeometry(geometry);
  const material = new THREE.LineBasicMaterial({ color: COLORS.cavity, transparent: true, opacity: 0.72 });
  const lines = new THREE.LineSegments(edges, material);
  lines.position.set(center[0], center[1], center[2]);
  lines.userData.previewId = item.id;
  item.object.add(lines);
  item.meshes.push(lines);
  return item;
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
    detail: "真实 KiCad 板级模型；板框 86 × 32 mm，包含板上器件的 3D 包络。",
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

function addBattery(sideName) {
  const mirrored = sideName === "left";
  const item = makeItem(`battery:${sideName}`, `${sideName === "right" ? "右侧主控" : "左侧发射"} 电池包（安装包络）`, "battery", mirrored ? [-D.batteryXMax, D.batteryYMin, D.batteryBottomZ] : [D.batteryXMin, D.batteryYMin, D.batteryBottomZ], [0, 0, -22], {
    side: mirrored ? -1 : 1,
    role: "battery",
    detail: "65 × 30 × 7 mm 受保护电池包占位；位置来自当前 SCAD 的二层托位，实际电池型号/绝缘/固定方式仍需首样复核。",
    visibleWhen: () => sideVisible(sideName) && state.showBattery,
  });
  const mesh = addBox(item, [D.batteryXMax - D.batteryXMin, 30, 7], [0, 0, 0], COLORS.battery, { opacity: 0.78, roughness: 0.44, metalness: 0.08 });
  return item;
}

async function addUiStack() {
  const item = await addStlItem({
    id: "electronics:ui-stack:right",
    name: "UI 交互板与 y+ 侧面板（真实板 + 安装包络）",
    category: "ui",
    file: "ui-panel-v0.2.stl",
    basePosition: [D.uiBoardXMin, D.uiSideBoardPlaneY, D.uiSideZMin + D.uiBoardWidth],
    color: COLORS.uiBoard,
    side: 1,
    role: "ui",
    explosion: [0, 34, 0],
    detail: "UI 板使用 KiCad STL；面框、屏幕、按钮、LED、扬声器和 USB-C 全部布置在 y+ 侧壁，代理件之间按 0.8 mm 最小间隙排布，取消底部 UI 盖板。侧面面框当前是检修/安装包络，螺钉与密封尺寸冻结后再进入正式打印清单。",
    visibleWhen: () => sideVisible("right") && state.showUi,
  });
  // Rotate the KiCad board so its 58 x 28 face becomes an x/z panel on the
  // positive-Y wall. The normalized STL is top-anchored in z; board/component
  // material ends at the side opening and the service face projects to y+.
  item.object.rotation.x = -Math.PI / 2;
  addBox(item, [64, 34, 4], [-3, -3, 6.2], COLORS.faceplate, { opacity: 0.36, side: THREE.DoubleSide });
  addBox(item, [D.screenLength, D.screenWidth, 1.1], [15, 7, 6.5], COLORS.screen, { opacity: 0.94, roughness: 0.3, metalness: 0.12 });
  const outwardCylinder = [-Math.PI / 2, 0, 0];
  for (const [x, y] of D.buttonCenters) addCylinder(item, D.buttonDiameter, 4.2, [x, y, 6.5], COLORS.button, { opacity: 0.96, roughness: 0.3, rotation: outwardCylinder });
  for (const [x, y] of D.ledCenters) addCylinder(item, D.ledDiameter, 3.0, [x, y, 6.5], COLORS.led, { opacity: 0.92, roughness: 0.25, rotation: outwardCylinder });
  addCylinder(item, D.speakerDiameter, 2.8, [D.speakerCenter[0], D.speakerCenter[1], 6.5], COLORS.speaker, { opacity: 0.88, roughness: 0.5, rotation: outwardCylinder });
  addBox(item, [8, 6, 2.8], [D.usbCenter[0] - 4, D.usbCenter[1] - 3, 6.5], COLORS.usb, { opacity: 0.92, roughness: 0.34, metalness: 0.18 });
  return item;
}

function addBosses(sideName) {
  const mirrored = sideName === "left";
  const sign = mirrored ? -1 : 1;
  const item = makeItem(`reference:mounting:${sideName}`, `${sideName === "right" ? "右侧主控" : "左侧发射"} 支柱与电池止挡`, "fastener", [0, 0, 0], [0, 0, 0], {
    side: sign,
    role: "bosses",
    detail: "显示当前结构中的 PCB 支柱、发射板边缘夹块和电池端部止挡；它们是几何参考，不是额外外凸加强柱。",
    visibleWhen: () => sideVisible(sideName) && state.showBosses,
  });
  const boardHoles = [[806.4, -9.5], [837.9, -9.5], [867.9, 15], [867.9, -9.5]];
  for (const [x, y] of boardHoles) {
    const px = mirrored ? -x : x;
    const floor = floorAt(x) + 0.8;
    addCylinder(item, 6, D.boardBottomZ - floor, [px, y, floor + (D.boardBottomZ - floor) / 2], COLORS.fastener, { opacity: 0.76, segments: 24 });
  }
  const stops = [803.4, 863.4];
  for (const x of stops) {
    const px = mirrored ? -(x + 5) : x;
    for (const y of [-16.5, 14.5]) addBox(item, [5, 2, 8], [px, y, D.batteryBottomZ], COLORS.fastener, { opacity: 0.78 });
  }
  return item;
}

function addWiring(sideName) {
  const mirrored = sideName === "left";
  const sign = mirrored ? -1 : 1;
  const item = makeItem(`reference:wiring:${sideName}`, `${sideName === "right" ? "右侧主控" : "左侧发射"} 短距离走线参考`, "wiring", [0, 0, 0], [0, 0, 7], {
    side: sign,
    role: "wiring",
    detail: "蓝色软管是从板边到腔体外侧的短距离路线参考，金色块表示连接器/扎带位置，不是最终线束模型。",
    visibleWhen: () => sideVisible(sideName) && state.showWiring,
  });
  const boardEdge = mirrored ? -873.9 : 873.9;
  const route = mirrored ? -899.3 : 899.3;
  addTube(item, [boardEdge, 10, D.boardBottomZ + 2.8], [route, 10, D.boardBottomZ + 2.8], 2.6, COLORS.wiring, { opacity: 0.9 });
  addTube(item, [route, 10, D.boardBottomZ + 2.8], [route, 10, -18], 2.6, COLORS.wiring, { opacity: 0.9 });
  addBox(item, [8, 6, 4], [mirrored ? route - 4 - 8 : route - 4, 7, D.boardBottomZ + 0.8], COLORS.usb, { opacity: 0.92, roughness: 0.34 });
  return item;
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
  const sideText = state.side === "right" ? "右侧主控电子腔" : state.side === "left" ? "左侧发射电子腔" : "双侧电子腔对照";
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
    const match = role === "cavity" ? ["shell", "cavity", "bosses", "battery", "main-board", "emitter-board", "ui"].includes(item.role)
      : role === "board" ? ["main-board", "emitter-board"].includes(item.role)
        : role === "ui" ? item.role === "ui"
          : role === "battery" ? item.role === "battery"
            : true;
    if (!match) continue;
    item.object.updateMatrixWorld(true);
    item.object.traverse((child) => {
      if (child.isMesh || child.isLineSegments) { box.expandByObject(child); hasMesh = true; }
    });
  }
  return hasMesh && !box.isEmpty() ? box : visibleBounds();
}

function setCameraView(view = state.view, focus = state.focus) {
  state.view = view;
  const box = focusBounds(focus);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const radius = Math.max(size.length() * 0.56, 60);
  const directions = {
    iso: new THREE.Vector3(1.18, -1.35, 0.92),
    split: new THREE.Vector3(0, -1.75, 0.04),
    side: new THREE.Vector3(0, 1.75, 0.12),
    top: new THREE.Vector3(0.08, -0.2, 1.8),
    bottom: new THREE.Vector3(-0.08, 0.2, -1.8),
  };
  const direction = (directions[view] || directions.iso).clone().normalize();
  state.camera.position.copy(center).addScaledVector(direction, radius * 1.62);
  state.camera.near = Math.max(0.1, radius / 1000);
  state.camera.far = Math.max(3000, radius * 10);
  state.camera.updateProjectionMatrix();
  state.controls.target.copy(center);
  state.controls.update();
  document.querySelectorAll("[data-view]").forEach((button) => button.classList.toggle("active", button.dataset.view === view));
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
    updateVisibility();
    setCameraView(state.view, state.focus);
  }));
  document.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => { state.focus = null; setCameraView(button.dataset.view); }));
  document.querySelectorAll("[data-focus]").forEach((button) => button.addEventListener("click", () => { state.focus = button.dataset.focus; setCameraView(state.view, state.focus); }));
  refs.explode.addEventListener("input", () => { state.explode = number(refs.explode.value) / 100; refs.explodeOutput.textContent = String(Math.round(state.explode * 100)); updateVisibility(); });
  refs.shellOpacity.addEventListener("input", () => { state.shellOpacity = number(refs.shellOpacity.value) / 100; refs.shellOpacityOutput.textContent = String(Math.round(state.shellOpacity * 100)); updateVisibility(); });
  const checks = {
    "show-user-shell": "showUserShell", "show-opponent-shell": "showOpponentShell", "show-cavity": "showCavity",
    "show-main-board": "showMainBoard", "show-emitter-board": "showEmitterBoard", "show-battery": "showBattery",
    "show-ui": "showUi", "show-bosses": "showBosses", "show-wiring": "showWiring",
  };
  Object.entries(checks).forEach(([id, key]) => document.querySelector(`#${id}`).addEventListener("change", (event) => { state[key] = event.target.checked; updateVisibility(); }));
  refs.host.addEventListener("dblclick", () => { state.focus = null; setCameraView(state.view); });
  document.querySelector("#fit-button").addEventListener("click", () => setCameraView(state.view, state.focus));
  document.querySelector("#reset-button").addEventListener("click", () => { state.explode = 0; refs.explode.value = "0"; refs.explodeOutput.textContent = "0"; state.focus = null; updateVisibility(); setCameraView("iso"); });
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
  state.root = new THREE.Group();
  state.scene.add(state.root);
  state.scene.add(new THREE.HemisphereLight("#d7ffff", "#142029", 2.0));
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
  const response = await fetch(`${MANIFEST_URL.href}?preview=electronics`);
  if (!response.ok) throw new Error(`manifest HTTP ${response.status}`);
  state.manifest = await response.json();
  refs.manifestLink.href = MANIFEST_URL.href;
  refs.manifestLink.textContent = `当前源 manifest · ${String(state.manifest.source_sha256 || "").slice(0, 12)} ↗`;
  addCavityReference();
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
  addBattery("right");
  addBattery("left");
  await addUiStack();
  addBosses("right");
  addBosses("left");
  addWiring("right");
  addWiring("left");
  state.loaded = true;
  refs.placeholder.hidden = true;
  setStatus(`当前源 ${String(state.manifest.source_sha256 || "").slice(0, 12)} · 电子对象已载入`, "ready");
  refs.caption.textContent = "当前正式壳体 STL + 当前 KiCad 板级 STL 已载入；颜色件是安装包络参考。网页检查通过后仍需切片、实物装配、绝缘与受力验证。";
  updateVisibility();
  setCameraView("iso");
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
