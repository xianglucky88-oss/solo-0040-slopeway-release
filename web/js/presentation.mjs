import {element} from './dom.mjs';

export const states = {
  passable: {label: '可通行', color: '#43765a'},
  restricted: {label: '条件不符', color: '#a26524'},
  closed: {label: '临时封闭', color: '#aa513e'},
  unknown: {label: '缺少量测', color: '#727d76'},
  conflict: {label: '证据冲突', color: '#885783'},
  route: {label: '选中路线', color: '#123e34'},
};
export const direction = value => value === 'ab' ? 'A→B' : 'B→A';
export const clipped = value => value ? value.slice(3, 13) : '未发布';
export const releaseLabel = row => `修订 ${row.revision} · ${row.start.slice(0, 16).replace('T', ' ')} · ${clipped(row.id)}`;
export const showTime = value => `${value.slice(0, 19).replace('T', ' ')} UTC`;

export function legend(container) {
  container.replaceChildren(...Object.values(states).map(state => {
    const swatch = element('i');
    swatch.style.backgroundColor = state.color;
    const item = element('span');
    item.append(swatch, document.createTextNode(state.label));
    return item;
  }));
}

export function line(primary, secondary) {
  const item = element('div', '', 'log-line');
  item.append(element('strong', primary), element('span', secondary));
  return item;
}
