import {api, districtPath, prefix} from './api.mjs';
import {$, choices, onSubmit, reportError, showMessage} from './dom.mjs';
import {clipped, line, releaseLabel, showTime} from './presentation.mjs';

export function channelPanel(updated) {
  const picker = $('#channel');
  const form = $('#channel-form');
  const history = $('#channel-history');
  const download = $('#channel-download');
  const heading = $('#channel-head');
  const feedback = $('#channel-message');
  let district = '';
  let head = null;
  let epoch = 0;
  const currentPath = () => `${districtPath(district)}/channels/${picker.value}`;

  async function load() {
    const request = ++epoch;
    head = null;
    download.hidden = true;
    heading.textContent = '当前渠道未发布';
    history.replaceChildren();
    if (!district) return;
    const link = currentPath();
    const result = await api(link);
    if (request !== epoch) return;
    head = result.head;
    heading.textContent = `代次 ${head.generation} · ${clipped(head.release_id)}`;
    if (head.release_id) {
      download.href = `${prefix}${link}/export`;
      download.hidden = false;
    }
    history.replaceChildren(...result.events.map(event => line(
      `代次 ${event.generation} · ${event.action === 'publish' ? '发布' : '恢复'} · ${clipped(event.release_id)}`,
      `${event.note} · ${showTime(event.changed_at)}`,
    )));
  }
  picker.addEventListener('change', () => {
    showMessage(feedback);
    load().catch(error => reportError(feedback, error));
  });
  onSubmit(form, async fields => {
    if (!head) return;
    const link = currentPath();
    const payload = {release: fields.release.value, generation: head.generation, action: fields.action.value, note: fields.note.value};
    let changed;
    try {
      changed = await api(link, {payload});
    } catch (error) {
      if (error.status === 409 && link === currentPath()) await load();
      throw error;
    }
    if (link !== currentPath()) return;
    fields.note.value = '';
    showMessage(feedback, `交接完成，渠道推进到第 ${changed.generation} 代。`);
    await load();
    await updated();
  }, error => reportError(feedback, error));

  return (id, releases) => {
    district = id;
    choices(form.elements.release, releases, releaseLabel);
    return load();
  };
}
