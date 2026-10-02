import { ApiError, logMeal } from '../api.js';
import { initSpeechInput } from './speechInput.js';

// onLogged is called after a successful log, so main.js can decide how to
// refresh state (currently: refetch totals + log from the backend).
export function initEntryForm(onLogged) {
  const textarea = document.getElementById('meal-input');
  const button = document.getElementById('logButton');
  const errorEl = document.getElementById('formError');
  const micButton = document.getElementById('micButton');
  const micStatus = document.getElementById('micStatus');

  const speech = initSpeechInput({ textarea, micButton, statusEl: micStatus });

  button.addEventListener('click', async () => {
    speech.stop();
    const text = textarea.value.trim();
    if (!text) return;

    button.disabled = true;
    button.textContent = 'Logging…';
    errorEl.textContent = '';

    try {
      // The pipeline (parse -> USDA lookup -> gram estimate) takes a
      // couple of seconds; the disabled/loading state covers that.
      await logMeal(text);
      textarea.value = '';
      await onLogged();
    } catch (err) {
      errorEl.textContent =
        err instanceof ApiError && err.status === 422 && err.detail
          ? err.detail
          : "Couldn't log that meal — try again.";
      console.error(err);
    } finally {
      button.disabled = false;
      button.textContent = 'Log meal';
    }
  });
}
