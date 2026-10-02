// Shared by the browser and the offline CLI. Keep project dimensions out of this module.
const fail = (where, message) => { throw new Error(`${where}: ${message}`); };
const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const finite = (value) => typeof value === "number" && Number.isFinite(value);
const id = (value, where) => {
  if (typeof value !== "string" || !value.trim()) fail(where, "expected a nonempty ID");
  return value;
};
const vector = (value, where, nonzero = false) => {
  if (!Array.isArray(value) || value.length !== 3 || !value.every(finite)) {
    fail(where, "expected three finite numbers");
  }
  if (nonzero && Math.hypot(...value) === 0) fail(where, "axis/direction cannot be zero");
};
const relativeStl = (value, where) => {
  if (typeof value !== "string" || !/\.stl$/i.test(value) || value.startsWith("/") ||
      value.includes("\\") || value.split("/").some((segment) => segment === ".." || !segment)) {
    fail(where, "expected a safe relative .stl path");
  }
};
const transform = (value, where) => {
  if (!isObject(value)) fail(where, "expected localTransform object");
  vector(value.position, `${where}.position`);
  vector(value.rotation, `${where}.rotation`);
  if ("scale" in value) fail(where, "scale is unsupported; fix units or export geometry");
};
const isIdentity = (value) => value.position.every((n) => n === 0) &&
  value.rotation.every((n) => n === 0);

