import {api, districtPath} from './api.mjs';
import {$, all, choices, reportError, showMessage} from './dom.mjs';
import {walkScreen} from './walk.mjs';
import {intakeScreen} from './intake.mjs';
import {channelPanel} from './channel.mjs';
import {reviewPanels} from './release-review.mjs';
import {compilerPanel} from './compiler.mjs';

const district = $('#district');
const banner = $('#app-message');
const walk = walkScreen(banner);
const intake = intakeScreen(refresh, banner);
const review = reviewPanels();
const channel = channelPanel(() => loadDistrict(district.value));
const compiler = compilerPanel(id => loadDistrict(district.value, id));
let epoch = 0;

for (const button of all('[data-screen]')) {
  button.addEventListener('click', () => {
    for (const control of all('[data-screen]')) {
      if (control === button) control.setAttribute('aria-current', 'page');
      else control.removeAttribute('aria-current');
      $(`#${control.dataset.screen}`).hidden = control !== button;
    }
  });
}

function applyDistrict(id, releases, revisions, preferred) {
  review.load(releases);
  compiler(id, revisions, releases[0]);
  return Promise.all([
    channel(id, releases), intake.load(id, revisions), walk.load(releases, preferred),
  ]);
}

async function loadDistrict(id, preferred) {
  const request = ++epoch;
  let releases = [], revisions = [], heads = {};
  if (id) {
    const path = districtPath(id);
    const data = await Promise.all([api(`${path}/releases`), api(`${path}/revisions`), api(`${path}/channels`)]);
    ({releases} = data[0]);
    ({revisions} = data[1]);
    ({heads} = data[2]);
  }
  if (request !== epoch) return;
  await applyDistrict(id, releases, revisions, preferred || heads.public?.release_id || heads.field?.release_id || releases[0]?.id);
}

async function refresh(preferred = district.value) {
  const data = await api('/catalog');
  choices(district, data.districts, row => row.label, row => row.id, preferred);
  walk.configure(data);
  intake.configure(data);
  review.configure(data);
  await loadDistrict(district.value);
}

district.addEventListener('change', () => {
  showMessage(banner);
  applyDistrict('', [], []).catch(error => reportError(banner, error));
  loadDistrict(district.value).catch(error => reportError(banner, error));
});
refresh().catch(error => reportError(banner, error));
