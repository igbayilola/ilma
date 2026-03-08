import { apiClient } from './apiClient';

export interface ChildDTO {
  id: string;
  name: string;
  avatar: string;
  level: number;
  role: string;
  weeklyGoalMinutes: number;
  hasPin: boolean;
  subscriptionTier: string;
}

export const parentService = {
  async listChildren(): Promise<ChildDTO[]> {
    const data = await apiClient.get<any[]>('/profiles');
    return (data || []).map((c: any) => ({
      id: String(c.id),
      name: c.display_name || c.displayName || c.name || '',
      avatar: c.avatar_url || c.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${c.id}`,
      level: c.level ?? 1,
      role: 'STUDENT',
      weeklyGoalMinutes: c.weekly_goal_minutes ?? c.weeklyGoalMinutes ?? 120,
      hasPin: c.has_pin ?? c.hasPin ?? false,
      subscriptionTier: c.subscription_tier || c.subscriptionTier || 'FREE',
    }));
  },

  async setWeeklyGoal(profileId: string, minutes: number): Promise<void> {
    await apiClient.patch(`/profiles/${profileId}/goal`, { weekly_goal_minutes: minutes });
  },

  async getChildProgress(profileId: string): Promise<any> {
    const data = await apiClient.get(`/students/${profileId}/progress/summary`);
    return data;
  },
};
