export const prefix = '/api/slopeway';
export const districtPath = district => `/districts/${district}`;
export const releasePath = id => `/releases/${id}`;

export async function api(path, {query, payload} = {}) {
  const suffix = query ? `?${new URLSearchParams(query)}` : '';
  const settings = payload === undefined ? {} : {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: typeof payload === 'string' ? payload : JSON.stringify(payload),
  };
  const response = await fetch(`${prefix}${path}${suffix}`, settings);
  const data = await response.json();
  if (!response.ok) {
    throw Object.assign(new Error(data.message || '请求失败。'), {data, status: response.status});
  }
  return data;
}
