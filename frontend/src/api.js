// All backend calls live here. Nothing else in the app touches fetch()
// directly - keeps auth headers, base URLs, and error handling in one place.

const API_URL = import.meta.env.VITE_API_URL;

if (!API_URL) {
  console.error('VITE_API_URL is not set - copy frontend/.env.example to frontend/.env.');
}

// Thrown for non-2xx responses. `detail` carries FastAPI's error message
// when it is a plain string, so the UI can show something specific.
export class ApiError extends Error {
  constructor(path, status, detail) {
    super(`Request to ${path} failed with status ${status}`);
    this.status = status;
    this.detail = typeof detail === 'string' ? detail : null;
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, options);

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(path, res.status, body.detail);
  }

  return res.json();
}

export function logMeal(text) {
  return request('/meals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
}

export function deleteMeal(mealId) {
  return request(`/meals/${mealId}`, {
    method: 'DELETE',
  });
}

export function getTodaysTotals() {
  return request('/today/totals');
}

export function getTodaysLog() {
  return request('/today/log');
}
