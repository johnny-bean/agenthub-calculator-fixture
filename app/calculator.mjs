const MAX_SIGNIFICANT_DIGITS = 12;

function roundNumber(value) {
  if (!Number.isFinite(value)) return value;
  if (value === 0) return 0;
  return Number(value.toPrecision(MAX_SIGNIFICANT_DIGITS));
}

function formatNumber(value) {
  if (!Number.isFinite(value)) return 'Error';
  return String(roundNumber(value));
}

export function createCalculator() {
  let display = '0';
  let accumulator = null;
  let operator = null;
  let startNewEntry = true;
  let error = false;

  function reset() {
    display = '0';
    accumulator = null;
    operator = null;
    startNewEntry = true;
    error = false;
    return getState();
  }

  function getState() {
    return {
      display,
      accumulator,
      operator,
      startNewEntry,
      error,
    };
  }

  function setError() {
    display = 'Error';
    accumulator = null;
    operator = null;
    startNewEntry = true;
    error = true;
  }

  function inputDigit(digit) {
    if (!/^\d$/.test(String(digit))) return getState();
    if (error) reset();

    if (startNewEntry) {
      display = String(digit);
      startNewEntry = false;
    } else if (display === '0') {
      display = String(digit);
    } else {
      display += String(digit);
    }
    return getState();
  }

  function decimal() {
    if (error) reset();
    if (startNewEntry) {
      display = '0.';
      startNewEntry = false;
    } else if (!display.includes('.')) {
      display += '.';
    }
    return getState();
  }

  function calculate(left, op, right) {
    switch (op) {
      case '+': return left + right;
      case '-': return left - right;
      case '*': return left * right;
      case '/': return right === 0 ? null : left / right;
      default: return right;
    }
  }

  function applyOperator(nextOperator) {
    if (!['+', '-', '*', '/'].includes(nextOperator) || error) return getState();
    const current = Number(display);
    if (operator !== null && !startNewEntry) {
      const result = calculate(accumulator, operator, current);
      if (result === null || !Number.isFinite(result)) {
        setError();
        return getState();
      }
      accumulator = roundNumber(result);
      display = formatNumber(accumulator);
    } else if (accumulator === null || operator === null) {
      accumulator = current;
    }
    operator = nextOperator;
    startNewEntry = true;
    return getState();
  }

  function equals() {
    if (error || operator === null || accumulator === null) return getState();
    const result = calculate(accumulator, operator, Number(display));
    if (result === null || !Number.isFinite(result)) {
      setError();
      return getState();
    }
    display = formatNumber(result);
    accumulator = null;
    operator = null;
    startNewEntry = true;
    return getState();
  }

  function sign() {
    if (error) return getState();
    const value = -Number(display);
    display = formatNumber(value);
    if (startNewEntry) startNewEntry = false;
    return getState();
  }

  function percent() {
    if (error) return getState();
    display = formatNumber(Number(display) / 100);
    if (startNewEntry) startNewEntry = false;
    return getState();
  }

  function backspace() {
    if (error) return reset();
    if (startNewEntry) return getState();
    display = display.length <= 1 || (display.length === 2 && display.startsWith('-'))
      ? '0'
      : display.slice(0, -1);
    if (display === '-0') display = '0';
    return getState();
  }

  return {
    getState,
    inputDigit,
    decimal,
    applyOperator,
    equals,
    sign,
    percent,
    backspace,
    clear: reset,
  };
}
