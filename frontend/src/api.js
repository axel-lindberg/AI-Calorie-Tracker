// All backend calls live here. Nothing else in the app touches fetch()
// directly - keeps auth headers, base URLs, and error handling in one place.

const API_URL = import.meta.env.VITE_API_URL;

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`Request to ${path} failed with status ${res.status}`);
  }

  return res.json();
}

export function logMeal(text) {
  return request('/meals', {
    method: 'POST',
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
