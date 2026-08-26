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
  rail: { label: "网顶 / 导轨", color: "#b28cff" },
  optical: { label: "M6 十路光电阵列", color: "#74a7ff" },
  sensor: { label: "PVDF 传感", color: "#62e4d1" },
  calibration: { label: "标定 / 参考", color: "#fb817c" },
  other: { label: "其他", color: "#a9bbc0" },
};

const ASSEMBLY_STEPS = [
  { number: 1, label: "桌下夹紧与立柱", description: "两侧传统 C 形夹、保护垫、M8 螺杆和旋钮固定在球台边缘；台边外伸段由前后两片三角侧肋加强。" },
  { number: 2, label: "立柱接缝与网顶承托", description: "上下立柱通过外套筒和防转内芯连接，网顶承载条落在两侧承托座上，左右外边界各离台边 152.5 mm。" },
  { number: 3, label: "网顶承载条与网布", description: "三段约 623.33 mm 的网顶承载条用拼接片锁紧，形成名义总宽 1830 mm 的网顶基准，再挂上真实网布。" },
  { number: 4, label: "M6 45° L 型主体、x 向分体壳与竖直球头", description: "先把左右各十个 M6 直角发射/接收器的中空 M6 外丝轴朝向球台中心：右侧螺纹末端中心孔朝 x-、左侧镜像后朝 x+；器件从各自 x 外侧插入 10×56×216 mm 加宽加厚主体，灰色六角留在外侧浅六角窝内，朝台内平滑面带一枚原配螺帽，蓝色尾线局部沿 z-，整件绕光束 x 轴转 -45° 后向 y-/z- 斜向离开；通道中心按 20 mm 节距排列，x- 光学前盖为正球弧、x+ 线缆后盖为圆角矩形，两盖共享 y± 边槽并配底盖；PETG 只保护/桥接，主要载荷走铝主体和金属 M8 接口。" },
  { number: 5, label: "机械参考线与最终检查", description: "历史参考线仍用 +10…+100 mm；当前 M6 阵列用 +10…+190 mm、20 mm 节距核对网顶高度、两侧阵列平行度与微调锁紧；器件输出参数仍以实测证据为准。" },
];

const ASSEMBLY_GROUPS = {
  clamp: { label: "台下夹紧", color: "#f6bd67", stage: 1 },
  post: { label: "左右立柱", color: "#f28b50", stage: 2 },
  rail: { label: "网顶承载", color: "#e9eef0", stage: 3 },
  optical: { label: "M6 十路光电阵列", color: "#74a7ff", stage: 4 },
  sensor: { label: "PVDF 擦网", color: "#62e4d1", stage: 4 },
  reference: { label: "标定参考", color: "#fb817c", stage: 5 },
  hardware: { label: "标准件 / 占位", color: "#d99bff", stage: 5 },
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
    showTable: true,
    showNonPrinted: true,
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
  if (part.includes("clamp") || part.includes("knob") || part.includes("lower_stand")) return "clamp";
  if (part.includes("post")) return "post";
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
    case "post": return [outward * 74, 0, 42];
    case "rail": return [0, 0, 82];
    case "optical": return [side ? outward * 162 : 0, 0, 28];
    case "sensor": return [0, -126, 48];
    case "reference": return [outward * 142, -78, 48];
    case "hardware": return [outward * 128, -32, -70];
    default: return [0, 0, 0];
  }
}

function sourcePrintableEntries() {
  const entries = state.sourceManifest?.parts || state.manifest?.parts || [];
  return entries.filter((entry) => entry && entry.file && entry.printable !== false);
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
    side: options.side || 0,
    object: null,
  };
}

function makePrintableAssemblyItem(entry) {
  const bounds = boundsFromEntry(entry);
  if (!bounds) return null;
  const group = assemblyGroupKey(entry);
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
    base_min: bounds.min,
    size: bounds.size,
    side: sideSign(entry),
    explosion: explosionVector(group, sideSign(entry)),
  });
}

function firstEntry(entries, predicate) {
  return entries.find(predicate) || null;
}

