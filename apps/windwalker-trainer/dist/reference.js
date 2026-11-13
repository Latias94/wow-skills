import { Combat } from './combat.js';
import { referenceDecision, POLICY } from './policy.js';

export function performReference(combat) {
  const d = referenceDecision(combat);
  if (!d.skill) return false;
  if (d.skill === 'cancel') return combat.cancel({ source: 'reference', decision: d });
  return combat.cast(d.skill, { source: 'reference' }).ok;
}

export function buildReference(options = {}) {
  const combat = new Combat(options);
  const invalidActions = advanceReference(combat, combat.options.duration);
  return { options: combat.options, policy: POLICY, casts: combat.casts, controls: combat.controls,
    fistsOpportunities: combat.fistsOpportunities, summary: combat.summary(), invalidActions };
}

export function advanceReference(combat, seconds) {
  const end = Math.min(combat.options.duration, combat.time + seconds);
  let invalidActions = 0;
  let iterations = 0;
  while (combat.time < end - 1e-7) {
    if (++iterations > 30000) throw new Error('Reference exceeded its bounded simulation budget');
    const d = referenceDecision(combat);
    if (d.skill) {
      if (!performReference(combat)) invalidActions++;
    } else {
      // Stop at engine events so the replay does not depend on UI frame rate.
      combat.advance(Math.min(end - combat.time, d.wait || 0.05, combat.nextBoundary() - combat.time));
    }
  }
  return invalidActions;
}
