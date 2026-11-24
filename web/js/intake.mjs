import {api, districtPath} from './api.mjs';
import {$, choices, element, onSubmit, reportError, showMessage} from './dom.mjs';
import {line, showTime} from './presentation.mjs';

export function intakeScreen(refresh, banner) {
  const form = $('#intake-form');
  const file = $('#intake-file');
  const feedback = $('#intake-message');
  const picker = $('#revisions');
  const history = $('#feed-history');
  let district = '';
  let sourceNames = new Map();
  let epoch = 0;

  async function loadFeeds() {
    const request = ++epoch;
    history.replaceChildren();
    if (!district || !picker.value) return;
    const {feeds} = await api(`${districtPath(district)}/revisions/${picker.value}/feeds`);
    if (request !== epoch) return;
    history.replaceChildren(...feeds.map(row => {
      const type = row.kind === 'survey' ? '量测' : '通告';
      return line(`${row.batch} · ${type} ${row.count} 条`, `${sourceNames.get(row.source) || row.source} · ${showTime(row.reported_at)}`);
    }));
    if (!feeds.length) history.append(line('该修订尚无证据批次', ''));
  }

  picker.addEventListener('change', () => loadFeeds().catch(error => reportError(banner, error)));
  file.addEventListener('change', async () => {
    const selected = file.files[0];
    if (!selected) return;
    try {
      if (selected.size > 1_048_576) {
        showMessage(feedback, '请求超过 1 MiB。', true);
        return;
      }
      const contents = await selected.text();
      if (file.files[0] === selected) form.elements.payload.value = contents;
      showMessage(feedback);
    } catch (error) {
      reportError(feedback, error);
    }
  });

  onSubmit(form, async fields => {
    showMessage(feedback);
    const result = await api(`/${fields.kind.value}`, {payload: fields.payload.value});
    const description = fields.kind.value === 'topologies' ? `已登记拓扑修订 ${result.revision}。`
      : result.replayed ? `批次 ${result.batch} 已登记，共 ${result.count} 条。` : `批次 ${result.batch} 已入库，共 ${result.count} 条。`;
    showMessage(feedback, description);
    await refresh(result.district || district);
  }, error => reportError(feedback, error));

  return {
    configure({sources}) {
      sourceNames = new Map(sources.map(row => [row.id, row.label]));
      $('#source-list').replaceChildren(...sources.map(row => element('li', `${row.label}（${row.id}）`)));
    },
    load(id, revisions) {
      district = id;
      choices(picker, revisions, row => `修订 ${row.revision}`, row => row.revision);
      return loadFeeds();
    },
  };
}
