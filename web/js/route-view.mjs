import {element} from './dom.mjs';
import {direction, states} from './presentation.mjs';

function sectionLabel(row, overview) {
  const section = overview.topology.segments.find(segment => segment.id === row.segment);
  return `${section.label} ${direction(row.direction)}`;
}

export function renderRoute(target, result, overview, selectArc) {
  if (result.status === 'unreachable') {
    const title = element('p', `当前条件下无可通行路线。已确认可达 ${result.reachable.length} 个节点。`);
    target.replaceChildren(title);
    if (result.boundary.length) {
      const list = element('ul', '', 'route-list');
      for (const row of result.boundary) {
        const item = element('li');
        const button = element('button', `${sectionLabel(row, overview)} · ${states[row.status].label}`, 'link-button');
        button.addEventListener('click', () => selectArc(row.id));
        item.append(button);
        list.append(item);
      }
      target.append(list);
    }
    return;
  }
  const distance = element('p', `${result.distance_m} 米`, 'route-total');
  const list = element('ol', '', 'route-list');
  for (const step of result.steps) {
    const item = element('li');
    const button = element('button', `${sectionLabel(step, overview)} · ${step.length_m} 米`, 'link-button');
    button.addEventListener('click', () => selectArc(step.id));
    item.append(button);
    list.append(item);
  }
  target.replaceChildren(distance, result.steps.length ? list : element('p', '起点和终点相同。'));
}
