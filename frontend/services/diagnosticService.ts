import { apiClient } from './apiClient';

export interface DiagnosticQuestionDTO {
  question_id: string;
  skill_id: string;
  domain_id: string;
  text: string;
  choices: string[];
  difficulty: string | null;
}

export interface DiagnosticQuestionsResponse {
  completed_at: string | null;
  questions: DiagnosticQuestionDTO[];
}

export interface DiagnosticDomainResult {
  domain_id: string;
  correct: number;
  total: number;
  accuracy: number;
}

export interface DiagnosticSummary {
  questions_answered: number;
  overall_accuracy: number;
  predicted: number;
  per_domain: DiagnosticDomainResult[];
}

export interface DiagnosticAnswer {
  question_id: string;
  answer: string;
}

export const diagnosticService = {
  getQuestions: () => apiClient.get<DiagnosticQuestionsResponse>('/diagnostic/questions'),
  submit: (answers: DiagnosticAnswer[]) =>
    apiClient.post<DiagnosticSummary>('/diagnostic/submit', { answers }),
};
