import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useAuthStore } from '../store/authStore';
import { authService } from '../services/authService';
import { SubscriptionTier, Profile } from '../types';

// Mock AuthService
vi.mock('../services/authService', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    refresh: vi.fn(),
  },
}));

// Mock telemetry
vi.mock('../services/telemetry', () => ({
  telemetry: {
    logEvent: vi.fn(),
    logError: vi.fn(),
    setUser: vi.fn(),
  },
}));

const mockProfile = (overrides: Partial<Profile> = {}): Profile => ({
  id: '1',
  displayName: 'Test Child',
  avatarUrl: '',
  isActive: true,
  hasPin: false,
  subscriptionTier: SubscriptionTier.FREE,
  weeklyGoalMinutes: 120,
  ...overrides,
});

describe('AuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      profiles: [],
      activeProfile: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should have initial state', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.profiles).toEqual([]);
    expect(state.activeProfile).toBeNull();
  });

  it('should login successfully with profiles', async () => {
    const mockUser = { id: '1', name: 'Test', role: 'STUDENT' };
    const mockToken = 'abc.123.xyz';
    const profiles = [mockProfile()];

    (authService.login as any).mockResolvedValue({
      user: mockUser,
      accessToken: mockToken,
      profiles,
    });

    await useAuthStore.getState().login({ identifier: 'test', password: '123' });

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.accessToken).toBe(mockToken);
    expect(state.user).toEqual(mockUser);
    expect(state.profiles).toEqual(profiles);
    // Single profile auto-selected
    expect(state.activeProfile).toEqual(profiles[0]);
    expect(state.isLoading).toBe(false);
  });

  it('should handle login error', async () => {
    const errorMsg = 'Invalid credentials';
    (authService.login as any).mockRejectedValue(new Error(errorMsg));

    await expect(
      useAuthStore.getState().login({ identifier: 'test', password: 'wrong' })
    ).rejects.toThrow(errorMsg);

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.error).toBe(errorMsg);
  });

  it('should logout correctly and clear profiles', async () => {
    useAuthStore.setState({
      isAuthenticated: true,
      accessToken: 'token',
      user: {} as any,
      profiles: [mockProfile()],
      activeProfile: mockProfile(),
    });

    await useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.profiles).toEqual([]);
    expect(state.activeProfile).toBeNull();
    expect(authService.logout).toHaveBeenCalled();
  });

  // --- Profile-specific tests ---

  it('selectProfile sets the active profile', () => {
    const p1 = mockProfile({ id: 'p1', displayName: 'Aïcha' });
    const p2 = mockProfile({ id: 'p2', displayName: 'Kofi' });

    useAuthStore.setState({ profiles: [p1, p2] });
    useAuthStore.getState().selectProfile('p2');

    expect(useAuthStore.getState().activeProfile).toEqual(p2);
  });

  it('clearProfile resets active profile to null', () => {
    const p1 = mockProfile({ id: 'p1' });
    useAuthStore.setState({ profiles: [p1], activeProfile: p1 });

    useAuthStore.getState().clearProfile();

    expect(useAuthStore.getState().activeProfile).toBeNull();
  });

  it('setProfiles auto-selects when only one profile exists', () => {
    const p1 = mockProfile({ id: 'p1' });

    useAuthStore.getState().setProfiles([p1]);

    const state = useAuthStore.getState();
    expect(state.profiles).toEqual([p1]);
    expect(state.activeProfile).toEqual(p1);
  });

  it('setProfiles does not auto-select when multiple profiles exist', () => {
    const p1 = mockProfile({ id: 'p1' });
    const p2 = mockProfile({ id: 'p2' });

    useAuthStore.getState().setProfiles([p1, p2]);

    const state = useAuthStore.getState();
    expect(state.profiles).toHaveLength(2);
    expect(state.activeProfile).toBeNull();
  });

  it('setProfiles restores previously selected profile from localStorage', () => {
    const p1 = mockProfile({ id: 'p1' });
    const p2 = mockProfile({ id: 'p2' });

    localStorage.setItem('sitou_active_profile_id', 'p2');

    useAuthStore.getState().setProfiles([p1, p2]);

    expect(useAuthStore.getState().activeProfile).toEqual(p2);
  });

  it('login with multiple profiles does not auto-select', async () => {
    const mockUser = { id: '1', name: 'Parent', role: 'PARENT' };
    const profiles = [
      mockProfile({ id: 'p1', displayName: 'Child 1' }),
      mockProfile({ id: 'p2', displayName: 'Child 2' }),
    ];

    (authService.login as any).mockResolvedValue({
      user: mockUser,
      accessToken: 'tok',
      profiles,
    });

    await useAuthStore.getState().login({ identifier: 'test', password: '123' });

    const state = useAuthStore.getState();
    expect(state.profiles).toHaveLength(2);
    expect(state.activeProfile).toBeNull();
  });
});
