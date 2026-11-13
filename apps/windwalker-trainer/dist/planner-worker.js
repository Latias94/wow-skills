import { Combat } from './combat.js';
import { createPlan } from './planner.js';

export function handlePlannerMessage({ revision, state, settings } = {}) {
  try {
    if (!state || !Number.isFinite(state.time) || !state.options || !Array.isArray(state.pending)) {
      throw new TypeError('Planner worker requires a saved current Combat state');
    }
    return { revision, ...createPlan(Combat.fromState(state), settings) };
  } catch (error) {
    return { revision, error: error instanceof Error ? error.message : String(error) };
  }
}

// A module worker only; importing this module in tests requires no DOM.
if (typeof WorkerGlobalScope !== 'undefined' && globalThis instanceof WorkerGlobalScope) {
  globalThis.addEventListener('message', event => {
    globalThis.postMessage(handlePlannerMessage(event.data));
  });
}
