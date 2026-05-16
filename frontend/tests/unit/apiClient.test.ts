import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// We test the apiClient error mapping logic and X-Profile-Id header injection
// Since apiClient uses fetch internally, we mock global fetch

describe('ApiClient Error Mapping', () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.resetModules();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('throws TIMEOUT error on AbortController signal', async () => {
    global.fetch = vi.fn().mockImplementation(() => {
      return new Promise((_, reject) => {
        const error = new Error('AbortError');
        error.name = 'AbortError';
        reject(error);
      });
    });

    // Import fresh module after mock
    const { apiClient } = await import('../../services/apiClient');

    await expect(apiClient.get('/test', { timeout: 1 })).rejects.toMatchObject({
      code: 'TIMEOUT',
    });
  });

  it('maps 404 to NOT_FOUND error', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve({ message: 'Not found' }),
    });

    const { apiClient } = await import('../../services/apiClient');

    await expect(apiClient.get('/missing')).rejects.toMatchObject({
      code: 'NOT_FOUND',
      status: 404,
    });
  });

  it('maps 500 to SERVER_ERROR', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.resolve({ message: 'Server error' }),
    });

    const { apiClient } = await import('../../services/apiClient');

    await expect(apiClient.get('/crash')).rejects.toMatchObject({
      code: 'SERVER_ERROR',
      status: 500,
    });
  });

  it('returns parsed JSON on success', async () => {
    const mockData = { id: '1', name: 'Test' };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockData),
    });

    const { apiClient } = await import('../../services/apiClient');
    const result = await apiClient.get('/success');
    expect(result).toEqual(mockData);
  });

  it('sends X-Profile-Id header when active profile exists', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ ok: true }),
    });

    // Set the active profile in the auth store before importing apiClient
    const { useAuthStore } = await import('../../store/authStore');
    useAuthStore.setState({
      accessToken: 'test-token',
      activeProfile: {
        id: 'profile-123',
        displayName: 'Test Child',
        avatarUrl: '',
        isActive: true,
        hasPin: false,
        subscriptionTier: 'FREE' as any,
        weeklyGoalMinutes: 120,
      },
      isAuthenticated: true,
    });

    const { apiClient } = await import('../../services/apiClient');
    await apiClient.get('/test-profile');

    // Verify fetch was called with the X-Profile-Id header
    expect(global.fetch).toHaveBeenCalled();
    const [, fetchOptions] = (global.fetch as any).mock.calls[0];
    const headers = fetchOptions.headers;
    expect(headers.get('X-Profile-Id')).toBe('profile-123');
    expect(headers.get('Authorization')).toBe('Bearer test-token');
  });

  it('does not send X-Profile-Id header when no active profile', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ ok: true }),
    });

    const { useAuthStore } = await import('../../store/authStore');
    useAuthStore.setState({
      accessToken: 'test-token',
      activeProfile: null,
      isAuthenticated: true,
    });

    const { apiClient } = await import('../../services/apiClient');
    await apiClient.get('/test-no-profile');

    const [, fetchOptions] = (global.fetch as any).mock.calls[0];
    const headers = fetchOptions.headers;
    expect(headers.get('X-Profile-Id')).toBeNull();
  });

  it('does not override X-Profile-Id when caller passes one explicitly', async () => {
    // Regression for iter 13 / A6.6: parent dashboard joining a classroom for
    // a specific kid must be able to target that kid's profile even when a
    // different activeProfile is set globally.
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ ok: true }),
    });

    const { useAuthStore } = await import('../../store/authStore');
    useAuthStore.setState({
      accessToken: 'test-token',
      activeProfile: {
        id: 'parent-active-profile',
        displayName: 'Parent',
        avatarUrl: '',
        isActive: true,
        hasPin: false,
        subscriptionTier: 'FREE' as any,
        weeklyGoalMinutes: 120,
      },
      isAuthenticated: true,
    });

    const { apiClient } = await import('../../services/apiClient');
    await apiClient.post('/teacher/classrooms/join', { invite_code: 'X' }, {
      headers: { 'X-Profile-Id': 'kid-2-profile' },
    });

    const [, fetchOptions] = (global.fetch as any).mock.calls[0];
    expect(fetchOptions.headers.get('X-Profile-Id')).toBe('kid-2-profile');
  });
});
