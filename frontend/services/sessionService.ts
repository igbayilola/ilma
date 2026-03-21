import { apiClient } from './apiClient';

export interface SessionDTO {
  id: string;
  skillId: string;
  status: string;
  score?: number;
  totalQuestions?: number;
  correctAnswers?: number;
  smartScoreBefore?: number;
  smartScoreAfter?: number;
  xpEarned?: number;
}

export interface NextQuestionDTO {
  questionId: string;
  text: string;
  questionType: string;
  difficulty: string;
  choices?: string[];
  mediaUrl?: string;
  timeLimitSeconds?: number;
  points: number;
  microSkillId?: string;
}

export interface AttemptResultDTO {
  id: string;
  isCorrect: boolean;
  correctAnswer: any;
  explanation?: string;
  pointsEarned: number;
}

function genEventId(): string {
  try { return crypto.randomUUID(); } catch { return `evt_${Date.now()}_${Math.random().toString(36).slice(2)}`; }
}

export const sessionService = {
  async startSession(skillId: string, mode: string = 'practice', microSkillId?: string): Promise<SessionDTO> {
    const body: Record<string, any> = { skill_id: skillId, mode };
    if (microSkillId) body.micro_skill_id = microSkillId;
    const data = await apiClient.post<any>('/sessions/start', body);
    return {
      id: String(data.id),
      skillId: String(data.skill_id),
      status: data.status,
      score: data.score,
      totalQuestions: data.total_questions,
      correctAnswers: data.correct_answers,
    };
  },

  async getNextQuestion(sessionId: string): Promise<NextQuestionDTO | null> {
    const data = await apiClient.get<any>(`/sessions/${sessionId}/next`);
    if (!data) return null;
    return {
      questionId: String(data.question_id),
      text: data.text,
      questionType: data.question_type,
      difficulty: data.difficulty,
      choices: data.choices,
      mediaUrl: data.media_url,
      timeLimitSeconds: data.time_limit_seconds,
      points: data.points,
      microSkillId: data.micro_skill_id ? String(data.micro_skill_id) : undefined,
    };
  },

  async recordAttempt(sessionId: string, questionId: string, answer: any, timeSpent: number = 0): Promise<AttemptResultDTO> {
    const data = await apiClient.post<any>(`/sessions/${sessionId}/attempt`, {
      question_id: questionId,
      client_event_id: genEventId(),
      answer,
      time_spent_seconds: timeSpent,
    });
    return {
      id: String(data.id),
      isCorrect: data.is_correct,
      correctAnswer: data.correct_answer,
      explanation: data.explanation,
      pointsEarned: data.points_earned ?? 0,
    };
  },

  async completeSession(sessionId: string): Promise<SessionDTO> {
    const data = await apiClient.post<any>(`/sessions/${sessionId}/complete`, {});
    return {
      id: String(data.id),
      skillId: String(data.skill_id),
      status: data.status,
      score: data.score,
      totalQuestions: data.total_questions,
      correctAnswers: data.correct_answers,
      smartScoreBefore: data.smart_score_before,
      smartScoreAfter: data.smart_score_after,
      xpEarned: data.xp_earned,
    };
  },
};