export function validateManifest(manifest) {
  if (!isObject(manifest) || manifest.schemaVersion !== 1) fail("manifest", "schemaVersion must be 1");
  if (manifest.ui !== undefined && (!isObject(manifest.ui) ||
      ["persistPanelState", "showSearch", "showGroups"].some((key) =>
        manifest.ui[key] !== undefined && typeof manifest.ui[key] !== "boolean"))) {
    fail("ui", "persistPanelState, showSearch, and showGroups must be booleans");
  }
  if (!isObject(manifest.assembly)) fail("assembly", "missing assembly object");
  const { assembly } = manifest;
  const cs = assembly.coordinateSystem;
  if (!isObject(cs) || cs.units !== "mm" || cs.handedness !== "right" ||
      !["x", "y", "z"].includes(cs.up)) {
    fail("assembly.coordinateSystem", "declare units:mm, handedness:right, and up:x/y/z");
  }
  const rootId = id(assembly.rootFrameId, "assembly.rootFrameId");
  if (!Array.isArray(assembly.frames) || !assembly.frames.length) fail("assembly.frames", "empty frame list");
  const frames = new Map();
  for (const frame of assembly.frames) {
    if (!isObject(frame)) fail("assembly.frames", "frame must be an object");
    const frameId = id(frame.id, "frame.id");
    if (frames.has(frameId)) fail(`frame:${frameId}`, "duplicate ID");
    transform(frame.localTransform, `frame:${frameId}.localTransform`);
    const kind = frame.kind || "fixed";
    if (!["fixed", "prismatic", "revolute"].includes(kind)) fail(`frame:${frameId}`, "invalid kind");
    if (kind !== "fixed") {
      vector(frame.axis, `frame:${frameId}.axis`, true);
      if (!Array.isArray(frame.range) || frame.range.length !== 2 ||
          !frame.range.every(finite) || frame.range[0] > frame.range[1]) {
        fail(`frame:${frameId}.range`, "expected [minimum, maximum]");
      }
      if (!finite(frame.defaultValue) || frame.defaultValue < frame.range[0] ||
          frame.defaultValue > frame.range[1]) {
        fail(`frame:${frameId}.defaultValue`, "outside motion range");
      }
    }
    frames.set(frameId, frame);
  }
  if (!frames.has(rootId) || frames.get(rootId).parentFrameId !== null ||
      (frames.get(rootId).kind || "fixed") !== "fixed") {
    fail("assembly.rootFrameId", "root must exist, be fixed, and have parentFrameId:null");
  }
  if (!isIdentity(frames.get(rootId).localTransform)) {
    fail("assembly.rootFrameId", "root transform must be identity");
  }
  const visited = new Set();
  const visiting = new Set();
  const visit = (frameId) => {
    if (visiting.has(frameId)) fail(`frame:${frameId}`, "parent cycle");
    if (visited.has(frameId)) return;
    visiting.add(frameId);
    const parent = frames.get(frameId).parentFrameId;
    if (frameId !== rootId) {
      if (!frames.has(parent)) fail(`frame:${frameId}`, `missing parent ${String(parent)}`);
      visit(parent);
    }
    visiting.delete(frameId);
    visited.add(frameId);
  };
  for (const frameId of frames.keys()) visit(frameId);

  const groups = new Map();
  for (const group of manifest.groups || []) {
    if (!isObject(group)) fail("groups", "group must be an object");
    const groupId = id(group.id, "group.id");
    if (groups.has(groupId)) fail(`group:${groupId}`, "duplicate ID");
    if (typeof group.label !== "string" || !group.label.trim()) fail(`group:${groupId}`, "missing label");
    groups.set(groupId, group);
  }
  if (!Array.isArray(manifest.parts) || !manifest.parts.length) fail("parts", "empty part list");
  const parts = new Map();
  const instances = new Map();
  for (const part of manifest.parts) {
    if (!isObject(part)) fail("parts", "part must be an object");
    const partId = id(part.id, "part.id");
    if (parts.has(partId)) fail(`part:${partId}`, "duplicate ID");
    relativeStl(part.file, `part:${partId}.file`);
    if (!isObject(part.source) || !["scad", "external"].includes(part.source.kind) ||
        typeof part.source.file !== "string" || !part.source.file.trim()) {
      fail(`part:${partId}.source`, "declare source kind and file");
    }
    if (part.source.kind === "scad" &&
        (typeof part.source.selector !== "string" || !part.source.selector.trim())) {
      fail(`part:${partId}.source.selector`, "SCAD exports need a selector or entry module");
    }
    if (part.geometrySpace !== "local" && part.geometrySpace !== "world") {
      fail(`part:${partId}`, "geometrySpace must be local or world");
    }
    if (part.componentMode !== undefined && part.componentMode !== "connected-islands") {
      fail(`part:${partId}.componentMode`, "only connected-islands is supported");
    }
    const bindings = new Map();
    if (part.componentMode === "connected-islands") {
      if (part.geometrySpace !== "local" || !Array.isArray(part.componentBindings) ||
          !part.componentBindings.length) {
        fail(`part:${partId}.componentBindings`, "local geometry and explicit bindings required");
      }
      for (const binding of part.componentBindings) {
        if (!isObject(binding)) fail(`part:${partId}.componentBindings`, "binding must be an object");
        const bindingId = id(binding.id, `part:${partId}.componentBinding.id`);
        if (bindings.has(bindingId)) fail(`part:${partId}.componentBinding:${bindingId}`, "duplicate ID");
        if (typeof binding.islandId !== "string" || !/^ci1-\d+-[0-9a-f]{16}$/.test(binding.islandId)) {
          fail(`part:${partId}.componentBinding:${bindingId}`, "invalid stable island ID");
        }
        if ([...bindings.values()].some((existing) => existing.islandId === binding.islandId)) {
          fail(`part:${partId}.componentBinding:${bindingId}`, "island already bound");
        }
        bindings.set(bindingId, binding);
      }
    } else if (part.componentBindings !== undefined) {
      fail(`part:${partId}.componentBindings`, "componentMode required");
    }
    if (part.role !== undefined && !["printed", "purchased", "diagnostic"].includes(part.role)) {
      fail(`part:${partId}.role`, "expected printed, purchased, or diagnostic");
    }
    if (part.groupId !== undefined && !groups.has(part.groupId)) {
      fail(`part:${partId}`, `unknown group ${String(part.groupId)}`);
    }
    if (part.opacity !== undefined && (!finite(part.opacity) || part.opacity < 0 || part.opacity > 1)) {
      fail(`part:${partId}.opacity`, "expected 0..1");
    }
    if (!Array.isArray(part.instances) || !part.instances.length) fail(`part:${partId}`, "missing instances");
    if (part.geometrySpace === "world" && part.instances.length !== 1) {
      fail(`part:${partId}`, "world STL cannot be repeated");
    }
    for (const instance of part.instances) {
      if (!isObject(instance)) fail(`part:${partId}.instances`, "instance must be an object");
      const instanceId = id(instance.id, `part:${partId}.instance.id`);
      if (instances.has(instanceId)) fail(`instance:${instanceId}`, "duplicate global ID");
      if (part.componentMode === "connected-islands") {
        if (!bindings.has(instance.componentBindingId)) {
          fail(`instance:${instanceId}.componentBindingId`, "unknown component binding");
        }
      } else if (instance.componentBindingId !== undefined) {
        fail(`instance:${instanceId}.componentBindingId`, "componentMode required");
      }
      if (!frames.has(instance.parentFrameId)) fail(`instance:${instanceId}`, "missing parent frame");
      transform(instance.localTransform, `instance:${instanceId}.localTransform`);
      if (instance.explosion !== undefined) vector(instance.explosion, `instance:${instanceId}.explosion`);
      if (part.geometrySpace === "world" &&
          (instance.parentFrameId !== rootId || !isIdentity(instance.localTransform))) {
        fail(`instance:${instanceId}`, "world STL must use root frame and identity transform");
      }
      instances.set(instanceId, { ...instance, part });
    }
    if (part.componentMode === "connected-islands") {
      for (const bindingId of bindings.keys()) {
        if (!part.instances.some((instance) => instance.componentBindingId === bindingId)) {
          fail(`part:${partId}.componentBinding:${bindingId}`, "binding has no instance");
        }
      }
    }
    parts.set(partId, part);
  }

  const moving = [...frames].filter(([, frame]) => frame.kind === "prismatic" ||
    frame.kind === "revolute").map(([frameId]) => frameId);
  const stages = new Map();
  for (const stage of manifest.stages || []) {
    if (!isObject(stage)) fail("stages", "stage must be an object");
    const stageId = id(stage.id, "stage.id");
    if (stages.has(stageId)) fail(`stage:${stageId}`, "duplicate ID");
    if (!isObject(stage.values)) fail(`stage:${stageId}`, "missing values");
    if (Object.keys(stage.values).length !== moving.length ||
        moving.some((frameId) => !Object.hasOwn(stage.values, frameId))) {
      fail(`stage:${stageId}`, "declare a value for every moving frame");
    }
    for (const [frameId, value] of Object.entries(stage.values)) {
      const frame = frames.get(frameId);
      if (!frame || frame.kind === "fixed" || !finite(value) ||
          value < frame.range[0] || value > frame.range[1]) {
        fail(`stage:${stageId}.${frameId}`, "invalid motion value");
      }
    }
    stages.set(stageId, stage);
  }
  if (moving.length && !stages.size) fail("stages", "moving frames require at least one stage");
  if (manifest.playback !== undefined) {
    const playback = manifest.playback;
    if (!isObject(playback) || !Array.isArray(playback.sequence) ||
        playback.sequence.length < 2 || playback.sequence.some((stageId) => !stages.has(stageId)) ||
        !finite(playback.secondsPerTransition) || playback.secondsPerTransition <= 0 ||
        typeof playback.loop !== "boolean") {
      fail("playback", "expected stage sequence, positive secondsPerTransition, and loop boolean");
    }
  }
  const views = new Map();
  for (const view of manifest.views || []) {
    if (!isObject(view)) fail("views", "view must be an object");
    const viewId = id(view.id, "view.id");
    if (views.has(viewId)) fail(`view:${viewId}`, "duplicate ID");
    vector(view.direction, `view:${viewId}.direction`, true);
    if (view.focusInstanceIds !== undefined &&
        (!Array.isArray(view.focusInstanceIds) ||
         view.focusInstanceIds.some((instanceId) => !instances.has(instanceId)))) {
      fail(`view:${viewId}.focusInstanceIds`, "unknown instance");
    }
    views.set(viewId, view);
  }
  if (manifest.motionAdapterModule !== undefined &&
      (typeof manifest.motionAdapterModule !== "string" ||
       !/^\.\/[a-zA-Z0-9_./-]+\.mjs$/.test(manifest.motionAdapterModule) ||
       manifest.motionAdapterModule.split("/").includes(".."))) {
    fail("motionAdapterModule", "expected a safe relative .mjs path starting with ./");
  }
  return { frames, groups, parts, instances, stages, views, rootId };
}
