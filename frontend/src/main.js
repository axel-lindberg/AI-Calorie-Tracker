import './styles.css';

import { getTodaysTotals, getTodaysLog, deleteMeal } from './api.js';
import { setState, subscribe } from './state.js';
import { renderTotals } from './render/totals.js';
import { renderLog } from './render/log.js';
import { initEntryForm } from './render/entryForm.js';

async function refresh() {
  const [totals, log] = await Promise.all([getTodaysTotals(), getTodaysLog()]);
  setState({ totals, log });
}

async function handleDelete(mealId) {
  try {
    await deleteMeal(mealId);
    await refresh();
  } catch (err) {
    console.error('Failed to delete meal', err);
  }
}

subscribe((state) => {
  renderTotals(state);
  renderLog(state, handleDelete);
});

initEntryForm(refresh);

refresh().catch((err) => {
  console.error('Failed to load today\'s data', err);
});