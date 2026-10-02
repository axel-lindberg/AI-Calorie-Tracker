import './styles.css';

import { getTodaysTotals, getTodaysLog, deleteMeal } from './api.js';
import { setState, subscribe } from './state.js';
import { renderTotals } from './render/totals.js';
import { renderLog } from './render/log.js';
import { initEntryForm } from './render/entryForm.js';

const logError = document.getElementById('logError');

async function refresh() {
  const [totals, log] = await Promise.all([getTodaysTotals(), getTodaysLog()]);
  setState({ totals, log });
  logError.textContent = '';
}

async function handleDelete(mealId) {
  try {
    await deleteMeal(mealId);
    await refresh();
  } catch (err) {
    logError.textContent = "Couldn't delete that entry — try again.";
    console.error('Failed to delete meal', err);
  }
}

subscribe((state) => {
  renderTotals(state);
  renderLog(state, handleDelete);
});

initEntryForm(refresh);

refresh().catch((err) => {
  logError.textContent = "Couldn't load today's log — is the backend running?";
  console.error('Failed to load today\'s data', err);
});