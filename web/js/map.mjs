import {plot, parallelOffsets} from './geometry.mjs';
import {states} from './presentation.mjs';

function grid(ctx, width, height) {
  ctx.fillStyle = '#cbd7c6';
  for (let x = 14; x < width; x += 18) {
    for (let y = 14; y < height; y += 18) {
      ctx.fillRect(x, y, 1, 1);
    }
  }
}

function path(ctx, a, b, color, selected, offset) {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const length = Math.hypot(dx, dy);
  if (length < 1) return;
  ctx.save();
  ctx.translate(a.x, a.y);
  ctx.rotate(Math.atan2(dy, dx));
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = selected ? 5 : 2.4;
  if (!selected && color === states.unknown.color) ctx.setLineDash([4, 3]);
  ctx.beginPath();
  ctx.moveTo(0, offset);
  ctx.lineTo(length, offset);
  ctx.stroke();
  const end = length * .64;
  ctx.beginPath();
  ctx.moveTo(end + 5, offset);
  ctx.lineTo(end - 4, offset - 4);
  ctx.lineTo(end - 4, offset + 4);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function nodesLayer(ctx, points, ends, height) {
  ctx.font = '12px system-ui, sans-serif';
  ctx.textAlign = 'center';
  for (const node of points.values()) {
    const endpoint = ends.has(node.id);
    ctx.fillStyle = endpoint ? '#123e34' : '#fffefa';
    ctx.strokeStyle = '#245a44';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(node.x, node.y, endpoint ? 7 : 4, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
    const labelY = node.y + (node.y > height * .75 ? 24 : -14);
    ctx.strokeStyle = '#edf1e7';
    ctx.lineWidth = 4;
    ctx.strokeText(node.label, node.x, labelY);
    ctx.fillStyle = '#263f30';
    ctx.fillText(node.label, node.x, labelY);
  }
}

export function streetMap(canvas) {
  let scene = null;
  function repaint() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (!scene || !width || !height) return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    const ctx = canvas.getContext('2d');
    ctx.scale(ratio, ratio);
    grid(ctx, width, height);
    const {topology, sections, selected, ends} = scene;
    const points = plot(topology.nodes, width, height);
    const offsets = parallelOffsets(topology.segments);
    const paint = (section, highlighted) => {
      const a = points.get(section.start);
      const b = points.get(section.end);
      const displacement = offsets.get(section.segment) * (a.id < b.id ? 1 : -1);
      path(ctx, a, b, states[highlighted ? 'route' : section.status].color, highlighted, 3 + displacement);
    };
    sections.forEach(section => paint(section, false));
    sections.filter(section => selected.has(section.id)).forEach(section => paint(section, true));
    nodesLayer(ctx, points, ends, height);
  }
  new ResizeObserver(repaint).observe(canvas);
  return (overview, route = null) => {
    scene = {
      ...overview,
      selected: new Set(route?.steps?.map(step => step.id)),
      ends: new Set(route ? [route.origin, route.target] : []),
    };
    repaint();
  };
}
