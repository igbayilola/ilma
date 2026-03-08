
import { create } from 'zustand';
import { AuthState } from '../types/auth';
import { Profile } from '../types';
import { authService } from '../services/authService';
import { telemetry } from '../services/telemetry';

// Token refresh timer handle
let refreshTimerId: ReturnType<typeof setTimeout> | null = null;

// Storage keys
const STORAGE_KEYS = {
  LAST_USER: 'ilma_last_user',
  TOKEN_EXPIRY: 'ilma_token_expiry',
  REFRESH_TOKEN: 'ilma_refresh_token',
  ACTIVE_PROFILE_ID: 'ilma_active_profile_id',
  PROFILES: 'ilma_profiles',
} as const;

/**
 * Schedule a token refresh before it expires.
 * Refreshes 60 seconds before actual expiry.
 */
function scheduleTokenRefresh(expiresIn: number) {
    clearScheduledRefresh();
    // Refresh 60s before expiry, minimum 10s
    const refreshDelay = Math.max((expiresIn - 60) * 1000, 10000);
    refreshTimerId = setTimeout(async () => {
        try {
            const storedRefresh = getStoredRefreshToken();
            if (!storedRefresh) return;
            const response = await authService.refresh(storedRefresh);
            if (response?.accessToken) {
                useAuthStore.getState().setAccessToken(response.accessToken);
                if (response.refreshToken) {
                    storeRefreshToken(response.refreshToken);
                }
                if (response.profiles) {
                    useAuthStore.getState().setProfiles(response.profiles);
                }
                if (response.expiresIn) {
                    scheduleTokenRefresh(response.expiresIn);
                }
            }
        } catch {
            // Silent fail - the 401 interceptor in apiClient will handle it
            console.warn('[Auth] Auto-refresh failed, will retry on next API call');
        }
    }, refreshDelay);
}

function clearScheduledRefresh() {
    if (refreshTimerId) {
        clearTimeout(refreshTimerId);
        refreshTimerId = null;
    }
}

/**
 * Persist minimal user info for fast warm-start.
 */
function cacheUser(user: any) {
    try {
        localStorage.setItem(STORAGE_KEYS.LAST_USER, JSON.stringify({
            id: user.id,
            name: user.name,
            role: user.role,
            avatarUrl: user.avatarUrl,
        }));
    } catch { /* quota or private mode */ }
}

function getCachedUser() {
    try {
        const cached = localStorage.getItem(STORAGE_KEYS.LAST_USER);
        return cached ? JSON.parse(cached) : null;
    } catch { return null; }
}

function storeRefreshToken(token: string) {
    try {
        localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, token);
    } catch { /* ignore */ }
}

function getStoredRefreshToken(): string | null {
    try {
        return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    } catch { return null; }
}

function storeProfiles(profiles: Profile[]) {
    try {
        localStorage.setItem(STORAGE_KEYS.PROFILES, JSON.stringify(profiles));
    } catch { /* ignore */ }
}

function getStoredProfiles(): Profile[] {
    try {
        const cached = localStorage.getItem(STORAGE_KEYS.PROFILES);
        return cached ? JSON.parse(cached) : [];
    } catch { return []; }
}

function storeActiveProfileId(profileId: string | null) {
    try {
        if (profileId) {
            localStorage.setItem(STORAGE_KEYS.ACTIVE_PROFILE_ID, profileId);
        } else {
            localStorage.removeItem(STORAGE_KEYS.ACTIVE_PROFILE_ID);
        }
    } catch { /* ignore */ }
}

function getStoredActiveProfileId(): string | null {
    try {
        return localStorage.getItem(STORAGE_KEYS.ACTIVE_PROFILE_ID);
    } catch { return null; }
}

function clearCache() {
    try {
        localStorage.removeItem(STORAGE_KEYS.LAST_USER);
        localStorage.removeItem(STORAGE_KEYS.TOKEN_EXPIRY);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.ACTIVE_PROFILE_ID);
        localStorage.removeItem(STORAGE_KEYS.PROFILES);
    } catch { /* ignore */ }
}

