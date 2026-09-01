const $ = (selector) => document.querySelector(selector);

const refs = {
  loadStatus: $("#load-status"),
  sourceManifestLink: $("#source-manifest-link"),
  errorBanner: $("#error-banner"),
  modeTabs: $("#mode-tabs"),
  assemblyControlCard: $("#assembly-control-card"),
  explodeRange: $("#explode-range"),
  explodeOutput: $("#explode-output"),
  assembledButton: $("#assembled-button"),
  explodedButton: $("#exploded-button"),
  assemblyStep: $("#assembly-step"),
  assemblyStepOutput: $("#assembly-step-output"),
  showTable: $("#show-table"),
  showNonPrinted: $("#show-nonprinted"),
  showSkpCandidate: $("#show-skp-candidate"),
  showSkpFit: $("#show-skp-fit"),
  bedPreset: $("#bed-preset"),
  bedWidth: $("#bed-width"),
  bedDepth: $("#bed-depth"),
  bedHeight: $("#bed-height"),
  edgeMargin: $("#edge-margin"),
  partGap: $("#part-gap"),
  gapOutput: $("#gap-output"),
  repackButton: $("#repack-button"),
  resetButton: $("#reset-button"),
  showLabels: $("#show-labels"),
  showSafeArea: $("#show-safe-area"),
  fitModel: $("#fit-model"),
  downloadLayout: $("#download-layout"),
  plateCount: $("#plate-count"),
  placedCount: $("#placed-count"),
  oversizedCount: $("#oversized-count"),
  plateTabs: $("#plate-tabs"),
  layoutTitle: $("#layout-title"),
  layoutBadge: $("#layout-badge"),
  bedCanvas: $("#bed-canvas"),
  canvasHoverLabel: $("#canvas-hover-label"),
  legend: $("#legend"),
  modelTitle: $("#model-title"),
  modelHost: $("#model-host"),
  modelPlaceholder: $("#model-placeholder"),
  modelKicker: $("#model-kicker"),
  modelCaption: $("#model-caption"),
  modelCard: $(".model-card"),
  layoutCard: $(".layout-card"),
  visualGrid: $(".visual-grid"),
  assemblyToolbar: $("#assembly-toolbar"),
  assemblyStatusBadge: $("#assembly-status-badge"),
  assemblySelectionBadge: $("#assembly-selection-badge"),
  fitM6: $("#fit-m6"),
  fitSkp: $("#fit-skp"),
  assemblyHoverLabel: $("#assembly-hover-label"),
  assemblyGuideCard: $("#assembly-guide-card"),
  assemblyStepList: $("#assembly-step-list"),
  assemblySelectionPanel: $("#assembly-selection-panel"),
  clearAssemblySelection: $("#clear-assembly-selection"),
  detailGrid: $(".detail-grid"),
  componentCard: $("#component-card"),
  partsCardTitle: $("#parts-card-title"),
  showPlateModel: $("#show-plate-model"),
  showPartModel: $("#show-part-model"),
  downloadPlate: $("#download-plate"),
  partFilter: $("#part-filter"),
  partList: $("#part-list"),
  oversizedBadge: $("#oversized-badge"),
  oversizedList: $("#oversized-list"),
  componentList: $("#component-list"),
  oversizeNoteTitle: $("#oversize-note-title"),
  oversizeNoteText: $("#oversize-note-text"),
};

const PRESETS = {
  "256": { width_mm: 256, depth_mm: 256, height_mm: 256, edge_margin_mm: 5 },
  "300": { width_mm: 300, depth_mm: 300, height_mm: 300, edge_margin_mm: 5 },
  "400": { width_mm: 400, depth_mm: 400, height_mm: 400, edge_margin_mm: 5 },
};

const COLORS = {
  stand: { label: "立柱 / 夹持", color: "#f6bd67" },
  net: { label: "网布 / 卡网夹", color: "#e9eef0" },
  rail: { label: "历史网顶轨道（不在当前装配）", color: "#b28cff" },
  optical: { label: "M6 十路光电阵列", color: "#74a7ff" },
  sensor: { label: "PVDF 传感", color: "#62e4d1" },
  calibration: { label: "标定 / 参考", color: "#fb817c" },
  other: { label: "其他", color: "#a9bbc0" },
};

const ASSEMBLY_STEPS = [
  { number: 1, label: "桌下夹紧与立柱", description: "两侧传统 C 形夹、保护垫、加长 M8 螺杆和旋钮固定在球台边缘；上下结构舌头同步向台内延长 20 mm，台下有效伸入为 82 mm，M8 压紧件位于下舌头中点；台底压紧盘放大为 Ø50。保留桌面夹持开口、压块和螺杆工作区，桌边外侧非接触区沿 y 全深做成实心桥体；上下结构夹臂均为 14 mm，靠球台侧下部支撑厚 40 mm，向外侧以 14 mm 下夹臂收口并形成斜底；底部手拧旋钮采用外径 36 mm、18 齿圆角锯齿握持圈，接触软垫仍独立可替换。" },
  { number: 2, label: "固定灰色主体 / 立柱共面落座", description: "完整固定灰色 C 形主体包含梯形电子腔、外侧 C 壁和立柱最高水平承托面；固定网柱从黄灰交界 z=16 mm 共面起步，网布/卡夹工作高度仍到 z=168.5 mm，实体继续到按球头底座自动计算的顶端 z=260.5 mm，底端不插入 C 形座。网柱下端 35×58 mm，从承托面起经 30 mm 实心锥形过渡收至 28×38 mm，之后保持恒定到顶端；没有台阶、外套圈、后置延长块、两只脚、裤裆或独立滑靴。图示的 0.1 mm 只用于预览分色，不是实体间隙。" },
  { number: 3, label: "网布/U 夹装入整根立柱", description: "立柱本体没有上下分段接缝，网顶也不设置轨道：真实网布先从球台中心侧穿过每根整根立柱的 3 mm y 向过道，网布端部止在连续立柱本体外侧面；随后把全高 U 形卡夹从连续立柱本体的外侧开口沿 x+ 向 x− 滑入，两片 jaw 夹住 1.2 mm 网布。网布张力和绳的拉力把卡夹压在承托面上；立柱内嵌的一处被动止挡只负责防止卡夹向外拔出，正侧 jaw 的一体弹性扣舌负责让止挡越过并在回拉时闭合肩拦住。解锁时按开对应 jaw 再反向滑出；没有穿钉、横向销钉或网夹螺钉。这里是外侧开口的 U 夹滑入路径，不是圆柱件轴向硬插。" },
  { number: 4, label: "M6 45° L 型主体、x 向分体壳与竖直球头", description: "先把左右各十个 M6 直角发射/接收器的中空 M6 外丝轴朝向球台中心：右侧螺纹末端中心孔朝 x-、左侧镜像后朝 x+；器件从各自 x 外侧插入 10×56×216 mm 加宽加厚 PETG 长方条主体，灰色六角留在外侧浅六角窝内，朝台内平滑面带一枚原配螺帽，蓝色尾线局部沿 z-，整件绕光束 x 轴转 -45° 后向 y-/z- 斜向离开；通道中心按 20 mm 节距排列，x- 光学前盖为正球弧、x+ 线缆后盖在接驳边保留直角、仅后端两个角圆滑，两盖共享 y± 边槽并配底盖；后盖 boss 根部由 y± 两条实体桥接肋连接到后壳侧壁，中央 Ø7 通孔保持无遮挡；竖直采购 13 mm 球头按实物包络显示，下端 M8 外牙沿 z- 进入浅黄色固定网柱顶面中心的攻丝底孔，后盖 boss 与球头水平安装轴心共线；取消旧版横向承托臂和旧版独立连接器。" },
  { number: 5, label: "机械参考线与最终检查", description: "历史参考线仍用 +10…+100 mm；当前 M6 阵列原始通道用 +10…+190 mm、安装后按壳体底部越过网顶 2 mm 自动抬高 29 mm，为 +39…+219 mm，按 20 mm 节距核对两侧阵列平行度与微调锁紧；最后检查黄灰交界 z=16 mm、固定网柱底端与承托面共面、网布/卡夹顶端 z=168.5 mm、球头底座与立柱顶端 z=260.5 mm 共面、接触面以上 30 mm 实心锥形渐变到 z=46 mm 后保持 28×38 mm、网布 3 mm 过道和 U 形卡网夹开口畅通、两侧 PVDF 传感器和所有盖板严丝合缝；器件输出参数仍以实测证据为准。" },
];

const ASSEMBLY_GROUPS = {
  clamp: { label: "台下夹紧", color: "#f6bd67", stage: 1 },
  clamp_fixed: { label: "固定夹体 / 立柱基台", color: "#687985", stage: 1 },
  post: { label: "左右立柱", color: "#f28b50", stage: 2 },
  net: { label: "网布 / 卡网夹", color: "#e9eef0", stage: 3 },
  rail: { label: "历史网顶轨道（不在当前装配）", color: "#b28cff", stage: 5 },
  optical: { label: "M6 十路光电阵列", color: "#74a7ff", stage: 4 },
  sensor: { label: "PVDF 擦网", color: "#62e4d1", stage: 4 },
  reference: { label: "标定参考", color: "#fb817c", stage: 5 },
  hardware: { label: "标准件 / 占位", color: "#d99bff", stage: 5 },
  skp_candidate: { label: "SKP 腿脚候选", color: "#43d34d", stage: 2 },
  context: { label: "球台背景", color: "#75858b", stage: 0 },
};

const ASSEMBLY_DEFAULT_EXPLODE = 0.72;

const state = {
  manifest: null,
  sourceManifest: null,
  manifestUrl: null,
  sourceManifestUrl: null,
  generatedLayout: null,
  layout: null,
  generated: true,
  uiMode: "assembly",
  activePlateIndex: 0,
  selectedFile: null,
  hoveredFile: null,
  modelMode: "plate",
  canvasTransform: null,
  assembly: {
    explode: 0,
    step: ASSEMBLY_STEPS.length,
    selectedId: null,
    hoveredId: null,
    focusM6: false,
    focusSkpCandidate: false,
    showTable: true,
    showNonPrinted: true,
    showSkpCandidate: true,
    showSkpFit: true,
    items: [],
    loaded: false,
    loadError: null,
  },
  three: {
    ready: false,
    THREE: null,
    STLLoader: null,
    OrbitControls: null,
    renderer: null,
    scene: null,
    camera: null,
    controls: null,
    modelRoot: null,
    grid: null,
    globalAxes: null,
    m6AxesHelper: null,
    loadId: 0,
    raycaster: null,
    pointer: null,
  },
};

function setStatus(message, tone = "idle") {
  refs.loadStatus.textContent = message;
  const dot = document.querySelector(".status-dot");
  if (!dot) return;
  const colors = { ok: "#62e4d1", idle: "#f6bd67", error: "#fb817c" };
  dot.style.background = colors[tone] || colors.idle;
  dot.style.boxShadow = `0 0 0 4px ${tone === "error" ? "rgba(251,129,124,.1)" : "rgba(98,228,209,.1)"}`;
}

function showError(message) {
  refs.errorBanner.textContent = message;
  refs.errorBanner.hidden = false;
  setStatus("打印清单读取失败", "error");
}

function clearError() {
  refs.errorBanner.textContent = "";
  refs.errorBanner.hidden = true;
}

