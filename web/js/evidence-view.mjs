import {element} from './dom.mjs';
import {line, showTime, states} from './presentation.mjs';

const phases = {future: '尚未生效', expired: '已失效', effective: '有效'};
const rules = {width: '净宽不足', uphill: '上坡过陡', downhill: '下坡过陡', step: '台阶过高'};

function metric(label, data) {
  const item = element('div', '', 'metric');
  item.append(element('span', label), element('strong', data));
  return item;
}

export function renderEvidence(target, row) {
  const summary = element('p', states[row.status].label, 'tag');
  const measures = row.evidence.measurement;
  const metrics = element('div', '', 'evidence-lines');
  if (measures) {
    metrics.append(metric('净宽', `${measures.width_mm} 毫米`),
      metric('有符号坡度', `${measures.grade_permille} ‰`), metric('台阶', `${measures.step_mm} 毫米`));
  } else {
    metrics.append(metric('量测结论', row.evidence.status === 'conflict' ? '同优先级量测互相矛盾' : '没有有效量测'));
  }
  target.replaceChildren(summary, metrics);
  for (const entry of row.violations) {
    target.append(line(rules[entry.rule], `量测 ${entry.actual} · 条件界限 ${entry.limit}`));
  }
  for (const event of row.closures) {
    target.append(line(event.reason, `${showTime(event.start)} — ${showTime(event.end)}`));
  }
  const reports = [...row.reports.survey, ...row.reports.notice];
  if (reports.length) {
    const detail = element('details', '', 'inline-details');
    detail.append(element('summary', `报送依据（${reports.length}）`));
    for (const item of reports) {
      const adopted = row.evidence.selected.includes(item.ref) ? ' · 入选依据' : '';
      detail.append(line(item.ref, `${phases[item.phase]}${adopted} · 报送 ${showTime(item.reported_at)}`));
    }
    target.append(detail);
  }
}
