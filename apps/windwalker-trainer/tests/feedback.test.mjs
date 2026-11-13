import test from 'node:test';
import assert from 'node:assert/strict';
import { critFeedback, channelFeedback } from '../dist/feedback.js';

test('crit feedback separates main and Dawn crits and reports measured cooldown change', () => {
  const event = { crits: 2, dawn: true, mainCrit: true, dawnCrit: true, fistsBefore: 5, fistsAfter: 1.8, reductionSeconds: 3.2 };
  const result = critFeedback(event);
  assert.equal(result.label, '双暴');
  assert.equal(result.parts[0].crit, true);
  assert.equal(result.parts[1].crit, true);
  assert.match(result.cooldown, /3.20/);
  assert.doesNotMatch(result.cooldown, /8秒/);
});

test('Dawn-only crit and absent Dawn are distinct states', () => {
  const dawn = critFeedback({ crits: 1, dawn: true, mainCrit: false, dawnCrit: true, fistsBefore: 9, fistsAfter: 5 });
  assert.equal(dawn.label, '单暴');
  assert.equal(dawn.parts[0].crit, false);
  assert.equal(dawn.parts[1].crit, true);
  const none = critFeedback({ crits: 0, dawn: false, mainCrit: false, dawnCrit: null, fistsBefore: 9, fistsAfter: 9 });
  assert.equal(none.parts[1].label, '晨晖未触发');
});

test('SCK coexistence feedback differs from FoF protection and Conduit cancellation', () => {
  assert.match(channelFeedback({ channel: { skill: 'crane' }, options: { protectCrane: true } }).text, /旭日/);
  assert.match(channelFeedback({ channel: { skill: 'fists' }, options: { inputMode: 'protected' } }).text, /保护/);
  assert.match(channelFeedback({ channel: { skill: 'conduit' }, options: {} }).text, /大青龙/);
});
