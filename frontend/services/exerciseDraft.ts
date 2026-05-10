/**
 * Persist/restore in-progress exercise state so the user can resume
 * after an accidental refresh, navigation, or connection loss.
 *
 * Stored in localStorage under key "sitou_exercise_draft".
 * Only ONE draft is kept at a time (latest session overwrites previous).
 */

export interface ExerciseDraft {
  /** Backend session ID */
  sessionId: string;
  /** Skill being exercised */
  skillId: string;
  skillName: string;
  microSkillId?: string;
  /** Current question data (from backend NextQuestionDTO) */
  currentQuestion: {
    questionId: string;
    text: string;
    questionType: string;
    difficulty: string;
    choices?: any;
    mediaUrl?: string;
    timeLimitSeconds?: number;
    points: number;
    microSkillId?: string;
  };
  /** User's answer for the current question (may be null if not yet answered) */
  selectedAnswer: any;
  /** 0-based index of the current question */
  currentQIndex: number;
  /** Running score */
  score: number;
  mistakes: number;
  totalQuestions: number;
  /** ISO timestamp of when the session started */
  sessionStartedAt: string;
  /** ISO timestamp of last save */
  savedAt: string;
  /** Navigation context */
  navState?: {
    returnPath?: string;
    subjectId?: string;
    subjectName?: string;
  };
}

const STORAGE_KEY = 'sitou_exercise_draft';
const MAX_AGE_MS = 2 * 60 * 60 * 1000; // 2 hours — discard stale drafts

export function saveDraft(draft: ExerciseDraft): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...draft, savedAt: new Date().toISOString() }));
  } catch {
    // Storage full or unavailable — silently ignore
  }
}

export function loadDraft(skillId: string): ExerciseDraft | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const draft: ExerciseDraft = JSON.parse(raw);
    // Must match the requested skill
    if (draft.skillId !== skillId) return null;
    // Must not be stale
    if (Date.now() - new Date(draft.savedAt).getTime() > MAX_AGE_MS) {
      clearDraft();
      return null;
    }
    return draft;
  } catch {
    clearDraft();
    return null;
  }
}

export function clearDraft(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