function number(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function formatNumber(value) {
  const rounded = Math.round(number(value) * 10) / 10;
  return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
}

function formatSize(size) {
  if (!Array.isArray(size)) return "尺寸未知";
  return `${size.slice(0, 3).map(formatNumber).join(" × ")} mm`;
}

function partName(entry) {
  return String(entry?.name_zh || entry?.label || entry?.file || "未命名零件").replace(/\.stl$/i, "");
}

function categoryKey(entry) {
  const text = `${entry?.part || ""} ${entry?.file || ""} ${entry?.name_zh || ""}`.toLowerCase();
  if (text.includes("m6") || text.includes("十路") || text.includes("stg120") || text.includes("stg-120") || text.includes("光纤")
      || text.includes("optical") || text.includes("module") || text.includes("光学")) return "optical";
  if (text.includes("sensor") || text.includes("pvdf") || text.includes("film")) return "sensor";
  if (text.includes("net") && !text.includes("net-rail")) return "net";
  if (text.includes("rail") || text.includes("net-rail")) return "rail";
  if (text.includes("gauge") || text.includes("reference") || text.includes("pin")) return "calibration";
  if (text.includes("stand") || text.includes("post") || text.includes("clamp") || text.includes("knob")) return "stand";
  return "other";
}

function category(entry) {
  return COLORS[categoryKey(entry)] || COLORS.other;
}

function materialGroup(entry) {
  const explicit = String(entry?.material_group || "").trim();
  if (explicit) return explicit;
  const material = String(entry?.material || "");
  return material.toUpperCase().includes("TPU") || material.includes("硅胶") ? "TPU/柔性" : "PETG";
}

function materialClass(group) {
  return String(group).toUpperCase().includes("TPU") ? "material-tpu" : "material-petg";
}

function sourceSize(entry) {
  if (Array.isArray(entry?.source_size_mm)) return entry.source_size_mm.map(number);
  const declaredBounds = boundsFromEntry(entry);
  if (declaredBounds) return declaredBounds.size;
  if (Array.isArray(entry?.source_bounds) && entry.source_bounds.length === 2) {
    return entry.source_bounds[1].map(number).map((value, index) => value - number(entry.source_bounds[0][index]));
  }
  if (Array.isArray(entry?.placed_bounds) && entry.placed_bounds.length === 2) {
    return entry.placed_bounds[1].map(number).map((value, index) => value - number(entry.placed_bounds[0][index]));
  }
  return [0, 0, 0];
}

function boundsSize(entry) {
  if (!Array.isArray(entry?.placed_bounds) || entry.placed_bounds.length !== 2) return sourceSize(entry);
  return entry.placed_bounds[1].map(number).map((value, index) => value - number(entry.placed_bounds[0][index]));
}

function sourcePathFor(entry) {
  const relative = entry?.source_path || `../${entry?.file || ""}`;
  return new URL(relative, state.manifestUrl).href;
}

function partSearchText(entry) {
  return [entry?.name_zh, entry?.name_en, entry?.part, entry?.file, entry?.side, entry?.material, materialGroup(entry)]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function assetPath(relative) {
  return new URL(relative, state.manifestUrl).href;
}

function boundsFromEntry(entry) {
  const bounds = entry?.bounds || entry?.source_bounds || entry?.placed_bounds;
  if (bounds && !Array.isArray(bounds) && Array.isArray(bounds.min) && Array.isArray(bounds.max)) {
    const min = bounds.min.map(number);
    const max = bounds.max.map(number);
    const size = Array.isArray(bounds.size)
      ? bounds.size.map(number)
      : max.map((value, index) => value - min[index]);
    return { min, max, size };
  }
  if (!Array.isArray(bounds) || bounds.length !== 2) return null;
  const min = bounds[0].map(number);
  const max = bounds[1].map(number);
  return { min, max, size: max.map((value, index) => value - min[index]) };
}

function sideSign(entry) {
  if (entry?.side === "left" || number(entry?.side_value) < 0) return -1;
  if (entry?.side === "right" || number(entry?.side_value) > 0) return 1;
  return 0;
}

function assemblyGroupKey(entry) {
  const part = String(entry?.part || entry?.file || entry?.id || "").toLowerCase();
  if (part.includes("net_clamp") || part.includes("net-clamp") || part.includes("net-fabric")) return "net";
  if (part.includes("post_clamp_carrier") || part.includes("post")) return "post";
  if (part.includes("clamp_body_segment")) return "clamp_fixed";
  if (part.includes("clamp") || part.includes("knob") || part.includes("lower_stand")) return "clamp";
  if (part.includes("net_rail")) return "rail";
  if (part.includes("m6") || part.includes("stg120") || part.includes("stg-120") || part.includes("optical")) return "optical";
  if (part.includes("sensor") || part.includes("pvdf")) return "sensor";
  if (part.includes("reference") || part.includes("calibration") || part.includes("pin")) return "reference";
  return "hardware";
}

function assemblyStage(entry) {
  return ASSEMBLY_GROUPS[assemblyGroupKey(entry)]?.stage || 5;
}

function explosionVector(group, side = 0) {
  const outward = side || 1;
  switch (group) {
    case "clamp": return [outward * 118, 0, -74];
    // The inboard shell owns the fixed seating shelf. Keep this datum fixed
    // while covers, pads and knobs are exploded as service items; only the
    // one-piece post carrier travels along the real x slide direction.
    case "clamp_fixed": return [0, 0, 0];
    // The post/carrier is a true x-direction slide-in.  Do not lift it in z
    // during the exploded view: at explode=0 its bottom must remain seated on
    // the clamp-base datum, and the only separation shown is the real slide
    // direction.
    case "post": return [outward * 74, 0, 0];
    case "net": return [0, 0, 82];
    case "rail": return [0, 0, 82];
    case "optical": return [side ? outward * 162 : 0, 0, 28];
    case "sensor": return [0, -126, 48];
    case "reference": return [outward * 142, -78, 48];
    case "hardware": return [outward * 128, -32, -70];
    // Keep the SKP candidate visually separate from the post in the exploded
    // view. Its real installed position remains directly under the post when
    // amount=0; the larger x offset is only a review aid.
    case "skp_candidate": return [outward * 154, 0, -12];
    default: return [0, 0, 0];
  }
}

function sourcePrintableEntries() {
  const entries = state.sourceManifest?.parts || state.manifest?.parts || [];
  // Filter retired split-post/seam parts so an old cached manifest cannot
  // resurrect them before the regenerated one-piece print package is loaded.
  const removedActiveParts = new Set([
    "post_segment",
    "lower_stand_segment",
    "upper_stand_segment",
    "post_joint_sleeve",
    "post_joint_key",
    "net_rail_segment",
    "net_rail_splice",
    "net_rail_saddle",
    "net_clamp_rod",
    "m6_detector_net_connector",
  ]);
  return entries.filter((entry) => entry && entry.file && entry.printable !== false
    && !removedActiveParts.has(entry.part));
}

// The source M6 STL files are exported in the reusable/raw coordinate frame.
// The SCAD assembly applies one rigid x/z translation to the complete optical
// package. Keep that datum here as a value derived from the actual manifest so
// the browser cannot silently fall back to the old hand-written 901/84.6
// placement when the post or rear-cover dimensions change.
const M6_PREVIEW_MIN_RAISE_Z = 20;
const M6_PREVIEW_NET_TOP_Z = 168.5;
const M6_PREVIEW_SHELL_CLEARANCE_Z = 2;
const M6_PREVIEW_BALLHEAD_STUD_LENGTH_X = 16;
const M6_PREVIEW_BALLHEAD_STUD_ENGAGEMENT_X = 12;
const M6_PREVIEW_BALLHEAD_GAP_X = 2;
const M6_PREVIEW_BALLHEAD_HOUSING_D = 28;
const M6_PREVIEW_BALLHEAD_HOUSING_LENGTH_Z = 26;
const M6_PREVIEW_BALLHEAD_BASE_T = 8;
const M6_PREVIEW_BALLHEAD_NET_STUD_LENGTH_Z = 28;

function deriveAssemblyDatums(entries) {
  const rightPost = entries.find((entry) => entry.part === "post_clamp_carrier"
    && sideSign(entry) > 0)
    || entries.find((entry) => entry.part === "post_clamp_carrier");
  const rightRear = entries.find((entry) => entry.part === "m6_detector_shell_rear"
    && sideSign(entry) > 0)
    || entries.find((entry) => entry.part === "m6_detector_shell_rear");
  const rightBody = entries.find((entry) => entry.part === "m6_detector_body"
    && sideSign(entry) > 0)
    || entries.find((entry) => entry.part === "m6_detector_body");
  const postBounds = boundsFromEntry(rightPost);
  const rearBounds = boundsFromEntry(rightRear);
  const bodyBounds = boundsFromEntry(rightBody);

  // These fallbacks match the current SCAD design only for an old/corrupt
  // manifest. Normal preview loads always take the values from the source
  // manifest above.
  const postCenterX = postBounds
    ? (postBounds.min[0] + postBounds.max[0]) / 2
    : 901;
  const postTopZ = postBounds?.max?.[2] ?? 260.5;
  const rearMaxX = rearBounds?.max?.[0] ?? 796.4;
  const rawBallheadCenterX = rearMaxX
    + (M6_PREVIEW_BALLHEAD_STUD_LENGTH_X - M6_PREVIEW_BALLHEAD_STUD_ENGAGEMENT_X)
    + M6_PREVIEW_BALLHEAD_GAP_X
    + M6_PREVIEW_BALLHEAD_HOUSING_D / 2;
  const rawBallheadCenterZ = rearBounds
    ? (rearBounds.min[2] + rearBounds.max[2]) / 2
    : 252.5;
  const rawBallheadBaseCenterZ = rawBallheadCenterZ
    - M6_PREVIEW_BALLHEAD_HOUSING_LENGTH_Z / 2
    - M6_PREVIEW_BALLHEAD_BASE_T / 2;
  const rawBallheadBaseBottomZ = rawBallheadBaseCenterZ
    - M6_PREVIEW_BALLHEAD_BASE_T / 2;
  const rawShellBottomZ = rearBounds?.min?.[2] ?? 141.5;
  const m6RaiseZ = Math.max(
    M6_PREVIEW_MIN_RAISE_Z,
    M6_PREVIEW_NET_TOP_Z + M6_PREVIEW_SHELL_CLEARANCE_Z - rawShellBottomZ,
  );
  const installedBallheadBaseBottomZ = rawBallheadBaseBottomZ + m6RaiseZ;
  const postTopErrorZ = postTopZ - installedBallheadBaseBottomZ;
  const rawBodyCenterX = bodyBounds
    ? (bodyBounds.min[0] + bodyBounds.max[0]) / 2
    : 766.25;
  const rawBodyCenterZ = bodyBounds
    ? (bodyBounds.min[2] + bodyBounds.max[2]) / 2
    : 252.5;

  return {
    postCenterX,
    postTopZ,
    rawRearMaxX: rearMaxX,
    rawBallheadCenterX,
    rawBallheadCenterZ,
    rawBallheadBaseCenterZ,
    rawBallheadBaseBottomZ,
    rawBodyCenterX,
    rawBodyCenterZ,
    m6OffsetX: postCenterX - rawBallheadCenterX,
    m6RaiseZ,
    installedBallheadCenterX: postCenterX,
    installedBallheadCenterZ: rawBallheadCenterZ + m6RaiseZ,
    installedBallheadBaseCenterZ: rawBallheadBaseCenterZ + m6RaiseZ,
    installedBallheadBaseBottomZ,
    postTopErrorZ,
    installedBodyCenterX: rawBodyCenterX
      + (postCenterX - rawBallheadCenterX),
    installedBodyCenterZ: rawBodyCenterZ + m6RaiseZ,
  };
}

function assemblySourcePath(entry) {
  const base = state.sourceManifestUrl || state.manifestUrl;
  return new URL(entry.file, base).href;
}

function makeAssemblyItem(options) {
  const min = options.base_min.map(number);
  const size = options.size.map(number);
  return {
    id: options.id,
    name_zh: options.name_zh,
    name_en: options.name_en || options.name_zh,
    kind: options.kind || "装配件",
    material: options.material || "装配占位",
    material_group: options.material_group || "装配占位",
    notes: options.notes || "",
    group: options.group || "hardware",
    stage: options.stage ?? (ASSEMBLY_GROUPS[options.group] || ASSEMBLY_GROUPS.hardware).stage,
    color: options.color || (ASSEMBLY_GROUPS[options.group] || ASSEMBLY_GROUPS.hardware).color,
    nonPrinted: options.nonPrinted !== false,
    context: Boolean(options.context),
    shape: options.shape || "box",
    shapeOptions: options.shapeOptions || {},
    baseMin: min,
    baseSize: size,
    baseMax: min.map((value, index) => value + size[index]),
    explosion: options.explosion || explosionVector(options.group || "hardware", options.side || 0),
    sourceEntry: options.sourceEntry || null,
    sourcePath: options.sourcePath || null,
    stlTransform: options.stlTransform || null,
    candidate: Boolean(options.candidate),
    fitCandidate: Boolean(options.fitCandidate),
    side: options.side || 0,
    object: null,
  };
}

function makePrintableAssemblyItem(entry, assemblyDatums) {
  const bounds = boundsFromEntry(entry);
  if (!bounds) return null;
  const group = assemblyGroupKey(entry);
  let baseMin = bounds.min;
  let stlTransform = null;
  if (entry.part === "net_clamp_clip") {
    // The printable STL is deliberately laid flat: SCAD rotates the installed
    // x/y/z clip datum onto x/y/z print axes. Restore that transform only in
    // the assembly viewer so the source STL remains print-friendly.
    const side = sideSign(entry);
    baseMin = side > 0
      ? [893.2, -3.3, 168.5]
      : [-919.3, -3.3, 168.5];
    stlTransform = { rotation: [-Math.PI / 2, 0, 0] };
  }
  if (String(entry.part || "").startsWith("m6_detector_")) {
    // M6 parts are exported in the raw positive/negative coordinate frame,
    // while all non-printable optical proxies below use installed coordinates.
    // Apply the same rigid transform to every printable M6 STL, including the
    // rear cover and bottom cable exit, so the rear-cover boss shares the
    // purchased ballhead's installation axis instead of floating at x=raw.
    const side = sideSign(entry);
    baseMin = [
      bounds.min[0] + side * assemblyDatums.m6OffsetX,
      bounds.min[1],
      bounds.min[2] + assemblyDatums.m6RaiseZ,
    ];
  }
  return makeAssemblyItem({
    id: `stl:${entry.file}`,
    name_zh: partName(entry),
    name_en: entry.name_en || entry.part,
    kind: entry.component_kind || "打印件",
    material: entry.material || materialGroup(entry),
    material_group: entry.material_group || materialGroup(entry),
    notes: entry.notes || entry.orientation || "",
    group,
    stage: assemblyStage(entry),
    nonPrinted: false,
    shape: "stl",
    sourceEntry: entry,
    sourcePath: assemblySourcePath(entry),
    base_min: baseMin,
    size: bounds.size,
    side: sideSign(entry),
    stlTransform,
    explosion: explosionVector(group, sideSign(entry)),
  });
}

function firstEntry(entries, predicate) {
  return entries.find(predicate) || null;
}

function makeProxyAssemblyItems(entries, assemblyDatums) {
  const items = [];
  // The printable M6 body/covers are already loaded from the current source
  // manifest.  Keep only the purchased optical hardware as browser proxies;
  // otherwise the same blue body/shell is shown once from STL and once again
  // as a proxy, which looks like extra vertical parts in the assembly.
  const sourceM6Parts = new Set(
    entries
      .filter((entry) => String(entry?.part || "").startsWith("m6_detector_"))
      .map((entry) => entry.part),
  );
  const hasSourceM6Part = (part) => sourceM6Parts.has(part);
  const stgHead = {
    length: 130,
    activeLength: 120,
    width: 19,
    thickness: 6,
    bottomZ: 147.5,
    pitch: 3.87,
    count: 32,
  };
  // The active net has no top rail. These are the direct cloth datum values;
  // legacy rail entries are filtered before this proxy is built.
  const netMinX = -915;
  const netMaxX = 915;
  const netBottomZ = 16;
  const netTopZ = 168.5;
  const netSpan = netMaxX - netMinX;

  items.push(makeAssemblyItem({
    id: "context:table",
    name_zh: "球台台面（背景）",
    name_en: "tabletop context",
    kind: "背景包络",
    material: "显示占位",
    group: "context",
    context: true,
    nonPrinted: false,
    shape: "box",
    base_min: [-762.5, -250, -25],
    size: [1525, 500, 25],
    explosion: [0, 0, 0],
    notes: "只用于确认两侧传统桌下夹的安装关系，不是打印件。",
  }));
  items.push(makeAssemblyItem({
    id: "hardware:net-fabric",
    name_zh: "乒乓球网布（装配占位）",
    name_en: "table-tennis net fabric",
    kind: "网布装配件",
    material: "外购网布",
    group: "net",
    shape: "box",
    base_min: [netMinX, -0.6, netBottomZ],
    size: [netSpan, 1.2, netTopZ - netBottomZ],
    explosion: [0, 0, 82],
    notes: "半透明真实网布占位；网顶不设置轨道。网布端部止在立柱外侧面，卡夹由网布张力和绳的拉力压住，立柱内嵌单一止挡配合卡夹一体扣舌只防向外拔出；无穿钉。",
  }));
  items.push(makeAssemblyItem({
    id: "hardware:reference-line",
    name_zh: "M6 十路机械参考线（+50 mm 示例）",
    name_en: "M6 ten-channel mechanical reference line example",
    kind: "机械校准参考",
    material: "外购线材",
    group: "reference",
    shape: "box",
    base_min: [netMinX, -0.5, 202],
    size: [netSpan, 1, 1],
    explosion: [0, -78, 48],
    notes: "只用于核对十路机械高度和两侧阵列平行度；电子高度输出必须以 M6 器件接口证据为准。",
  }));

  // The gray C-clamp fit candidate is a separate STL made by subtracting the
  // combined yellow/green seating tool. Keep the formal gray clamp in the
  // array as well; assemblyVisible() swaps it out when this review switch is
  // enabled, so the page can compare the uncut and fitted versions.
  const skpFitClampAssets = [
    {
      sideLabel: "right",
      side: 1,
      name: "右侧",
      file: "right-clamp-body-skp-leg-foot-fit.stl",
      baseMin: [680.5, -29, -75],
    },
    {
      sideLabel: "left",
      side: -1,
      name: "左侧",
      file: "left-clamp-body-skp-leg-foot-fit.stl",
      baseMin: [-918.5, -29, -75],
    },
  ];
  for (const asset of skpFitClampAssets) {
    items.push(makeAssemblyItem({
      id: `candidate:skp-fit-clamp:${asset.sideLabel}`,
      name_zh: `灰色 C 型夹让位候选（${asset.name}）`,
      name_en: `gray C-clamp fit candidate (${asset.sideLabel})`,
      kind: "候选装配件",
      material: "待定（显示/验证用）",
      material_group: "候选件",
      group: "clamp_fixed",
      stage: 1,
      color: "#687985",
      nonPrinted: false,
      fitCandidate: true,
      shape: "stl",
      sourcePath: new URL(
        `../../post-skp-leg-foot-stage1-v0.1/${asset.file}?preview=skp-leg-foot-fit`,
        state.manifestUrl,
      ).href,
      base_min: asset.baseMin,
      size: [238, 58, 91],
      side: asset.side,
      explosion: [0, 0, 0],
      notes: "灰色 C 型夹由黄色立柱下端与绿色 SKP 腿脚候选的组合外形做让位差集得到；保持原夹紧结构，其余区域不变。这里是可装配候选版，尚未替换正式打印件。",
    }));
  }

  // The SKP-derived lower leg/foot remains outside the formal print manifest
  // while the user reviews the new C-clamp fit candidate. Load the chamfered
  // STL here so the existing assembly/explosion viewer can inspect the same
  // coordinate frame without changing the 33-piece printable package.
  const skpCandidateAssets = [
    {
      sideLabel: "right",
      side: 1,
      name: "右侧",
      file: "right-post-skp-leg-foot-stage1.stl",
      baseMin: [859.8, -18, -4],
    },
    {
      sideLabel: "left",
      side: -1,
      name: "左侧",
      file: "left-post-skp-leg-foot-stage1.stl",
      baseMin: [-918.5, -18, -4],
    },
  ];
  for (const asset of skpCandidateAssets) {
    items.push(makeAssemblyItem({
      id: `candidate:skp-leg-foot:${asset.sideLabel}`,
      name_zh: `SKP 腿脚候选（${asset.name}，3 mm 终端倒角）`,
      name_en: `SKP-derived lower leg/foot candidate (${asset.sideLabel}, chamfered)`,
      kind: "候选 CAD 件",
      material: "待定（显示/验证用）",
      material_group: "候选件",
      group: "skp_candidate",
      stage: 2,
      color: "#43d34d",
      nonPrinted: false,
      candidate: true,
      shape: "stl",
      sourcePath: new URL(
        `../../post-skp-leg-foot-stage1-v0.1/${asset.file}?preview=skp-stage1-chamfered`,
        state.manifestUrl,
      ).href,
      base_min: asset.baseMin,
      size: [58.7, 36, 20],
      side: asset.side,
      explosion: explosionVector("skp_candidate", asset.side),
      notes: "来自用户提供的 SKP 形状关系：下段向下延伸至脚底，左右两组对称侧形状仍属于同一个候选件；蓝色脚沿 x 向台内伸入 15 mm，终端上缘做 3×3 mm、45° 倒角，底面保持平面。这里只用于网页装配/爆炸检查，尚未进入正式打印 manifest，也尚未与 C 型夹做干涉。",
    }));
  }

  // Current M6 assembly contract. The detector is a plain PETG rectangle;
  // the rear PETG cover has the visible thickened 1/4-20 boss. The purchased
  // ballhead is vertical and its downward M8 stud lands on the flat top of the
  // same fixed post. All z values below start in the raw source frame and are
  // shifted together by the derived shell-clearance datum.
  const m6Geometry = {
    axisX: 763,
    mountRaiseZ: assemblyDatums.m6RaiseZ,
    // Vendor drawing: 20 mm overall from the gray cable-side hex to the
    // threaded optical tip, with the final 14 mm being the hollow M6x0.75
    // barrel. The blue guard is a perpendicular local-z cable branch, not an
    // x-axis cable body.
    headLengthX: 6,
    headDepthY: 10,
    headWidthZ: 8,
    headHexAF: 8,
    sensorPitch: 20,
    deviceD: 6,
    sensorOpticalBoreD: 3,
    stemLength: 14,
    fitProbeOnly: false,
    fitCaptureDepthX: 2,
    fitHeadLengthX: 6,
    fitHeadWidthY: 10,
    fitHeadHeightZ: 8,
    fitThreadTipX: 755.25,
    fitThreadLengthX: 14,
    fitThreadVisibleLengthX: 6,
    fitThreadTipAllowanceX: 1,
    sensorInstallOffsetX: 6.25,
    cableGuardLength: 10,
    cablePreviewLength: 18,
    cableD: 3,
    bodyMinX: 761.25,
    bodyMaxX: 771.25,
    sensorRollDeg: -45,
    bodyCenterY: 0,
    bodyDepthY: 56,
    bodyBottomZ: 144.5,
    sensorBaseZ: 162.5,
    bodyHeightZ: 216,
    showShell: true,
    shellMinX: 748,
    shellMaxX: 785.4,
    shellMinY: -30.4,
    shellMaxY: 30.4,
    shellWidthY: 60.8,
    shellBottomZ: 141.5,
    shellHeightZ: 222,
    shellCornerRadius: 4,
    frontCapLengthX: 18,
    splitX: 766,
    splitClearanceX: 0.2,
    frontMaxX: 765.8,
    rearMinX: 766.2,
    grooveWidthX: 4,
    grooveDepthY: 1.2,
    grooveMarginZ: 5,
    tongueClearance: 0.25,
    wall: 2.4,
    hexPocketAF: 8,
    hexPocketDepthX: 2.1,
    threadClearanceD: 6.6,
    cableExitD: 12,
    cableExitX: 766,
    headCenterX: 766,
    installedCableExitX: 772.25,
    installedHeadMinX: 769.25,
    threadEndX: 755.25,
    receiverThreadMinX: 755.25,
    receiverOpticalMinX: 754.85,
    receiverNutMinX: 756.25,
    shellSupportBossMinX: 782.4,
    shellSupportBossMaxX: 796.4,
    shellSupportBossLengthX: 14,
    shellSupportBossOverlapX: 3,
    shellSupportBossMinY: -9,
    shellSupportBossMaxY: 9,
    shellSupportBossDepthY: 18,
    shellSupportBossCenterX: 789.4,
    shellSupportBossCenterY: 0,
    shellSupportBossBottomZ: 234.5,
    shellSupportBossTopZ: 270.5,
    shellSupportBossHeightZ: 36,
    shellSupportBossRadius: 2,
    shellSupportGussetMinX: 782.2,
    shellSupportGussetMaxX: 785.6,
    shellSupportGussetXOverlap: 0.2,
    shellSupportGussetRootYStart: 4,
    shellSupportGussetWallYStart: 28,
    shellSupportGussetRootWidthY: 5,
    shellSupportGussetWallWidthY: 2.4,
    shellSupportGussetBottomZ: 246.5,
    shellSupportGussetTopZ: 258.5,
    shellSupportGussetHeightZ: 12,
    shellSupportHoleD: 7,
    shellSupportHoleDepthX: 14,
    shellSupportHoleEntryX: 796.4,
    shellSupportStudEngagementX: 12,
    ballheadBallD: 13,
    ballheadHousingD: 28,
    ballheadHousingLength: 26,
    ballheadBodyDepthY: 24,
    ballheadBodyCornerRadius: 4,
    ballheadBallSocketD: 17,
    ballheadSidePlateD: 24,
    ballheadSidePlateTX: 4,
    ballheadLockKnobD: 18,
    ballheadLockKnobTY: 8,
    ballheadLockKnobRidgeCount: 24,
    ballheadCenterX: assemblyDatums.rawBallheadCenterX,
    ballheadCenterY: 0,
    ballheadCenterZ: assemblyDatums.rawBallheadCenterZ,
    ballheadBaseCenterZ: assemblyDatums.rawBallheadBaseCenterZ,
    ballheadBaseD: 32,
    ballheadBaseT: 8,
    ballheadNetStudCenterZ: assemblyDatums.rawBallheadBaseCenterZ
      - M6_PREVIEW_BALLHEAD_BASE_T / 2
      - M6_PREVIEW_BALLHEAD_NET_STUD_LENGTH_Z / 2,
    ballheadNetStudLength: M6_PREVIEW_BALLHEAD_NET_STUD_LENGTH_Z,
    ballheadSensorStudCenterX: assemblyDatums.rawRearMaxX
      + M6_PREVIEW_BALLHEAD_STUD_LENGTH_X / 2
      - M6_PREVIEW_BALLHEAD_STUD_ENGAGEMENT_X,
    ballheadSensorStudD: 6.35,
    ballheadSensorThreadCoreD: 5.35,
    ballheadSensorThreadPitch: 1.27,
    ballheadNetStudD: 8,
    ballheadSensorStudLength: 16,
    ballheadNetThreadCoreD: 6.6,
    ballheadNetThreadPitch: 1.25,
    ballheadTopNutAF: 11.1,
    ballheadTopNutH: 5.5,
    ballheadBottomNutAF: 13,
    ballheadBottomNutH: 6.5,
    ballheadNutClearance: 0.35,
    ballheadTiltDeg: 90,
    ballheadRotationDeg: 360,
    netClampChannelDepthX: 25,
    netClampCylinderInsertionDepthX: 25,
    netClampChannelBackWallTX: 3,
    netPassageWidthY: 3,
    netClampCylinderInterferenceD: 14,
    netClampCylinderActualD: 12,
    netClampChannelWidthY: 8,
    netClampChannelBottomZ: 0,
    netClampChannelTopZ: 152.5,
    netClampChannelVoidMinX: 893,
    netClampChannelVoidMaxX: 919.5,
    netClampCylinderCenterX: 900.6,
    netClampCylinderHeight: 152.5,
  };
  // The detector/ballhead is installed as one rigid group. Move its raw
  // right-side coordinate chain to the net-post centre so the purchased
  // ballhead's downward interface lands directly on the one-piece upright socket;
  // this removes the previous horizontal support arm.
  const detectorOffsetX = assemblyDatums.m6OffsetX;
  const absoluteXFields = [
    "axisX",
    "fitThreadTipX",
    "bodyMinX",
    "bodyMaxX",
    "shellMinX",
    "shellMaxX",
    "splitX",
    "frontMaxX",
    "rearMinX",
    "cableExitX",
    "headCenterX",
    "installedCableExitX",
    "installedHeadMinX",
    "threadEndX",
    "receiverThreadMinX",
    "receiverOpticalMinX",
    "receiverNutMinX",
    "shellSupportBossMinX",
    "shellSupportBossMaxX",
    "shellSupportBossCenterX",
    "shellSupportHoleEntryX",
    "shellSupportGussetMinX",
    "shellSupportGussetMaxX",
    "ballheadCenterX",
    "ballheadSensorStudCenterX",
  ];
  for (const field of absoluteXFields) {
    m6Geometry[field] += detectorOffsetX;
  }
  const detectorRaiseZ = assemblyDatums.m6RaiseZ;
  for (const field of [
    "bodyBottomZ",
    "sensorBaseZ",
    "shellBottomZ",
    "shellSupportBossBottomZ",
    "shellSupportBossTopZ",
    "shellSupportGussetBottomZ",
    "shellSupportGussetTopZ",
    "ballheadCenterZ",
    "ballheadBaseCenterZ",
    "ballheadNetStudCenterZ",
  ]) {
    m6Geometry[field] += detectorRaiseZ;
  }
  m6Geometry.assemblyOffsetX = detectorOffsetX;
  m6Geometry.assembledBallheadCenterX = m6Geometry.ballheadCenterX;
  // The beam datum is the hollow M6 optical tip, not the sensor head axis.
  // This keeps the red direction references on the actual apertures.
  m6Geometry.assembledOpticalAxisX = m6Geometry.fitThreadTipX;
  Object.assign(m6Geometry, {
    postCenterX: assemblyDatums.postCenterX,
    postBodyWidth: 28,
    postBodyDepth: 38,
    postInnerFaceX: assemblyDatums.postCenterX - 28 / 2,
    ballheadNetInterfaceBottomZ:
      m6Geometry.ballheadNetStudCenterZ - m6Geometry.ballheadNetStudLength / 2,
    directMountArmWidthY: 0,
    directMountArmThicknessZ: 0,
    // Compatibility fields: the fixed-net post has no horizontal seat or
    // side-return web. Its flat top owns the central M8 tap pilot.
    directMountWebWidthY: 0,
    directMountWebThicknessX: 0,
    directMountPostOverlapX: 2,
    // The active post socket is a tap pilot in the flat top; the clearance
    // diameter remains a first-article mouth/fit reference for the bought M8.
    directMountSocketOuterD: 24,
    directMountSocketTapD: 6.8,
    directMountSocketClearanceD: 8.6,
    directMountSocketBaseOverlapZ: 0,
    directMountNutLoadingClearanceZ: 0,
    directMountThreadDepthExtraZ: 2,
    directMountThreadDepthZ:
      m6Geometry.ballheadNetStudLength + 2,
    directMountThreadBottomZ:
      m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2
      - m6Geometry.ballheadNetStudLength - 2,
    directMountThreadTopZ:
      m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2,
    directMountSocketBottomZ:
      m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2
      - m6Geometry.ballheadNetStudLength - 2,
    directMountSocketTopZ:
      m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2,
    directMountSocketHeightZ:
      m6Geometry.ballheadNetStudLength + 2,
    directMountSocketCenterZ:
      (m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2
        + m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2
        - m6Geometry.ballheadNetStudLength - 2) / 2,
    directMountSocketCenterX: assemblyDatums.postCenterX,
    directMountNutPocketBottomZ:
      m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2
      - m6Geometry.ballheadNetStudLength - 2,
    directMountNutPocketCenterZ:
      m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2
      - m6Geometry.ballheadNetStudLength - 2,
    directMountNutLoadingDepthZ: 0,
    directMountArmMinX: assemblyDatums.postCenterX,
    directMountArmMaxX: assemblyDatums.postCenterX,
    directMountArmBottomZ:
      m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2,
    directMountArmTopZ:
      m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2,
    directMountLowerPostTopZ: assemblyDatums.postTopZ,
    directMountWebMinX: assemblyDatums.postCenterX - 28 / 2,
    directMountWebMaxX: assemblyDatums.postCenterX - 28 / 2,
    directMountWebMinZ:
      m6Geometry.ballheadNetStudCenterZ - m6Geometry.ballheadNetStudLength / 2,
    directMountWebMaxZ:
      m6Geometry.ballheadNetStudCenterZ - m6Geometry.ballheadNetStudLength / 2,
  });
  for (const sideLabel of ["left", "right"]) {
    const side = sideLabel === "left" ? -1 : 1;
    const sideName = side < 0 ? "左" : "右";
    const mirrorX = (minX, sizeX) => side > 0 ? minX : -minX - sizeX;
    const bodyMinX = side > 0 ? m6Geometry.bodyMinX : -m6Geometry.bodyMaxX;
    const shellMinX = side > 0 ? m6Geometry.shellMinX : -m6Geometry.shellMaxX;
    const frontShellMinX = side > 0 ? m6Geometry.shellMinX : -m6Geometry.frontMaxX;
    const rearShellMinX = side > 0 ? m6Geometry.rearMinX : -m6Geometry.shellMaxX;
    // Rotation pivots are expressed relative to each item's base_min. The
    // actual axis is the global x line at y=0 and the sensor's z center.
    const rotationPivotFor = (baseMin, sensorZ) => [
      0,
      -baseMin[1],
      sensorZ - baseMin[2],
    ];
    const ballheadMinX = side > 0
      ? m6Geometry.ballheadCenterX - m6Geometry.ballheadHousingD / 2
      : -m6Geometry.ballheadCenterX - m6Geometry.ballheadHousingD / 2;
    const ballheadBaseMinX = side > 0
      ? m6Geometry.ballheadCenterX - m6Geometry.ballheadBaseD / 2
      : -m6Geometry.ballheadCenterX - m6Geometry.ballheadBaseD / 2;
    const ballheadStudMinX = side > 0
      ? m6Geometry.ballheadSensorStudCenterX - m6Geometry.ballheadSensorStudLength / 2
      : -m6Geometry.ballheadSensorStudCenterX - m6Geometry.ballheadSensorStudLength / 2;
    if (m6Geometry.fitProbeOnly) {
      const fitHeadInnerX = m6Geometry.bodyMaxX - m6Geometry.fitCaptureDepthX;
      const fitHeadCenterX = fitHeadInnerX + m6Geometry.fitHeadLengthX / 2;
      const fitTranslationX = fitHeadCenterX - m6Geometry.headCenterX;
      const fitCableExitX = m6Geometry.cableExitX + fitTranslationX;
      items.push(makeAssemblyItem({
        id: `hardware:m6-fit-body:${sideLabel}`,
        name_zh: `M6 首样长条主体（${sideName}）`,
        name_en: "M6 first-article rectangular fit body",
        kind: "机加工主体首样",
        material: "PETG 首样；后续可换 6061-T6 CNC",
        group: "optical",
        color: "#aeb5bb",
        shape: "box",
        base_min: [bodyMinX, -m6Geometry.bodyDepthY / 2, m6Geometry.bodyBottomZ],
        size: [m6Geometry.bodyMaxX - m6Geometry.bodyMinX,
          m6Geometry.bodyDepthY,
          m6Geometry.bodyHeightZ],
        side,
        explosion: [0, 0, 0],
        notes: "本阶段只显示 PETG 长条主体与真实三维 L 型器件；主体截面加宽到 y=56 mm、加厚到 x=10 mm。灰色 AF8 六角从外侧卡入 2 mm，中空 M6 外丝贯穿主体，朝台内的平滑面带一枚原配螺帽。蓝色护套和黑色尾线按实物绕光束 x 轴 -45° 显示；后盖 boss、壳子和采购球头在完整装配模式显示。",
      }));
      for (let index = 0; index < 10; index += 1) {
        const z = m6Geometry.sensorBaseZ + index * m6Geometry.sensorPitch;
        const headMinX = side > 0
          ? fitHeadInnerX
          : mirrorX(fitHeadInnerX, m6Geometry.fitHeadLengthX);
        const threadMinX = side > 0
          ? m6Geometry.fitThreadTipX
          : mirrorX(m6Geometry.fitThreadTipX, m6Geometry.fitThreadLengthX);
        const apertureMinX = side > 0
          ? m6Geometry.fitThreadTipX - 0.4
          : mirrorX(m6Geometry.fitThreadTipX - 0.4, 0.4);
        const cableGuardMinX = mirrorX(
          fitCableExitX - m6Geometry.deviceD / 2,
          m6Geometry.deviceD,
        );
        const cableMinX = mirrorX(
          fitCableExitX - m6Geometry.cableD / 2,
          m6Geometry.cableD,
        );
        const headBaseMin = [
          headMinX,
          -m6Geometry.fitHeadWidthY / 2,
          z - m6Geometry.fitHeadHeightZ / 2,
        ];
        const guardBaseMin = [
          cableGuardMinX,
          -m6Geometry.deviceD / 2,
          z - m6Geometry.fitHeadHeightZ / 2 - m6Geometry.cableGuardLength,
        ];
        const cableBaseMin = [
          cableMinX,
          -m6Geometry.cableD / 2,
          z - m6Geometry.fitHeadHeightZ / 2 -
            m6Geometry.cableGuardLength - m6Geometry.cablePreviewLength,
        ];
        items.push(makeAssemblyItem({
          id: `hardware:m6-fit-head:${sideLabel}:${index}`,
          name_zh: `真实三维 M6 L 型激光头（卡入 2 mm）+${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
          name_en: "real 3D M6 right-angle laser head captured 2 mm into body",
          kind: "外购器件三维包络",
          material: "用户指定 M6 L 型对射器件",
          group: "optical",
          color: "#69747d",
          shape: "hex",
          base_min: headBaseMin,
          size: [m6Geometry.fitHeadLengthX,
            m6Geometry.fitHeadWidthY,
            m6Geometry.fitHeadHeightZ],
          shapeOptions: {
            radius: m6Geometry.headHexAF / (2 * Math.cos(Math.PI / 6)),
            axis: "x",
            rotation_x_deg: m6Geometry.sensorRollDeg,
            rotation_pivot: rotationPivotFor(headBaseMin, z),
          },
          side,
          explosion: [0, 0, 0],
          notes: "灰色 AF8 六角是线缆侧主体/防转面，外侧有 4 mm 露出，内侧 2 mm 被主体的同形浅六角窝卡住；它不是光学端。",
        }));
        items.push(makeAssemblyItem({
          id: `hardware:m6-fit-guard:${sideLabel}:${index}`,
          name_zh: `真实蓝色 L 型护套 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
          name_en: "real 3D blue right-angle cable guard",
          kind: "外购器件三维包络",
          material: "用户指定 M6 L 型对射器件",
          group: "optical",
          color: "#2764d7",
          shape: "cylinder",
          shapeOptions: {
            radius: m6Geometry.deviceD / 2,
            axis: "z",
            rotation_x_deg: m6Geometry.sensorRollDeg,
            rotation_pivot: rotationPivotFor(guardBaseMin, z),
          },
          base_min: guardBaseMin,
          size: [m6Geometry.deviceD, m6Geometry.deviceD, m6Geometry.cableGuardLength],
          side,
          explosion: [0, 0, 0],
          notes: "蓝色 L 型护套从灰色六角侧沿局部 z- 出线，再绕光束 x 轴 -45° 斜向 y-/z-，用于给相邻 20 mm 通道让线。",
        }));
        items.push(makeAssemblyItem({
          id: `hardware:m6-fit-cable:${sideLabel}:${index}`,
          name_zh: `真实黑色尾线 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
          name_en: "real 3D cable continuation",
          kind: "外购器件三维包络",
          material: "用户指定 M6 L 型对射器件",
          group: "optical",
          color: "#20252b",
          shape: "cylinder",
          shapeOptions: {
            radius: m6Geometry.cableD / 2,
            axis: "z",
            rotation_x_deg: m6Geometry.sensorRollDeg,
            rotation_pivot: rotationPivotFor(cableBaseMin, z),
          },
          base_min: cableBaseMin,
          size: [m6Geometry.cableD, m6Geometry.cableD, m6Geometry.cablePreviewLength],
          side,
          explosion: [0, 0, 0],
          notes: "黑色尾线沿蓝色护套继续斜向下；这里只显示实际器件的短线缆代理，后续底盖统一套管另行设计。",
        }));
        items.push(makeAssemblyItem({
          id: `hardware:m6-fit-thread:${sideLabel}:${index}`,
          name_zh: `中空 M6 外丝筒 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
          name_en: "hollow M6 threaded optical barrel",
          kind: "外购器件简化包络",
          material: "用户指定 M6 L 型对射器件",
          group: "optical",
          color: "#b9c0c5",
          shape: "cylinder",
          shapeOptions: { radius: m6Geometry.deviceD / 2, axis: "x" },
          base_min: [threadMinX, -m6Geometry.deviceD / 2, z - m6Geometry.deviceD / 2],
          size: [m6Geometry.fitThreadLengthX, m6Geometry.deviceD, m6Geometry.deviceD],
          side,
          explosion: [0, 0, 0],
          notes: "M6 外丝不是单纯安装螺丝；它是中空光学筒，末端中心孔朝球台中心。10 mm 主体内侧露出 6 mm，容纳 5 mm 厚螺帽并保留约 1 mm 端部余量。",
        }));
        const nutHeight = 5;
        const nutAF = 10;
        const nutMinX = side > 0
          ? m6Geometry.bodyMinX - nutHeight
          : mirrorX(m6Geometry.bodyMinX - nutHeight, nutHeight);
        const nutBaseMin = [
          nutMinX,
          -nutAF / 2,
          z - nutAF / 2,
        ];
        items.push(makeAssemblyItem({
          id: `hardware:m6-fit-nut:${sideLabel}:${index}`,
          name_zh: `M6 原配螺帽（朝台内平滑面）+${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
          name_en: "one supplied M6 lock nut on the smooth inner face",
          kind: "外购紧固件三维包络",
          material: "随 M6 L 型对射器件附带",
          group: "hardware",
          color: "#d0a72b",
          shape: "hex",
          shapeOptions: {
            radius: nutAF / (2 * Math.cos(Math.PI / 6)),
            axis: "x",
            rotation_x_deg: m6Geometry.sensorRollDeg,
            rotation_pivot: rotationPivotFor(nutBaseMin, z),
          },
          base_min: nutBaseMin,
          size: [nutHeight, nutAF, nutAF],
          side,
          explosion: [0, 0, 0],
          notes: "只带一枚原配 M6 螺帽；位于主体朝台内的平滑面，螺帽不嵌入主体，固定螺丝也不进入主体。",
        }));
        items.push(makeAssemblyItem({
          id: `hardware:m6-fit-aperture:${sideLabel}:${index}`,
          name_zh: `中空 M6 末端中心孔 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
          name_en: "hollow M6 tip aperture",
          kind: "光学端视觉标记",
          material: "显示参考，不是独立零件",
          group: "optical",
          color: "#111820",
          shape: "cylinder",
          shapeOptions: { radius: m6Geometry.sensorOpticalBoreD / 2, axis: "x" },
          base_min: [apertureMinX,
            -m6Geometry.sensorOpticalBoreD / 2,
            z - m6Geometry.sensorOpticalBoreD / 2],
          size: [0.4, m6Geometry.sensorOpticalBoreD, m6Geometry.sensorOpticalBoreD],
          side,
          explosion: [0, 0, 0],
          notes: "黑色只表示中空 M6 外丝末端的中心孔；灰色 AF8 六角和蓝色尾部都没有独立光学面。",
        }));
        items.push(makeAssemblyItem({
          id: `reference:m6-fit-beam:${sideLabel}:${index}`,
          name_zh: `M6 光束方向（${sideName}，+${10 + index * m6Geometry.sensorPitch} mm）`,
          name_en: "M6 beam direction reference",
          kind: "光束方向参考",
          material: "显示参考，不是实体",
          group: "reference",
          color: "#f35f5f",
          shape: "cylinder",
          shapeOptions: { radius: 0.45, axis: "x" },
          base_min: side > 0
            ? [m6Geometry.fitThreadTipX - 80, -0.45, z - 0.45]
            : [-m6Geometry.fitThreadTipX, -0.45, z - 0.45],
          size: [80, 0.9, 0.9],
          side,
          explosion: [0, 0, 0],
          notes: side > 0
            ? "右侧接收端：中心孔位于 x-，光束由左向右进入。"
            : "左侧发射端：中心孔位于 x+，光束由这里向右发出。",
        }));
      }
      continue;
    }

    if (!hasSourceM6Part("m6_detector_body")) items.push(makeAssemblyItem({
      id: `hardware:m6-detector-body:${sideLabel}`,
      name_zh: `M6 PETG 长条主体（${sideName}）`,
      name_en: "M6 rectangular PETG detector body, future CNC-compatible",
      kind: "可打印结构主体",
      material: "PETG 首样；后续可换 6061-T6 CNC",
      group: "optical",
      color: "#4a7da8",
      base_min: [bodyMinX, m6Geometry.bodyCenterY - m6Geometry.bodyDepthY / 2, m6Geometry.bodyBottomZ],
      size: [m6Geometry.bodyMaxX - m6Geometry.bodyMinX, m6Geometry.bodyDepthY, m6Geometry.bodyHeightZ],
      side,
      explosion: [side * 54, 0, 28],
      notes: "主体就是 x=10 mm 厚、y=56 mm 宽、z=216 mm 的连续矩形长条；真实 M6 L 型器件从外侧沿 x 装入，灰色 AF8 六角卡入浅窝，中空外丝朝台内穿出并由一枚原配螺帽锁紧。两条 y± 边槽只导向前后盖舌片，主体不带 T 尾座、M8 孔或主体内线缆槽。",
    }));
    if (m6Geometry.showShell && !hasSourceM6Part("m6_detector_shell_front")) items.push(makeAssemblyItem({
      id: `hardware:m6-shell-front:${sideLabel}`,
      name_zh: `M6 前盖：x- 光学端正球弧（${sideName}）`,
      name_en: "M6 front spherical-arc cover",
      kind: "保护壳（非承力）",
      material: "PETG 尺寸样件",
      group: "optical",
      shape: "front-arc",
      shapeOptions: {
        front_length_x: m6Geometry.frontMaxX - m6Geometry.shellMinX,
        mirror_x: side < 0,
      },
      base_min: [frontShellMinX, m6Geometry.shellMinY, m6Geometry.shellBottomZ],
      size: [m6Geometry.frontMaxX - m6Geometry.shellMinX,
        m6Geometry.shellWidthY,
        m6Geometry.shellHeightZ],
      side,
      explosion: [side * -92, 0, 46],
      notes: "x- 光学端前盖为正球弧，从主体 z+ 套入；它占两条 y± 边槽的 x- 半，M3/M4 沉头螺钉只锁入主体导孔。",
    }));
    if (m6Geometry.showShell && !hasSourceM6Part("m6_detector_shell_rear")) items.push(makeAssemblyItem({
      id: `hardware:m6-shell-rear:${sideLabel}`,
      name_zh: `M6 后盖：直角接驳边/后端圆角与加厚 1/4-20 支撑 boss（${sideName}）`,
      name_en: "M6 rear cover with straight joint edge, rounded rear corners, and 1/4-20 boss",
      kind: "保护壳（非承力）",
      material: "PETG 尺寸样件",
      group: "optical",
      shape: "rear-back-rounded-support-boss",
      shapeOptions: {
        radius: m6Geometry.shellCornerRadius,
        outer_y_offset: 0,
        outer_depth_y: m6Geometry.shellMaxY - m6Geometry.shellMinY,
        boss_x_offset: m6Geometry.shellSupportBossMinX - m6Geometry.rearMinX,
        boss_y_offset: m6Geometry.shellSupportBossMinY - m6Geometry.shellMinY,
        boss_z_offset: m6Geometry.shellSupportBossBottomZ - m6Geometry.shellBottomZ,
        boss_length_x: m6Geometry.shellSupportBossLengthX,
        boss_depth_y: m6Geometry.shellSupportBossMaxY - m6Geometry.shellSupportBossMinY,
        boss_height_z: m6Geometry.shellSupportBossHeightZ,
        boss_radius: m6Geometry.shellSupportBossRadius,
        boss_hole_d: m6Geometry.shellSupportHoleD,
        boss_hole_depth_x: m6Geometry.shellSupportHoleDepthX,
        gusset_x_offset: m6Geometry.shellSupportGussetMinX - m6Geometry.rearMinX,
        gusset_length_x: m6Geometry.shellSupportGussetMaxX - m6Geometry.shellSupportGussetMinX,
        gusset_root_y_offset: m6Geometry.shellSupportGussetRootYStart - m6Geometry.shellMinY,
        gusset_wall_y_offset: m6Geometry.shellSupportGussetWallYStart - m6Geometry.shellMinY,
        gusset_root_width_y: m6Geometry.shellSupportGussetRootWidthY,
        gusset_wall_width_y: m6Geometry.shellSupportGussetWallWidthY,
        gusset_z_offset: m6Geometry.shellSupportGussetBottomZ - m6Geometry.shellBottomZ,
        gusset_height_z: m6Geometry.shellSupportGussetHeightZ,
        mirror_x: side < 0,
      },
      base_min: [rearShellMinX, m6Geometry.shellMinY, m6Geometry.shellBottomZ],
      size: [m6Geometry.shellMaxX - m6Geometry.rearMinX,
        m6Geometry.shellMaxY - m6Geometry.shellMinY,
        m6Geometry.shellHeightZ],
      side,
      explosion: [side * 118, 0, 38],
      notes: "x+ 线缆端后盖在与前盖接驳处保持直角，只有自身 x+ 后部两个角圆滑；背面中央（y=0、z 中心）适当增厚形成支撑 boss，并开 x 向 Ø7.0 1/4-20 外牙通孔，内藏一颗标准 1/4-20 螺母。boss 根部在 y± 两侧各有一条约 3.4×26.4×12 mm 的实体桥接肋，根部从 |y|=4 mm 起并跨到后壳侧壁，避开中央 Ø7 通孔；后盖与主体通过沉头螺丝连接，首样不把薄壳作为唯一弯矩承力件。",
    }));
    if (m6Geometry.showShell && !hasSourceM6Part("m6_detector_bottom_cover")) items.push(makeAssemblyItem({
      id: `hardware:m6-bottom-cover:${sideLabel}`,
      name_zh: `M6 底盖与线缆套管孔（${sideName}）`,
      name_en: "M6 bottom cover with cable sleeve exit",
      kind: "保护盖（非承力）",
      material: "PETG 尺寸样件",
      group: "optical",
      shape: "combined-footprint",
      shapeOptions: {
        front_length_x: m6Geometry.frontMaxX - m6Geometry.shellMinX,
        rear_x_offset: m6Geometry.rearMinX - m6Geometry.shellMinX,
        rear_length_x: m6Geometry.shellMaxX - m6Geometry.rearMinX,
        parting_gap_x: m6Geometry.rearMinX - m6Geometry.frontMaxX,
        width_y: m6Geometry.shellWidthY,
        radius: m6Geometry.shellCornerRadius,
        mirror_x: side < 0,
      },
      base_min: [shellMinX, -m6Geometry.shellWidthY / 2, m6Geometry.shellBottomZ - 3],
      size: [m6Geometry.shellMaxX - m6Geometry.shellMinX, m6Geometry.shellWidthY, 3],
      side,
      explosion: [side * 42, 0, -46],
      notes: "底盖按下方截面封闭，两个沉头螺钉固定到主体；Ø12 mm 孔贯通用于剥皮后统一线缆套管，当前明确为非密封设计。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-ballhead-housing:${sideLabel}`,
      name_zh: `13 mm 采购球头（竖直姿态，${sideName}）`,
      name_en: "13 mm purchased ball head, vertical posture",
      kind: "外购云台占位",
      material: "外购金属件（非打印）",
      group: "optical",
      shape: "ballhead-body",
      shapeOptions: {
        radius: m6Geometry.ballheadBodyCornerRadius,
        ball_d: m6Geometry.ballheadBallD,
        ball_socket_d: m6Geometry.ballheadBallSocketD,
        side_plate_d: m6Geometry.ballheadSidePlateD,
        side_plate_t_x: m6Geometry.ballheadSidePlateTX,
        lock_knob_d: m6Geometry.ballheadLockKnobD,
        lock_knob_t_y: m6Geometry.ballheadLockKnobTY,
        lock_knob_ridge_count: m6Geometry.ballheadLockKnobRidgeCount,
      },
      base_min: [ballheadMinX, m6Geometry.ballheadCenterY - m6Geometry.ballheadBodyDepthY / 2, m6Geometry.ballheadCenterZ - m6Geometry.ballheadHousingLength / 2],
      size: [m6Geometry.ballheadHousingD, m6Geometry.ballheadBodyDepthY, m6Geometry.ballheadHousingLength],
      side,
      explosion: [side * 154, -28, 20],
      notes: "云台本体不打印；按商品实景的 13 mm 球、360°旋转、90°开口和竖直壳体姿态占位。上端 1/4-20 外牙朝 x- 连接后盖；下端 M8 外牙朝 z- 进入浅黄色立柱顶面中心的 M8 攻丝底孔；旋钮/球体为可见金属包络。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-ballhead-base:${sideLabel}`,
      name_zh: `采购球头底座与竖直 M8 外牙（${sideName}）`,
      name_en: "purchased ball-head base with selected M8 external stud",
      kind: "外购云台接口占位",
      material: "外购金属件（非打印）",
      group: "optical",
      shape: "cylinder",
      shapeOptions: { radius: m6Geometry.ballheadBaseD / 2, axis: "z" },
      base_min: [ballheadBaseMinX, m6Geometry.ballheadCenterY - m6Geometry.ballheadBaseD / 2, m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2],
      size: [m6Geometry.ballheadBaseD, m6Geometry.ballheadBaseD, m6Geometry.ballheadBaseT],
      side,
      explosion: [side * 154, -28, -4],
      notes: `底座是采购云台的一部分，商品上端固定螺纹为 1/4-20 外牙（约 6.35 mm）；本项目下端选择 M8 外牙，直接落在网架立柱顶端 z=${formatNumber(assemblyDatums.postTopZ)} mm 的中心 M8 安装轴线上。立柱和后盖共用 y=0 轴心，不增加横向桥件。`,
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-ballhead-sensor-stud:${sideLabel}`,
      name_zh: `后盖 boss x 轴 1/4-20 连接螺柱（${sideName}）`,
      name_en: "1/4-20 horizontal ball-head stud into rear-cover boss",
      kind: "外购云台接口占位",
      material: "外购金属件（非打印）",
      group: "optical",
      shape: "threaded-stud",
      shapeOptions: {
        radius: m6Geometry.ballheadSensorStudD / 2,
        axis: "x",
        outer_d: m6Geometry.ballheadSensorStudD,
        core_d: m6Geometry.ballheadSensorThreadCoreD,
        pitch: m6Geometry.ballheadSensorThreadPitch,
      },
      base_min: [ballheadStudMinX,
        m6Geometry.ballheadCenterY - m6Geometry.ballheadSensorStudD / 2,
        m6Geometry.ballheadCenterZ - m6Geometry.ballheadSensorStudD / 2],
      size: [m6Geometry.ballheadSensorStudLength,
        m6Geometry.ballheadSensorStudD,
        m6Geometry.ballheadSensorStudD],
      side,
      explosion: [side * 162, -28, 24],
      notes: "商品上端 1/4-20 外牙金属螺柱沿 x-（左侧镜像为 x+）直接进入各自 x 后端背面中央 boss 的 Ø7.0 通孔，并由隐藏的标准 1/4-20 螺母锁紧；主体保持长方条，不制作 T 尾座。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-ballhead-net-stud:${sideLabel}`,
      name_zh: `采购球头向下的竖直接口（${sideName}）`,
      name_en: "purchased ball-head downward M8 interface",
      kind: "外购云台接口占位",
      material: "外购金属件（非打印）",
      group: "optical",
      shape: "threaded-stud",
      shapeOptions: {
        radius: m6Geometry.ballheadNetStudD / 2,
        axis: "z",
        outer_d: m6Geometry.ballheadNetStudD,
        core_d: m6Geometry.ballheadNetThreadCoreD,
        pitch: m6Geometry.ballheadNetThreadPitch,
      },
      base_min: [mirrorX(m6Geometry.ballheadCenterX - m6Geometry.ballheadNetStudD / 2,
        m6Geometry.ballheadNetStudD),
        m6Geometry.ballheadCenterY - m6Geometry.ballheadNetStudD / 2,
        m6Geometry.ballheadNetStudCenterZ - m6Geometry.ballheadNetStudLength / 2],
      size: [m6Geometry.ballheadNetStudD,
        m6Geometry.ballheadNetStudD,
        m6Geometry.ballheadNetStudLength],
      side,
      explosion: [side * 154, -28, -24],
      notes: `采购球头下端选择 M8 外牙，朝 z- 插入浅黄色立柱顶面中心的 M8 攻丝底孔；安装顶面 z=${formatNumber(assemblyDatums.postTopZ)} mm，孔轴 x=${formatNumber(assemblyDatums.postCenterX)}、y=0，与球头底座及后盖 boss 同轴。不设置外露圆形承座、六角螺母窝、侧向承力耳或旧版独立连接器。`,
    }));
    for (let index = 0; index < 10; index += 1) {
      const z = m6Geometry.sensorBaseZ + index * m6Geometry.sensorPitch;
      const beamLength = 80;
      items.push(makeAssemblyItem({
        id: `reference:m6-beam-direction:${sideLabel}:${index}`,
        name_zh: `M6 光束方向（${sideName}，+${10 + index * m6Geometry.sensorPitch} mm）`,
        name_en: "M6 optical beam direction",
        kind: "光束方向参考",
        material: "显示参考，不是实体",
        group: "optical",
        color: "#f35f5f",
        shape: "cylinder",
        shapeOptions: { radius: 0.45, axis: "x" },
        base_min: side > 0
          ? [m6Geometry.fitThreadTipX - beamLength, -0.45, z - 0.45]
          : [-m6Geometry.fitThreadTipX, -0.45, z - 0.45],
        size: [beamLength, 0.9, 0.9],
        side,
        explosion: [0, 0, 0],
        notes: side > 0
          ? "右侧接收器：红线从左侧进入，终止在中空 M6 外丝末端的中心孔（x-）。"
          : "左侧发射器：中心孔位于中空 M6 外丝末端（x+），红线从这里向球台中心发出。",
      }));
      // Positive geometry is the installed right receiver. Its gray
      // cable-side head is at x+; the hollow threaded barrel and optical
      // aperture pass toward the smooth x- body face. The left emitter is the
      // complete x mirror of that package.
      const headMinX = side > 0
        ? m6Geometry.installedHeadMinX
        : mirrorX(m6Geometry.installedHeadMinX, m6Geometry.headLengthX);
      const faceMinX = side > 0
        ? m6Geometry.receiverOpticalMinX
        : mirrorX(m6Geometry.receiverOpticalMinX, 0.4);
      const threadMinX = side > 0
        ? m6Geometry.receiverThreadMinX
        : mirrorX(m6Geometry.receiverThreadMinX, m6Geometry.stemLength);
      const cableGuardMinX = mirrorX(
        m6Geometry.installedCableExitX - m6Geometry.deviceD / 2,
        m6Geometry.deviceD,
      );
      const cableMinX = mirrorX(
        m6Geometry.installedCableExitX - m6Geometry.cableD / 2,
        m6Geometry.cableD,
      );
      const hexMinX = mirrorX(
        m6Geometry.bodyMaxX - m6Geometry.hexPocketDepthX,
        m6Geometry.hexPocketDepthX,
      );
      const nutMinX = side > 0
        ? m6Geometry.receiverNutMinX
        : mirrorX(m6Geometry.receiverNutMinX, 5);
      const headBaseMin = [
        headMinX,
        -m6Geometry.headDepthY / 2,
        z - m6Geometry.headWidthZ / 2,
      ];
      const faceBaseMin = [
        faceMinX,
        -m6Geometry.sensorOpticalBoreD / 2,
        z - m6Geometry.sensorOpticalBoreD / 2,
      ];
      const bodyBaseMin = [
        cableGuardMinX,
        -m6Geometry.deviceD / 2,
        z - m6Geometry.headWidthZ / 2 - m6Geometry.cableGuardLength,
      ];
      const cableBaseMin = [
        cableMinX,
        -m6Geometry.cableD / 2,
        z - m6Geometry.headWidthZ / 2 -
          m6Geometry.cableGuardLength - m6Geometry.cablePreviewLength,
      ];
      const hexBaseMin = [
        hexMinX,
        -m6Geometry.hexPocketAF / 2,
        z - m6Geometry.hexPocketAF / 2,
      ];
      const threadBaseMin = [
        threadMinX,
        -m6Geometry.deviceD / 2,
        z - m6Geometry.deviceD / 2,
      ];
      items.push(makeAssemblyItem({
        id: `hardware:m6-device-head:${sideLabel}:${index}`,
        name_zh: `M6 直角光学头 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
        name_en: "M6 right-angle optical head proxy",
        kind: "外购光学器件占位",
        material: "用户指定 M6 SKU 6122579349941",
        group: "optical",
        color: "#69747d",
        shape: "hex",
        base_min: headBaseMin,
        size: [m6Geometry.headLengthX, m6Geometry.headDepthY, m6Geometry.headWidthZ],
        shapeOptions: {
          radius: m6Geometry.headHexAF / (2 * Math.cos(Math.PI / 6)),
          axis: "x",
          rotation_x_deg: m6Geometry.sensorRollDeg,
          rotation_pivot: rotationPivotFor(headBaseMin, z),
        },
        side,
        explosion: [side * 68, -96, 16],
        notes: "灰色六角是尾线连接/防转主体，位于外侧浅窝；中空 M6 外丝筒沿 x 伸向球台中心，末端中心孔才是光学端。右侧从 x+、左侧从 x- 外侧装入；蓝色尾线随后绕光束 x 轴 -45°。",
      }));
      items.push(makeAssemblyItem({
        id: `hardware:m6-device-face:${sideLabel}:${index}`,
        name_zh: `M6 中空外丝末端中心光学孔 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
        name_en: "M6 hollow-thread tip optical aperture",
        kind: "外购光学器件占位",
        material: "用户指定 M6 SKU 6122579349941",
        group: "optical",
        shape: "cylinder",
        shapeOptions: {
          radius: m6Geometry.sensorOpticalBoreD / 2,
          axis: "x",
          rotation_x_deg: m6Geometry.sensorRollDeg,
          rotation_pivot: rotationPivotFor(faceBaseMin, z),
        },
        base_min: faceBaseMin,
        size: [0.4, m6Geometry.sensorOpticalBoreD, m6Geometry.sensorOpticalBoreD],
        side,
        explosion: [side * 68, -102, 16],
        notes: "黑色只表示中空 M6 外丝筒末端的中心孔；灰色六角处没有独立黑色光学面。左右件由镜像得到，孔口均朝向球台中心。",
      }));
      items.push(makeAssemblyItem({
        id: `hardware:m6-device-body:${sideLabel}:${index}`,
        name_zh: `M6 蓝色 L 型线缆护套 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
        name_en: "M6 right-angle blue cable guard proxy",
        kind: "外购光学器件占位",
        material: "用户指定 M6 SKU 6122579349941",
        group: "optical",
        shape: "cylinder",
        color: "#2764d7",
        shapeOptions: {
          radius: m6Geometry.deviceD / 2,
          axis: "z",
          rotation_x_deg: m6Geometry.sensorRollDeg,
          rotation_pivot: rotationPivotFor(bodyBaseMin, z),
        },
        base_min: bodyBaseMin,
        size: [m6Geometry.deviceD, m6Geometry.deviceD, m6Geometry.cableGuardLength],
        side,
        explosion: [side * 76, -106, 16],
        notes: "蓝色护套从头部沿局部 z- 出线；绕光束 x 轴 -45° 后朝 y-/z-，不与红色 x 向光束同轴。",
      }));
      items.push(makeAssemblyItem({
        id: `hardware:m6-device-cable:${sideLabel}:${index}`,
        name_zh: `M6 黑色尾线 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
        name_en: "M6 cable continuation proxy",
        kind: "外购光学器件占位",
        material: "用户指定 M6 SKU 6122579349941",
        group: "optical",
        shape: "cylinder",
        color: "#20252b",
        shapeOptions: {
          radius: m6Geometry.cableD / 2,
          axis: "z",
          rotation_x_deg: m6Geometry.sensorRollDeg,
          rotation_pivot: rotationPivotFor(cableBaseMin, z),
        },
        base_min: cableBaseMin,
        size: [m6Geometry.cableD, m6Geometry.cableD, m6Geometry.cablePreviewLength],
        side,
        explosion: [side * 80, -112, 14],
        notes: "黑色线缆沿蓝色护套继续向局部 z-；这里只画装配内的短代理，实际线缆将剥皮后汇入底盖套管。",
      }));
      items.push(makeAssemblyItem({
        id: `hardware:m6-rear-hex-seat:${sideLabel}:${index}`,
        name_zh: `x+ 后方水平浅六角沉孔 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
        name_en: "rear shallow horizontal hex anti-rotation pocket",
        kind: "主体加工特征",
        material: "PETG 首样主体；后续可换 6061-T6 CNC",
        group: "optical",
        shape: "hex",
        shapeOptions: {
          radius: m6Geometry.hexPocketAF / (2 * Math.cos(Math.PI / 6)),
          axis: "x",
          rotation_x_deg: m6Geometry.sensorRollDeg,
          rotation_pivot: rotationPivotFor(hexBaseMin, z),
        },
        base_min: hexBaseMin,
        size: [m6Geometry.hexPocketDepthX, m6Geometry.hexPocketAF, m6Geometry.hexPocketAF],
        side,
        explosion: [side * 92, -130, 16],
        notes: "2.1 mm x 向浅窝按真实 AF8 六角外形加工，只卡住水平外丝上的六角，不压住六角与外丝接驳平面；最终公差按到货件复核。",
      }));
      items.push(makeAssemblyItem({
        id: `hardware:m6-device-thread:${sideLabel}:${index}`,
        name_zh: `M6×0.75 水平外丝 +${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
        name_en: "M6 x 0.75 horizontal threaded barrel",
        kind: "外购光学器件占位",
        material: "304 不锈钢 / 用户指定 M6 SKU 6122579349941",
        group: "optical",
        color: "#b9c0c5",
        shape: "cylinder",
        shapeOptions: {
          radius: m6Geometry.deviceD / 2,
          axis: "x",
          rotation_x_deg: m6Geometry.sensorRollDeg,
          rotation_pivot: rotationPivotFor(threadBaseMin, z),
        },
        base_min: threadBaseMin,
        size: [m6Geometry.stemLength, m6Geometry.deviceD, m6Geometry.deviceD],
        side,
        explosion: [side * 72, -120, 18],
        notes: "这是中空 M6×0.75 光学外丝筒，不是实心安装螺丝；右侧从 x+ 外侧进入后筒端朝 x-，左侧镜像后筒端朝 x+。",
      }));
      const nutBaseMin = [
        nutMinX,
        -m6Geometry.hexPocketAF / 2,
        z - m6Geometry.hexPocketAF / 2,
      ];
      items.push(makeAssemblyItem({
        id: `hardware:m6-device-nut:${sideLabel}:${index}`,
        name_zh: `M6 外螺帽（主体平滑面单枚）+${10 + index * m6Geometry.sensorPitch} mm（${sideName}）`,
        name_en: "M6 supplied lock nut, minimum one",
        kind: "外购紧固件占位",
        material: "不锈钢/随传感器附带",
        group: "hardware",
        color: "#d0a72b",
        shape: "hex",
        shapeOptions: {
          radius: 5,
          axis: "x",
          rotation_x_deg: m6Geometry.sensorRollDeg,
          rotation_pivot: rotationPivotFor(nutBaseMin, z),
        },
        base_min: nutBaseMin,
        size: [5, 10, 10],
        side,
        explosion: [side * 86, 112, 16],
        notes: "一枚原配螺帽位于主体平滑的另一侧表面，用来压紧中空外丝筒；螺帽不嵌入主体，不使用打印固定螺丝，也不再显示第二枚螺帽。",
      }));
    }
  }
  // calibration_gauge remains a separately printable calibration tool in the
  // manifest, but it is deliberately absent from the installed assembly. It
  // was the tall red/pink proxy that made the current web preview look as if an
  // extra component had been mounted beside the clamp.

  for (const entry of entries) {
    const group = assemblyGroupKey(entry);
    const side = sideSign(entry);
    const bounds = boundsFromEntry(entry);
    if (!bounds) continue;
    if (entry.part === "stg120_outer_carrier") {
      const headMinX = side > 0
        ? bounds.min[0] + 3
        : bounds.max[0] - stgHead.thickness - 3;
      const outerFaceX = side > 0 ? headMinX : headMinX + stgHead.thickness;
      const segmentMinX = side > 0 ? 0 : outerFaceX;
      const segmentMaxX = side > 0 ? outerFaceX : 0;
      items.push(makeAssemblyItem({
        id: `hardware:stg120-head:outer:${entry.file}`,
        name_zh: `STG-120ML 光纤头（${side < 0 ? "左外侧" : "右外侧"}）`,
        name_en: "STG-120ML opposed fiber head",
        kind: "外购光学器件占位",
        material: "金属光纤头",
        group: "optical",
        shape: "stg120-head",
        shapeOptions: { face_direction: side > 0 ? -1 : 1 },
        base_min: [headMinX, -stgHead.width / 2, stgHead.bottomZ],
        size: [stgHead.thickness, stgHead.width, stgHead.length],
        side,
        explosion: explosionVector("optical", side),
        notes: "历史 STG-120ML 金属光纤头兼容占位；不属于当前 M6 采购主线，只保留用于旧 manifest 回溯。",
      }));
      items.push(makeAssemblyItem({
        id: `hardware:stg120-window:${entry.file}`,
        name_zh: `STG-120ML ${side < 0 ? "左" : "右"}段检测窗口（32 点 × 3.87 mm）`,
        name_en: "STG-120ML detection segment proxy",
        kind: "光路占位",
        material: "光学占位",
        group: "optical",
        shape: "stg120-beam-window",
        shapeOptions: { count: stgHead.count, pitch: stgHead.pitch },
        base_min: [segmentMinX, -0.4, stgHead.bottomZ + 5],
        size: [Math.abs(segmentMaxX - segmentMinX), 0.8, stgHead.activeLength],
        side,
        explosion: explosionVector("optical", side),
        notes: "历史 STG-120ML 两段光路兼容占位；不作为当前 M6 逐通道输出或精度证据。",
      }));
    }
    if (entry.part === "stg120_center_bridge") {
      const centerHeads = [
        { minX: bounds.min[0] + 4, face: 1, label: "右段中央" },
        { minX: bounds.max[0] - 10, face: -1, label: "左段中央" },
      ];
      centerHeads.forEach((head, index) => {
        items.push(makeAssemblyItem({
          id: `hardware:stg120-head:center:${index}`,
          name_zh: `STG-120ML 光纤头（${head.label}）`,
          name_en: "STG-120ML center fiber head",
          kind: "外购光学器件占位",
          material: "金属光纤头",
          group: "optical",
          shape: "stg120-head",
          shapeOptions: { face_direction: head.face },
          base_min: [head.minX, -stgHead.width / 2, stgHead.bottomZ],
          size: [stgHead.thickness, stgHead.width, stgHead.length],
          side: 0,
          explosion: explosionVector("optical", 0),
          notes: "历史中央桥背靠背 STG-120ML 兼容占位；当前 M6 主线不使用。",
        }));
      });
    }
    if (entry.part === "optical_module_carrier") {
      const center = bounds.min.map((value, index) => value + bounds.size[index] / 2);
      items.push(makeAssemblyItem({
        id: `hardware:optical-module:${entry.file}`,
        name_zh: `调制红外光学模块 ${entry.name_zh?.match(/\+\d+ mm/)?.[0] || "占位"}（${side < 0 ? "左" : "右"}）`,
        name_en: "modulated IR emitter / receiver module proxy",
        kind: "光学器件占位",
        material: "外购模块",
        group: "optical",
        shape: "optical-module",
        base_min: [center[0] - 6, -9, center[2] - 3],
        size: [12, 18, 6],
        side,
        explosion: explosionVector("optical", side),
        notes: "旧版离散红外发射/接收模块兼容占位；当前主线使用 M6 直角对射器件。",
      }));
    }
    if (entry.part === "sensor_mount_body") {
      const centerX = bounds.min[0] + bounds.size[0] / 2;
      items.push(makeAssemblyItem({
        id: `hardware:pvdf:${entry.file}`,
        name_zh: `PVDF 压电薄膜（${side < 0 ? "左" : "右"}）`,
        name_en: "PVDF piezo film proxy",
        kind: "传感器占位",
        material: "外购 PVDF",
        group: "sensor",
        shape: "box",
        base_min: [centerX - 18, -31, bounds.min[2]],
        size: [36, 2, 3],
        side,
        explosion: explosionVector("sensor", side),
        notes: "薄膜夹在网顶白边的可拆座中；这里只显示动态振动传感器的安装位置。",
      }));
    }
  }

  for (const sideLabel of ["left", "right"]) {
    const side = sideLabel === "left" ? -1 : 1;
    const knob = firstEntry(entries, (entry) => entry.part === "clamp_knob" && entry.side === sideLabel);
    const pressurePad = firstEntry(entries, (entry) => entry.part === "clamp_pressure_pad" && entry.side === sideLabel);
    const knobBounds = boundsFromEntry(knob);
    const padBounds = boundsFromEntry(pressurePad);
    if (!knobBounds || !padBounds) continue;
    const centerX = knobBounds.min[0] + knobBounds.size[0] / 2;
    const rodMinZ = knobBounds.min[2] + 4.4;
    const rodHeight = Math.max(12, padBounds.min[2] - rodMinZ);
    items.push(makeAssemblyItem({
      id: `hardware:m8-rod:${sideLabel}`,
      name_zh: `M8×1.25 金属螺杆（${sideLabel === "left" ? "左" : "右"}）`,
      name_en: "M8 × 1.25 metal threaded rod",
      kind: "外购标准件",
      material: "金属",
      group: "hardware",
      shape: "cylinder",
      shapeOptions: { radius: 4, axis: "z" },
      base_min: [centerX - 4, -4, rodMinZ],
      size: [8, 8, rodHeight],
      side,
      explosion: explosionVector("hardware", side),
      notes: "真实 M8×1.25 螺杆，不打印螺纹；圆头顶住独立台底压块。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m8-body-nut:${sideLabel}`,
      name_zh: `M8 六角螺母（下臂固定，${sideLabel === "left" ? "左" : "右"}）`,
      name_en: "M8 fixed nut",
      kind: "外购标准件",
      material: "金属",
      group: "hardware",
      shape: "hex",
      shapeOptions: { radius: 7, axis: "z" },
      base_min: [centerX - 6.5, -6.5, padBounds.min[2] - 19],
      size: [13, 13, 6.5],
      side,
      explosion: explosionVector("hardware", side),
      notes: "固定在下臂捕获窝中的螺母，形成唯一固定螺纹。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m8-jam-nuts:${sideLabel}`,
      name_zh: `M8 对锁螺母组（旋钮内，${sideLabel === "left" ? "左" : "右"}）`,
      name_en: "M8 jam-nut pair",
      kind: "外购标准件",
      material: "金属",
      group: "hardware",
      shape: "hex-stack",
      shapeOptions: { radius: 7, axis: "z" },
      base_min: [centerX - 6.5, -6.5, knobBounds.max[2] - 13],
      size: [13, 13, 13.4],
      side,
      explosion: explosionVector("hardware", side),
      notes: "两枚标准 M8 螺母预先对锁后装入打印旋钮，不使用 PETG 内螺纹。",
    }));
  }

  const carriageEntries = entries.filter((entry) => entry.part === "reference_carriage_body");
  for (const entry of carriageEntries) {
    const bounds = boundsFromEntry(entry);
    if (!bounds) continue;
    const side = sideSign(entry);
    const center = bounds.min.map((value, index) => value + bounds.size[index] / 2);
    items.push(makeAssemblyItem({
      id: `hardware:reference-pin:${entry.file}`,
      name_zh: `Ø3 弹簧定位销（${side < 0 ? "左" : "右"}）`,
      name_en: "spring locating pin",
      kind: "外购标准件",
      material: "金属",
      group: "reference",
      shape: "cylinder",
      shapeOptions: { radius: 1.5, axis: "y" },
      base_min: [center[0] - 1.5, center[1] - 15, center[2] - 1.5],
      size: [3, 30, 3],
      side,
      explosion: explosionVector("reference", side),
      notes: "仅保留为历史参考 carriage 的兼容诊断对象；当前 M6 结构不使用这套旧版定位销。",
    }));
  }
  return items;
}

function buildAssemblyItems() {
  const sourceEntries = sourcePrintableEntries();
  const assemblyDatums = deriveAssemblyDatums(sourceEntries);
  state.assembly.datums = assemblyDatums;
  const printable = sourceEntries
    .filter((entry) => entry.part !== "calibration_gauge")
    .map((entry) => makePrintableAssemblyItem(entry, assemblyDatums))
    .filter(Boolean);
  return printable.concat(makeProxyAssemblyItems(sourceEntries, assemblyDatums));
}

function assemblyItemById(id) {
  return state.assembly.items.find((item) => item.id === id) || null;
}

function isM6FocusItem(item) {
  if (!item || item.side !== 1) return false;
  const key = `${item.id || ""} ${item.name_zh || ""}`.toLowerCase();
  return key.includes("m6");
}

function isSkpCandidateItem(item) {
  return Boolean(item?.candidate && item.group === "skp_candidate");
}

function setM6FocusVisuals(focus) {
  const { THREE, scene } = state.three;
  if (!THREE || !scene) return;
  const datums = state.assembly.datums || deriveAssemblyDatums(sourcePrintableEntries());
  if (!state.three.m6AxesHelper) {
    const helper = new THREE.AxesHelper(34);
    // Local origin: center of the right M6 body. Positive x is the beam
    // direction, positive y is toward the table/front, and positive z is up.
    helper.position.set(
      datums.installedBodyCenterX,
      0,
      datums.installedBodyCenterZ,
    );
    helper.traverse((child) => {
      if (!child.material) return;
      child.material.depthTest = false;
      child.material.depthWrite = false;
    });
    scene.add(helper);
    state.three.m6AxesHelper = helper;
  }
  if (state.three.grid) state.three.grid.visible = !focus;
  if (state.three.globalAxes) state.three.globalAxes.visible = !focus;
  state.three.m6AxesHelper.visible = focus;
}

function assemblyVisible(item) {
  if (item.context && !state.assembly.showTable) return false;
  if (item.nonPrinted && !item.context && !state.assembly.showNonPrinted) return false;
  if (item.candidate && !state.assembly.showSkpCandidate) return false;
  if (item.fitCandidate && !state.assembly.showSkpFit) return false;
  if (item.sourceEntry?.part === "clamp_body_segment" && state.assembly.showSkpFit) return false;
  if (state.assembly.focusM6 && !isM6FocusItem(item)) return false;
  if (state.assembly.focusSkpCandidate && !(isSkpCandidateItem(item) && item.side === 1)) return false;
  return true;
}

function assemblyStageLabel(stage) {
  if (stage <= 0) return "背景";
  return ASSEMBLY_STEPS.find((step) => step.number === stage)?.label || `步骤 ${stage}`;
}

function generatedLayoutFromManifest(manifest) {
  return {
    schema_version: manifest.schema_version,
    generated: true,
    print_bed: { ...manifest.print_bed },
    plates: (manifest.plates || []).map((plate) => {
      const parts = (plate.parts || []).map((entry) => ({
        ...entry,
        material_group: entry.material_group || materialGroup(entry),
      }));
      return {
        ...plate,
        material_group: plate.material_group || materialGroup(parts[0]),
        parts,
      };
    }),
    oversized: (manifest.oversized || []).map((entry) => ({
      ...entry,
      material_group: entry.material_group || materialGroup(entry),
    })),
    parts: (manifest.parts || []).map((entry) => ({
      ...entry,
      material_group: entry.material_group || materialGroup(entry),
    })),
    material_groups: [...(manifest.material_groups || [])],
    assembly_components: (manifest.assembly_components || []).map((entry) => ({ ...entry })),
  };
}

function currentPlate() {
  return state.layout?.plates?.[state.activePlateIndex] || null;
}

function setBedInputs(bed) {
  refs.bedWidth.value = formatNumber(bed.width_mm);
  refs.bedDepth.value = formatNumber(bed.depth_mm);
  refs.bedHeight.value = formatNumber(bed.height_mm);
  refs.edgeMargin.value = formatNumber(bed.edge_margin_mm);
  refs.partGap.value = formatNumber(bed.part_gap_mm || 5);
  refs.gapOutput.value = formatNumber(bed.part_gap_mm || 5);
  const matchingPreset = Object.entries(PRESETS).find(([, preset]) => (
    preset.width_mm === number(bed.width_mm)
    && preset.depth_mm === number(bed.depth_mm)
    && preset.height_mm === number(bed.height_mm)
    && preset.edge_margin_mm === number(bed.edge_margin_mm)
  ));
  refs.bedPreset.value = matchingPreset ? matchingPreset[0] : "custom";
}

function readBed() {
  return {
    width_mm: number(refs.bedWidth.value),
    depth_mm: number(refs.bedDepth.value),
    height_mm: number(refs.bedHeight.value),
    edge_margin_mm: number(refs.edgeMargin.value),
    part_gap_mm: number(refs.partGap.value, 5),
  };
}

function dimensionsForAngle(size, angle) {
  return angle === 90 ? [size[1], size[0], size[2]] : [...size];
}

function matrixMultiply(left, right) {
  return [0, 1, 2].map((row) => [0, 1, 2].map((column) => (
    left[row][0] * right[0][column]
    + left[row][1] * right[1][column]
    + left[row][2] * right[2][column]
  )));
}

function rotationMatrixXYZ([rxDeg, ryDeg, rzDeg]) {
  const rx = rxDeg * Math.PI / 180;
  const ry = ryDeg * Math.PI / 180;
  const rz = rzDeg * Math.PI / 180;
  const cx = Math.cos(rx);
  const sx = Math.sin(rx);
  const cy = Math.cos(ry);
  const sy = Math.sin(ry);
  const cz = Math.cos(rz);
  const sz = Math.sin(rz);
  const rotateX = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]];
  const rotateY = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]];
  const rotateZ = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]];
  return matrixMultiply(rotateZ, matrixMultiply(rotateY, rotateX));
}

