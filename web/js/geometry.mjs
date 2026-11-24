export function plot(nodes, width, height) {
  const minX = Math.min(...nodes.map(node => node.x));
  const maxX = Math.max(...nodes.map(node => node.x));
  const minY = Math.min(...nodes.map(node => node.y));
  const maxY = Math.max(...nodes.map(node => node.y));
  const paddingX = Math.min(73, width * .17);
  const paddingY = Math.min(57, height * .19);
  const scale = Math.min((width - paddingX * 2) / (maxX - minX || 1), (height - paddingY * 2) / (maxY - minY || 1));
  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;
  const locations = new Map();
  for (const node of nodes) {
    const key = `${node.x}:${node.y}`;
    if (!locations.has(key)) locations.set(key, []);
    locations.get(key).push(node);
  }
  const points = new Map();
  for (const group of locations.values()) {
    const radius = group.length > 1 ? 12 : 0;
    group.forEach((node, index) => {
      const angle = index * Math.PI * 2 / group.length;
      points.set(node.id, {
        ...node,
        x: width / 2 + (node.x - centerX) * scale + radius * Math.cos(angle),
        y: height / 2 + (node.y - centerY) * scale + radius * Math.sin(angle),
      });
    });
  }
  return points;
}

export function parallelOffsets(segments) {
  const groups = new Map();
  for (const segment of segments) {
    const key = [segment.a, segment.b].sort().join(':');
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(segment);
  }
  const offsets = new Map();
  for (const group of groups.values()) {
    group.forEach((segment, index) => offsets.set(segment.id, (index - (group.length - 1) / 2) * 13));
  }
  return offsets;
}
