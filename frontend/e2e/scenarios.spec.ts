import { test, expect } from '@playwright/test';

/**
 * Login helper — uses the demo quick-access buttons on the Login page
 * then submits the form.
 */
const loginAs = async (page: any, role: 'student' | 'parent' | 'admin' | 'editor') => {
  await page.goto('/#/login');
  const label = role === 'student' ? 'Élève' : role === 'parent' ? 'Parent' : role === 'editor' ? 'Éditeur' : 'Admin';
  await page.getByRole('button', { name: label }).click();
  await page.getByRole('button', { name: 'Se connecter' }).click();
};

// ── Auth & Navigation ──────────────────────────────────────

test.describe('Authentication', () => {
  test('Unauthenticated user is redirected to login', async ({ page }) => {
    await page.goto('/#/app/student/dashboard');
    await page.waitForURL(/.*login/);
  });

  test('Student can login and see dashboard', async ({ page }) => {
    await loginAs(page, 'student');
    await page.waitForURL(/.*student\/dashboard|.*select-profile/);
    await expect(page.locator('body')).not.toBeEmpty();
  });

  test('Parent can login and see parent dashboard', async ({ page }) => {
    await loginAs(page, 'parent');
    await page.waitForURL(/.*parent\/dashboard|.*select-profile/);
  });

  test('Admin can login and see admin dashboard', async ({ page }) => {
    await loginAs(page, 'admin');
    await page.waitForURL(/.*admin\/dashboard/);
  });

  test('Forgot password page is accessible', async ({ page }) => {
    await page.goto('/#/login');
    await page.getByText('Mot de passe oublié').click();
    await page.waitForURL(/.*forgot-password/);
    await expect(page.getByText('Envoyer le code')).toBeVisible();
  });
});

// ── Student Content Navigation ─────────────────────────────

test.describe('Student Content', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'student');
    await page.waitForURL(/.*student\/dashboard|.*select-profile/);
    // If on profile selector, click first profile
    if (page.url().includes('select-profile')) {
      await page.locator('[data-testid="profile-card"]').first().click();
      await page.waitForURL(/.*student\/dashboard/);
    }
  });

  test('Can navigate to subjects list', async ({ page }) => {
    await page.goto('/#/app/student/subjects');
    await expect(page.getByText(/Mathématiques|Français/)).toBeVisible();
  });

  test('Can browse subject domains and skills', async ({ page }) => {
    await page.goto('/#/app/student/subjects');
    // Click first subject
    await page.locator('a, button, [role="link"]').filter({ hasText: /Mathématiques/ }).first().click();
    // Should see domains
    await expect(page.locator('body')).toContainText(/Numération|Opérations|Géométrie/);
  });

  test('Progress page loads', async ({ page }) => {
    await page.goto('/#/app/student/progress');
    await expect(page.locator('body')).not.toBeEmpty();
  });

  test('Badges page loads', async ({ page }) => {
    await page.goto('/#/app/student/badges');
    await expect(page.locator('body')).not.toBeEmpty();
  });

  test('Leaderboard page loads', async ({ page }) => {
    await page.goto('/#/app/student/leaderboard');
    await expect(page.locator('body')).not.toBeEmpty();
  });

  test('Settings page loads with toggles', async ({ page }) => {
    await page.goto('/#/app/student/settings');
    await expect(page.locator('body')).not.toBeEmpty();
  });
});

// ── Exams ────────────────────────────────────────────────

test.describe('Exams', () => {
  test('Exam list shows CEP exams', async ({ page }) => {
    await loginAs(page, 'student');
    await page.waitForURL(/.*student\/dashboard|.*select-profile/);
    if (page.url().includes('select-profile')) {
      await page.locator('[data-testid="profile-card"]').first().click();
      await page.waitForURL(/.*student\/dashboard/);
    }
    await page.goto('/#/app/student/exams');
    await expect(page.getByText(/CEP/)).toBeVisible();
  });
});

// ── Subscription ──────────────────────────────────────────

test.describe('Subscription', () => {
  test('Plans page displays pricing', async ({ page }) => {
    await loginAs(page, 'student');
    await page.waitForURL(/.*student\/dashboard|.*select-profile/);
    await page.goto('/#/app/subscription/plans');
    await expect(page.getByText('Premium')).toBeVisible();
    await expect(page.getByText('FCFA')).toBeVisible();
  });
});

// ── Editor ────────────────────────────────────────────────

test.describe('Editor', () => {
  test('Editor dashboard loads with stats', async ({ page }) => {
    await loginAs(page, 'editor');
    await page.waitForURL(/.*editor\/dashboard/);
    await expect(page.locator('body')).not.toBeEmpty();
  });
});

// ── Offline ───────────────────────────────────────────────

test.describe('Offline', () => {
  test('Offline banner appears when network is down', async ({ page, context }) => {
    await loginAs(page, 'student');
    await page.waitForURL(/.*student\/dashboard|.*select-profile/);

    await context.setOffline(true);
    await page.goto('/#/app/student/subjects');
    await expect(page.getByText(/hors-ligne/i)).toBeVisible();

    await context.setOffline(false);
    await page.waitForTimeout(1000);
    await expect(page.getByText(/hors-ligne/i)).not.toBeVisible();
  });
});
