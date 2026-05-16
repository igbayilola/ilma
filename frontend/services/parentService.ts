import { apiClient } from './apiClient';
import { avatarUrl } from '../utils/avatar';

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

export interface ChildHealthDTO {
  profileId: string;
  displayName: string;
  avatarUrl: string;
  weeklyGoalMinutes: number;
  averageScore: number;
  streak: number;
  status: 'green' | 'orange' | 'red';
  timeThisWeekMinutes: number;
  timeDeltaMinutes: number;
  daysInactive: number;
  weakestSkillName: string | null;
  advice: string | null;
  riskLevel: 'low' | 'medium' | 'high';
  suggestedAction: string;
}

export const parentService = {
  async listChildren(): Promise<ChildDTO[]> {
    const data = await apiClient.get<any[]>('/profiles');
    return (data || []).map((c: any) => ({
      id: String(c.id),
      name: c.display_name || c.displayName || c.name || '',
      avatar: c.avatar_url || c.avatarUrl || avatarUrl(c.id),
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

  async triggerDigest(): Promise<void> {
    await apiClient.post('/notifications/trigger-digest', {});
  },

  /**
   * Enroll a child profile into a teacher's classroom using their 8-char invite
   * code. Sets X-Profile-Id explicitly so the backend's `get_active_profile`
   * resolves to the targeted kid (and not the parent's auto-picked profile).
   */
  async joinClassroomForChild(profileId: string, inviteCode: string): Promise<{
    classroom_id: string;
    classroom_name: string;
  }> {
    return apiClient.post(
      '/teacher/classrooms/join',
      { invite_code: inviteCode.trim().toUpperCase() },
      { headers: { 'X-Profile-Id': profileId } },
    );
  },

  async getHealthSummary(): Promise<ChildHealthDTO[]> {
    const data = await apiClient.get<any[]>('/students/health-summary');
    return (data || []).map((c: any) => ({
      profileId: c.profile_id,
      displayName: c.display_name,
      avatarUrl: c.avatar_url || avatarUrl(c.profile_id),
      weeklyGoalMinutes: c.weekly_goal_minutes ?? 120,
      averageScore: c.average_score ?? 0,
      streak: c.streak ?? 0,
      status: c.status || 'orange',
      timeThisWeekMinutes: c.time_this_week_minutes ?? 0,
      timeDeltaMinutes: c.time_delta_minutes ?? 0,
      daysInactive: c.days_inactive ?? 0,
      weakestSkillName: c.weakest_skill_name || null,
      advice: c.advice || null,
      riskLevel: c.risk_level || 'low',
      suggestedAction: c.suggested_action || '',
    }));
  },
};
