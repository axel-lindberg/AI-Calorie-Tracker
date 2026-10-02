export function renderLog(state, onDelete) {
  const container = document.getElementById('mealLog');
  const { log } = state;

  if (!log.length) {
    container.innerHTML = '<p class="log__empty">Nothing logged yet today — your first entry will show up here.</p>';
    return;
  }

  const meals = new Map();
  for (const row of log) {
    if (!meals.has(row.meal_id)) {
      meals.set(row.meal_id, { raw_text: row.raw_text, logged_at: row.logged_at, items: [] });
    }
    // Meals are LEFT JOINed to their items, so an item-less meal yields
    // one row with null item columns.
    if (row.raw_name != null) {
      meals.get(row.meal_id).items.push(row);
    }
  }

  container.innerHTML = '';
  for (const [mealId, meal] of meals.entries()) {
    const entry = document.createElement('div');
    entry.className = 'log__entry';

    const time = new Date(meal.logged_at).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });

    const itemsHtml = meal.items
      .map((item) => {
        const cal = item.calories != null ? `${Math.round(item.calories)} kcal` : 'no nutrition match';
        return `<li>${escapeHtml(item.raw_name)} — ${cal}</li>`;
      })
      .join('');

    entry.innerHTML = `
      <div class="log__entry-header">
        <p class="log__entry-time">${time}</p>
        <button type="button" class="log__delete" aria-label="Delete this entry">×</button>
      </div>
      <p class="log__entry-text">${escapeHtml(meal.raw_text)}</p>
      <ul class="log__entry-items">${itemsHtml}</ul>
    `;

    entry.querySelector('.log__delete').addEventListener('click', () => {
      if (window.confirm('Delete this entry?')) {
        onDelete(mealId);
      }
    });

    container.appendChild(entry);
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}