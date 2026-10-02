// Small in-memory store. No framework needed for this much state - a plain
// object plus a subscribe/notify list is enough for a single-page app with
// two pieces of data (totals, log).

const state = {
  totals: { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0, unmatched_items: 0 },
  log: [],
};

const listeners = new Set();

export function setState(partial) {
  Object.assign(state, partial);
  for (const listener of listeners) {
    listener(state);
  }
}

export function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
