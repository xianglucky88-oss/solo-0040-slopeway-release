export const $ = (selector, root = document) => root.querySelector(selector);
export const all = selector => [...document.querySelectorAll(selector)];

export function element(tag, value = '', className = '') {
  const result = document.createElement(tag);
  result.textContent = value;
  if (className) result.className = className;
  return result;
}

export function choices(select, records, label, value = item => item.id, preferred = select.value) {
  select.replaceChildren(...records.map(item => new Option(label(item), value(item))));
  if (records.some(item => String(value(item)) === String(preferred))) select.value = preferred;
  select.disabled = records.length === 0;
}

export function utc(value) {
  return value ? `${value}${value.length === 16 ? ':00' : ''}Z` : '';
}

export function showMessage(target, value = '', isError = false) {
  target.textContent = value;
  target.hidden = !value;
  target.dataset.error = isError;
}

export function reportError(target, error) {
  const fields = error.data || {};
  const suffix = [fields.row, fields.segment, fields.field].filter(Boolean).join(' / ');
  showMessage(target, `${error.status ? error.message : '页面请求未能完成，请重试。'}${suffix ? `（${suffix}）` : ''}`, true);
}

export function onSubmit(form, run, onError) {
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = $('button[type="submit"]', form);
    if (button.disabled) return;
    button.disabled = true;
    try {
      await run(form.elements);
    } catch (error) {
      onError(error);
    } finally {
      button.disabled = false;
    }
  });
}
