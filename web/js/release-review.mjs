import {api, prefix, releasePath} from './api.mjs';
import {$, choices, element, onSubmit, reportError, utc} from './dom.mjs';
import {line, releaseLabel, states} from './presentation.mjs';

const checks = {
  format: '发布格式', identity: '内容编号', body_hash: '内容指纹', topology: '拓扑指纹',
  input_cutoff: '批次与知识截点', compiled_index: '编译索引',
};

export function reviewPanels() {
  const verify = $('#verify-form');
  const compare = $('#compare-form');
  const download = $('#release-download');
  const verifyResult = $('#verify-result');
  const compareResult = $('#compare-result');
  let releases = [];
  let epoch = 0;

  function overlapStart() {
    const pair = [compare.elements.before.value, compare.elements.after.value].map(id => releases.find(row => row.id === id));
    if (pair.every(Boolean)) compare.elements.at.value = pair.map(row => row.start).sort().at(-1).slice(0, 19);
  }
  verify.elements.release.addEventListener('change', () => {
    download.hidden = true;
    verifyResult.replaceChildren();
  });
  for (const selector of [compare.elements.before, compare.elements.after]) selector.addEventListener('change', overlapStart);
  onSubmit(verify, async fields => {
    const request = epoch;
    const id = fields.release.value;
    if (!id) return;
    const link = releasePath(id);
    download.hidden = true;
    const report = await api(`${link}/verify`);
    if (request !== epoch || id !== fields.release.value) return;
    verifyResult.replaceChildren(element('strong', report.verified ? '复核通过' : '发现完整性异常'),
      ...Object.entries(report.checks).map(([key, value]) => line(checks[key], value ? '通过' : '不一致')));
    download.href = `${prefix}${link}/export`;
    download.hidden = !report.verified;
  }, error => reportError(verifyResult, error));

  onSubmit(compare, async fields => {
    const request = epoch;
    const before = fields.before.value;
    const after = fields.after.value;
    if (!before || !after) return;
    const query = {before, at: utc(fields.at.value), profile: fields.profile.value};
    const result = await api(`${releasePath(after)}/compare`, {query});
    if (request !== epoch || after !== fields.after.value || before !== fields.before.value) return;
    compareResult.replaceChildren(element('strong', result.changes.length ? `${result.changes.length} 个方向存在差异` : '当前时点没有差异'));
    for (const change of result.changes) {
      const beforeLabel = states[change.before?.status]?.label || '无此方向';
      const afterLabel = states[change.after?.status]?.label || '无此方向';
      const label = beforeLabel === afterLabel ? `${beforeLabel} · 依据或街段数据变更` : `${beforeLabel} → ${afterLabel}`;
      compareResult.append(line(change.arc, label));
    }
  }, error => reportError(compareResult, error));

  return {
    configure(catalog) {
      choices(compare.elements.profile, Object.entries(catalog.profiles), ([, profile]) => profile.label, ([id]) => id);
    },
    load(rows) {
      epoch++;
      releases = rows;
      verifyResult.replaceChildren();
      compareResult.replaceChildren();
      download.hidden = true;
      choices(verify.elements.release, rows, releaseLabel);
      choices(compare.elements.before, rows, releaseLabel, row => row.id, compare.elements.before.value || rows.at(-1)?.id);
      choices(compare.elements.after, rows, releaseLabel);
      overlapStart();
    },
  };
}
