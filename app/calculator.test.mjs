import test from 'node:test';
import assert from 'node:assert/strict';
import { createCalculator } from './calculator.mjs';

function enter(calc, text) {
  for (const char of text) {
    if (char === '.') calc.decimal();
    else calc.inputDigit(char);
  }
}

test('executes operations left to right', () => {
  const calc = createCalculator();
  enter(calc, '2'); calc.applyOperator('+'); enter(calc, '3');
  calc.applyOperator('*'); enter(calc, '4'); calc.equals();
  assert.equal(calc.getState().display, '20');
});

test('rounds to twelve significant digits', () => {
  const calc = createCalculator();
  enter(calc, '0.1'); calc.applyOperator('+'); enter(calc, '0.2'); calc.equals();
  assert.equal(calc.getState().display, '0.3');
  calc.clear(); enter(calc, '1'); calc.applyOperator('/'); enter(calc, '3'); calc.equals();
  assert.equal(calc.getState().display, '0.333333333333');
});

test('division by zero enters error state and next digit starts over', () => {
  const calc = createCalculator();
  enter(calc, '8'); calc.applyOperator('/'); enter(calc, '0'); calc.equals();
  assert.equal(calc.getState().display, 'Error');
  calc.inputDigit('7');
  assert.equal(calc.getState().display, '7');
  assert.equal(calc.getState().error, false);
});

test('clear resets all pending calculation state', () => {
  const calc = createCalculator();
  enter(calc, '9'); calc.applyOperator('+'); calc.clear();
  assert.deepEqual(calc.getState(), {
    display: '0', accumulator: null, operator: null, startNewEntry: true, error: false,
  });
});

test('sign and percent transform the current entry', () => {
  const calc = createCalculator();
  enter(calc, '5'); calc.sign();
  assert.equal(calc.getState().display, '-5');
  calc.percent();
  assert.equal(calc.getState().display, '-0.05');
});

test('a repeated operator replaces the pending operator', () => {
  const calc = createCalculator();
  enter(calc, '8'); calc.applyOperator('+'); calc.applyOperator('*');
  enter(calc, '3'); calc.equals();
  assert.equal(calc.getState().display, '24');
});

test('decimal and backspace edit the current entry', () => {
  const calc = createCalculator();
  enter(calc, '12'); calc.decimal(); enter(calc, '5'); calc.backspace();
  assert.equal(calc.getState().display, '12.');
});