function makeProxyAssemblyItems(entries) {
  const items = [];
  const stgHead = {
    length: 130,
    activeLength: 120,
    width: 19,
    thickness: 6,
    bottomZ: 147.5,
    pitch: 3.87,
    count: 32,
  };
  const railEntries = entries.filter((entry) => entry.part === "net_rail_segment");
  const railBounds = railEntries.map(boundsFromEntry).filter(Boolean);
  const railMinX = railBounds.length ? Math.min(...railBounds.map((item) => item.min[0])) : -915;
  const railMaxX = railBounds.length ? Math.max(...railBounds.map((item) => item.max[0])) : 915;
  const railTopZ = railBounds.length ? Math.min(...railBounds.map((item) => item.min[2])) : 142.5;
  const netSpan = railMaxX - railMinX;

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
    group: "rail",
    shape: "box",
    base_min: [railMinX, -0.6, 0],
    size: [netSpan, 1.2, railTopZ],
    explosion: [0, 0, 82],
    notes: "半透明网布占位，用于确认网顶承载条与过网窗口关系。",
  }));
  items.push(makeAssemblyItem({
    id: "hardware:reference-line",
    name_zh: "M6 十路机械参考线（+50 mm 示例）",
    name_en: "M6 ten-channel mechanical reference line example",
    kind: "机械校准参考",
    material: "外购线材",
    group: "reference",
    shape: "box",
    base_min: [railMinX, -0.5, 202],
    size: [netSpan, 1, 1],
    explosion: [0, -78, 48],
    notes: "只用于核对十路机械高度和两侧阵列平行度；电子高度输出必须以 M6 器件接口证据为准。",
  }));

  // Current M6 assembly contract. The metal bar is the load-bearing body;
  // the completed x-split PETG covers and metal M8 bridge are shown together
  // so the installed orientation can be checked before exploded export.
  const m6Geometry = {
    axisX: 763,
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
    cableGuardLength: 10,
    cablePreviewLength: 18,
    cableD: 3,
    bodyMinX: 761.25,
    bodyMaxX: 771.25,
    sensorRollDeg: -45,
    bodyCenterY: 0,
    bodyDepthY: 56,
    bodyBottomZ: 144.5,
    bodyHeightZ: 216,
    showShell: true,
    shellMinX: 760.6,
    shellMaxX: 785.4,
    shellMinY: -30.4,
    shellMaxY: 30.4,
    shellWidthY: 60.8,
    shellBottomZ: 141.5,
    shellHeightZ: 222,
    splitX: 766,
    frontMaxX: 766.3,
    rearMinX: 765.7,
    grooveWidthX: 4,
    grooveDepthY: 1.2,
    grooveMarginZ: 5,
    tongueClearance: 0.25,
    wall: 2.4,
    hexPocketAF: 10.7,
    hexPocketDepthX: 2.5,
    threadClearanceD: 6.6,
    cableExitD: 12,
    cableExitX: 766,
    headCenterX: 766,
    threadEndX: 783,
    receiverThreadMinX: 749,
    receiverOpticalMinX: 748.6,
    receiverNutMinX: 756.25,
    mountX: 881,
    mountT: 6,
    mountWidth: 56,
    mountHeight: 228,
    bossCenterX: 774.3,
    bossWidthX: 18,
    bossDepthY: 8,
    bossHeightZ: 24,
    supportY: -34.4,
    supportArmMinX: 790.3,
    supportArmMaxX: 889,
    supportArmZ: 227.5,
    supportArmWidthY: 18,
    supportArmT: 8,
    supportLegX: 884,
    supportGussetInsetX: 8,
    supportLegBottomZ: 171.5,
    supportLegTopZ: 231.5,
    ballheadBallD: 13,
    ballheadHousingD: 28,
    ballheadHousingLength: 26,
    ballheadCenterX: 806.3,
    ballheadCenterY: -34.4,
    ballheadCenterZ: 252.5,
    ballheadBaseCenterZ: 235.5,
    ballheadBaseD: 32,
    ballheadBaseT: 8,
    ballheadNetStudCenterZ: 217.5,
    ballheadNetStudLength: 28,
    ballheadSensorStudCenterX: 782.3,
    ballheadSensorStudD: 8,
    ballheadNetStudD: 8,
    supportThreadNominalD: 8,
    supportClearanceD: 8.6,
    supportMetalInsertD: 12,
    supportMetalInsertLengthX: 16,
    ballheadSensorStudLength: 16,
    ballheadTiltDeg: 90,
    ballheadRotationDeg: 360,
  };
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
    const supportEnvelopeMaxX = m6Geometry.supportLegX + m6Geometry.supportGussetInsetX;

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
        material: "6061-T6 铝合金",
        group: "optical",
        color: "#aeb5bb",
        shape: "box",
        base_min: [bodyMinX, -m6Geometry.bodyDepthY / 2, m6Geometry.bodyBottomZ],
        size: [m6Geometry.bodyMaxX - m6Geometry.bodyMinX,
          m6Geometry.bodyDepthY,
          m6Geometry.bodyHeightZ],
        side,
        explosion: [0, 0, 0],
        notes: "本阶段只显示长条主体与真实三维 L 型器件；主体截面加宽到 y=56 mm、加厚到 x=10 mm。灰色 AF8 六角从外侧卡入 2 mm，中空 M6 外丝贯穿主体，朝台内的平滑面带一枚原配螺帽。蓝色护套和黑色尾线按实物绕光束 x 轴 -45° 显示；壳子、支撑和云台暂不加入。",
      }));
      for (let index = 0; index < 10; index += 1) {
        const z = 162.5 + index * m6Geometry.sensorPitch;
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

    items.push(makeAssemblyItem({
      id: `hardware:m6-mount-adapter:${sideLabel}`,
      name_zh: `竖直网夹适配板（${sideName}）`,
      name_en: "vertical net-clamp adapter plate",
      kind: "机加工网架接口",
      material: "6061-T6 铝合金",
      group: "optical",
      base_min: [side > 0 ? m6Geometry.mountX : -m6Geometry.mountX - m6Geometry.mountT, -m6Geometry.mountWidth / 2, m6Geometry.ballheadCenterZ - m6Geometry.mountHeight / 2],
      size: [m6Geometry.mountT, m6Geometry.mountWidth, m6Geometry.mountHeight],
      side,
      explosion: explosionVector("optical", side),
      notes: "竖直金属适配板通过两条 M6 长孔固定到网架；当前不再使用旧的水平球头三孔背板模式。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-detector-body:${sideLabel}`,
      name_zh: `M6 长条铝合金主体（${sideName}）`,
      name_en: "M6 long aluminum detector body",
      kind: "机加工承力主体",
      material: "6061-T6 铝合金",
      group: "optical",
      base_min: [bodyMinX, m6Geometry.bodyCenterY - m6Geometry.bodyDepthY / 2, m6Geometry.bodyBottomZ],
      size: [m6Geometry.bodyMaxX - m6Geometry.bodyMinX, m6Geometry.bodyDepthY, m6Geometry.bodyHeightZ],
      side,
      explosion: [side * 54, 0, 28],
      notes: "当前验收 x=10 mm 厚、y=56 mm 宽的长条主体与真实三维激光头干涉：灰色 AF8 六角从外侧插入并卡入约 2 mm；中空 M6 外丝穿过主体，朝台内平滑面带一枚原配螺帽。两条 y± 边槽只导向前后盖舌片，主体仍是传感器和支撑的基准承力件。",
    }));
    if (m6Geometry.showShell) items.push(makeAssemblyItem({
      id: `hardware:m6-shell-front:${sideLabel}`,
      name_zh: `M6 前盖：x- 光学端正球弧（${sideName}）`,
      name_en: "M6 front spherical-arc cover",
      kind: "保护壳（非承力）",
      material: "PETG 尺寸样件",
      group: "optical",
      base_min: [frontShellMinX, m6Geometry.shellMinY, m6Geometry.shellBottomZ],
      size: [m6Geometry.frontMaxX - m6Geometry.shellMinX,
        m6Geometry.shellWidthY,
        m6Geometry.shellHeightZ],
      side,
      explosion: [side * -92, 0, 46],
      notes: "x- 光学端前盖为正球弧，从主体 z+ 套入；它占两条 y± 边槽的 x- 半，M3/M4 沉头螺钉只锁入铝主体导孔。",
    }));
    if (m6Geometry.showShell) items.push(makeAssemblyItem({
      id: `hardware:m6-shell-rear:${sideLabel}`,
      name_zh: `M6 后盖：x+ 圆角矩形与 y- M8 桥接 boss（${sideName}）`,
      name_en: "M6 rear rounded cover and support boss",
      kind: "保护壳/桥接件（非承力）",
      material: "PETG 尺寸样件",
      group: "optical",
      base_min: [rearShellMinX,
        m6Geometry.shellMinY - m6Geometry.bossDepthY,
        m6Geometry.shellBottomZ],
      size: [m6Geometry.shellMaxX - m6Geometry.rearMinX,
        m6Geometry.shellWidthY + m6Geometry.bossDepthY,
        m6Geometry.shellHeightZ],
      side,
      explosion: [side * 118, 0, 38],
      notes: "x+ 线缆端后盖为圆角矩形，并在 y- 外侧带桥接 boss；boss 只提供金属 M8 外牙/衬套的定位和接口，弯矩经金属件、盖件螺钉和铝主体传递。",
    }));
    if (m6Geometry.showShell) items.push(makeAssemblyItem({
      id: `hardware:m6-bottom-cover:${sideLabel}`,
      name_zh: `M6 底盖与线缆套管孔（${sideName}）`,
      name_en: "M6 bottom cover with cable sleeve exit",
      kind: "保护盖（非承力）",
      material: "PETG 尺寸样件",
      group: "optical",
      base_min: [shellMinX, -m6Geometry.shellWidthY / 2, m6Geometry.shellBottomZ - 3],
      size: [m6Geometry.shellMaxX - m6Geometry.shellMinX, m6Geometry.shellWidthY, 3],
      side,
      explosion: [side * 42, 0, -46],
      notes: "底盖按下方截面封闭，两个沉头螺钉固定到主体；Ø12 mm 孔贯通用于剥皮后统一线缆套管，当前明确为非密封设计。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-support-bracket:${sideLabel}`,
      name_zh: `金属 90° 支撑件（${sideName}）`,
      name_en: "metal 90-degree detector support",
      kind: "机加工承力支撑",
      material: "6061-T6 铝合金/金属件",
      group: "optical",
      base_min: [side > 0 ? m6Geometry.supportArmMinX : -supportEnvelopeMaxX, m6Geometry.supportY - m6Geometry.supportArmWidthY / 2, m6Geometry.supportLegBottomZ],
      size: [supportEnvelopeMaxX - m6Geometry.supportArmMinX, m6Geometry.supportArmWidthY, m6Geometry.supportLegTopZ - m6Geometry.supportLegBottomZ],
      side,
      explosion: [side * 138, 18, -16],
      notes: "水平托臂承接球头底部，竖直腿贴合网夹适配板，内角加三角侧肋；这是主体到网架的真实承力路径。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-ballhead-housing:${sideLabel}`,
      name_zh: `13 mm 采购球头（竖直姿态，${sideName}）`,
      name_en: "13 mm purchased ball head, vertical posture",
      kind: "外购云台占位",
      material: "外购金属件（非打印）",
      group: "optical",
      shape: "cylinder",
      shapeOptions: { radius: m6Geometry.ballheadHousingD / 2, axis: "z" },
      base_min: [ballheadMinX, m6Geometry.ballheadCenterY - m6Geometry.ballheadHousingD / 2, m6Geometry.ballheadCenterZ - m6Geometry.ballheadHousingLength / 2],
      size: [m6Geometry.ballheadHousingD, m6Geometry.ballheadHousingD, m6Geometry.ballheadHousingLength],
      side,
      explosion: [side * 154, -28, 20],
      notes: "云台本体不打印；当前按 13 mm 球、360° 旋转、90° 开口和竖直壳体姿态占位，实际螺纹选项/旋钮净空待到货复核。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-ballhead-base:${sideLabel}`,
      name_zh: `采购球头底座与竖直外牙（${sideName}）`,
      name_en: "purchased ball-head base and vertical stud",
      kind: "外购云台接口占位",
      material: "外购金属件（非打印）",
      group: "optical",
      shape: "cylinder",
      shapeOptions: { radius: m6Geometry.ballheadBaseD / 2, axis: "z" },
      base_min: [ballheadBaseMinX, m6Geometry.ballheadCenterY - m6Geometry.ballheadBaseD / 2, m6Geometry.ballheadBaseCenterZ - m6Geometry.ballheadBaseT / 2],
      size: [m6Geometry.ballheadBaseD, m6Geometry.ballheadBaseD, m6Geometry.ballheadBaseT],
      side,
      explosion: [side * 154, -28, -4],
      notes: "底座把竖直球头传给 90° 金属支撑；可选 1/4 内牙、1/4 外牙、3/8 外牙、M6/M8/M10 外牙只改接口件。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-ballhead-sensor-stud:${sideLabel}`,
      name_zh: `后盖 x 轴球头连接螺柱（${sideName}）`,
      name_en: "ball-head sensor-side horizontal stud",
      kind: "外购云台接口占位",
      material: "外购金属件（非打印）",
      group: "optical",
      shape: "cylinder",
      shapeOptions: { radius: m6Geometry.ballheadSensorStudD / 2, axis: "x" },
      base_min: [ballheadStudMinX,
        m6Geometry.ballheadCenterY - m6Geometry.ballheadSensorStudD / 2,
        m6Geometry.ballheadCenterZ - m6Geometry.ballheadSensorStudD / 2],
      size: [m6Geometry.ballheadSensorStudLength,
        m6Geometry.ballheadSensorStudD,
        m6Geometry.ballheadSensorStudD],
      side,
      explosion: [side * 162, -28, 24],
      notes: "M8 外牙金属螺柱沿 x- 插入 x+ 后盖 y- boss 的金属衬套/通孔；不是旧版水平球头背板的三孔结构。",
    }));
    items.push(makeAssemblyItem({
      id: `hardware:m6-ballhead-net-stud:${sideLabel}`,
      name_zh: `球头到 90° 支撑的竖直螺柱（${sideName}）`,
      name_en: "vertical ball-head support stud",
      kind: "外购云台接口占位",
      material: "外购金属件（非打印）",
      group: "optical",
      shape: "cylinder",
      shapeOptions: { radius: m6Geometry.ballheadNetStudD / 2, axis: "z" },
      base_min: [mirrorX(m6Geometry.ballheadCenterX - m6Geometry.ballheadNetStudD / 2,
        m6Geometry.ballheadNetStudD),
        m6Geometry.ballheadCenterY - m6Geometry.ballheadNetStudD / 2,
        m6Geometry.ballheadNetStudCenterZ - m6Geometry.ballheadNetStudLength / 2],
      size: [m6Geometry.ballheadNetStudD,
        m6Geometry.ballheadNetStudD,
        m6Geometry.ballheadNetStudLength],
      side,
      explosion: [side * 154, -28, -24],
      notes: "竖直姿态下用 M8 外牙把球头底部接到金属 90° 支撑托臂；实际端部螺纹由采购 SKU 决定。",
    }));
    for (let index = 0; index < 10; index += 1) {
      const z = 162.5 + index * m6Geometry.sensorPitch;
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
          ? [m6Geometry.axisX - beamLength, -0.45, z - 0.45]
          : [-m6Geometry.axisX, -0.45, z - 0.45],
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
        ? m6Geometry.axisX
        : mirrorX(m6Geometry.axisX, m6Geometry.headLengthX);
      const faceMinX = side > 0
        ? m6Geometry.receiverOpticalMinX
        : mirrorX(m6Geometry.receiverOpticalMinX, 0.4);
      const threadMinX = side > 0
        ? m6Geometry.receiverThreadMinX
        : mirrorX(m6Geometry.receiverThreadMinX, m6Geometry.stemLength);
      const cableGuardMinX = mirrorX(
        m6Geometry.cableExitX - m6Geometry.deviceD / 2,
        m6Geometry.deviceD,
      );
      const cableMinX = mirrorX(
        m6Geometry.cableExitX - m6Geometry.cableD / 2,
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
        material: "6061-T6 铝合金主体",
        group: "optical",
        shape: "hex",
        shapeOptions: {
          radius: m6Geometry.hexPocketAF / 2,
          axis: "x",
          rotation_x_deg: m6Geometry.sensorRollDeg,
          rotation_pivot: rotationPivotFor(hexBaseMin, z),
        },
        base_min: hexBaseMin,
        size: [m6Geometry.hexPocketDepthX, m6Geometry.hexPocketAF, m6Geometry.hexPocketAF],
        side,
        explosion: [side * 92, -130, 16],
        notes: "2.5 mm x 向浅窝只卡住水平外丝上的六角，不压住六角与外丝接驳平面；实际对边按到货件复核。",
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
  const gauge = firstEntry(entries, (entry) => entry.part === "calibration_gauge");
  const gaugeBounds = boundsFromEntry(gauge);
  if (gaugeBounds) {
    items.push(makeAssemblyItem({
      id: "tool:calibration-gauge",
      name_zh: "过网高度标定规（装配外工具）",
      name_en: "height calibration gauge",
      kind: "标定工具",
      material: "PETG",
      group: "reference",
      nonPrinted: false,
      shape: "box",
      base_min: [900, 120, 0],
      size: gaugeBounds.size,
      explosion: [0, 128, 56],
      notes: "这是历史 STG-120ML 的 32 点 / 3.87 mm 间距标定工具，不安装在当前 M6 网架上；只用于历史资料回溯。",
    }));
  }

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
  const printable = sourceEntries
    .filter((entry) => entry.part !== "calibration_gauge")
    .map(makePrintableAssemblyItem)
    .filter(Boolean);
  return printable.concat(makeProxyAssemblyItems(sourceEntries));
}

function assemblyItemById(id) {
  return state.assembly.items.find((item) => item.id === id) || null;
}

function isM6FocusItem(item) {
  if (!item || item.side !== 1) return false;
  const key = `${item.id || ""} ${item.name_zh || ""}`.toLowerCase();
  return key.includes("m6");
}

function setM6FocusVisuals(focus) {
  const { THREE, scene } = state.three;
  if (!THREE || !scene) return;
  if (!state.three.m6AxesHelper) {
    const helper = new THREE.AxesHelper(34);
    // Local origin: center of the right M6 body. Positive x is the beam
    // direction, positive y is toward the table/front, and positive z is up.
    helper.position.set(768, 0, 207.5);
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
  if (state.assembly.focusM6 && !isM6FocusItem(item)) return false;
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
      const candidates = [0, 90]
        .map((angle) => ({ angle, size: dimensionsForAngle(size, angle) }))
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
            const score = [Math.max(row.height, depth), candidate.angle, width, x, y];
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
            const score = [depth, candidate.angle, width, x, y];
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
          rotation_z_deg: best.angle,
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
    ? "网顶承载条约 623 mm，不能硬塞进当前打印床。页面会保留它们，等待换大床或再次拆分。"
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
      ? "爆炸距离只改变显示位置；打印件仍按源 STL 的真实装配坐标加载，紫色半透明件为非打印占位。"
      : "主体与壳体总成预览；坐标约定为 x=光束左右、y=前后、z=竖直。球台、网布、PVDF、M6 45° L 型宽体主体、20 mm 节距、x 向前后分段壳体、共享 y± 边槽、斜向 7 字让位孔、90°支撑和竖直采购球头按装配清单显示。";
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
  return new Promise((resolve, reject) => {
    const loader = new Loader();
    loader.load(url, resolve, undefined, reject);
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
    const angle = number(entry.rotation_z_deg);
    mesh.rotation.z = angle * Math.PI / 180;
    mesh.position.set(angle === 90 ? number(entry.x_mm) + size.y : number(entry.x_mm), number(entry.y_mm), 0);
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
  if (item.shape === "cylinder" || item.shape === "hex") {
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
      opacity: isBeamWindow ? 0.18 : (item.group === "rail" && item.nonPrinted ? 0.34 : undefined),
      depthWrite: isBeamWindow ? false : (item.group !== "rail" || !item.nonPrinted),
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
  const amount = state.assembly.explode;
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
    refs.assemblyStatusBadge.textContent = `${state.assembly.items.filter(assemblyVisible).length} 个装配对象 · ${Math.round(amount * 100)}% 爆炸`;
  }
}

async function loadAssemblyModel() {
  if (!state.three.ready) return;
  const { THREE } = state.three;
  const requestId = ++state.three.loadId;
  clearThreeModel();
  state.assembly.items = buildAssemblyItems();
  state.assembly.loadError = null;
  setModelPlaceholder("正在载入装配预览…", `${state.assembly.items.length} 个对象；打印件按源 STL 坐标恢复`);
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
    state.assembly.items = [];
    state.assembly.loaded = false;
    state.assembly.selectedId = null;
    state.assembly.hoveredId = null;
    state.assembly.focusM6 = false;
    refs.fitM6.textContent = "M6 右侧近景";
    refs.fitM6.classList.remove("active");
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
