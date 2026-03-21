import { apiClient } from './apiClient';

export interface LeaderboardEntry {
  rank: number;
  pseudonym: string;
  xp_earned: number;
  is_me: boolean;
}

export interface LeaderboardData {
  week: string;
  entries: LeaderboardEntry[];
  my_rank: number | null;
  my_xp: number;
  my_pseudonym: string | null;
}

export interface ChallengeDTO {
  id: string;
  challenger_id: string;
  challenged_id: string;
  skill_id: string | null;
  status: string;
  challenger_score: number | null;
  challenged_score: number | null;
  expires_at: string | null;
  created_at: string | null;
  is_challenger: boolean;
}

export interface LeaderboardHistoryEntry {
  week: string;
  xp_earned: number;
  pseudonym: string;
  rank: number | null;
  total_participants: number;
  is_current: boolean;
}

export const socialService = {
  async getWeeklyLeaderboard(limit = 20): Promise<LeaderboardData> {
    return apiClient.get<LeaderboardData>(`/social/leaderboard/weekly?limit=${limit}`);
  },

  async getLeaderboardHistory(weeks = 4): Promise<LeaderboardHistoryEntry[]> {
    return apiClient.get<LeaderboardHistoryEntry[]>(`/social/leaderboard/weekly/history?weeks=${weeks}`);
  },

  async createChallenge(challengedId: string, skillId?: string): Promise<{ id: string; status: string }> {
    return apiClient.post('/social/challenges', {
      challenged_id: challengedId,
      skill_id: skillId || null,
    });
  },

  async acceptChallenge(challengeId: string): Promise<{ id: string; status: string }> {
    return apiClient.post(`/social/challenges/${challengeId}/accept`, {});
  },

  async completeChallenge(challengeId: string, score: number): Promise<any> {
    return apiClient.post(`/social/challenges/${challengeId}/complete`, { score });
  },

  async getMyChallenges(status?: string): Promise<ChallengeDTO[]> {
    const params = status ? `?status=${status}` : '';
    return apiClient.get<ChallengeDTO[]>(`/social/challenges${params}`);
  },
};
