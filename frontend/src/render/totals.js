export function renderTotals(state) {
  const { totals } = state;

  document.getElementById('totalCalories').textContent = `${Math.round(totals.calories)} kcal`;
  document.getElementById('totalProtein').textContent = `${Math.round(totals.protein_g)} g`;
  document.getElementById('totalCarbs').textContent = `${Math.round(totals.carbs_g)} g`;
  document.getElementById('totalFat').textContent = `${Math.round(totals.fat_g)} g`;

  // Items without a USDA match contribute nothing to the sums above, so
  // say so rather than letting the totals look silently low.
  const unmatched = totals.unmatched_items ?? 0;
  let note = '';
  if (unmatched === 1) {
    note = "1 item has no nutrition match and isn't counted.";
  } else if (unmatched > 1) {
    note = `${unmatched} items have no nutrition match and aren't counted.`;
  }
  document.getElementById('totalsNote').textContent = note;
}
