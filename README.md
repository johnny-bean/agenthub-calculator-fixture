# AgentHub calculator fixture (disposable)

Acceptance fixture for [AgentHub AH-042](https://github.com/johnny-bean/agenthub/issues/123).
It is owned by AgentHub, holds no secrets and may be deleted after the proof.

- `reference/` - reference X: the UI and behaviour the objective must match.
- `acceptance/` - fixed checks: `smoke.py` on every PR, `test_calculator.py`
  (headless Chromium) on `main`.
- `.github/workflows/app.yml` - fixed gate: `app-test` (PR), then
  `acceptance` and `deploy` (GitHub Pages) on `main`.
- `app/` - the only directory AgentHub agents may write.

Delivery URL: https://johnny-bean.github.io/agenthub-calculator-fixture/
