const $ = (selector) => document.querySelector(selector);

const refs = {
  loadStatus: $("#load-status"),
  sourceManifestLink: $("#source-manifest-link"),
  errorBanner: $("#error-banner"),
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
  modelCaption: $("#model-caption"),
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
  optical: { label: "光学模块", color: "#74a7ff" },
  sensor: { label: "PVDF 传感", color: "#62e4d1" },
  calibration: { label: "标定 / 参考", color: "#fb817c" },
  other: { label: "其他", color: "#a9bbc0" },
};

const state = {
  manifest: null,
  manifestUrl: null,
  generatedLayout: null,
  layout: null,
  generated: true,
  activePlateIndex: 0,
  selectedFile: null,
  hoveredFile: null,
  modelMode: "plate",
  canvasTransform: null,
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
    loadId: 0,
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
  if (text.includes("optical") || text.includes("module") || text.includes("光学")) return "optical";
  if (text.includes("sensor") || text.includes("pvdf") || text.includes("film")) return "sensor";
  if (text.includes("rail") || text.includes("net-rail")) return "rail";
  if (text.includes("gauge") || text.includes("reference") || text.includes("pin")) return "calibration";
  if (text.includes("stand") || text.includes("post") || text.includes("clamp") || text.includes("knob")) return "stand";
  return "other";
}

function category(entry) {
  return COLORS[categoryKey(entry)] || COLORS.other;
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
  return [entry?.name_zh, entry?.name_en, entry?.part, entry?.file, entry?.side, entry?.material]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function assetPath(relative) {
  return new URL(relative, state.manifestUrl).href;
}

function generatedLayoutFromManifest(manifest) {
  return {
    schema_version: manifest.schema_version,
    generated: true,
    print_bed: { ...manifest.print_bed },
    plates: (manifest.plates || []).map((plate) => ({
      ...plate,
      parts: (plate.parts || []).map((entry) => ({ ...entry })),
    })),
    oversized: (manifest.oversized || []).map((entry) => ({ ...entry })),
    parts: (manifest.parts || []).map((entry) => ({ ...entry })),
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

  const ordered = [...(state.manifest.parts || [])].sort((left, right) => {
    const leftSize = sourceSize(left);
    const rightSize = sourceSize(right);
    const leftMax = Math.max(leftSize[0], leftSize[1]);
    const rightMax = Math.max(rightSize[0], rightSize[1]);
    return rightMax - leftMax || (rightSize[0] * rightSize[1] - leftSize[0] * leftSize[1]) || String(left.file).localeCompare(String(right.file));
  });

  const plates = [];
  const rowsByPlate = [];
  const oversized = [];
  const startPlate = () => {
    plates.push({
      id: `plate-${String(plates.length + 1).padStart(2, "0")}`,
      label: `浏览器预览拼盘 ${String(plates.length + 1).padStart(2, "0")}`,
      description: "按当前参数在浏览器中排版；不会生成或覆盖 STL 文件。",
      part_count: 0,
      parts: [],
    });
    rowsByPlate.push([]);
  };
  startPlate();

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
          startPlate();
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

  const usablePlates = plates.filter((plate) => plate.parts.length);
  state.layout = {
    schema_version: "0.1",
    generated: false,
    print_bed: bed,
    plates: usablePlates,
    oversized,
    parts: usablePlates.flatMap((plate) => plate.parts).concat(oversized),
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
    ? "网顶承载条约 537 mm，不能硬塞进当前打印床。页面会保留它们，等待换大床或再次拆分。"
    : "当前打印床可以容纳源清单中的全部零件。仍需在切片器中复核方向、支撑和首层。";

  if (state.activePlateIndex >= plates.length) state.activePlateIndex = Math.max(0, plates.length - 1);
  renderTabs();
  const plate = currentPlate();
  const bed = state.layout.print_bed;
  refs.layoutTitle.textContent = plate ? `${plate.label} · ${formatNumber(bed.width_mm)} × ${formatNumber(bed.depth_mm)} mm` : "没有零件适合当前打印床";
  refs.layoutBadge.textContent = state.generated ? "已生成 STL" : "仅浏览器预览";
  refs.layoutBadge.classList.toggle("preview-badge", !state.generated);
  refs.modelTitle.textContent = state.modelMode === "part" && state.selectedFile ? partName(findPart(state.selectedFile)) : (plate?.label || "等待选择模型");
  refs.modelCaption.textContent = state.generated ? "当前显示脚本生成的拼盘 STL；源零件仍保持独立尺寸。" : "当前布局由浏览器按源 STL 计算，仅供核对；如需拼盘 STL，请重新运行拼盘脚本。";
  updateDownloadLink();
  drawBed();
  renderLegend();
  renderPartList();
  renderOversized();
  renderComponents();
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
    label.textContent = `${plate.label} · ${plate.parts.length} 件`;
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
  const entries = (plate?.parts || []).filter((entry) => partSearchText(entry).includes(query));
  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = plate ? "当前筛选没有匹配零件" : "没有可显示的排版零件";
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
    sub.textContent = `${entry.file || entry.part || "STL"}${entry.side ? ` · ${entry.side}` : ""}${entry.index !== null && entry.index !== undefined ? ` · #${entry.index}` : ""}`;
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
    reason.textContent = entry.reason || "需要更大打印床或再次拆分";
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
  const available = Boolean(state.generated && plate?.path);
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

function fitThreeCamera() {
  const { THREE, camera, controls, modelRoot } = state.three;
  if (!THREE || !camera || !controls || !modelRoot || !modelRoot.children.length) return;
  const box = new THREE.Box3().setFromObject(modelRoot);
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

function resizeThree() {
  const { renderer, camera } = state.three;
  if (!renderer || !camera) return;
  const width = Math.max(1, refs.modelHost.clientWidth);
  const height = Math.max(1, refs.modelHost.clientHeight);
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

async function loadModel() {
  if (!state.three.ready) return;
  const { THREE } = state.three;
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
    state.generatedLayout = generatedLayoutFromManifest(state.manifest);
    state.layout = state.generatedLayout;
    state.generated = true;
    state.activePlateIndex = 0;
    state.selectedFile = null;
    state.modelMode = "plate";
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
refs.downloadLayout.addEventListener("click", downloadLayout);
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
