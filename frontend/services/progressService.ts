import { apiClient } from './apiClient';

export interface SkillProgressDTO {
  skillId: string;
  skillName: string;
  score: number;
  totalAttempts: number;
  lastPlayedAt?: string;
}

export interface ProgressSummaryDTO {
  totalSkills: number;
  masteredSkills: number;
  averageScore: number;
  totalSessions: number;
  totalTimeMinutes: number;
}

export interface BadgeDTO {
  id: string;
  name: string;
  description: string;
  iconUrl?: string;
  rule: string;
  unlockedAt?: string;
  progress: number;
  current: number;
  total: number;
}

export interface MicroSkillProgressDTO {
  microSkillId: string;
  microSkillName: string;
  externalId?: string;
  difficultyIndex?: number;
  smartScore: number;
  totalAttempts: number;
  correctAttempts: number;
  streak: number;
  bestStreak: number;
  lastAttemptAt?: string;
}

export const progressService = {
  async getSummary(): Promise<ProgressSummaryDTO> {
    return apiClient.get<ProgressSummaryDTO>('/students/me/progress/summary');
  },

  async getSkillsProgress(): Promise<SkillProgressDTO[]> {
    const data = await apiClient.get<any[]>('/students/me/progress/skills');
    return (data || []).map((s: any) => ({
      skillId: String(s.skill_id || s.id),
      skillName: s.skill_name || s.name || '',
      score: s.smart_score ?? s.score ?? 0,
      totalAttempts: s.total_attempts ?? 0,
      lastPlayedAt: s.last_played_at || s.updated_at,
    }));
  },

  async getMyBadges(): Promise<BadgeDTO[]> {
    const data = await apiClient.get<any[]>('/students/me/badges');
    return (data || []).map((b: any) => ({
      id: String(b.badge_id || b.id),
      name: b.badge_name || b.name || '',
      description: b.badge_description || b.description || '',
      iconUrl: b.badge_icon_url || b.icon_url,
      rule: b.badge_rule || b.rule || '',
      unlockedAt: b.awarded_at || b.unlocked_at,
      progress: b.progress ?? (b.awarded_at ? 100 : 0),
      current: b.current ?? (b.awarded_at ? b.threshold : 0),
      total: b.threshold ?? b.total ?? 1,
    }));
  },

  async getMicroSkillsProgress(skillId: string): Promise<MicroSkillProgressDTO[]> {
    const data = await apiClient.get<any[]>(`/students/me/progress/micro-skills?skill_id=${skillId}`);
    return (data || []).map((ms: any) => ({
      microSkillId: String(ms.micro_skill_id),
      microSkillName: ms.micro_skill_name || '',
      externalId: ms.external_id,
      difficultyIndex: ms.difficulty_index,
      smartScore: ms.smart_score ?? 0,
      totalAttempts: ms.total_attempts ?? 0,
      correctAttempts: ms.correct_attempts ?? 0,
      streak: ms.streak ?? 0,
      bestStreak: ms.best_streak ?? 0,
      lastAttemptAt: ms.last_attempt_at,
    }));
  },

  async getStudentProgress(studentId: string): Promise<SkillProgressDTO[]> {
    const data = await apiClient.get<any[]>(`/students/${studentId}/progress/skills`);
    return (data || []).map((s: any) => ({
      skillId: String(s.skill_id || s.id),
      skillName: s.skill_name || s.name || '',
      score: s.smart_score ?? s.score ?? 0,
      totalAttempts: s.total_attempts ?? 0,
      lastPlayedAt: s.last_played_at || s.updated_at,
    }));
  },
};
