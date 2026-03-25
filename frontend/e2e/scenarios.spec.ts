import { test, expect } from '@playwright/test';

/**
 * Login helper — uses the demo quick-access buttons on the Login page
 * then submits the form.
 */
const loginAs = async (page: any, role: 'student' | 'parent' | 'admin') => {
  await page.goto('/#/login');
  // Click the demo quick-fill button
  const label = role === 'student' ? 'Élève' : role === 'parent' ? 'Parent' : 'Admin';
  await page.getByRole('button', { name: label }).click();
  // Submit the form
  await page.getByRole('button', { name: 'Se connecter' }).click();
};

test.describe('Sitou Core User Flows', () => {

  test('Student can login and see dashboard', async ({ page }) => {
    await loginAs(page, 'student');
    // Should redirect to student dashboard
    await page.waitForURL(/.*student\/dashboard/);
    await expect(page.getByText('Bonjour')).toBeVisible();
  });

  test('Parent can login and see parent dashboard', async ({ page }) => {
    await loginAs(page, 'parent');
    await page.waitForURL(/.*parent\/dashboard/);
    await expect(page.getByText('Mes enfants')).toBeVisible();
  });

  test('Admin can login and see admin dashboard', async ({ page }) => {
    await loginAs(page, 'admin');
    await page.waitForURL(/.*admin\/dashboard/);
  });

  test('Offline banner appears when network is down', async ({ page, context }) => {
    await loginAs(page, 'student');
    await page.waitForURL(/.*student\/dashboard/);

    // Go offline
    await context.setOffline(true);
    // Trigger a navigation to force offline detection
    await page.goto('/#/app/student/subjects');
    await expect(page.getByText(/hors-ligne/i)).toBeVisible();

    // Go back online
    await context.setOffline(false);
    await page.waitForTimeout(1000);
    await expect(page.getByText(/hors-ligne/i)).not.toBeVisible();
  });

  test('Subscription plans page displays pricing', async ({ page }) => {
    await loginAs(page, 'student');
    await page.goto('/#/app/subscription/plans');
    await expect(page.getByText('Premium')).toBeVisible();
    await expect(page.getByText('FCFA')).toBeVisible();
  });

  test('Unauthenticated user is redirected to login', async ({ page }) => {
    await page.goto('/#/app/student/dashboard');
    // Should redirect to login
    await page.waitForURL(/.*login/);
  });
});
