import { apiClient } from './apiClient';
import { AuthResponse, LoginCredentials, RegisterData } from '../types/auth';
import { User, Profile, SubscriptionTier } from '../types';

const ENDPOINTS = {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me'
};

/**
 * Map backend user (snake_case) to frontend User (camelCase).
 * Gamification fields default to 0/FREE since they come from the progress API.
 */
function mapUser(u: any): User {
    return {
        id: String(u.id),
        name: u.full_name || u.name || '',
        email: u.email,
        phone: u.phone,
        avatarUrl: u.avatar_url || u.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${u.id}`,
        role: (u.role || '').toUpperCase(),
        gradeLevelId: u.grade_level_id || u.gradeLevelId || undefined,
        level: u.level ?? 1,
        xp: u.xp ?? 0,
        xpToNextLevel: u.xp_to_next_level ?? 1000,
        streak: u.streak ?? 0,
        smartScore: u.smart_score ?? 0,
        subscriptionTier: (u.subscription_tier || '').toUpperCase() || SubscriptionTier.FREE,
    };
}

/**
 * Map backend profile (snake_case) to frontend Profile (camelCase).
 */
function mapProfile(p: any): Profile {
    return {
        id: String(p.id),
        displayName: p.display_name || p.displayName || '',
        avatarUrl: p.avatar_url || p.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${p.id}`,
        gradeLevelId: p.grade_level_id || p.gradeLevelId || undefined,
        isActive: p.is_active ?? p.isActive ?? true,
        hasPin: p.has_pin ?? p.hasPin ?? false,
        subscriptionTier: ((p.subscription_tier || p.subscriptionTier || '').toUpperCase() || SubscriptionTier.FREE) as SubscriptionTier,
        weeklyGoalMinutes: p.weekly_goal_minutes ?? p.weeklyGoalMinutes ?? 120,
    };
}

/**
 * Map backend auth response to frontend AuthResponse.
 * Backend returns: {access_token, refresh_token, token_type, expires_in, user, profiles}
 */
function mapAuthResponse(data: any): AuthResponse {
    return {
        user: mapUser(data.user),
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        expiresIn: data.expires_in,
        profiles: (data.profiles || []).map(mapProfile),
    };
}

export const authService = {
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const data = await apiClient.post<any>(ENDPOINTS.LOGIN, {
            identifier: credentials.identifier,
            password: credentials.password,
        });
        return mapAuthResponse(data);
    },

    async register(data: RegisterData): Promise<AuthResponse> {
        const res = await apiClient.post<any>(ENDPOINTS.REGISTER, {
            email: data.email || undefined,
            phone: data.phone || undefined,
            full_name: data.name || data.fullName,
            password: data.password,
            role: (data.role || 'student').toUpperCase(),
            grade_level_id: data.gradeLevelId || undefined,
        });
        return mapAuthResponse(res);
    },

    async logout(): Promise<void> {
        return apiClient.post(ENDPOINTS.LOGOUT, {});
    },

    /**
     * Refresh token — sends refresh_token in body.
     */
    async refresh(refreshToken: string): Promise<AuthResponse> {
        const data = await apiClient.post<any>(
            ENDPOINTS.REFRESH,
            { refresh_token: refreshToken },
            { skipAuth: true }
        );
        return mapAuthResponse(data);
    },

    async getCurrentUser(): Promise<User> {
        const data = await apiClient.get<any>(ENDPOINTS.ME);
        return mapUser(data);
    }
};

export { mapProfile };
