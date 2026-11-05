# Reference X: "Slate" calculator

This file is the UI and behaviour reference for the AH-042 acceptance
objective. It is read-only input for AgentHub; the fixed suite in
`acceptance/` checks it. The picture `reference/calculator.svg` shows the
intended look.

## Layout (portrait, centred, works from 320 px wide)

- One calculator panel, `id="calculator"`, background `#10151c`, rounded
  corners, centred on a page whose background is `#0a0d12`.
- A display, `id="display"`, at the top of the panel: right-aligned text,
  white (`#ffffff`), at least 40 px font size, showing `0` at start.
- Below it, a keypad laid out as a grid of **4 equal columns and 5 rows**:

| col 1 | col 2 | col 3 | col 4 |
| --- | --- | --- | --- |
| AC | ± | % | ÷ |
| 7 | 8 | 9 | × |
| 4 | 5 | 6 | − |
| 1 | 2 | 3 | + |
| 0 | (0, spanned) | . | = |

  The last row is `0` spanning columns 1–2, `.` in column 3 and `=` in
  column 4.
- Every key is a `<button>` with a `data-key` attribute:
  digits `0`–`9`, `.`, `+`, `-`, `*`, `/`, `=`, `clear` (AC),
  `sign` (±) and `percent` (%).
- Colours: digit and `.` keys `#263241`; `clear`, `sign`, `percent`
  `#4a5a6e`; operator keys `/ * - + =` `#e07a2e`. Key text is white.
- Keys are at least 44 × 44 px; no horizontal scrolling at 360 × 640.
- The page loads no external resources (fonts, scripts, CDNs).

## Behaviour

- Immediate execution, left to right like a basic pocket calculator:
  `2 + 3 × 4 =` gives `20`.
- Results are rounded to at most 12 significant digits and shown without
  trailing zeros: `0.1 + 0.2 =` gives `0.3`.
- Division by zero shows `Error`; the next digit starts a new number.
- `AC` resets to `0`. `±` negates the current entry (`5 ±` → `-5`).
  `%` divides the current entry by 100 (`50 %` → `0.5`).
- Pressing an operator twice in a row replaces the pending operator.
- Keyboard: digits, `.`, `+ - * /`, `Enter` or `=` for equals, `Escape`
  for AC, `Backspace` deletes the last typed digit.

## Acceptance checklist

1. Functional: the behaviours above, through clicks and through the keyboard.
2. Visual fidelity: layout, grid, `0` width, colours and sizes above.
3. Self-contained static app under `app/` with `app/index.html` as entry.
4. Unit tests for the calculation logic under `app/` (`*.test.mjs`, Node's
   built-in test runner, no dependencies).
5. Published on GitHub Pages and the published page equals the merged files.