function rotatePoint(matrix, point) {
  return [0, 1, 2].map((row) => (
    matrix[row][0] * point[0]
    + matrix[row][1] * point[1]
    + matrix[row][2] * point[2]
  ));
}

function rotatedBoundsForMatrix(entry, matrix) {
  const bounds = boundsFromEntry(entry);
  if (!bounds) return null;
  const points = [];
  [bounds.min[0], bounds.max[0]].forEach((x) => {
    [bounds.min[1], bounds.max[1]].forEach((y) => {
      [bounds.min[2], bounds.max[2]].forEach((z) => points.push(rotatePoint(matrix, [x, y, z])));
    });
  });
  const min = [0, 1, 2].map((axis) => Math.min(...points.map((point) => point[axis])));
  const max = [0, 1, 2].map((axis) => Math.max(...points.map((point) => point[axis])));
  return { min, max, size: max.map((value, axis) => value - min[axis]) };
}

function printOrientations(entry) {
  // Keep the browser result identical to build_print_platter.py.  The active
  // The upright/carrier is one whole active post part; its first-article
  // contract is the tested rigid diagonal pose, so do not offer upright
  // candidates that look geometrically possible but are not the locked print
  // orientation.
  const rotations = entry?.part === "post_clamp_carrier"
    ? [{ label: "diagonal-rx0-ry51-rz45", euler: [0, 51, 45] }]
    : [
        { label: "z0", euler: [0, 0, 0] },
        { label: "z90", euler: [0, 0, 90] },
      ];
  return rotations.map((rotation, rank) => {
    const matrix = rotationMatrixXYZ(rotation.euler);
    const bounds = rotatedBoundsForMatrix(entry, matrix);
    return { ...rotation, rank, matrix, bounds, size: bounds?.size || sourceSize(entry) };
  });
}

