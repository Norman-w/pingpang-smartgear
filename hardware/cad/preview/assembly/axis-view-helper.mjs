import * as THREE from "three";

const axes = [
  { label: "X", vector: [1, 0, 0], color: "#ff6177" },
  { label: "Y", vector: [0, 1, 0], color: "#96e76b" },
  { label: "Z", vector: [0, 0, 1], color: "#6aa8ff" },
];

function labelSprite(label, color, direction) {
  const canvas = document.createElement("canvas");
  canvas.width = 96;
  canvas.height = 96;
  const context = canvas.getContext("2d");
  context.fillStyle = color;
  context.beginPath();
  context.arc(48, 48, 38, 0, Math.PI * 2);
  context.fill();
  context.fillStyle = "#101826";
  context.font = "bold 31px sans-serif";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(label, 48, 49);
  const material = new THREE.SpriteMaterial({
    map: new THREE.CanvasTexture(canvas),
    transparent: true,
    depthWrite: false,
  });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(0.48, 0.48, 1);
  sprite.userData.direction = direction;
  return sprite;
}

export class AxisViewHelper {
  constructor(camera, canvas, onSelect) {
    this.camera = camera;
    this.canvas = canvas;
    this.onSelect = onSelect;
    this.size = 132;
    this.bottom = 16;
    this.right = 16;
    this.scene = new THREE.Scene();
    this.root = new THREE.Group();
    this.scene.add(this.root);
    this.widgetCamera = new THREE.OrthographicCamera(-1.4, 1.4, 1.4, -1.4, 0.1, 10);
    this.widgetCamera.position.set(0, 0, 3);
    this.widgetCamera.lookAt(0, 0, 0);
    this.targets = [];
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    for (const axis of axes) {
      const positive = new THREE.Vector3(...axis.vector);
      const points = [positive.clone().multiplyScalar(-0.78), positive.clone().multiplyScalar(0.78)];
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(points),
        new THREE.LineBasicMaterial({ color: axis.color, transparent: true, opacity: 0.75 }),
      );
      this.root.add(line);
      for (const sign of [1, -1]) {
        const direction = positive.clone().multiplyScalar(sign);
        const sprite = labelSprite(sign === 1 ? axis.label : `−${axis.label}`,
          sign === 1 ? axis.color : "#9aa8b8", direction.toArray());
        sprite.position.copy(direction.multiplyScalar(1.02));
        this.root.add(sprite);
        this.targets.push(sprite);
      }
    }
    canvas.addEventListener("pointerdown", (event) => {
      if (this.contains(event)) event.stopImmediatePropagation();
    }, true);
    canvas.addEventListener("click", (event) => {
      if (!this.contains(event)) return;
      this.root.quaternion.copy(this.camera.quaternion).invert();
      this.root.updateMatrixWorld(true);
      const rect = this.rect();
      this.pointer.set(
        ((event.clientX - rect.left) / this.size) * 2 - 1,
        -((event.clientY - rect.top) / this.size) * 2 + 1,
      );
      this.raycaster.setFromCamera(this.pointer, this.widgetCamera);
      const hit = this.raycaster.intersectObjects(this.targets)[0];
      if (hit) this.onSelect(hit.object.userData.direction);
      event.stopImmediatePropagation();
    }, true);
  }

  rect() {
    const canvas = this.canvas.getBoundingClientRect();
    return { left: canvas.right - this.right - this.size,
      top: canvas.bottom - this.bottom - this.size };
  }

  contains(event) {
    const { left, top } = this.rect();
    return event.clientX >= left && event.clientX <= left + this.size &&
      event.clientY >= top && event.clientY <= top + this.size;
  }

  render(renderer) {
    this.root.quaternion.copy(this.camera.quaternion).invert();
    const viewport = renderer.getViewport(new THREE.Vector4());
    const previousAutoClear = renderer.autoClear;
    const x = this.canvas.clientWidth - this.right - this.size;
    const y = this.bottom;
    renderer.autoClear = false;
    renderer.clearDepth();
    renderer.setViewport(x, y, this.size, this.size);
    renderer.render(this.scene, this.widgetCamera);
    renderer.setViewport(viewport.x, viewport.y, viewport.z, viewport.w);
    renderer.autoClear = previousAutoClear;
  }
}
