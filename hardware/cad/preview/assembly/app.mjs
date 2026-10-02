import { AssemblyScene } from "./assembly-scene.mjs";
import { installFloatingPanels } from "./floating-panels.mjs";

const $ = (selector) => document.querySelector(selector);
const status = (message) => { $("#status").textContent = message; };
const button = (label, action, className = "") => {
  const element = document.createElement("button");
  element.type = "button";
  element.textContent = label;
  element.className = className;
  element.addEventListener("click", action);
  return element;
};

async function main() {
  if (location.protocol === "file:") throw new Error("请从 HTTP 服务打开预览，不要用 file://");
  const response = await fetch("./manifest.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`manifest.json: HTTP ${response.status}`);
  const manifest = await response.json();
  installFloatingPanels($("#canvas-panel"), {
    persist: manifest.ui?.persistPanelState === true,
  });
  const runtime = new AssemblyScene($("#viewport"), manifest);
  await runtime.load();
  if (manifest.motionAdapterModule) {
    const module = await import(new URL(manifest.motionAdapterModule, import.meta.url));
    if (typeof module.createMotionAdapter !== "function") {
      throw new Error("motion adapter must export createMotionAdapter(runtime, manifest)");
    }
    runtime.setMotionAdapter(module.createMotionAdapter(runtime, manifest));
  }
  $("#title").textContent = manifest.title || "装配预览";
  const groups = runtime.index.groups;
  const groupSelect = $("#group-filter");
  for (const group of groups.values()) {
    const option = document.createElement("option");
    option.value = group.id;
    option.textContent = group.label;
    groupSelect.append(option);
  }
  const showSearch = manifest.ui?.showSearch !== false;
  const showGroups = manifest.ui?.showGroups !== false && groups.size > 0;
  $("#search").hidden = !showSearch;
  groupSelect.hidden = !showGroups;
  $("#group-actions").hidden = !showGroups;
  $("#filters").hidden = !showSearch && !showGroups;
  $("#filters").classList.toggle("single-control", !showSearch || !showGroups);
  const stageSelect = $("#stage");
  for (const stage of runtime.index.stages.values()) {
    const option = document.createElement("option");
    option.value = stage.id;
    option.textContent = stage.label || stage.id;
    stageSelect.append(option);
  }
  if (!runtime.index.stages.size) $("#stage-controls").hidden = true;
  if (!manifest.playback) $("#play").hidden = true;
  let activeFocusIds = manifest.views?.[0]?.focusInstanceIds || null;
  let activeDirection = manifest.views?.[0]?.direction || [1, 0.75, 1];
  const focus = (ids, direction = activeDirection) => {
    activeFocusIds = ids || null;
    activeDirection = direction;
    runtime.focus(activeFocusIds, activeDirection);
  };
  runtime.onAxisView = (direction) => { activeDirection = direction; };
  for (const [label, direction] of [
    ["+X", [1, 0, 0]], ["−X", [-1, 0, 0]],
    ["+Y", [0, 1, 0]], ["−Y", [0, -1, 0]],
    ["+Z", [0, 0, 1]], ["−Z", [0, 0, -1]],
  ]) {
    $("#axis-views").append(button(label, () => {
      runtime.orientToAxis(direction);
      activeDirection = direction;
    }));
  }
  stageSelect.addEventListener("change", () => {
    runtime.setStage(stageSelect.value);
    focus(activeFocusIds, activeDirection);
  });
  $("#play").addEventListener("click", () => {
    if (runtime.playing) runtime.pause();
    else {
      if (activeFocusIds) focus(null, activeDirection);
      runtime.play();
    }
  });
  runtime.onPlaybackUpdate = (stageId, playing) => {
    $("#play").textContent = playing ? "暂停" : "播放";
    if (stageId) stageSelect.value = stageId;
  };

  const views = $("#views");
  for (const view of runtime.index.views.values()) {
    views.append(button(view.label || view.id,
      () => focus(view.focusInstanceIds, view.direction)));
  }
  if (!runtime.index.views.size) {
    views.append(button("全局", () => focus(null)));
  }
  $("#explode").addEventListener("input", (event) => {
    runtime.setExplosion(Number(event.target.value) / 100);
    $("#explode-value").textContent = `${event.target.value}%`;
  });
  $("#global-opacity").addEventListener("input", (event) => {
    runtime.setGlobalOpacity(Number(event.target.value) / 100);
    $("#global-opacity-value").textContent = `${event.target.value}%`;
  });

  let selectedId = null;
  const inspector = $("#inspector");
  const selectedName = $("#selected-name");
  const selectedSource = $("#selected-source");
  const selectedMount = $("#selected-mount");
  const selectedOpacity = $("#selected-opacity");
  const selectedOpacityValue = $("#selected-opacity-value");
  const mountRelations = new Map((manifest.extensions?.mountRelations || [])
    .map((relation) => [relation.childFrameId, relation]));
  const renderInspector = () => {
    const record = runtime.instances.get(selectedId);
    inspector.hidden = !record;
    if (!record) {
      selectedMount.textContent = "";
      return;
    }
    selectedName.textContent = record.spec.name || record.part.name || selectedId;
    const binding = record.part.componentBindings?.find((item) =>
      item.id === record.spec.componentBindingId);
    selectedSource.textContent = `${record.part.source.file} · ${record.part.file}` +
      (binding ? ` · ${binding.name || binding.id} (${binding.islandId})` : "");
    const selectedFrame = runtime.index.frames.get(record.spec.parentFrameId);
    const relation = mountRelations.get(selectedFrame?.parentFrameId) ||
      mountRelations.get(record.spec.parentFrameId);
    selectedMount.textContent = relation
      ? `挂载关系：${relation.childLabel} ← ${relation.parentLabel} · ${relation.interface}`
      : `挂载关系：${selectedFrame?.parentFrameId || "世界坐标"}`;
    selectedOpacity.value = String(Math.round(record.opacity * 100));
    selectedOpacityValue.textContent = `${selectedOpacity.value}%`;
  };
  selectedOpacity.addEventListener("input", () => {
    runtime.setOpacity(selectedId, Number(selectedOpacity.value) / 100);
    selectedOpacityValue.textContent = `${selectedOpacity.value}%`;
  });
  $("#focus-selected").addEventListener("click", () => focus([selectedId]));
  $("#show-selected").addEventListener("click", () => {
    runtime.setVisible(selectedId, true);
    renderTree();
  });
  $("#hide-selected").addEventListener("click", () => {
    runtime.setVisible(selectedId, false);
    renderTree();
  });

  const tree = $("#tree");
  const frameSpecs = manifest.assembly.frames;
  const byParent = new Map();
  for (const frame of frameSpecs) {
    if (!byParent.has(frame.parentFrameId)) byParent.set(frame.parentFrameId, []);
    byParent.get(frame.parentFrameId).push(frame);
  }
  const recordsByFrame = new Map();
  for (const [instanceId, record] of runtime.instances) {
    const frameId = record.spec.parentFrameId;
    if (!recordsByFrame.has(frameId)) recordsByFrame.set(frameId, []);
    recordsByFrame.get(frameId).push([instanceId, record]);
  }
  const matches = (record) => {
    const group = groupSelect.value;
    const query = $("#search").value.trim().toLocaleLowerCase();
    if (group && record.part.groupId !== group) return false;
    if (!query) return true;
    const binding = record.part.componentBindings?.find((item) =>
      item.id === record.spec.componentBindingId);
    return [record.part.name, record.part.id, record.spec.name, record.spec.id,
      record.part.file, record.part.groupId, binding?.id, binding?.name, binding?.islandId].some((value) =>
      String(value || "").toLocaleLowerCase().includes(query));
  };
  const frameMatches = (frameId) => {
    if ((recordsByFrame.get(frameId) || []).some(([, record]) => matches(record))) return true;
    return (byParent.get(frameId) || []).some((child) => frameMatches(child.id));
  };
  const renderFrame = (frame) => {
    const details = document.createElement("details");
    details.open = true;
    details.className = "frame";
    const summary = document.createElement("summary");
    const label = document.createElement("span");
    label.textContent = frame.label || frame.id;
    summary.append(label);
    const actions = document.createElement("span");
    actions.className = "inline-actions";
    const click = (fn) => (event) => { event.preventDefault(); event.stopPropagation(); fn(); renderTree(); };
    actions.append(button("显", click(() => runtime.setFrameVisible(frame.id, true)), "small"));
    actions.append(button("隐", click(() => runtime.setFrameVisible(frame.id, false)), "small"));
    summary.append(actions);
    details.append(summary);
    const children = document.createElement("div");
    children.className = "tree-children";
    for (const [instanceId, record] of recordsByFrame.get(frame.id) || []) {
      if (!matches(record)) continue;
      const row = document.createElement("div");
      row.className = "instance-row";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = record.visible;
      checkbox.setAttribute("aria-label", `显示 ${instanceId}`);
      checkbox.addEventListener("change", () => runtime.setVisible(instanceId, checkbox.checked));
      const name = record.spec.name || record.part.name || instanceId;
      const inspect = button(name, () => {
        selectedId = instanceId;
        renderInspector();
        focus([instanceId]);
      }, selectedId === instanceId ? "selected part-button" : "part-button");
      row.append(checkbox, inspect);
      children.append(row);
    }
    for (const child of byParent.get(frame.id) || []) {
      if (frameMatches(child.id)) children.append(renderFrame(child));
    }
    details.append(children);
    return details;
  };
  function renderTree() {
    tree.replaceChildren();
    const root = runtime.index.frames.get(runtime.index.rootId);
    if (frameMatches(root.id)) tree.append(renderFrame(root));
    else tree.textContent = "没有匹配的实例";
  }
  groupSelect.addEventListener("change", renderTree);
  $("#search").addEventListener("input", renderTree);
  $("#show-group").addEventListener("click", () => {
    if (groupSelect.value) runtime.setGroupVisible(groupSelect.value, true);
    else for (const instanceId of runtime.instances.keys()) runtime.setVisible(instanceId, true);
    renderTree();
  });
  $("#hide-group").addEventListener("click", () => {
    if (groupSelect.value) runtime.setGroupVisible(groupSelect.value, false);
    else for (const instanceId of runtime.instances.keys()) runtime.setVisible(instanceId, false);
    renderTree();
  });
  renderTree();
  renderInspector();
  status(`${runtime.index.parts.size} 种几何 · ${runtime.instances.size} 个实例 · ${runtime.index.frames.size} 个 frame`);

  const stage = $("#canvas-panel");
  const resize = () => runtime.resize(stage.clientWidth, stage.clientHeight);
  new ResizeObserver(resize).observe(stage);
  resize();
  let last = performance.now();
  const tick = (now) => {
    runtime.tick((now - last) / 1000);
    last = now;
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

main().catch((error) => {
  status(`加载失败：${error.message}`);
  console.error(error);
});
