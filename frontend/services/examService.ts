import { apiClient } from './apiClient';

export interface MockExamDTO {
  id: string;
  title: string;
  description?: string;
  duration_minutes: number;
  total_questions: number;
  is_free: boolean;
  grade_level_id?: string;
  exam_type?: 'cep' | 'qcm';
}

// QCM format
export interface ExamQuestionDTO {
  id: string;
  text: string;
  question_type: 'mcq' | 'true_false' | 'fill_blank';
  choices?: string[];
  media_url?: string;
  order: number;
}

// CEP format
export interface ExamSubQuestionDTO {
  id: string;
  sub_label: string;
  text: string;
  question_type: 'numeric_input' | 'fill_blank' | 'true_false' | 'mcq';
  choices?: string[];
  depends_on_previous: boolean;
  hint?: string;
  points: number;
}

export interface ExamItemDTO {
  item_number: number;
  domain: string;
  context_text: string;
  points: number;
  sub_questions: ExamSubQuestionDTO[];
}

export interface ExamSessionDTO {
  session_id: string;
  exam_type?: 'cep' | 'qcm';
  duration_minutes?: number;
  // QCM format
  questions?: ExamQuestionDTO[];
  // CEP format
  context_text?: string;
  items?: ExamItemDTO[];
  total_questions?: number;
}

export interface ExamAnswerResultDTO {
  question_id?: string;
  item_number?: number;
  sub_label?: string;
  answer: string;
  recorded: boolean;
  correct?: boolean;
  points_earned?: number;
}

export interface ExamCompletionDTO {
  score: number;
  total_correct: number;
  total_questions: number;
  predicted_cep_score: number;
  percentage: number;
  exam_type?: string;
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
  exam_type?: 'cep' | 'qcm';
  // QCM format
  answers: ExamAnswerDetailDTO[];
  // CEP format
  context_text?: string;
  items?: ExamItemCorrectionDTO[];
  corrections?: ExamAnswerDetailDTO[];
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

export interface ExamSubQuestionCorrectionDTO {
  sub_question_id: string;
  sub_label: string;
  text: string;
  question_type: string;
  choices?: string[];
  student_answer?: string;
  correct_answer: string;
  is_correct: boolean;
  points_earned: number;
  points_possible: number;
  explanation?: string;
  hint?: string;
  depends_on_previous: boolean;
  time_seconds?: number;
}

export interface ExamItemCorrectionDTO {
  item_number: number;
  domain: string;
  context_text: string;
  points: number;
  sub_questions: ExamSubQuestionCorrectionDTO[];
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
  exam_type?: string;
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
  submitCepAnswer: (sessionId: string, itemNumber: number, subLabel: string, answer: string) =>
    apiClient.post<ExamAnswerResultDTO>(`/exams/sessions/${sessionId}/answer`, {
      item_number: itemNumber,
      sub_label: subLabel,
      answer,
    }),
  completeExam: (sessionId: string) =>
    apiClient.post<ExamCompletionDTO>(`/exams/sessions/${sessionId}/complete`, {}),
  getSession: (sessionId: string) =>
    apiClient.get<ExamSessionDetailDTO>(`/exams/sessions/${sessionId}`),
  getHistory: () => apiClient.get<ExamHistoryItemDTO[]>('/exams/history'),
};
