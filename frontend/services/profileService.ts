import { apiClient } from './apiClient';
import { Profile, SubscriptionTier } from '../types';

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

export interface CreateProfileData {
    displayName: string;
    avatarUrl?: string;
    pin?: string;
    gradeLevelId?: string;
}

export interface UpdateProfileData {
    displayName?: string;
    avatarUrl?: string;
    pin?: string;
    gradeLevelId?: string;
}

export const profileService = {
    async listProfiles(): Promise<Profile[]> {
        const data = await apiClient.get<any[]>('/profiles');
        return (data || []).map(mapProfile);
    },

    async createProfile(data: CreateProfileData): Promise<Profile> {
        const res = await apiClient.post<any>('/profiles', {
            display_name: data.displayName,
            avatar_url: data.avatarUrl || undefined,
            pin: data.pin || undefined,
            grade_level_id: data.gradeLevelId || undefined,
        });
        return mapProfile(res);
    },

    async updateProfile(profileId: string, data: UpdateProfileData): Promise<void> {
        await apiClient.patch(`/profiles/${profileId}`, {
            display_name: data.displayName || undefined,
            avatar_url: data.avatarUrl || undefined,
            pin: data.pin || undefined,
            grade_level_id: data.gradeLevelId || undefined,
        });
    },

    async deleteProfile(profileId: string): Promise<void> {
        await apiClient.delete(`/profiles/${profileId}`);
    },

    async verifyPin(profileId: string, pin: string): Promise<boolean> {
        try {
            await apiClient.post(`/profiles/${profileId}/verify-pin`, { pin });
            return true;
        } catch {
            return false;
        }
    },

    async setWeeklyGoal(profileId: string, minutes: number): Promise<void> {
        await apiClient.patch(`/profiles/${profileId}/goal`, { weekly_goal_minutes: minutes });
    },
};