function packPreview() {
  const bed = readBed();
  if (bed.width_mm <= 0 || bed.depth_mm <= 0 || bed.height_mm <= 0 || bed.part_gap_mm <= 0 || bed.edge_margin_mm < 0 || bed.width_mm <= bed.edge_margin_mm * 2 || bed.depth_mm <= bed.edge_margin_mm * 2) {
    showError("打印床尺寸、边缘余量和零件间距必须是有效的正数；可打印区域必须大于零。");
    return;
  }

  const groupedParts = new Map();
  for (const entry of state.manifest.parts || []) {
    const group = materialGroup(entry);
    if (!groupedParts.has(group)) groupedParts.set(group, []);
    groupedParts.get(group).push({ ...entry, material_group: group });
  }
  const materialGroups = [...groupedParts.keys()].sort((left, right) => (
    (left === "PETG" ? 0 : 1) - (right === "PETG" ? 0 : 1) || left.localeCompare(right)
  ));

  const plates = [];
  const rowsByPlate = [];
  const oversized = [];
  const startPlate = (group) => {
    const nextNumber = plates.length + 1;
    plates.push({
      id: `plate-${String(nextNumber).padStart(2, "0")}`,
      label: `浏览器预览 · ${group} 拼盘 ${String(nextNumber).padStart(2, "0")}`,
      material_group: group,
      description: "按当前参数在浏览器中排版；不同材料不混盘，不会生成或覆盖 STL 文件。",
      part_count: 0,
      parts: [],
    });
    rowsByPlate.push([]);
  };
  for (const group of materialGroups) {
    startPlate(group);
    const ordered = groupedParts.get(group).sort((left, right) => {
      const leftSize = sourceSize(left);
      const rightSize = sourceSize(right);
      const leftMax = Math.max(leftSize[0], leftSize[1]);
      const rightMax = Math.max(rightSize[0], rightSize[1]);
      return rightMax - leftMax || (rightSize[0] * rightSize[1] - leftSize[0] * leftSize[1]) || String(left.file).localeCompare(String(right.file));
    });

    for (const entry of ordered) {
      const size = sourceSize(entry);
      const candidates = printOrientations(entry)
        .filter(({ size: candidate }) => (
          candidate[0] <= bed.width_mm - bed.edge_margin_mm * 2 + 1e-6
          && candidate[1] <= bed.depth_mm - bed.edge_margin_mm * 2 + 1e-6
          && candidate[2] <= bed.height_mm + 1e-6
        ));
      if (!candidates.length) {
        oversized.push({
          ...entry,
          status: "oversized",
          material_group: group,
          source_size_mm: size,
          reason: "XY 或 Z 尺寸超过当前打印床（预览未缩放、未裁切）",
        });
        continue;
      }

      let placed = false;
      while (!placed) {
        const plate = plates[plates.length - 1];
        const rows = rowsByPlate[rowsByPlate.length - 1];
        const row = rows[rows.length - 1] || null;
        let best = null;
        if (row) {
          for (const candidate of candidates) {
            const [width, depth] = candidate.size;
            const x = row.x;
            const y = row.y;
            if (x + width > bed.width_mm - bed.edge_margin_mm + 1e-6 || y + depth > bed.depth_mm - bed.edge_margin_mm + 1e-6) continue;
            const score = [Math.max(row.height, depth), candidate.rank, width, x, y];
            if (!best || score.some((value, index) => value < best.score[index] && score.slice(0, index).every((before, beforeIndex) => before === best.score[beforeIndex]))) {
              best = { ...candidate, x, y, score };
            }
          }
        }
        if (!best) {
          const rowY = row ? row.y + row.height + bed.part_gap_mm : bed.edge_margin_mm;
          for (const candidate of candidates) {
            const [width, depth] = candidate.size;
            const x = bed.edge_margin_mm;
            const y = rowY;
            if (y + depth > bed.depth_mm - bed.edge_margin_mm + 1e-6) continue;
            const score = [depth, candidate.rank, width, x, y];
            if (!best || score.some((value, index) => value < best.score[index] && score.slice(0, index).every((before, beforeIndex) => before === best.score[beforeIndex]))) {
              best = { ...candidate, x, y, score };
            }
          }
          if (best) {
            rows.push({ x: best.x + best.size[0] + bed.part_gap_mm, y: best.y, height: best.size[1] });
          } else {
            startPlate(group);
            continue;
          }
        } else {
          row.x = best.x + best.size[0] + bed.part_gap_mm;
          row.height = Math.max(row.height, best.size[1]);
        }

        const placedBounds = [
          [best.x, best.y, 0],
          [best.x + best.size[0], best.y + best.size[1], best.size[2]],
        ];
        plate.parts.push({
          ...entry,
          status: "placed",
          material_group: group,
          plate_id: plate.id,
          orientation_label: best.label,
          rotation_euler_deg: best.euler,
          rotation_matrix: best.matrix,
          rotation_z_deg: best.euler[0] === 0 && best.euler[1] === 0 ? best.euler[2] : null,
          x_mm: best.x,
          y_mm: best.y,
          source_size_mm: size,
          placed_bounds: placedBounds,
        });
        plate.part_count = plate.parts.length;
        placed = true;
      }
    }

    if (plates.length && !plates[plates.length - 1].parts.length) {
      plates.pop();
      rowsByPlate.pop();
    }
  }

  const usablePlates = plates.filter((plate) => plate.parts.length);
  state.layout = {
    schema_version: "0.1",
    generated: false,
    print_bed: bed,
    plates: usablePlates,
    oversized,
    parts: usablePlates.flatMap((plate) => plate.parts).concat(oversized),
    material_groups: materialGroups,
    assembly_components: (state.manifest.assembly_components || []).map((entry) => ({ ...entry })),
  };
  state.generated = false;
  state.activePlateIndex = 0;
  state.selectedFile = null;
  state.hoveredFile = null;
  state.modelMode = "plate";
  clearError();
  render();
  loadModel();
}

