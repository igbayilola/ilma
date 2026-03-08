
# ILMA QA Pipeline

This project includes a comprehensive testing suite covering Unit, Integration, and E2E layers.

## 1. Setup

Ensure you have the testing dependencies installed:

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom @vitejs/plugin-react vitest-axe
npm install -D @playwright/test
```

## 2. Unit & Integration Tests (Vitest)

These tests cover component logic, store state, and accessibility of individual components.

**Run Tests:**
```bash
npx vitest run
```

**Watch Mode (Dev):**
```bash
npx vitest
```

**Coverage Report:**
```bash
npx vitest run --coverage
```

## 3. End-to-End Tests (Playwright)

These tests simulate real user scenarios in a browser instance (Chromium/Mobile).

**Install Browsers (First time):**
```bash
npx playwright install
```

**Run All E2E Tests:**
```bash
npx playwright test
```

**Run with UI (Visual Debugger):**
```bash
npx playwright test --ui
```

## 4. Accessibility Audits

- **Component Level**: Integrated into `tests/unit/*.test.tsx` using `vitest-axe`. Runs automatically with Unit Tests.
- **Page Level**: Can be enabled in Playwright tests using `@axe-core/playwright`.

## 5. CI/CD Pipeline Example (GitHub Actions)

Create `.github/workflows/test.yml`:

```yaml
name: QA Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npx vitest run --coverage
      - run: npx playwright install --with-deps
      - run: npx playwright test
```