export const useAuthStore = create<AuthState>((set, get) => ({
    user: null,
    accessToken: null,
    profiles: [],
    activeProfile: null,
    isAuthenticated: false,
    isLoading: true, // Start loading to check session
    error: null,

    setAccessToken: (token: string) => set({ accessToken: token }),

    setProfiles: (profiles: Profile[]) => {
        storeProfiles(profiles);
        set({ profiles });

        // Auto-restore active profile if previously selected
        const storedId = getStoredActiveProfileId();
        if (storedId) {
            const found = profiles.find(p => p.id === storedId && p.isActive);
            if (found) {
                set({ activeProfile: found });
            }
        }

        // Auto-select if only one profile WITHOUT a PIN (standalone students)
        if (profiles.length === 1 && profiles[0].isActive && !profiles[0].hasPin) {
            set({ activeProfile: profiles[0] });
            storeActiveProfileId(profiles[0].id);
        }
    },

    selectProfile: (profileId: string) => {
        const { profiles } = get();
        const profile = profiles.find(p => p.id === profileId);
        if (profile) {
            set({ activeProfile: profile });
            storeActiveProfileId(profileId);
        }
    },

    clearProfile: () => {
        set({ activeProfile: null });
        storeActiveProfileId(null);
    },

    login: async (credentials) => {
        set({ isLoading: true, error: null });
        telemetry.logEvent('Auth', 'Login Attempt', credentials.identifier);

        try {
            const response = await authService.login(credentials);
            const profiles = response.profiles || [];
            set({
                user: response.user,
                accessToken: response.accessToken,
                profiles,
                isAuthenticated: true,
                isLoading: false
            });
            cacheUser(response.user);
            storeProfiles(profiles);

            // Auto-select if only one profile WITHOUT a PIN (standalone students)
            if (profiles.length === 1 && profiles[0].isActive && !profiles[0].hasPin) {
                set({ activeProfile: profiles[0] });
                storeActiveProfileId(profiles[0].id);
            } else {
                // Try to restore previously selected profile
                const storedId = getStoredActiveProfileId();
                if (storedId) {
                    const found = profiles.find(p => p.id === storedId && p.isActive);
                    if (found) {
                        set({ activeProfile: found });
                    }
                }
            }

            if (response.refreshToken) {
                storeRefreshToken(response.refreshToken);
            }
            if (response.expiresIn) {
                scheduleTokenRefresh(response.expiresIn);
            }
            telemetry.setUser(response.user);
            telemetry.logEvent('Auth', 'Login Success', response.user.id);
        } catch (error: any) {
            console.error("Login failed", error);
            telemetry.logError(error, { identifier: credentials.identifier }, 'AuthStore');
            set({ error: error.message || 'Erreur de connexion', isLoading: false });
            throw error;
        }
    },

    register: async (data) => {
        set({ isLoading: true, error: null });
        telemetry.logEvent('Auth', 'Register Attempt', data.email);
        try {
            const response = await authService.register(data);
            const profiles = response.profiles || [];
            set({
                user: response.user,
                accessToken: response.accessToken,
                profiles,
                isAuthenticated: true,
                isLoading: false
            });
            cacheUser(response.user);
            storeProfiles(profiles);

            // Auto-select if only one profile WITHOUT a PIN (standalone student)
            if (profiles.length === 1 && profiles[0].isActive && !profiles[0].hasPin) {
                set({ activeProfile: profiles[0] });
                storeActiveProfileId(profiles[0].id);
            }

            if (response.refreshToken) {
                storeRefreshToken(response.refreshToken);
            }
            if (response.expiresIn) {
                scheduleTokenRefresh(response.expiresIn);
            }
            telemetry.setUser(response.user);
            telemetry.logEvent('Auth', 'Register Success', response.user.id);
        } catch (error: any) {
            telemetry.logError(error, { email: data.email }, 'AuthStore');
            set({ error: error.message, isLoading: false });
            throw error;
        }
    },

    logout: async () => {
        telemetry.logEvent('Auth', 'Logout');
        clearScheduledRefresh();
        try {
            await authService.logout();
        } catch (e) {
            console.warn("Logout API failed, clearing local state anyway");
        }
        set({ user: null, accessToken: null, isAuthenticated: false, profiles: [], activeProfile: null });
        clearCache();
        telemetry.setUser(null);
    },

    checkAuth: async () => {
        set({ isLoading: true });
        try {
            const storedRefresh = getStoredRefreshToken();
            if (!storedRefresh) {
                throw new Error("No refresh token");
            }
            const response = await authService.refresh(storedRefresh);
            if (response && response.user) {
                const profiles = response.profiles || getStoredProfiles();
                set({
                    user: response.user,
                    accessToken: response.accessToken,
                    profiles,
                    isAuthenticated: true
                });
                cacheUser(response.user);
                storeProfiles(profiles);

                // Restore active profile
                const storedId = getStoredActiveProfileId();
                if (storedId) {
                    const found = profiles.find(p => p.id === storedId && p.isActive);
                    if (found) {
                        set({ activeProfile: found });
                    }
                } else if (profiles.length === 1 && profiles[0].isActive && !profiles[0].hasPin) {
                    set({ activeProfile: profiles[0] });
                    storeActiveProfileId(profiles[0].id);
                }

                if (response.refreshToken) {
                    storeRefreshToken(response.refreshToken);
                }
                if (response.expiresIn) {
                    scheduleTokenRefresh(response.expiresIn);
                }
                telemetry.setUser(response.user);
            } else {
                 throw new Error("No session");
            }
        } catch (error) {
            // No valid session — check if we have cached user for offline warm-start
            const cached = getCachedUser();
            if (cached) {
                console.info('[Auth] Using cached user for warm-start');
            }
            set({ user: null, accessToken: null, isAuthenticated: false, profiles: [], activeProfile: null });
        } finally {
            set({ isLoading: false });
        }
    }
}));