function render() {
  if (!state.layout) return;
  const plates = state.layout.plates || [];
  const placedCount = plates.reduce((total, plate) => total + (plate.parts || []).length, 0);
  refs.plateCount.textContent = String(plates.length);
  refs.placedCount.textContent = String(placedCount);
  refs.oversizedCount.textContent = String((state.layout.oversized || []).length);
  refs.oversizedBadge.textContent = `${(state.layout.oversized || []).length} 件`;
  if (refs.oversizeNoteTitle) refs.oversizeNoteTitle.textContent = `当前有 ${(state.layout.oversized || []).length} 件需要处理`;
  if (refs.oversizeNoteText) refs.oversizeNoteText.textContent = (state.layout.oversized || []).length
    ? "有零件超出当前打印床，页面会保留它们，等待换大床或再次拆分。"
    : "当前打印床可以容纳源清单中的全部零件。仍需在切片器中复核方向、支撑和首层。";

  if (state.activePlateIndex >= plates.length) state.activePlateIndex = Math.max(0, plates.length - 1);
  renderTabs();
  const plate = currentPlate();
  const bed = state.layout.print_bed;
  refs.layoutTitle.textContent = plate ? `${plate.label} · ${formatNumber(bed.width_mm)} × ${formatNumber(bed.depth_mm)} mm` : "没有零件适合当前打印床";
  refs.layoutBadge.textContent = state.generated ? "已生成 STL" : "仅浏览器预览";
  refs.layoutBadge.classList.toggle("preview-badge", !state.generated);
  updateDownloadLink();
  drawBed();
  renderLegend();
  renderPartList();
  renderOversized();
  renderComponents();
  renderMode();
  renderAssemblyGuide();
}

function renderMode() {
  const designMode = state.uiMode === "assembly" || state.uiMode === "exploded";
  const printMode = state.uiMode === "print";
  const partsMode = state.uiMode === "parts";
  document.body.dataset.viewMode = state.uiMode;

  refs.modeTabs?.querySelectorAll("[data-view-mode]").forEach((button) => {
    button.setAttribute("aria-selected", String(button.dataset.viewMode === state.uiMode));
  });
  document.querySelectorAll("[data-print-only]").forEach((element) => {
    element.hidden = !printMode;
  });
  if (refs.assemblyControlCard) refs.assemblyControlCard.hidden = !designMode;
  if (refs.layoutCard) refs.layoutCard.hidden = designMode || partsMode;
  if (refs.visualGrid) refs.visualGrid.hidden = partsMode;
  if (refs.modelCard) {
    refs.modelCard.hidden = partsMode;
    refs.modelCard.classList.toggle("design-model", designMode);
  }
  if (refs.detailGrid) refs.detailGrid.hidden = designMode;
  if (refs.componentCard) refs.componentCard.hidden = false;
  if (refs.assemblyGuideCard) refs.assemblyGuideCard.hidden = !designMode;
  if (refs.assemblyToolbar) refs.assemblyToolbar.hidden = !designMode;
  if (refs.showPlateModel) refs.showPlateModel.hidden = designMode;
  if (refs.showPartModel) refs.showPartModel.hidden = designMode;

  if (designMode) {
    refs.modelKicker.textContent = state.uiMode === "exploded" ? "三维爆炸检查" : "三维装配检查";
    refs.modelTitle.textContent = state.uiMode === "exploded" ? "网架爆炸预览" : "网架完整装配";
    refs.modelCaption.textContent = state.uiMode === "exploded"
      ? "爆炸距离只沿真实 x 向滑入方向改变显示位置；立柱保持原 z 坐标，爆炸归零时其底端与固定 C 夹最高承托面 z=16 mm 共面，不进入 C 形座。网布/卡夹功能区到 z=168.5 mm；固定网柱顶面按当前装配基准为 z=260.5 mm，球头下端 M8 与顶面中心孔同轴；从承托面起 30 mm 为 35×58→28×38 mm 的一体实心渐变，之后保持 28×38 mm；打印件仍按源 STL 的真实装配坐标加载，紫色半透明件为非打印占位。"
      : "主体与壳体总成预览；坐标约定为 x=光束左右、y=前后、z=竖直。球台、无网顶轨道的真实网布、PVDF、M6 45° L 型主体、x 向分体壳、后盖 boss、竖直采购球头和电子腔体按装配包络显示；完整装配态把每个打印件和外购件都放在同一套安装基准，爆炸偏移只在爆炸标签启用。完整灰色 C 形主体与整根橙色固定网柱分开打印；立柱从黄灰交界 z=16 mm 起一体延伸到 z=260.5 mm，顶面中心开 M8 攻丝底孔，M6 球头下端 M8 直接进入固定网柱顶面中心孔，球头轴心与后盖 boss 共线；网布/卡夹仍只在 z=16…168.5 mm 的通道内工作，从承托面起 30 mm 做 35×58→28×38 mm 的一体实心渐变。网布先穿过立柱 3 mm 过道，再从外侧开口装入全高 U 形卡网夹；盖板、boss、按钮/指示和线缆路径按当前机械包络检查；取消旧版横向承托臂，不再显示旧版独立上段外件和旧版独立连接器。";
    refs.assemblyStatusBadge.textContent = `${state.assembly.items.filter(assemblyVisible).length} 个装配对象 · mm`;
    refs.explodeOutput.textContent = `${Math.round(state.assembly.explode * 100)}`;
    refs.explodeRange.value = String(Math.round(state.assembly.explode * 100));
    refs.assemblyStepOutput.textContent = state.assembly.step >= ASSEMBLY_STEPS.length
      ? "完整"
      : `步骤 ${state.assembly.step}`;
    refs.assemblyStep.value = String(state.assembly.step);
  } else if (printMode) {
    refs.modelKicker.textContent = "STL 几何检查";
    refs.modelTitle.textContent = state.modelMode === "part" && state.selectedFile
      ? partName(findPart(state.selectedFile))
      : (currentPlate()?.label || "等待选择模型");
    refs.modelCaption.textContent = state.generated
      ? "当前显示脚本生成的拼盘 STL；源零件仍保持独立尺寸。"
      : "当前布局由浏览器按源 STL 计算，仅供核对；如需拼盘 STL，请重新运行拼盘脚本。";
  } else {
    refs.modelKicker.textContent = "零件检视";
    refs.modelTitle.textContent = "从清单选择一个打印件查看几何";
    refs.modelCaption.textContent = "零件清单保留中文名称、材料组、尺寸和 STL 下载入口。点击条目会切换到打印检查。";
  }
}

