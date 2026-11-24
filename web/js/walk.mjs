import {api, releasePath} from './api.mjs';
import {$, choices, onSubmit, reportError, showMessage, utc} from './dom.mjs';
import {clipped, direction, legend, releaseLabel} from './presentation.mjs';
import {streetMap} from './map.mjs';
import {renderRoute} from './route-view.mjs';
import {renderEvidence} from './evidence-view.mjs';

export function walkScreen(message) {
  const form = $('#preview-form');
  const routeForm = $('#route-form');
  const arcPicker = $('#arc-picker');
  const workbench = $('#walk-workbench');
  const routeResult = $('#route-result');
  const evidence = $('#arc-evidence');
  const draw = streetMap($('#street-map'));
  legend($('#map-legend'));
  let view = null;
  let releases = [];
  let previewEpoch = 0;
  let traceEpoch = 0;

  async function loadEvidence(id) {
    if (!view) return;
    arcPicker.value = id;
    const capture = view;
    const request = ++traceEpoch;
    const row = await api(`${releasePath(capture.id)}/arcs/${id}`, {query: {at: capture.at, profile: capture.profile}});
    if (capture === view && request === traceEpoch) renderEvidence(evidence, row);
  }

  async function preview(fields) {
    if (!fields.release.value) return;
    const request = ++previewEpoch;
    const release = fields.release.value;
    const query = {at: utc(fields.at.value), profile: fields.profile.value};
    const data = await api(`${releasePath(release)}/overview`, {query});
    if (request !== previewEpoch) return;
    const sameDistrict = view?.topology.district === data.topology.district;
    view = data;
    workbench.hidden = false;
    $('#walk-empty').hidden = true;
    $('#release-badge').textContent = `修订 ${data.topology.revision} · ${clipped(data.id)}`;
    $('#map-title').textContent = `${data.topology.label}通行图`;
    $('#map-summary').textContent = `${data.topology.nodes.length} 个节点 · ${data.coverage.direction_count} 个方向`;
    const {unknown, conflict} = data.coverage.evidence;
    $('#gap-summary').textContent = `${unknown} 个方向缺量测 · ${conflict} 个方向存在冲突`;
    const {origin, target} = routeForm.elements;
    const nodes = data.topology.nodes;
    choices(origin, nodes, node => node.label, node => node.id, sameDistrict ? origin.value : nodes[0].id);
    choices(target, nodes, node => node.label, node => node.id, sameDistrict ? target.value : nodes.at(-1).id);
    const segments = new Map(data.topology.segments.map(row => [row.id, row.label]));
    choices(arcPicker, data.sections, row => `${segments.get(row.segment)} · ${direction(row.direction)}`);
    evidence.replaceChildren();
    routeResult.replaceChildren();
    showMessage(message);
    draw(data);
    if (arcPicker.value) await loadEvidence(arcPicker.value);
  }

  function chooseTime() {
    const selected = releases.find(row => row.id === form.elements.release.value);
    if (selected) form.elements.at.value = selected.start.slice(0, 19);
  }

  arcPicker.addEventListener('change', () => loadEvidence(arcPicker.value).catch(error => reportError(message, error)));
  form.elements.release.addEventListener('change', chooseTime);
  onSubmit(form, preview, error => reportError(message, error));
  onSubmit(routeForm, async fields => {
    const capture = view;
    if (!capture) return;
    const query = {at: capture.at, profile: capture.profile, origin: fields.origin.value, target: fields.target.value};
    const result = await api(`${releasePath(capture.id)}/route`, {query});
    if (capture !== view) return;
    showMessage(message);
    renderRoute(routeResult, result, capture, id => loadEvidence(id).catch(error => reportError(message, error)));
    draw(capture, result);
  }, error => reportError(message, error));

  return {
    configure(catalog) {
      choices(form.elements.profile, Object.entries(catalog.profiles), ([, profile]) => profile.label, ([id]) => id);
    },
    async load(rows, preferred) {
      previewEpoch++;
      view = null;
      releases = rows;
      choices(form.elements.release, rows, releaseLabel, row => row.id, preferred);
      workbench.hidden = true;
      $('#walk-empty').hidden = rows.length > 0;
      $('#release-badge').textContent = '';
      chooseTime();
      if (rows.length) await preview(form.elements);
    },
  };
}
