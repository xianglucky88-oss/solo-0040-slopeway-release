import {api} from './api.mjs';
import {$, choices, onSubmit, reportError, showMessage, utc} from './dom.mjs';
import {clipped} from './presentation.mjs';

export function compilerPanel(updated) {
  const form = $('#compile-form');
  const message = $('#compile-message');
  let district = '';

  onSubmit(form, async fields => {
    if (!district || !fields.revision.value) return;
    const payload = {district, revision: Number(fields.revision.value), cutoff: utc(fields.cutoff.value),
      start: utc(fields.start.value), end: utc(fields.end.value)};
    const result = await api('/releases', {payload});
    showMessage(message, `${result.created ? '已封存' : '相同内容已封存'} ${clipped(result.id)}，入选 ${result.feed_count} 个批次。`);
    if (payload.district === district) await updated(result.id);
  }, error => reportError(message, error));

  return (id, revisions, release) => {
    const changed = district !== id;
    district = id;
    if (changed) showMessage(message);
    choices(form.elements.revision, revisions, row => `修订 ${row.revision}`, row => row.revision, changed ? '' : form.elements.revision.value);
    for (const field of ['cutoff', 'start', 'end']) {
      const input = form.elements[field];
      if (changed || !input.value) input.value = release?.[field]?.slice(0, 19) || '';
    }
  };
}