function renderAssemblyGuide() {
  if (!refs.assemblyStepList || !refs.assemblySelectionPanel) return;
  refs.assemblyStepList.textContent = "";
  ASSEMBLY_STEPS.forEach((step) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "assembly-step-row";
    button.classList.toggle("active", state.assembly.step === step.number);
    button.dataset.step = String(step.number);
    const numberBadge = document.createElement("span");
    numberBadge.className = "assembly-step-number";
    numberBadge.textContent = String(step.number).padStart(2, "0");
    const copy = document.createElement("span");
    copy.className = "assembly-step-copy";
    const title = document.createElement("strong");
    title.textContent = step.label;
    const description = document.createElement("small");
    description.textContent = step.description;
    copy.append(title, description);
    button.append(numberBadge, copy);
    button.addEventListener("click", () => {
      state.assembly.step = step.number;
      refs.assemblyStep.value = String(step.number);
      updateAssemblyScene();
      render();
    });
    refs.assemblyStepList.append(button);
  });

  const selected = assemblyItemById(state.assembly.selectedId || state.assembly.hoveredId);
  refs.assemblySelectionPanel.textContent = "";
  if (!selected) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "点击三维零件或左侧步骤查看对应的中文名称、材料和装配说明。";
    refs.assemblySelectionPanel.append(empty);
    refs.assemblySelectionBadge.textContent = "悬停或点击三维零件查看中文名称";
    return;
  }
  const heading = document.createElement("div");
  heading.className = "selection-heading";
  const swatch = document.createElement("i");
  swatch.className = "legend-swatch";
  swatch.style.background = selected.color;
  const title = document.createElement("strong");
  title.textContent = selected.name_zh;
  heading.append(swatch, title);
  const meta = document.createElement("div");
  meta.className = "selection-meta";
  meta.textContent = `${ASSEMBLY_GROUPS[selected.group]?.label || "装配件"} · ${selected.kind} · ${selected.material}`;
  const stage = document.createElement("div");
  stage.className = "selection-meta";
  stage.textContent = selected.context ? "仅作球台背景显示" : `装配步骤 ${selected.stage} · ${assemblyStageLabel(selected.stage)}`;
  const notes = document.createElement("p");
  notes.className = "selection-notes";
  notes.textContent = selected.notes || "当前对象没有额外装配说明。";
  refs.assemblySelectionPanel.append(heading, meta, stage, notes);
  refs.assemblySelectionBadge.textContent = `${selected.name_zh} · ${selected.kind}`;
}

function renderTabs() {
  refs.plateTabs.textContent = "";
  if (!state.layout.plates?.length) {
    const empty = document.createElement("div");
    empty.className = "plate-empty";
    empty.textContent = "当前打印床没有可排版零件";
    refs.plateTabs.append(empty);
    return;
  }
  state.layout.plates.forEach((plate, index) => {
    const tab = document.createElement("button");
    tab.type = "button";
    tab.className = "plate-tab";
    tab.setAttribute("role", "tab");
    tab.setAttribute("aria-selected", String(index === state.activePlateIndex));
    const strong = document.createElement("strong");
    strong.textContent = String(index + 1).padStart(2, "0");
    const label = document.createElement("span");
    label.className = "plate-tab-label";
    const material = document.createElement("b");
    material.className = `plate-material ${materialClass(materialGroup(plate))}`;
    material.textContent = materialGroup(plate);
    const count = document.createElement("span");
    count.textContent = `${plate.parts.length} 件`;
    label.append(material, count);
    tab.append(strong, label);
    tab.addEventListener("click", () => {
      state.activePlateIndex = index;
      state.selectedFile = null;
      state.hoveredFile = null;
      state.modelMode = "plate";
      render();
      loadModel();
    });
    refs.plateTabs.append(tab);
  });
}

function findPart(file) {
  return (state.layout?.parts || []).find((entry) => entry.file === file)
    || (state.manifest?.parts || []).find((entry) => entry.file === file)
    || null;
}

function renderLegend() {
  refs.legend.textContent = "";
  Object.values(COLORS).forEach((item) => {
    const wrapper = document.createElement("span");
    wrapper.className = "legend-item";
    const swatch = document.createElement("i");
    swatch.className = "legend-swatch";
    swatch.style.background = item.color;
    const label = document.createElement("span");
    label.textContent = item.label;
    wrapper.append(swatch, label);
    refs.legend.append(wrapper);
  });
}

function renderPartList() {
  refs.partList.textContent = "";
  const plate = currentPlate();
  const query = refs.partFilter.value.trim().toLowerCase();
  const sourceEntries = state.uiMode === "parts"
    ? (state.manifest?.parts || state.layout?.parts || [])
    : (plate?.parts || []);
  const entries = sourceEntries.filter((entry) => partSearchText(entry).includes(query));
  if (refs.partsCardTitle) {
    refs.partsCardTitle.textContent = state.uiMode === "parts" ? "全部打印零件" : "当前拼盘包含的打印件";
  }
  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = sourceEntries.length ? "当前筛选没有匹配零件" : "没有可显示的排版零件";
    refs.partList.append(empty);
    return;
  }
  entries.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "part-row";
    row.dataset.file = entry.file;
    row.tabIndex = 0;
    row.setAttribute("role", "button");
    row.classList.toggle("selected", entry.file === state.selectedFile);
    const dot = document.createElement("i");
    dot.className = "part-dot";
    dot.style.background = category(entry).color;
    const info = document.createElement("div");
    const name = document.createElement("div");
    name.className = "part-name";
    name.textContent = partName(entry);
    const sub = document.createElement("div");
    sub.className = "part-sub";
    sub.textContent = `${entry.file || entry.part || "STL"}${entry.side ? ` · ${entry.side}` : ""}${entry.index !== null && entry.index !== undefined ? ` · #${entry.index}` : ""} · 材料组：${materialGroup(entry)}`;
    info.append(name, sub);
    const dim = document.createElement("span");
    dim.className = "part-dim";
    dim.textContent = formatSize(sourceSize(entry));
    const link = document.createElement("a");
    link.className = "part-download";
    link.href = sourcePathFor(entry);
    link.target = "_blank";
    link.rel = "noreferrer";
    link.download = entry.file || "part.stl";
    link.textContent = "STL ↗";
    link.addEventListener("click", (event) => event.stopPropagation());
    row.append(dot, info, dim, link);
    const select = () => selectPart(entry.file);
    row.addEventListener("click", select);
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select();
      }
    });
    refs.partList.append(row);
  });
}

function renderOversized() {
  refs.oversizedList.textContent = "";
  const entries = state.layout.oversized || [];
  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "当前打印床没有超尺寸件";
    refs.oversizedList.append(empty);
    return;
  }
  entries.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "oversized-row";
    const info = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = partName(entry);
    const reason = document.createElement("span");
    reason.textContent = `${materialGroup(entry)} · ${entry.reason || "需要更大打印床或再次拆分"}`;
    info.append(title, reason);
    const meta = document.createElement("div");
    const size = document.createElement("b");
    size.textContent = formatSize(sourceSize(entry));
    const link = document.createElement("a");
    link.className = "source-link";
    link.href = sourcePathFor(entry);
    link.target = "_blank";
    link.rel = "noreferrer";
    link.download = entry.file || "part.stl";
    link.textContent = "源 STL ↗";
    meta.append(size, link);
    row.append(info, meta);
    refs.oversizedList.append(row);
  });
}

function renderComponents() {
  if (!refs.componentList) return;
  refs.componentList.textContent = "";
  const entries = state.layout?.assembly_components || state.manifest?.assembly_components || [];
  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "当前 manifest 没有装配物料清单";
    refs.componentList.append(empty);
    return;
  }
  entries.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "component-row";
    const name = document.createElement("div");
    name.className = "component-name";
    const title = document.createElement("strong");
    title.textContent = entry.name_zh || entry.name_en || entry.id || "未命名元器件";
    const english = document.createElement("span");
    english.textContent = entry.name_en || entry.id || "";
    name.append(title, english);
    const kind = document.createElement("span");
    kind.className = "component-kind";
    kind.textContent = entry.kind || "装配件";
    const quantity = document.createElement("span");
    quantity.className = "component-quantity";
    quantity.textContent = entry.quantity || "—";
    const status = document.createElement("span");
    status.className = `component-status ${entry.printable ? "component-status-print" : "component-status-purchase"}`;
    status.textContent = entry.status || (entry.printable ? "打印件" : "非打印件");
    const notes = document.createElement("span");
    notes.className = "component-notes";
    notes.textContent = [entry.scad_part ? `SCAD: ${entry.scad_part}` : "", entry.notes || ""]
      .filter(Boolean)
      .join(" · ");
    row.append(name, kind, quantity, status, notes);
    refs.componentList.append(row);
  });
}

function selectPart(file) {
  const entry = findPart(file);
  if (!entry) return;
  const plateIndex = state.layout.plates.findIndex((plate) => plate.parts.some((part) => part.file === file));
  if (plateIndex >= 0) state.activePlateIndex = plateIndex;
  if (state.uiMode === "parts") state.uiMode = "print";
  state.selectedFile = file;
  state.hoveredFile = file;
  state.modelMode = "part";
  render();
  loadModel();
}

function drawBed() {
  const canvas = refs.bedCanvas;
  const rect = canvas.getBoundingClientRect();
  const width = Math.max(1, rect.width);
  const height = Math.max(1, rect.height);
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const pixelWidth = Math.floor(width * dpr);
  const pixelHeight = Math.floor(height * dpr);
  if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
    canvas.width = pixelWidth;
    canvas.height = pixelHeight;
  }
  const context = canvas.getContext("2d");
  context.setTransform(dpr, 0, 0, dpr, 0, 0);
  context.clearRect(0, 0, width, height);
  context.fillStyle = "#071319";
  context.fillRect(0, 0, width, height);

  const bed = state.layout?.print_bed || { width_mm: 256, depth_mm: 256, edge_margin_mm: 5 };
  const padding = 34;
  const scale = Math.min((width - padding * 2) / bed.width_mm, (height - padding * 2) / bed.depth_mm);
  const originX = (width - bed.width_mm * scale) / 2;
  const originY = (height - bed.depth_mm * scale) / 2;
  state.canvasTransform = { originX, originY, scale, width, height, bed };
  const mapX = (value) => originX + value * scale;
  const mapY = (value) => originY + (bed.depth_mm - value) * scale;

  context.fillStyle = "rgba(20, 43, 51, .82)";
  context.fillRect(originX, originY, bed.width_mm * scale, bed.depth_mm * scale);
  context.strokeStyle = "rgba(98, 228, 209, .44)";
  context.lineWidth = 1;
  context.strokeRect(originX + .5, originY + .5, bed.width_mm * scale - 1, bed.depth_mm * scale - 1);

  context.font = "10px Inter, sans-serif";
  context.fillStyle = "#6c8b92";
  context.textAlign = "center";
  for (let x = 0; x <= bed.width_mm; x += 50) {
    const px = mapX(x);
    context.strokeStyle = "rgba(148, 184, 198, .1)";
    context.beginPath();
    context.moveTo(px, originY);
    context.lineTo(px, originY + bed.depth_mm * scale);
    context.stroke();
    if (x < bed.width_mm) context.fillText(`${x}`, px + 2, originY + bed.depth_mm * scale + 17);
  }
  context.textAlign = "right";
  for (let y = 0; y <= bed.depth_mm; y += 50) {
    const py = mapY(y);
    context.strokeStyle = "rgba(148, 184, 198, .1)";
    context.beginPath();
    context.moveTo(originX, py);
    context.lineTo(originX + bed.width_mm * scale, py);
    context.stroke();
    if (y < bed.depth_mm) context.fillText(`${y}`, originX - 7, py - 3);
  }
  if (refs.showSafeArea.checked) {
    const margin = bed.edge_margin_mm;
    context.setLineDash([4, 4]);
    context.strokeStyle = "rgba(246, 189, 103, .55)";
    context.strokeRect(mapX(margin), mapY(bed.depth_mm - margin), (bed.width_mm - margin * 2) * scale, (bed.depth_mm - margin * 2) * scale);
    context.setLineDash([]);
  }

  const plate = currentPlate();
  (plate?.parts || []).forEach((entry) => {
    if (!Array.isArray(entry.placed_bounds)) return;
    const [lo, hi] = entry.placed_bounds;
    const partWidth = number(hi[0]) - number(lo[0]);
    const partDepth = number(hi[1]) - number(lo[1]);
    const x = mapX(number(lo[0]));
    const y = mapY(number(hi[1]));
    const w = partWidth * scale;
    const h = partDepth * scale;
    const itemColor = category(entry).color;
    const selected = entry.file === state.selectedFile;
    const hovered = entry.file === state.hoveredFile;
    context.fillStyle = `${itemColor}${selected ? "d8" : hovered ? "b0" : "70"}`;
    context.fillRect(x, y, w, h);
    context.strokeStyle = selected ? "#ffffff" : hovered ? "#ffffff" : itemColor;
    context.lineWidth = selected ? 2.5 : hovered ? 2 : 1;
    context.strokeRect(x + .5, y + .5, Math.max(1, w - 1), Math.max(1, h - 1));
    if (refs.showLabels.checked && w > 34 && h > 14) {
      context.save();
      context.beginPath();
      context.rect(x + 3, y + 2, Math.max(0, w - 6), Math.max(0, h - 4));
      context.clip();
      context.fillStyle = "#061115";
      context.font = "10px Inter, sans-serif";
      context.textAlign = "left";
      context.fillText(partName(entry), x + 5, y + 13);
      context.restore();
    }
  });
}

function canvasEntryAt(clientX, clientY) {
  if (!state.canvasTransform) return null;
  const { originX, originY, scale, bed } = state.canvasTransform;
  const rect = refs.bedCanvas.getBoundingClientRect();
  const x = (clientX - rect.left - originX) / scale;
  const y = bed.depth_mm - (clientY - rect.top - originY) / scale;
  const plate = currentPlate();
  return (plate?.parts || []).slice().reverse().find((entry) => {
    if (!Array.isArray(entry.placed_bounds)) return false;
    const [lo, hi] = entry.placed_bounds;
    return x >= number(lo[0]) && x <= number(hi[0]) && y >= number(lo[1]) && y <= number(hi[1]);
  }) || null;
}

function updateCanvasHoverLabel(entry, clientX = 0, clientY = 0) {
  const label = refs.canvasHoverLabel;
  if (!label) return;
  if (!entry) {
    label.hidden = true;
    return;
  }
  const rect = refs.bedCanvas.getBoundingClientRect();
  label.textContent = `${partName(entry)} · ${formatSize(sourceSize(entry))}`;
  label.hidden = false;
  const maxLeft = Math.max(8, rect.width - label.offsetWidth - 8);
  const maxTop = Math.max(8, rect.height - label.offsetHeight - 8);
  label.style.left = `${Math.min(maxLeft, Math.max(8, clientX - rect.left + 12))}px`;
  label.style.top = `${Math.min(maxTop, Math.max(8, clientY - rect.top + 12))}px`;
}

function updateDownloadLink() {
  const plate = currentPlate();
  const available = Boolean(state.uiMode === "print" && state.generated && plate?.path);
  refs.downloadPlate.hidden = !available;
  if (!available) {
    refs.downloadPlate.removeAttribute("href");
    return;
  }
  refs.downloadPlate.href = assetPath(plate.path);
  refs.downloadPlate.download = plate.file || `${plate.id}.stl`;
  refs.downloadPlate.textContent = `下载 ${plate.label} STL`;
}

function downloadLayout() {
  if (!state.layout) return;
  const snapshot = {
    ...state.layout,
    generated: state.generated,
    source_manifest: state.manifestUrl?.href || null,
    note: state.generated ? "来自脚本生成的实际拼盘布局。" : "浏览器内实时预览布局，尚未生成合并 STL。",
  };
  const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `smartgear-${state.generated ? "print-platter" : "preview-layout"}.json`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function setModelPlaceholder(title, detail = "") {
  refs.modelPlaceholder.hidden = false;
  const paragraph = refs.modelPlaceholder.querySelector("p");
  const small = refs.modelPlaceholder.querySelector("small");
  if (paragraph) paragraph.textContent = title;
  if (small) small.textContent = detail;
}

function clearThreeModel() {
  const root = state.three.modelRoot;
  if (!root) return;
  state.assembly.items.forEach((item) => { item.object = null; });
  while (root.children.length) {
    const object = root.children.pop();
    object.traverse((child) => {
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        const materials = Array.isArray(child.material) ? child.material : [child.material];
        materials.forEach((material) => material.dispose());
      }
    });
  }
  state.assembly.loaded = false;
}

function loadGeometry(url) {
  const Loader = state.three.STLLoader;
  const requestUrl = new URL(url, window.location.href);
  // STL filenames are stable across exports.  Key the browser request by the
  // current source manifest hash so the assembly view cannot keep an older
  // mesh after the printable geometry has been regenerated.
  const version = state.sourceManifest?.source_sha256 || state.manifest?.source_sha256;
  if (version) requestUrl.searchParams.set("v", String(version).slice(0, 16));
  return new Promise((resolve, reject) => {
    const loader = new Loader();
    loader.load(requestUrl.href, resolve, undefined, reject);
  });
}

function normalizedGeometry(THREE, geometry) {
  geometry.computeBoundingBox();
  const min = geometry.boundingBox.min;
  geometry.translate(-min.x, -min.y, -min.z);
  geometry.computeBoundingBox();
  geometry.computeVertexNormals();
  return geometry;
}

function addGeometryMesh(THREE, geometry, color, entry = null, center = false) {
  normalizedGeometry(THREE, geometry);
  const material = new THREE.MeshStandardMaterial({ color, roughness: 0.66, metalness: 0.04 });
  const mesh = new THREE.Mesh(geometry, material);
  const size = new THREE.Vector3();
  geometry.boundingBox.getSize(size);
  if (center) {
    mesh.position.set(-size.x / 2, -size.y / 2, 0);
  } else if (entry) {
    if (Array.isArray(entry.rotation_matrix) && entry.rotation_matrix.length === 3) {
      const matrixValues = entry.rotation_matrix.flat().map((value) => number(value));
      const placementMatrix = new THREE.Matrix4().set(...matrixValues, 0, 0, 0, 1);
      geometry.applyMatrix4(placementMatrix);
      geometry.computeBoundingBox();
      const rotatedMin = geometry.boundingBox.min;
      geometry.translate(-rotatedMin.x, -rotatedMin.y, -rotatedMin.z);
      geometry.computeBoundingBox();
      mesh.position.set(number(entry.x_mm), number(entry.y_mm), 0);
    } else {
      const angle = number(entry.rotation_z_deg);
      mesh.rotation.z = angle * Math.PI / 180;
      mesh.position.set(angle === 90 ? number(entry.x_mm) + size.y : number(entry.x_mm), number(entry.y_mm), 0);
    }
  }
  state.three.modelRoot.add(mesh);
  return mesh;
}

function fitThreeCamera(filter = null) {
  const { THREE, camera, controls, modelRoot } = state.three;
  if (!THREE || !camera || !controls || !modelRoot || !modelRoot.children.length) return;
  const candidates = modelRoot.children.filter((object) => (
    object.visible && (!filter || filter(object.userData.assemblyItem))
  ));
  if (!candidates.length) return;
  const box = new THREE.Box3();
  candidates.forEach((object) => box.expandByObject(object));
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDimension = Math.max(size.x, size.y, size.z, 1);
  const distance = maxDimension * 1.9;
  camera.position.set(center.x + distance, center.y - distance, center.z + distance * 0.8);
  camera.near = Math.max(0.1, maxDimension / 1000);
  camera.far = Math.max(5000, maxDimension * 10);
  camera.updateProjectionMatrix();
  controls.target.copy(center);
  controls.update();
}

function fitM6OrientationCamera() {
  state.assembly.focusM6 = !state.assembly.focusM6;
  if (state.assembly.focusM6) {
    state.assembly.focusSkpCandidate = false;
    refs.fitSkp.textContent = "SKP 腿脚近景";
    refs.fitSkp.classList.remove("active");
  }
  if (state.assembly.focusM6) {
    state.assembly.showTable = false;
    refs.showTable.checked = false;
    refs.fitM6.textContent = "恢复完整装配";
    refs.fitM6.classList.add("active");
  } else {
    state.assembly.showTable = true;
    refs.showTable.checked = true;
    refs.fitM6.textContent = "M6 右侧近景";
    refs.fitM6.classList.remove("active");
  }
  setM6FocusVisuals(state.assembly.focusM6);
  updateAssemblyScene();
  render();
  fitThreeCamera(state.assembly.focusM6 ? isM6FocusItem : null);
  if (state.assembly.focusM6 && state.three.camera && state.three.controls) {
    // Use a rear elevation for the check: x reads left-to-right on screen,
    // z reads bottom-to-top, and the -45 degree roll remains visible in the
    // y-z plane instead of looking down the optical axis from +x.
    const target = state.three.controls.target.clone();
    const distance = state.three.camera.position.distanceTo(target) * 0.68;
    state.three.camera.position.set(
      target.x + distance * 0.32,
      target.y - distance,
      target.z + distance * 0.18,
    );
    state.three.controls.update();
  }
}

