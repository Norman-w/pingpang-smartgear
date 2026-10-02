// Stable, order-independent IDs for disconnected triangle shells in an STL.
// Triangles are connected when they share an entire quantized edge.
const numberPattern = "[+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?";
const vertexPattern = new RegExp(`\\bvertex\\s+(${numberPattern})\\s+(${numberPattern})\\s+(${numberPattern})`, "gi");
const textEncoder = new TextEncoder();

export function positionsFromStl(input) {
  const bytes = input instanceof Uint8Array ? input : new Uint8Array(input);
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  if (bytes.byteLength >= 84) {
    const count = view.getUint32(80, true);
    if (count > 0 && 84 + count * 50 === bytes.byteLength) {
      const positions = new Float32Array(count * 9);
      for (let triangle = 0; triangle < count; triangle += 1) {
        const base = 84 + triangle * 50 + 12;
        for (let coordinate = 0; coordinate < 9; coordinate += 1) {
          positions[triangle * 9 + coordinate] = view.getFloat32(base + coordinate * 4, true);
        }
      }
      return positions;
    }
  }
  const text = new TextDecoder().decode(bytes);
  if (!/^\s*solid\b/i.test(text) || !/\bendsolid\b/i.test(text)) {
    throw new Error("STL must be nonempty binary or ASCII STL");
  }
  const coordinates = [];
  for (const match of text.matchAll(vertexPattern)) {
    coordinates.push(Number(match[1]), Number(match[2]), Number(match[3]));
  }
  const facetCount = (text.match(/\bfacet\s+normal\b/gi) || []).length;
  if (!facetCount || coordinates.length !== facetCount * 9 ||
      coordinates.some((value) => !Number.isFinite(value))) {
    throw new Error("ASCII STL has incomplete or invalid triangles");
  }
  return Float32Array.from(coordinates);
}

function fingerprint(canonicalTriangles) {
  let hash = 0xcbf29ce484222325n;
  for (const byte of textEncoder.encode(canonicalTriangles.join(";"))) {
    hash ^= BigInt(byte);
    hash = (hash * 0x100000001b3n) & 0xffffffffffffffffn;
  }
  return hash.toString(16).padStart(16, "0");
}

export function splitConnectedIslands(positions, precisionMm = 0.00001) {
  if (!positions || positions.length === 0 || positions.length % 9 !== 0 ||
      !Number.isFinite(precisionMm) || precisionMm <= 0) {
    throw new Error("expected nonempty triangle positions and positive precision");
  }
  const triangleCount = positions.length / 9;
  const parent = Array.from({ length: triangleCount }, (_, index) => index);
  const root = (index) => {
    while (parent[index] !== index) {
      parent[index] = parent[parent[index]];
      index = parent[index];
    }
    return index;
  };
  const join = (a, b) => { parent[root(a)] = root(b); };
  const edgeOwner = new Map();
  const triangleKeys = [];
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    const vertices = [];
    for (let vertex = 0; vertex < 3; vertex += 1) {
      const offset = triangle * 9 + vertex * 3;
      const coordinates = [0, 1, 2].map((axis) => {
        const value = positions[offset + axis];
        const quantized = Math.round(value / precisionMm);
        if (!Number.isFinite(value) || !Number.isSafeInteger(quantized)) {
          throw new Error(`triangle ${triangle} has invalid coordinates`);
        }
        return quantized;
      });
      vertices.push(coordinates.join(","));
    }
    triangleKeys.push([...vertices].sort().join("|"));
    for (const [a, b] of [[0, 1], [1, 2], [2, 0]]) {
      const edge = [vertices[a], vertices[b]].sort().join("|");
      if (edgeOwner.has(edge)) join(triangle, edgeOwner.get(edge));
      else edgeOwner.set(edge, triangle);
    }
  }
  const byRoot = new Map();
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    const componentRoot = root(triangle);
    if (!byRoot.has(componentRoot)) byRoot.set(componentRoot, []);
    byRoot.get(componentRoot).push(triangle);
  }
  const islands = [...byRoot.values()].map((triangleIndices) => {
    const keys = triangleIndices.map((index) => triangleKeys[index]).sort();
    const bounds = { min: [Infinity, Infinity, Infinity], max: [-Infinity, -Infinity, -Infinity] };
    for (const triangle of triangleIndices) {
      for (let coordinate = 0; coordinate < 9; coordinate += 1) {
        const axis = coordinate % 3;
        const value = positions[triangle * 9 + coordinate];
        bounds.min[axis] = Math.min(bounds.min[axis], value);
        bounds.max[axis] = Math.max(bounds.max[axis], value);
      }
    }
    return {
      id: `ci1-${triangleIndices.length}-${fingerprint(keys)}`,
      triangleIndices,
      bounds,
    };
  }).sort((a, b) => a.id.localeCompare(b.id));
  if (new Set(islands.map((island) => island.id)).size !== islands.length) {
    throw new Error("indistinguishable connected islands; split the source STL");
  }
  return islands;
}
