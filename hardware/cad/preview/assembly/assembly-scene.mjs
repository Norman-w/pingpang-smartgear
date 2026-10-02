import * as THREE from "three";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { validateManifest } from "./manifest-core.mjs";
import { splitConnectedIslands } from "./connected-islands.mjs";
import { AxisViewHelper } from "./axis-view-helper.mjs";

const vec = (xyz) => new THREE.Vector3(...xyz);
const applyTransform = (object, value) => {
  object.position.set(...value.position);
  object.rotation.set(...value.rotation);
};

export class AssemblyScene {
  constructor(canvas, manifest) {
    this.manifest = manifest;
    this.index = validateManifest(manifest);
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color("#111827");
    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100000);
    this.camera.up.set(...({ x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1] })[
      manifest.assembly.coordinateSystem.up
    ]);
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.axisHelper = new AxisViewHelper(this.camera, canvas, (direction) => {
      this.orientToAxis(direction);
      this.onAxisView?.(direction);
    });
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x334155, 2.3));
    const light = new THREE.DirectionalLight(0xffffff, 2.2);
    light.position.set(2, 4, 3);
    this.scene.add(light);
    this.frameNodes = new Map();
    this.instances = new Map();
    this.geometryCache = new Map();
    this.islandCache = new Map();
    this.loader = new STLLoader();
    this.explosion = 0;
    this.globalOpacity = 1;
    this.motionValues = {};
    this.motionAdapter = null;
    this.playing = false;
    this.playInitialized = false;
    this.playIndex = 0;
    this.playElapsed = 0;
    this.timeSeconds = 0;
    this.onPlaybackUpdate = null;
    this.onAxisView = null;
    this.reportedStage = null;
    this.installFrames();
  }

  installFrames() {
    const add = (frameId) => {
      if (this.frameNodes.has(frameId)) return this.frameNodes.get(frameId);
      const spec = this.index.frames.get(frameId);
      const node = new THREE.Group();
      node.name = `frame:${frameId}`;
      applyTransform(node, spec.localTransform);
      node.userData.basePosition = node.position.clone();
      node.userData.baseQuaternion = node.quaternion.clone();
      node.userData.spec = spec;
      if (spec.parentFrameId === null) this.scene.add(node);
      else add(spec.parentFrameId).add(node);
      this.frameNodes.set(frameId, node);
      if (spec.kind === "prismatic" || spec.kind === "revolute") {
        this.motionValues[frameId] = spec.defaultValue;
      }
      return node;
    };
    for (const frameId of this.index.frames.keys()) add(frameId);
    this.applyMotionValues(this.motionValues);
  }

  geometry(file) {
    if (!this.geometryCache.has(file)) {
      this.geometryCache.set(file, this.loader.loadAsync(file));
    }
    return this.geometryCache.get(file);
  }

  async geometryFor(part, instance) {
    if (part.componentMode !== "connected-islands") return this.geometry(part.file);
    if (!this.islandCache.has(part.file)) {
      this.islandCache.set(part.file, this.geometry(part.file).then((whole) => {
        if (whole.index) throw new Error(`${part.file}: indexed STL geometry is unsupported`);
        const positions = whole.getAttribute("position")?.array;
        const components = new Map();
        for (const island of splitConnectedIslands(positions)) {
          const geometry = new THREE.BufferGeometry();
          for (const [name, attribute] of Object.entries(whole.attributes)) {
            const values = new attribute.array.constructor(island.triangleIndices.length * 3 * attribute.itemSize);
            island.triangleIndices.forEach((triangle, index) => {
              const start = triangle * 3 * attribute.itemSize;
              values.set(attribute.array.subarray(start, start + 3 * attribute.itemSize),
                index * 3 * attribute.itemSize);
            });
            geometry.setAttribute(name, new THREE.BufferAttribute(values, attribute.itemSize, attribute.normalized));
          }
          components.set(island.id, geometry);
        }
        return components;
      }));
    }
    const binding = part.componentBindings.find((item) => item.id === instance.componentBindingId);
    const components = await this.islandCache.get(part.file);
    if (part.componentBindings.length !== components.size ||
        part.componentBindings.some((item) => !components.has(item.islandId))) {
      throw new Error(`${part.id}: componentBindings must cover every connected island in ${part.file}`);
    }
    const geometry = components.get(binding.islandId);
    if (!geometry) throw new Error(`${part.id}/${instance.id}: missing island ${binding.islandId}`);
    return geometry;
  }

  async load() {
    await Promise.all(this.manifest.parts.map(async (part) => {
      for (const spec of part.instances) {
        const geometry = await this.geometryFor(part, spec);
        const binding = part.componentMode === "connected-islands"
          ? part.componentBindings.find((item) => item.id === spec.componentBindingId)
          : null;
        const holder = new THREE.Group();
        holder.name = `instance:${spec.id}`;
        applyTransform(holder, spec.localTransform);
        const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({
          color: binding?.color || part.color || "#92b9f0",
          metalness: 0.05,
          roughness: 0.74,
          side: THREE.DoubleSide,
        }));
        holder.add(mesh);
        this.frameNodes.get(spec.parentFrameId).add(holder);
        const record = {
          holder, mesh, part, spec,
          basePosition: holder.position.clone(),
          explosion: vec(spec.explosion || [0, 0, 0]),
          visible: spec.visible !== false,
          opacity: part.opacity ?? 1,
        };
        mesh.visible = record.visible;
        this.instances.set(spec.id, record);
        this.updateOpacity(record);
      }
    }));
    if (this.index.stages.size) this.setStage([...this.index.stages.keys()][0]);
    this.focus(this.manifest.views?.[0]?.focusInstanceIds, this.manifest.views?.[0]?.direction);
  }

  setMotionAdapter(adapter) {
    if (adapter !== null && typeof adapter !== "function") {
      throw new Error("motion adapter must be a function or null");
    }
    this.motionAdapter = adapter;
    this.motionAdapter?.(this, this.timeSeconds, { ...this.motionValues });
  }

  applyMotionValues(values) {
    for (const [frameId, value] of Object.entries(values)) {
      const node = this.frameNodes.get(frameId);
      const spec = node?.userData.spec;
      if (!spec || spec.kind === "fixed") throw new Error(`unknown moving frame: ${frameId}`);
      if (value < spec.range[0] || value > spec.range[1]) {
        throw new Error(`${frameId} motion value outside declared range`);
      }
      const axis = vec(spec.axis).normalize();
      if (spec.kind === "prismatic") {
        node.position.copy(node.userData.basePosition).addScaledVector(axis, value);
      } else {
        node.quaternion.copy(new THREE.Quaternion().setFromAxisAngle(axis, value))
          .multiply(node.userData.baseQuaternion);
      }
    }
    this.motionValues = { ...values };
    this.motionAdapter?.(this, this.timeSeconds, { ...values });
  }

  setStage(stageId) {
    const stage = this.index.stages.get(stageId);
    if (!stage) throw new Error(`unknown stage: ${stageId}`);
    this.pause();
    this.playInitialized = false;
    this.applyMotionValues(stage.values);
    this.reportedStage = stageId;
    this.onPlaybackUpdate?.(stageId, false);
  }

  play() {
    if (!this.manifest.playback) return;
    if (!this.playInitialized) {
      this.playIndex = 0;
      this.playElapsed = 0;
      this.timeSeconds = 0;
      this.applyMotionValues(this.index.stages.get(this.manifest.playback.sequence[0]).values);
      this.playInitialized = true;
    }
    this.playing = true;
    this.reportedStage = this.manifest.playback.sequence[this.playIndex];
    this.onPlaybackUpdate?.(this.reportedStage, true);
  }

  pause() {
    this.playing = false;
    this.onPlaybackUpdate?.(null, false);
  }

  tick(deltaSeconds) {
    const dt = Math.max(0, Math.min(deltaSeconds, 0.1));
    if (this.playing) {
      this.timeSeconds += dt;
      const config = this.manifest.playback;
      const sequence = config.sequence;
      this.playElapsed += dt;
      while (this.playElapsed >= config.secondsPerTransition && this.playing) {
        this.playElapsed -= config.secondsPerTransition;
        this.playIndex += 1;
        if (!config.loop && this.playIndex >= sequence.length - 1) {
          this.applyMotionValues(this.index.stages.get(sequence.at(-1)).values);
          this.pause();
          this.playInitialized = false;
          this.reportedStage = sequence.at(-1);
          this.onPlaybackUpdate?.(sequence.at(-1), false);
        } else this.playIndex %= sequence.length;
      }
      if (this.playing) {
        const a = this.index.stages.get(sequence[this.playIndex]).values;
        const b = this.index.stages.get(sequence[(this.playIndex + 1) % sequence.length]).values;
        const t = this.playElapsed / config.secondsPerTransition;
        const values = Object.fromEntries(Object.keys(a).map((key) => [key, a[key] + (b[key] - a[key]) * t]));
        this.applyMotionValues(values);
        if (this.reportedStage !== sequence[this.playIndex]) {
          this.reportedStage = sequence[this.playIndex];
          this.onPlaybackUpdate?.(this.reportedStage, true);
        }
      }
    }
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
    this.axisHelper.render(this.renderer);
  }

  resize(width, height) {
    this.camera.aspect = width / Math.max(height, 1);
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height, false);
  }

  setVisible(instanceId, visible) {
    const record = this.instances.get(instanceId);
    if (!record) return;
    record.visible = Boolean(visible);
    record.mesh.visible = record.visible;
  }

  setFrameVisible(frameId, visible) {
    const root = this.frameNodes.get(frameId);
    for (const [instanceId, record] of this.instances) {
      let node = record.holder.parent;
      while (node) {
        if (node === root) {
          this.setVisible(instanceId, visible);
          break;
        }
        node = node.parent;
      }
    }
  }

  setGroupVisible(groupId, visible) {
    for (const [instanceId, record] of this.instances) {
      if (record.part.groupId === groupId) this.setVisible(instanceId, visible);
    }
  }

  updateOpacity(record) {
    const opacity = record.opacity * this.globalOpacity;
    record.mesh.material.opacity = opacity;
    record.mesh.material.transparent = opacity < 1;
    record.mesh.material.depthWrite = opacity >= 1;
    record.mesh.material.needsUpdate = true;
  }

  setOpacity(instanceId, opacity) {
    const record = this.instances.get(instanceId);
    if (!record || !Number.isFinite(opacity) || opacity < 0 || opacity > 1) return;
    record.opacity = opacity;
    this.updateOpacity(record);
  }

  setGlobalOpacity(opacity) {
    if (!Number.isFinite(opacity) || opacity < 0 || opacity > 1) return;
    this.globalOpacity = opacity;
    for (const record of this.instances.values()) this.updateOpacity(record);
  }

  setExplosion(fraction) {
    this.explosion = Math.max(0, Math.min(1, fraction));
    for (const record of this.instances.values()) {
      record.holder.position.copy(record.basePosition)
        .addScaledVector(record.explosion, this.explosion);
    }
  }

  focus(instanceIds, direction = [1, 0.75, 1]) {
    this.scene.updateMatrixWorld(true);
    const ids = Array.isArray(instanceIds) && instanceIds.length
      ? instanceIds : [...this.instances.keys()].filter((key) => this.instances.get(key).visible);
    const box = new THREE.Box3();
    for (const instanceId of ids) {
      const record = this.instances.get(instanceId);
      if (record) box.expandByObject(record.mesh);
    }
    if (box.isEmpty()) return;
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const radius = Math.max(size.length() * 0.5, 1);
    const distance = radius / Math.sin(THREE.MathUtils.degToRad(this.camera.fov / 2)) * 1.35;
    this.controls.target.copy(center);
    this.camera.position.copy(center).addScaledVector(vec(direction).normalize(), distance);
    this.camera.near = Math.max(distance / 1000, 0.01);
    this.camera.far = distance * 1000;
    this.camera.updateProjectionMatrix();
    this.controls.update();
  }

  orientToAxis(direction) {
    const axis = vec(direction).normalize();
    const distance = Math.max(this.camera.position.distanceTo(this.controls.target), 1);
    this.camera.position.copy(this.controls.target).addScaledVector(axis, distance);
    this.camera.lookAt(this.controls.target);
    this.controls.update();
  }
}