function fitSkpCandidateCamera() {
  const nextFocus = !state.assembly.focusSkpCandidate;
  if (nextFocus && state.assembly.focusM6) {
    state.assembly.focusM6 = false;
    setM6FocusVisuals(false);
    refs.fitM6.textContent = "M6 右侧近景";
    refs.fitM6.classList.remove("active");
  }
  state.assembly.focusSkpCandidate = nextFocus;
  if (nextFocus) {
    state.assembly.showSkpCandidate = true;
    refs.showSkpCandidate.checked = true;
    refs.fitSkp.textContent = "恢复完整装配";
    refs.fitSkp.classList.add("active");
  } else {
    refs.fitSkp.textContent = "SKP 腿脚近景";
    refs.fitSkp.classList.remove("active");
  }
  updateAssemblyScene();
  render();
  fitThreeCamera(nextFocus ? isSkpCandidateItem : null);
  if (nextFocus && state.three.camera && state.three.controls) {
    // The side elevation makes the candidate's x-direction 15 mm extension,
    // flat bottom and terminal chamfer readable before the user orbits it.
    const target = state.three.controls.target.clone();
    const distance = state.three.camera.position.distanceTo(target);
    state.three.camera.position.set(
      target.x + distance * 0.12,
      target.y - distance,
      target.z + distance * 0.18,
    );
    state.three.controls.update();
  }
}

