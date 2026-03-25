import { apiClient } from './apiClient';

export interface MockExamDTO {
  id: string;
  title: string;
  description?: string;
  duration_minutes: number;
  total_questions: number;
  is_free: boolean;
  grade_level_id?: string;
}

export interface ExamSessionDTO {
  session_id: string;
  questions: ExamQuestionDTO[];
}

export interface ExamQuestionDTO {
  id: string;
  text: string;
  question_type: 'mcq' | 'true_false' | 'fill_blank';
  choices?: string[];
  media_url?: string;
  order: number;
}

export interface ExamAnswerResultDTO {
  question_id: string;
  answer: string;
  recorded: boolean;
}

export interface ExamCompletionDTO {
  score: number;
  total_correct: number;
  total_questions: number;
  predicted_cep_score: number;
  percentage: number;
}

export interface ExamSessionDetailDTO {
  id: string;
  mock_exam_id: string;
  mock_exam_title: string;
  score: number;
  total_correct: number;
  total_questions: number;
  predicted_cep_score: number;
  percentage: number;
  completed_at: string;
  duration_minutes: number;
  answers: ExamAnswerDetailDTO[];
}

export interface ExamAnswerDetailDTO {
  question_id: string;
  question_text: string;
  question_type: string;
  choices?: string[];
  student_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation?: string;
  related_lesson_id?: string;
}

export interface ExamHistoryItemDTO {
  session_id: string;
  mock_exam_title: string;
  score: number;
  total_correct: number;
  total_questions: number;
  predicted_cep_score: number;
  percentage: number;
  completed_at: string;
}

export const examService = {
  listExams: () => apiClient.get<MockExamDTO[]>('/exams'),
  startExam: (mockExamId: string) =>
    apiClient.post<ExamSessionDTO>('/exams/start', { mock_exam_id: mockExamId }),
  submitAnswer: (sessionId: string, questionId: string, answer: string) =>
    apiClient.post<ExamAnswerResultDTO>(`/exams/sessions/${sessionId}/answer`, {
      question_id: questionId,
      answer,
    }),
  completeExam: (sessionId: string) =>
    apiClient.post<ExamCompletionDTO>(`/exams/sessions/${sessionId}/complete`, {}),
  getSession: (sessionId: string) =>
    apiClient.get<ExamSessionDetailDTO>(`/exams/sessions/${sessionId}`),
  getHistory: () => apiClient.get<ExamHistoryItemDTO[]>('/exams/history'),
};