function resizeThree() {
  const { renderer, camera } = state.three;
  if (!renderer || !camera) return;
  const width = Math.max(1, refs.modelHost.clientWidth);
  const height = Math.max(1, refs.modelHost.clientHeight);
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

function assemblyMaterial(THREE, item, options = {}) {
  const material = new THREE.MeshStandardMaterial({
    color: options.color || item.color,
    roughness: options.roughness ?? (item.group === "hardware" ? 0.32 : 0.66),
    metalness: options.metalness ?? (item.group === "hardware" ? 0.64 : 0.06),
    transparent: true,
    opacity: options.opacity ?? (item.context ? 0.28 : item.nonPrinted ? 0.72 : 1),
    depthWrite: options.depthWrite ?? !item.context,
  });
  material.userData.baseOpacity = material.opacity;
  material.userData.baseColor = material.color.clone();
  material.userData.assemblyId = item.id;
  return material;
}

function markAssemblyObject(object, item) {
  object.userData.assemblyId = item.id;
  object.userData.assemblyItem = item;
  object.traverse((child) => {
    child.userData.assemblyId = item.id;
    child.userData.assemblyItem = item;
  });
}

function addProxyPart(THREE, group, item, geometry, position, materialOptions = {}) {
  const mesh = new THREE.Mesh(geometry, assemblyMaterial(THREE, item, materialOptions));
  mesh.position.set(...position);
  group.add(mesh);
  return mesh;
}

function footprintPoints(kind, width, depth, options = {}) {
  const mirrorX = Boolean(options.mirror_x);
  const transform = ([x, y]) => [mirrorX ? width - x : x, y];
  if (kind === "front-arc") {
    const frontOffset = number(options.front_x_offset, 0);
    const frontLength = number(options.front_length_x, width);
    const frontEnd = frontOffset + frontLength;
    const centerY = depth / 2;
    const points = [[frontEnd, 0]];
    for (let angle = -90; angle <= 90; angle += 5) {
      const radians = angle * Math.PI / 180;
      points.push([
        frontEnd - frontLength * Math.cos(radians),
        centerY + centerY * Math.sin(radians),
      ]);
    }
    points.push([frontEnd, depth]);
    return points.map(transform);
  }

  if (kind === "rear-back-rounded-footprint") {
    const x0 = number(options.x0, 0);
    const x1 = number(options.x1, width);
    const y0 = number(options.y0, 0);
    const y1 = number(options.y1, depth);
    const radius = Math.min(
      number(options.radius, 2),
      Math.max(0.01, (x1 - x0) / 2 - 0.01),
      Math.max(0.01, (y1 - y0) / 2 - 0.01),
    );
    const points = [[x0, y0], [x1 - radius, y0]];
    const addArc = (cx, cy, start, end) => {
      for (let angle = start; angle <= end; angle += 10) {
        const radians = angle * Math.PI / 180;
        points.push([cx + radius * Math.cos(radians), cy + radius * Math.sin(radians)]);
      }
    };
    addArc(x1 - radius, y0 + radius, -90, 0);
    points.push([x1, y1 - radius]);
    addArc(x1 - radius, y1 - radius, 0, 90);
    points.push([x0, y1]);
    return points.map(transform);
  }

  if (kind === "rounded-footprint-tail-relief") {
    const radius = Math.min(
      number(options.radius, 2),
      Math.max(0.01, width / 2 - 0.01),
      Math.max(0.01, depth / 2 - 0.01),
    );
    const reliefX0 = number(options.relief_x0, 0);
    const reliefX1 = number(options.relief_x1, 0);
    const reliefDepth = Math.min(depth, number(options.relief_depth_y, 0));
    if (reliefX0 <= 0.01 && reliefX1 > reliefX0 && reliefDepth > 0) {
      const points = [
        [0, reliefDepth],
        [Math.min(width - radius, reliefX1), reliefDepth],
        [Math.min(width - radius, reliefX1), 0],
        [width - radius, 0],
      ];
      const addArc = (cx, cy, start, end) => {
        for (let angle = start; angle <= end; angle += 10) {
          const radians = angle * Math.PI / 180;
          points.push([cx + radius * Math.cos(radians), cy + radius * Math.sin(radians)]);
        }
      };
      addArc(width - radius, radius, -90, 0);
      points.push([width, depth - radius]);
      addArc(width - radius, depth - radius, 0, 90);
      points.push([radius, depth]);
      addArc(radius, depth - radius, 90, 180);
      points.push([0, Math.max(reliefDepth, radius)]);
      return points.map(transform);
    }
  }

  const x0 = number(options.x0, 0);
  const x1 = number(options.x1, width);
  const y0 = number(options.y0, 0);
  const y1 = number(options.y1, depth);
  const radius = Math.min(
    number(options.radius, 2),
    Math.max(0.01, (x1 - x0) / 2 - 0.01),
    Math.max(0.01, (y1 - y0) / 2 - 0.01),
  );
  const points = [];
  const addArc = (cx, cy, start, end) => {
    for (let angle = start; angle <= end; angle += 10) {
      const radians = angle * Math.PI / 180;
      points.push([cx + radius * Math.cos(radians), cy + radius * Math.sin(radians)]);
    }
  };
  points.push([x0 + radius, y0]);
  points.push([x1 - radius, y0]);
  addArc(x1 - radius, y0 + radius, -90, 0);
  points.push([x1, y1 - radius]);
  addArc(x1 - radius, y1 - radius, 0, 90);
  points.push([x0 + radius, y1]);
  addArc(x0 + radius, y1 - radius, 90, 180);
  points.push([x0, y0 + radius]);
  addArc(x0 + radius, y0 + radius, 180, 270);
  return points.map(transform);
}

function footprintGeometry(THREE, kind, width, depth, height, options = {}) {
  const shape = new THREE.Shape();
  const points = footprintPoints(kind, width, depth, options);
  shape.moveTo(points[0][0], points[0][1]);
  for (const [x, y] of points.slice(1)) shape.lineTo(x, y);
  shape.closePath();
  return new THREE.ExtrudeGeometry(shape, {
    depth: height,
    bevelEnabled: false,
    curveSegments: 16,
    steps: 1,
  });
}

function createAssemblyProxy(THREE, item) {
  const group = new THREE.Group();
  const [width, depth, height] = item.baseSize;
  const options = item.shapeOptions || {};
  const pivot = Array.isArray(options.rotation_pivot)
    ? options.rotation_pivot.map((value) => number(value, 0))
    : [0, 0, 0];
  const rotationX = number(options.rotation_x_deg, 0) * Math.PI / 180;
  group.position.set(
    item.baseMin[0] + pivot[0],
    item.baseMin[1] + pivot[1],
    item.baseMin[2] + pivot[2],
  );
  if (rotationX) group.rotation.x = rotationX;
  const place = (position) => position.map((value, index) => value - pivot[index]);
  if (item.shape === "front-arc" || item.shape === "combined-footprint") {
    const footprintKind = "front-arc";
    const frontOptions = {
      ...options,
      front_length_x: number(options.front_length_x, width),
    };
    const front = footprintGeometry(THREE, footprintKind, width, depth, height, frontOptions);
    addProxyPart(THREE, group, item, front, place([0, 0, 0]));
    if (item.shape === "combined-footprint") {
      const rearX = number(options.rear_x_offset, 0);
      const rearLength = number(options.rear_length_x, width - rearX);
      const rear = footprintGeometry(THREE, "rounded-footprint", width, depth, height, {
        ...options,
        x0: rearX,
        x1: rearX + rearLength,
        y0: 0,
        y1: number(options.width_y, depth),
      });
      addProxyPart(THREE, group, item, rear, place([0, 0, 0]));
      const partingGap = number(options.parting_gap_x, 0);
      if (partingGap > 0) {
        const bridge = new THREE.BoxGeometry(partingGap, depth, height);
        addProxyPart(
          THREE,
          group,
          item,
          bridge,
          place([rearX - partingGap / 2, depth / 2, height / 2]),
        );
      }
    }
  } else if (item.shape === "rounded-footprint" || item.shape === "rounded-footprint-tail-relief") {
    const footprintKind = item.shape === "rounded-footprint-tail-relief"
      ? "rounded-footprint-tail-relief"
      : "rounded-footprint";
    const outer = footprintGeometry(THREE, footprintKind, width, depth, height, {
      ...options,
      x0: number(options.outer_x_offset, 0),
      x1: number(options.outer_x_offset, 0) + number(options.outer_width_x, width),
      y0: number(options.outer_y_offset, 0),
      y1: number(options.outer_y_offset, 0) + number(options.outer_depth_y, depth),
    });
    addProxyPart(THREE, group, item, outer, place([0, 0, 0]));
  } else if (item.shape === "rear-back-rounded-support-boss") {
    const outer = footprintGeometry(THREE, "rear-back-rounded-footprint", width, depth, height, {
      ...options,
      x0: number(options.outer_x_offset, 0),
      x1: number(options.outer_x_offset, 0) + number(options.outer_width_x, width),
      y0: number(options.outer_y_offset, 0),
      y1: number(options.outer_y_offset, 0) + number(options.outer_depth_y, depth),
    });
    addProxyPart(THREE, group, item, outer, place([0, 0, 0]));

    // The rear-cover boss is a separate thickened PETG volume.  The browser
    // proxy keeps it separate so the centered rear-face seat and x-axis M8
    // interface remain obvious in the assembly even though the SCAD part is
    // one union.
    const bossLength = number(options.boss_length_x, 0);
    const bossDepth = number(options.boss_depth_y, 0);
    const bossHeight = number(options.boss_height_z, 0);
    const bossXOffset = number(options.boss_x_offset, 0);
    const bossYOffset = number(options.boss_y_offset, 0);
    const bossZOffset = number(options.boss_z_offset, 0);
    const bossX = options.mirror_x
      ? width - bossXOffset - bossLength
      : bossXOffset;
    if (bossLength > 0 && bossDepth > 0 && bossHeight > 0) {
      const boss = new THREE.BoxGeometry(bossLength, bossDepth, bossHeight);
      addProxyPart(
        THREE,
        group,
        item,
        boss,
        place([
          bossX + bossLength / 2,
          bossYOffset + bossDepth / 2,
          bossZOffset + bossHeight / 2,
        ]),
      );
      const holeD = number(options.boss_hole_d, 0);
      const holeDepth = number(options.boss_hole_depth_x, bossLength);
      if (holeD > 0 && holeDepth > 0) {
        const hole = new THREE.CylinderGeometry(holeD / 2, holeD / 2, holeDepth + 0.4, 24);
        hole.rotateZ(Math.PI / 2);
        addProxyPart(
          THREE,
          group,
          item,
          hole,
          place([
            bossX + bossLength / 2,
            bossYOffset + bossDepth / 2,
            bossZOffset + bossHeight / 2,
          ]),
          { color: "#26313b", opacity: 0.86, depthWrite: false, metalness: 0.2 },
        );
      }
      // The SCAD adds two solid y-side ribs after cutting the rear cavity.
      // Show the same load-path idea in the browser proxy: one rib clears the
      // positive-y half of the central bore and its mirror clears the negative
      // half, while both reach the rear shell wall.
      const gussetLength = number(options.gusset_length_x, 0);
      const gussetHeight = number(options.gusset_height_z, 0);
      const gussetRootY = number(options.gusset_root_y_offset, depth / 2);
      const gussetRootWidth = number(options.gusset_root_width_y, 0);
      if (gussetLength > 0 && gussetHeight > 0 && gussetRootWidth > 0) {
        const gussetXOffset = number(options.gusset_x_offset, bossXOffset);
        const gussetX = options.mirror_x
          ? width - gussetXOffset - gussetLength
          : gussetXOffset;
        const gussetZ = number(options.gusset_z_offset, 0);
        const ribSpecs = [
          [gussetRootY, depth],
          [0, depth - (gussetRootY + gussetRootWidth)],
        ];
        ribSpecs.forEach(([y0, y1]) => {
          const ribDepth = Math.max(0, y1 - y0);
          if (ribDepth <= 0) return;
          const rib = new THREE.BoxGeometry(gussetLength, ribDepth, gussetHeight);
          addProxyPart(
            THREE,
            group,
            item,
            rib,
            place([
              gussetX + gussetLength / 2,
              y0 + ribDepth / 2,
              gussetZ + gussetHeight / 2,
            ]),
            { color: "#657786", opacity: 0.92, depthWrite: true, metalness: 0.08 },
          );
        });
      }
    }
  } else if (item.shape === "ballhead-body") {
    // The purchased 13 mm ballhead is a real hardware envelope, not a blue
    // cylinder: show its rounded black clamp body, exposed metal ball, side
    // plate, and the transverse lock wheel.  The thread interfaces remain
    // separate assembly items so their axes and selected sizes are explicit.
    const outer = footprintGeometry(THREE, "rounded-footprint", width, depth, height, {
      x0: 0,
      x1: width,
      y0: 0,
      y1: depth,
      radius: number(options.radius, 4),
    });
    addProxyPart(THREE, group, item, outer, place([0, 0, 0]), {
      color: "#161b20",
      roughness: 0.28,
      metalness: 0.78,
    });
    const ballD = number(options.ball_d, 13);
    const ball = new THREE.SphereGeometry(ballD / 2, 32, 20);
    addProxyPart(THREE, group, item, ball, place([width / 2, depth / 2, height / 2]), {
      color: "#aeb5bb",
      roughness: 0.2,
      metalness: 0.9,
    });
    const plateD = number(options.side_plate_d, 24);
    const plateT = number(options.side_plate_t_x, 4);
    const plate = new THREE.CylinderGeometry(plateD / 2, plateD / 2, plateT, 32);
    plate.rotateZ(Math.PI / 2);
    addProxyPart(THREE, group, item, plate,
      place([0, depth / 2, height / 2]), {
        color: "#11161a",
        roughness: 0.26,
        metalness: 0.82,
      });
    const collar = new THREE.CylinderGeometry(5, 5, 2.2, 24);
    collar.rotateZ(Math.PI / 2);
    addProxyPart(THREE, group, item, collar,
      place([-plateT / 2 - 0.5, depth / 2, height / 2]), {
        color: "#b8bec2",
        roughness: 0.2,
        metalness: 0.9,
      });
    const knobD = number(options.lock_knob_d, 18);
    const knobT = number(options.lock_knob_t_y, 8);
    const knob = new THREE.CylinderGeometry(
      knobD / 2,
      knobD / 2,
      knobT,
      Math.max(12, Math.round(number(options.lock_knob_ridge_count, 24))),
    );
    addProxyPart(THREE, group, item, knob,
      place([width / 2, -knobT / 2 + 1, height / 2]), {
        color: "#11161a",
        roughness: 0.3,
        metalness: 0.76,
      });
  } else if (item.shape === "threaded-stud") {
    // Keep the purchased 1/4-20 and M8 interfaces visibly threaded while the
    // dimensions remain the simple measured outer envelopes used by the
    // matching OpenSCAD model.
    const axis = options.axis || "z";
    const outerD = number(options.outer_d, number(options.radius, 4) * 2);
    const coreD = number(options.core_d, outerD - 1);
    const pitch = Math.max(0.5, number(options.pitch, 1.25));
    const cylinderLength = axis === "x" ? width : axis === "y" ? depth : height;
    const core = new THREE.CylinderGeometry(coreD / 2, coreD / 2, cylinderLength, 24);
    if (axis === "x") core.rotateZ(Math.PI / 2);
    if (axis === "z") core.rotateX(Math.PI / 2);
    addProxyPart(THREE, group, item, core, place([width / 2, depth / 2, height / 2]), {
      color: "#aeb5bb",
      roughness: 0.2,
      metalness: 0.9,
    });
    const crest = Math.max(0.12, (outerD - coreD) / 4);
    const major = coreD / 2 + crest;
    for (let offset = pitch / 2; offset < cylinderLength; offset += pitch) {
      const ring = new THREE.TorusGeometry(major, crest, 8, 18);
      if (axis === "x") ring.rotateY(Math.PI / 2);
      if (axis === "y") ring.rotateX(Math.PI / 2);
      const position = axis === "x"
        ? [offset, depth / 2, height / 2]
        : axis === "y"
          ? [width / 2, offset, height / 2]
          : [width / 2, depth / 2, offset];
      addProxyPart(THREE, group, item, ring, place(position), {
        color: "#c5c9cc",
        roughness: 0.18,
        metalness: 0.92,
      });
    }
  } else if (item.shape === "detent") {
    const ballD = number(options.ball_d, 4);
    const ball = new THREE.SphereGeometry(ballD / 2, 24, 16);
    addProxyPart(THREE, group, item, ball,
      place([width / 2, depth / 2, number(options.ball_center_z, height * 0.85)]), {
        color: "#d8dde2",
        roughness: 0.18,
        metalness: 0.92,
      });
    const springD = number(options.spring_d, 3);
    const springH = number(options.spring_h, 8.5);
    const spring = new THREE.CylinderGeometry(springD / 2, springD / 2, springH, 16);
    spring.rotateX(Math.PI / 2);
    addProxyPart(THREE, group, item, spring,
      place([width / 2, depth / 2, number(options.spring_bottom_z, 1.2) + springH / 2]), {
        color: "#b8bec4",
        roughness: 0.24,
        metalness: 0.85,
        opacity: 0.7,
      });
    const retainerD = number(options.retainer_d, 5.5);
    const retainerH = number(options.retainer_h, 1.5);
    const retainer = new THREE.CylinderGeometry(retainerD / 2, retainerD / 2, retainerH, 24);
    retainer.rotateX(Math.PI / 2);
    addProxyPart(THREE, group, item, retainer,
      place([width / 2, depth / 2, number(options.retainer_center_z, retainerH / 2)]), {
        color: "#4b535b",
        roughness: 0.32,
        metalness: 0.72,
      });
  } else if (item.shape === "cylinder" || item.shape === "hex") {
    const radius = number(options.radius, Math.min(width, depth) / 2);
    const radialSegments = item.shape === "hex" ? 6 : 24;
    const cylinderLength = options.axis === "x"
      ? width
      : options.axis === "y"
        ? depth
        : height;
    const geometry = new THREE.CylinderGeometry(radius, radius, cylinderLength, radialSegments);
    if (options.axis === "x") geometry.rotateZ(Math.PI / 2);
    if (options.axis === "z") geometry.rotateX(Math.PI / 2);
    addProxyPart(THREE, group, item, geometry, place([width / 2, depth / 2, height / 2]));
  } else if (item.shape === "hex-stack") {
    const nutHeight = 6.5;
    for (const z of [0, nutHeight + 0.4]) {
      const geometry = new THREE.CylinderGeometry(number(options.radius, 7), number(options.radius, 7), nutHeight, 6);
      geometry.rotateX(Math.PI / 2);
      addProxyPart(THREE, group, item, geometry, place([width / 2, depth / 2, z + nutHeight / 2]), { metalness: 0.72 });
    }
  } else {
    const geometry = new THREE.BoxGeometry(width, depth, height);
    const isBeamWindow = item.shape === "stg120-beam-window";
    addProxyPart(THREE, group, item, geometry, place([width / 2, depth / 2, height / 2]), {
      color: isBeamWindow ? "#fb817c" : undefined,
      opacity: isBeamWindow ? 0.18 : ((item.group === "rail" || item.group === "net") && item.nonPrinted ? 0.34 : undefined),
      depthWrite: isBeamWindow ? false : ((item.group !== "rail" && item.group !== "net") || !item.nonPrinted),
    });
    if (item.shape === "stg120-head") {
      const slit = new THREE.BoxGeometry(0.35, Math.max(1, depth - 2), Math.min(height - 10, 120));
      const faceDirection = number(options.face_direction, 1);
      const slitX = faceDirection < 0 ? width - 0.18 : 0.18;
      addProxyPart(THREE, group, item, slit, place([slitX, depth / 2, Math.min(height - 5, 125) / 2 + 5]), {
        color: "#fb817c",
        roughness: 0.22,
        metalness: 0.18,
        opacity: 0.96,
      });
    }
    if (item.shape === "optical-module") {
      const lens = new THREE.CylinderGeometry(2, 2, 3, 24);
      lens.rotateZ(Math.PI / 2);
      addProxyPart(THREE, group, item, lens, place([1.5, depth / 2, height / 2]), {
        color: "#fb817c",
        roughness: 0.22,
        metalness: 0.2,
        opacity: 0.96,
      });
    }
  }
  markAssemblyObject(group, item);
  state.three.modelRoot.add(group);
  item.object = group;
  return group;
}

function setAssemblyMaterialState(material, active, progressAlpha) {
  const baseOpacity = number(material.userData.baseOpacity, 1);
  const baseColor = material.userData.baseColor;
  material.opacity = baseOpacity * progressAlpha;
  material.transparent = material.opacity < 0.999;
  if (baseColor) material.color.copy(baseColor);
  if (material.emissive) {
    material.emissive.set(active ? "#ffffff" : "#000000");
    material.emissiveIntensity = active ? 0.42 : 0;
  }
}

function updateAssemblyScene() {
  if (!state.three.ready) return;
  // Assembly and exploded views share the same loaded objects.  Never let a
  // stale slider value move objects while the normal assembly tab is active.
  const amount = state.uiMode === "assembly" ? 0 : state.assembly.explode;
  for (const item of state.assembly.items) {
    const object = item.object;
    if (!object) continue;
    object.visible = assemblyVisible(item);
    const pivot = Array.isArray(item.shapeOptions?.rotation_pivot)
      ? item.shapeOptions.rotation_pivot.map((value) => number(value, 0))
      : [0, 0, 0];
    // createAssemblyProxy positions a rotated group at base_min + pivot.
    // Keep that offset when the assembly/explosion state refreshes; dropping
    // it detached the M6 head, stem, hex and nut and made the axes look wrong.
    object.position.set(
      item.baseMin[0] + pivot[0] + item.explosion[0] * amount,
      item.baseMin[1] + pivot[1] + item.explosion[1] * amount,
      item.baseMin[2] + pivot[2] + item.explosion[2] * amount,
    );
    const future = state.assembly.step < ASSEMBLY_STEPS.length && item.stage > state.assembly.step;
    const progressAlpha = future ? 0.18 : 1;
    const active = item.id === state.assembly.selectedId || item.id === state.assembly.hoveredId;
    object.traverse((child) => {
      if (!child.material) return;
      const materials = Array.isArray(child.material) ? child.material : [child.material];
      materials.forEach((material) => setAssemblyMaterialState(material, active, progressAlpha));
    });
  }
  if (refs.assemblyStatusBadge) {
    refs.assemblyStatusBadge.textContent = state.uiMode === "assembly"
      ? `${state.assembly.items.filter(assemblyVisible).length} 个装配对象 · 完整装配`
      : `${state.assembly.items.filter(assemblyVisible).length} 个装配对象 · ${Math.round(amount * 100)}% 爆炸`;
  }
}

async function loadAssemblyModel() {
  if (!state.three.ready) return;
  const { THREE } = state.three;
  if (state.uiMode === "assembly") state.assembly.explode = 0;
  const requestId = ++state.three.loadId;
  clearThreeModel();
  state.assembly.items = buildAssemblyItems();
  state.assembly.loadError = null;
  setModelPlaceholder("正在载入装配预览…", `${state.assembly.items.length} 个对象；打印件已恢复到安装基准`);
  const failures = [];
  for (const item of state.assembly.items.filter((candidate) => candidate.shape !== "stl")) {
    createAssemblyProxy(THREE, item);
  }
  await Promise.all(state.assembly.items.filter((item) => item.shape === "stl").map(async (item) => {
    try {
      const geometry = await loadGeometry(item.sourcePath);
      if (requestId !== state.three.loadId) return;
      normalizedGeometry(THREE, geometry);
      const material = assemblyMaterial(THREE, item);
      const mesh = new THREE.Mesh(geometry, material);
      if (item.stlTransform?.rotation) {
        mesh.rotation.set(...item.stlTransform.rotation);
      }
      const group = new THREE.Group();
      group.position.set(...item.baseMin);
      group.add(mesh);
      markAssemblyObject(group, item);
      state.three.modelRoot.add(group);
      item.object = group;
    } catch (error) {
      failures.push(`${item.name_zh}: ${error?.message || error}`);
    }
  }));
  if (requestId !== state.three.loadId) return;
  state.assembly.loaded = true;
  state.assembly.loadError = failures.length ? failures : null;
  refs.modelPlaceholder.hidden = true;
  refs.modelCaption.textContent = failures.length
    ? `装配预览已载入，但有 ${failures.length} 个 STL 读取失败；非打印占位仍可检查。`
    : "装配预览已载入；鼠标悬停查看中文名称，点击零件查看材料和装配说明。";
  updateAssemblyScene();
  fitThreeCamera();
  renderAssemblyGuide();
}

function assemblyItemAtPointer(event) {
  const { camera, modelRoot, raycaster, pointer } = state.three;
  if (!camera || !modelRoot || !raycaster || !pointer) return null;
  const rect = refs.modelHost.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const intersections = raycaster.intersectObjects(modelRoot.children, true);
  for (const intersection of intersections) {
    const id = intersection.object.userData.assemblyId;
    const item = id ? assemblyItemById(id) : null;
    if (item && assemblyVisible(item)) return item;
  }
  return null;
}

function updateAssemblyHoverLabel(item, event) {
  const label = refs.assemblyHoverLabel;
  if (!label) return;
  if (!item || state.uiMode === "print" || state.uiMode === "parts") {
    label.hidden = true;
    return;
  }
  const rect = refs.modelHost.getBoundingClientRect();
  label.innerHTML = `<strong>${item.name_zh}</strong><span>${item.kind} · ${item.material}</span>`;
  label.hidden = false;
  const maxLeft = Math.max(8, rect.width - label.offsetWidth - 8);
  const maxTop = Math.max(8, rect.height - label.offsetHeight - 8);
  label.style.left = `${Math.min(maxLeft, Math.max(8, event.clientX - rect.left + 14))}px`;
  label.style.top = `${Math.min(maxTop, Math.max(8, event.clientY - rect.top + 14))}px`;
}

function handleAssemblyPointerMove(event) {
  if (state.uiMode !== "assembly" && state.uiMode !== "exploded") return;
  const item = assemblyItemAtPointer(event);
  const nextId = item?.id || null;
  if (nextId !== state.assembly.hoveredId) {
    state.assembly.hoveredId = nextId;
    updateAssemblyScene();
    renderAssemblyGuide();
  }
  updateAssemblyHoverLabel(item, event);
}

function handleAssemblyPointerLeave() {
  state.assembly.hoveredId = null;
  updateAssemblyScene();
  updateAssemblyHoverLabel(null);
  renderAssemblyGuide();
}

function handleAssemblyClick(event) {
  if (state.uiMode !== "assembly" && state.uiMode !== "exploded") return;
  const item = assemblyItemAtPointer(event);
  state.assembly.selectedId = item?.id || null;
  updateAssemblyScene();
  renderAssemblyGuide();
}

async function loadModel() {
  if (!state.three.ready) return;
  const { THREE } = state.three;
  const designMode = state.uiMode === "assembly" || state.uiMode === "exploded";
  if (designMode) {
    if (!state.assembly.loaded || !state.assembly.items.length) {
      await loadAssemblyModel();
    } else {
      updateAssemblyScene();
      fitThreeCamera();
    }
    return;
  }
  const plate = currentPlate();
  const requestId = ++state.three.loadId;
  clearThreeModel();
  refs.modelPlaceholder.hidden = false;

  if (state.modelMode === "part") {
    const entry = findPart(state.selectedFile);
    if (!entry) {
      setModelPlaceholder("先选择一个零件", "点击左侧零件或俯视图中的色块");
      return;
    }
    setModelPlaceholder("正在读取单件 STL…", sourcePathFor(entry));
    try {
      const geometry = await loadGeometry(sourcePathFor(entry));
      if (requestId !== state.three.loadId) return;
      addGeometryMesh(THREE, geometry, category(entry).color, null, true);
      refs.modelPlaceholder.hidden = true;
      refs.modelCaption.textContent = `${entry.file} · 源 STL ${formatSize(sourceSize(entry))} · 未改变源件尺寸`;
      fitThreeCamera();
    } catch (error) {
      setModelPlaceholder("单件 STL 暂不可读", "请确认先运行导出脚本并通过本地 HTTP 服务打开页面");
      refs.modelCaption.textContent = `读取失败：${error?.message || error}`;
    }
    return;
  }

  if (!plate) {
    setModelPlaceholder("当前床面没有可显示拼盘", "调大打印床尺寸后重新排版");
    return;
  }
  if (state.generated && plate.path) {
    setModelPlaceholder("正在读取拼盘 STL…", plate.path);
    try {
      const geometry = await loadGeometry(assetPath(plate.path));
      if (requestId !== state.three.loadId) return;
      addGeometryMesh(THREE, geometry, "#62e4d1", null, false);
      refs.modelPlaceholder.hidden = true;
      refs.modelCaption.textContent = `${plate.path} · ${plate.parts.length} 件独立打印件的合并预览`;
      fitThreeCamera();
    } catch (error) {
      setModelPlaceholder("拼盘 STL 暂不可读", "俯视图仍可使用；请检查本地导出目录");
      refs.modelCaption.textContent = `读取失败：${error?.message || error}`;
    }
    return;
  }

  setModelPlaceholder("正在组装浏览器预览…", `${plate.parts.length} 个源 STL`);
  try {
    await Promise.all(plate.parts.map(async (entry) => {
      const geometry = await loadGeometry(sourcePathFor(entry));
      if (requestId !== state.three.loadId) return;
      addGeometryMesh(THREE, geometry, category(entry).color, entry, false);
    }));
    if (requestId !== state.three.loadId) return;
    refs.modelPlaceholder.hidden = true;
    refs.modelCaption.textContent = `浏览器排版预览 · ${plate.parts.length} 件源 STL · 尚未生成拼盘文件`;
    fitThreeCamera();
  } catch (error) {
    setModelPlaceholder("源 STL 暂不可读", "请先执行导出脚本；俯视排版仍可查看");
    refs.modelCaption.textContent = `读取失败：${error?.message || error}`;
  }
}

async function initThree() {
  try {
    const [threeModule, loaderModule, controlsModule] = await Promise.all([
      import("three"),
      import("three/addons/loaders/STLLoader.js"),
      import("three/addons/controls/OrbitControls.js"),
    ]);
    const THREE = threeModule;
    state.three.THREE = THREE;
    state.three.STLLoader = loaderModule.STLLoader;
    state.three.OrbitControls = controlsModule.OrbitControls;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    refs.modelHost.append(renderer.domElement);
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 5000);
    camera.up.set(0, 0, 1);
    const controls = new state.three.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    const grid = new THREE.GridHelper(800, 32, "#31545b", "#173036");
    grid.rotation.x = Math.PI / 2;
    scene.add(grid);
    const axes = new THREE.AxesHelper(100);
    scene.add(axes);
    scene.add(new THREE.HemisphereLight("#d7f6f1", "#10242b", 1.6));
    const key = new THREE.DirectionalLight("#ffffff", 2.2);
    key.position.set(260, -280, 360);
    scene.add(key);
    const fill = new THREE.DirectionalLight("#74a7ff", 0.9);
    fill.position.set(-260, 200, 160);
    scene.add(fill);
    state.three.renderer = renderer;
    state.three.scene = scene;
    state.three.camera = camera;
    state.three.controls = controls;
    state.three.modelRoot = new THREE.Group();
    state.three.grid = grid;
    state.three.globalAxes = axes;
    state.three.raycaster = new THREE.Raycaster();
    state.three.pointer = new THREE.Vector2();
    scene.add(state.three.modelRoot);
    state.three.ready = true;
    resizeThree();
    const animate = () => {
      if (!state.three.ready) return;
      controls.update();
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
    window.addEventListener("resize", resizeThree);
    refs.modelCaption.textContent = "WebGL 3D 预览已就绪。";
    loadModel();
  } catch (error) {
    refs.modelCaption.textContent = "WebGL 3D 预览不可用；俯视拼盘和下载操作仍可使用。";
    setModelPlaceholder("3D 预览不可用", "当前浏览器未加载 Three.js/CDN，俯视图仍然有效");
    console.warn("Three.js preview unavailable", error);
  }
}

async function loadManifest() {
  const requested = new URLSearchParams(window.location.search).get("manifest");
  state.manifestUrl = requested
    ? new URL(requested, window.location.href)
    : new URL("../exports/net-stand-v0.1/print-platter-256/manifest.json", window.location.href);
  setStatus("正在读取打印清单…", "idle");
  try {
    const response = await fetch(state.manifestUrl, { cache: "no-store" });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    state.manifest = await response.json();
    state.sourceManifest = state.manifest;
    state.sourceManifestUrl = state.manifestUrl;
    if (state.manifest.source_manifest) {
      const sourceUrl = new URL(state.manifest.source_manifest, state.manifestUrl);
      const sourceResponse = await fetch(sourceUrl, { cache: "no-store" });
      if (sourceResponse.ok) {
        state.sourceManifest = await sourceResponse.json();
        state.sourceManifestUrl = sourceUrl;
      }
    }
    state.generatedLayout = generatedLayoutFromManifest(state.manifest);
    state.layout = state.generatedLayout;
    state.generated = true;
    state.activePlateIndex = 0;
    state.selectedFile = null;
    state.modelMode = "plate";
    state.uiMode = "assembly";
    state.assembly.items = [];
    state.assembly.loaded = false;
    state.assembly.explode = 0;
    state.assembly.datums = null;
    state.assembly.selectedId = null;
    state.assembly.hoveredId = null;
    state.assembly.focusM6 = false;
    state.assembly.focusSkpCandidate = false;
    state.assembly.showSkpCandidate = true;
    state.assembly.showSkpFit = true;
    refs.fitM6.textContent = "M6 右侧近景";
    refs.fitM6.classList.remove("active");
    refs.showSkpCandidate.checked = true;
    refs.showSkpFit.checked = true;
    refs.fitSkp.textContent = "SKP 腿脚近景";
    refs.fitSkp.classList.remove("active");
    setBedInputs(state.layout.print_bed);
    const sourceHref = state.manifest.source_manifest
      ? new URL(state.manifest.source_manifest, state.manifestUrl).href
      : new URL("../manifest.json", state.manifestUrl).href;
    refs.sourceManifestLink.href = sourceHref;
    refs.sourceManifestLink.textContent = "查看源 manifest ↗";
    clearError();
    state.hoveredFile = null;
    setStatus(`已载入 ${state.layout.parts.length} 个打印清单条目`, "ok");
    render();
    await initThree();
  } catch (error) {
    showError(`找不到或无法读取拼盘 manifest：${state.manifestUrl.href}。请先运行导出和拼盘脚本，再通过本地 HTTP 服务打开此页。(${error?.message || error})`);
    refs.plateCount.textContent = "—";
    refs.placedCount.textContent = "—";
    refs.oversizedCount.textContent = "—";
    setModelPlaceholder("等待打印清单", "生成 manifest 后刷新页面");
  }
}

function setViewMode(mode) {
  if (!["assembly", "exploded", "print", "parts"].includes(mode)) return;
  state.uiMode = mode;
  if (mode === "assembly") state.assembly.explode = 0;
  if (mode === "exploded" && state.assembly.explode === 0) state.assembly.explode = ASSEMBLY_DEFAULT_EXPLODE;
  if (mode === "parts") state.modelMode = "plate";
  render();
  if (mode === "parts") {
    if (state.three.ready) clearThreeModel();
    return;
  }
  loadModel();
}

refs.bedPreset.addEventListener("change", () => {
  const preset = PRESETS[refs.bedPreset.value];
  if (preset) {
    refs.bedWidth.value = preset.width_mm;
    refs.bedDepth.value = preset.depth_mm;
    refs.bedHeight.value = preset.height_mm;
    refs.edgeMargin.value = preset.edge_margin_mm;
    packPreview();
  }
});
[
  refs.bedWidth,
  refs.bedDepth,
  refs.bedHeight,
  refs.edgeMargin,
].forEach((input) => input.addEventListener("input", () => {
  refs.bedPreset.value = "custom";
}));
refs.partGap.addEventListener("input", () => {
  refs.gapOutput.value = formatNumber(refs.partGap.value);
});
refs.repackButton.addEventListener("click", packPreview);
refs.resetButton.addEventListener("click", () => {
  if (!state.generatedLayout) return;
  state.layout = generatedLayoutFromManifest(state.manifest);
  state.generated = true;
  state.activePlateIndex = 0;
  state.selectedFile = null;
  state.hoveredFile = null;
  state.modelMode = "plate";
  setBedInputs(state.layout.print_bed);
  clearError();
  render();
  loadModel();
});
refs.showLabels.addEventListener("change", drawBed);
refs.showSafeArea.addEventListener("change", drawBed);
refs.fitModel.addEventListener("click", fitThreeCamera);
refs.fitM6?.addEventListener("click", fitM6OrientationCamera);
refs.fitSkp?.addEventListener("click", fitSkpCandidateCamera);
refs.downloadLayout.addEventListener("click", downloadLayout);
refs.modeTabs?.querySelectorAll("[data-view-mode]").forEach((button) => {
  button.addEventListener("click", () => setViewMode(button.dataset.viewMode));
});
refs.explodeRange.addEventListener("input", () => {
  state.assembly.explode = number(refs.explodeRange.value) / 100;
  refs.explodeOutput.textContent = String(Math.round(state.assembly.explode * 100));
  updateAssemblyScene();
});
refs.assembledButton.addEventListener("click", () => setViewMode("assembly"));
refs.explodedButton.addEventListener("click", () => {
  state.assembly.explode = ASSEMBLY_DEFAULT_EXPLODE;
  setViewMode("exploded");
});
refs.assemblyStep.addEventListener("input", () => {
  state.assembly.step = number(refs.assemblyStep.value, ASSEMBLY_STEPS.length);
  updateAssemblyScene();
  render();
});
refs.showTable.addEventListener("change", () => {
  state.assembly.showTable = refs.showTable.checked;
  updateAssemblyScene();
});
refs.showNonPrinted.addEventListener("change", () => {
  state.assembly.showNonPrinted = refs.showNonPrinted.checked;
  updateAssemblyScene();
});
refs.showSkpCandidate?.addEventListener("change", () => {
  state.assembly.showSkpCandidate = refs.showSkpCandidate.checked;
  if (!state.assembly.showSkpCandidate && state.assembly.focusSkpCandidate) {
    state.assembly.focusSkpCandidate = false;
    refs.fitSkp.textContent = "SKP 腿脚近景";
    refs.fitSkp.classList.remove("active");
  }
  updateAssemblyScene();
  renderAssemblyGuide();
});
refs.showSkpFit?.addEventListener("change", () => {
  state.assembly.showSkpFit = refs.showSkpFit.checked;
  updateAssemblyScene();
  renderAssemblyGuide();
});
refs.clearAssemblySelection.addEventListener("click", () => {
  state.assembly.selectedId = null;
  state.assembly.hoveredId = null;
  updateAssemblyScene();
  renderAssemblyGuide();
});
refs.showPlateModel.addEventListener("click", () => {
  state.hoveredFile = state.selectedFile;
  state.modelMode = "plate";
  render();
  loadModel();
});
refs.showPartModel.addEventListener("click", () => {
  if (!state.selectedFile) {
    setStatus("请先选择一个零件", "idle");
    return;
  }
  state.modelMode = "part";
  render();
  loadModel();
});
refs.modelHost.addEventListener("pointermove", handleAssemblyPointerMove);
refs.modelHost.addEventListener("pointerleave", handleAssemblyPointerLeave);
refs.modelHost.addEventListener("click", handleAssemblyClick);
refs.partFilter.addEventListener("input", renderPartList);
refs.bedCanvas.addEventListener("click", (event) => {
  const entry = canvasEntryAt(event.clientX, event.clientY);
  if (entry) selectPart(entry.file);
});
refs.bedCanvas.addEventListener("mousemove", (event) => {
  const entry = canvasEntryAt(event.clientX, event.clientY);
  const nextFile = entry?.file || null;
  if (nextFile !== state.hoveredFile) {
    state.hoveredFile = nextFile;
    drawBed();
  }
  updateCanvasHoverLabel(entry, event.clientX, event.clientY);
});
refs.bedCanvas.addEventListener("mouseleave", () => {
  if (state.hoveredFile && state.hoveredFile !== state.selectedFile) {
    state.hoveredFile = null;
    drawBed();
  }
  updateCanvasHoverLabel(null);
});

refs.partList.addEventListener("mouseover", (event) => {
  const row = event.target.closest?.(".part-row");
  if (!row) return;
  state.hoveredFile = row.dataset.file || null;
  drawBed();
});
refs.partList.addEventListener("mouseout", (event) => {
  const row = event.target.closest?.(".part-row");
  if (!row || row.contains(event.relatedTarget)) return;
  if (state.hoveredFile !== state.selectedFile) {
    state.hoveredFile = null;
    drawBed();
  }
});

loadManifest();
