import { apiClient } from './apiClient';
import type { PaginatedResult, QuestionType } from '../types';

/** Map backend question_type (snake_case lowercase) to frontend QuestionType */
const QUESTION_TYPE_MAP: Record<string, QuestionType> = {
  mcq: 'MCQ',
  true_false: 'TRUE_FALSE',
  fill_blank: 'FILL_BLANK',
  numeric_input: 'NUMERIC_INPUT',
  short_answer: 'SHORT_ANSWER',
  ordering: 'ORDERING',
  matching: 'MATCHING',
  error_correction: 'ERROR_CORRECTION',
  contextual_problem: 'CONTEXTUAL_PROBLEM',
  guided_steps: 'GUIDED_STEPS',
  justification: 'JUSTIFICATION',
  tracing: 'TRACING',
  drag_drop: 'DRAG_DROP',
  interactive_draw: 'INTERACTIVE_DRAW',
  chart_input: 'CHART_INPUT',
  audio_comprehension: 'AUDIO_COMPREHENSION',
};

function mapQuestionType(backendType: string): QuestionType {
  return QUESTION_TYPE_MAP[backendType.toLowerCase()] || 'MCQ';
}

/** Map backend subject icon string to Lucide icon name */
const ICON_MAP: Record<string, string> = {
  math: 'Calculator', mathematics: 'Calculator', mathematiques: 'Calculator',
  fr: 'Book', français: 'Book', french: 'Book', francais: 'Book',
  sci: 'FlaskConical', sciences: 'FlaskConical', science: 'FlaskConical',
  geo: 'Globe', geographie: 'Globe', geography: 'Globe',
};

const COLOR_MAP: Record<string, { bg: string; text: string; gradient: string; emoji: string }> = {
  math: { bg: 'bg-blue-100', text: 'text-blue-700', gradient: 'gradient-math', emoji: '🧮' },
  fr: { bg: 'bg-purple-100', text: 'text-purple-700', gradient: 'gradient-french', emoji: '📖' },
  sci: { bg: 'bg-green-100', text: 'text-green-700', gradient: 'gradient-science', emoji: '🔬' },
  geo: { bg: 'bg-orange-100', text: 'text-orange-700', gradient: 'gradient-geo', emoji: '🌍' },
};

function getSubjectColors(slug: string) {
  return COLOR_MAP[slug] || { bg: 'bg-gray-100', text: 'text-gray-700', gradient: 'gradient-hero', emoji: '📚' };
}

function getIconName(slug: string): string {
  return ICON_MAP[slug] || 'BookOpen';
}

export interface GradeLevelDTO {
  id: string;
  name: string;
  slug: string;
  description?: string;
  order: number;
}

export interface SubjectDTO {
  id: string;
  name: string;
  slug: string;
  description?: string;
  iconName: string;
  color: string;
  textColor: string;
  gradient: string;
  emoji: string;
  order: number;
  gradeLevelId?: string;
}

export interface DomainDTO {
  id: string;
  name: string;
  slug: string;
  description?: string;
  subjectId: string;
  order: number;
}

export interface SkillDTO {
  id: string;
  name: string;
  slug: string;
  description?: string;
  domainId: string;
  domainName?: string;
  order: number;
}

export interface QuestionDTO {
  id: string;
  type: QuestionType;
  prompt: string;
  options?: string[];
  choices?: any;
  correctAnswer: any;
  explanation?: string;
  hint?: string;
  imageUrl?: string;
  points: number;
  timeLimitSeconds?: number;
  microSkillId?: string;
}

export interface LessonSectionBlock {
  title?: string;
  body_html: string;
  rules?: string[];
}

export interface LessonSections {
  activite_depart?: LessonSectionBlock;
  retenons?: LessonSectionBlock;
  exemples?: LessonSectionBlock;
  evaluation_note?: LessonSectionBlock;
}

export interface LessonDTO {
  id: string;
  title: string;
  contentHtml?: string;
  sections?: LessonSections;
  formula?: string;
  summary?: string;
  durationMinutes: number;
  skillId: string;
  externalId?: string;
}

// ── Formula DTOs ─────────────────────────────────────
export interface FormulaDTO {
  id: string;
  title: string;
  formula?: string;
  retenons?: {
    body_html: string;
    rules?: string[];
  };
  summary?: string;
  skillId: string;
  skillName: string;
  domainId: string;
  domainName: string;
  subjectName: string;
}

// ── Curriculum Tree DTOs ──────────────────────────────
export interface TreeMicroSkillDTO {
  id: string;
  external_id?: string;
  name: string;
  difficulty_index?: number;
  bloom_taxonomy_level?: string;
  mastery_threshold?: string;
  cep_frequency?: number;
  external_prerequisites?: Array<{ skill_id: string; micro_skill_id: string; why: string }>;
  order: number;
}

export interface TreeSkillDTO {
  id: string;
  external_id?: string;
  name: string;
  cep_frequency?: number;
  prerequisites?: string[];
  common_mistakes?: string[];
  exercise_types?: string[];
  mastery_threshold?: string;
  order: number;
  micro_skills: TreeMicroSkillDTO[];
}

export interface TreeDomainDTO {
  id: string;
  name: string;
  slug: string;
  order: number;
  skills: TreeSkillDTO[];
}

export interface TreeSubjectDTO {
  id: string;
  name: string;
  slug: string;
  icon?: string;
  color?: string;
  order: number;
  domains: TreeDomainDTO[];
}

export interface TreeGradeDTO {
  id: string;
  name: string;
  slug: string;
  description?: string;
  order: number;
  subjects: TreeSubjectDTO[];
}

export interface QuestionCommentDTO {
  id: string;
  questionId: string;
  authorId: string | null;
  authorName: string;
  text: string;
  createdAt: string;
}

export interface ContentVersionDTO {
  id: string;
  content_type: string;
  content_id: string;
  version: number;
  modified_by: string | null;
  modified_at: string;
  data_json?: Record<string, any>;
}

export interface KanbanQuestionDTO {
  id: string;
  text: string;
  questionType: string | null;
  difficulty: string | null;
  status: string;
  reviewerNotes: string | null;
  skillId: string;
  updatedAt: string | null;
}

export interface BulkImportRowError {
  row: number;
  message: string;
}

export interface BulkImportReport {
  status: 'success' | 'failed';
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  created: number;
  errors: BulkImportRowError[];
  rolled_back: boolean;
}

export interface CurriculumImportResult {
  grade_levels: number;
  subjects: number;
  domains: number;
  skills: number;
  micro_skills: number;
  created: number;
  updated: number;
  errors: Array<{ error: string }>;
}

export interface PrerequisiteItemDTO {
  externalId: string;
  name: string;
  skillId: string;
  smartScore: number;
  threshold: number;
  met: boolean;
}

export interface PrerequisiteCheckDTO {
  met: boolean;
  prerequisites: PrerequisiteItemDTO[];
}

export interface SearchResultDTO {
  type: 'skill' | 'question' | 'domain' | 'lesson';
  id: string;
  title: string;
  subtitle: string;
  score: number;
  skillId?: string;
  domainId?: string;
}

export const contentService = {
  // ── Grade Levels ──────────────────────────────────────
  async listGradeLevels(): Promise<GradeLevelDTO[]> {
    const data = await apiClient.get<any[]>('/subjects/grade-levels');
    return (data || []).map((g: any) => ({
      id: String(g.id),
      name: g.name,
      slug: g.slug,
      description: g.description,
      order: g.order,
    }));
  },

  async createGradeLevel(body: { name: string; slug: string; description?: string; order?: number }): Promise<GradeLevelDTO> {
    const data = await apiClient.post<any>('/admin/content/grade-levels', body);
    return { id: String(data.id), name: data.name, slug: data.slug, description: data.description, order: data.order };
  },

  async updateGradeLevel(id: string, body: { name?: string; slug?: string; description?: string; order?: number }): Promise<GradeLevelDTO> {
    const data = await apiClient.put<any>(`/admin/content/grade-levels/${id}`, body);
    return { id: String(data.id), name: data.name, slug: data.slug, description: data.description, order: data.order };
  },

  async deleteGradeLevel(id: string): Promise<void> {
    await apiClient.delete(`/admin/content/grade-levels/${id}`);
  },

  async deleteSubject(id: string): Promise<void> {
    await apiClient.delete(`/admin/content/subjects/${id}`);
  },

  // ── Subjects ──────────────────────────────────────────
  async listSubjects(gradeLevelId?: string): Promise<SubjectDTO[]> {
    const params = gradeLevelId ? `?grade_level_id=${gradeLevelId}` : '';
    const data = await apiClient.get<any[]>(`/subjects${params}`);
    return (data || []).map((s: any) => {
      const colors = getSubjectColors(s.slug);
      return {
        id: String(s.id),
        name: s.name,
        slug: s.slug,
        description: s.description,
        iconName: getIconName(s.slug),
        color: colors.bg,
        textColor: colors.text,
        gradient: colors.gradient,
        emoji: colors.emoji,
        order: s.order,
        gradeLevelId: s.grade_level_id ? String(s.grade_level_id) : undefined,
      };
    });
  },

  async getSubject(subjectId: string): Promise<SubjectDTO | null> {
    try {
      const data = await apiClient.get<any>(`/subjects/${subjectId}`);
      if (!data) return null;
      const colors = getSubjectColors(data.slug);
      return {
        id: String(data.id),
        name: data.name,
        slug: data.slug,
        description: data.description,
        iconName: getIconName(data.slug),
        color: colors.bg,
        textColor: colors.text,
        gradient: colors.gradient,
        emoji: colors.emoji,
        order: data.order,
        gradeLevelId: data.grade_level_id ? String(data.grade_level_id) : undefined,
      };
    } catch {
      return null;
    }
  },

  async getDomain(subjectId: string, domainId: string): Promise<DomainDTO | null> {
    try {
      const domains = await this.listDomains(subjectId);
      return domains.find(d => d.id === domainId) || null;
    } catch {
      return null;
    }
  },

  async listDomains(subjectId: string): Promise<DomainDTO[]> {
    const data = await apiClient.get<any[]>(`/subjects/${subjectId}/chapters`);
    return (data || []).map((d: any) => ({
      id: String(d.id),
      name: d.name,
      slug: d.slug,
      description: d.description,
      subjectId: String(d.subject_id),
      order: d.order,
    }));
  },

  async listSkills(subjectId: string, domainId?: string, page = 1, pageSize = 50): Promise<PaginatedResult<SkillDTO>> {
    const url = domainId
      ? `/subjects/${subjectId}/chapters/${domainId}/skills?page=${page}&page_size=${pageSize}`
      : `/subjects/${subjectId}/skills?page=${page}&page_size=${pageSize}`;
    const data = await apiClient.get<any>(url);
    const items = (data?.items || []).map((s: any) => ({
      id: String(s.id),
      name: s.name,
      slug: s.slug,
      description: s.description,
      domainId: String(s.domain_id),
      domainName: s.domain_name,
      order: s.order,
    }));
    return { items, total: data?.total || items.length, page: data?.page || 1, page_size: data?.page_size || pageSize, pages: data?.pages || 1 };
  },

  async getSkillWithLessons(skillId: string): Promise<{ skill: SkillDTO; lessons: LessonDTO[] }> {
    const data = await apiClient.get<any>(`/subjects/skills/${skillId}`);
    return {
      skill: {
        id: String(data.skill.id),
        name: data.skill.name,
        slug: data.skill.slug,
        description: data.skill.description,
        domainId: String(data.skill.domain_id),
        order: data.skill.order,
      },
      lessons: (data.lessons || []).map((l: any) => ({
        id: String(l.id),
        title: l.title,
        contentHtml: l.content_html,
        summary: l.summary,
        durationMinutes: l.duration_minutes,
        skillId: String(l.skill_id),
      })),
    };
  },

  async listQuestions(skillId: string, microSkillId?: string, page = 1, pageSize = 50): Promise<PaginatedResult<QuestionDTO>> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (microSkillId) params.set('micro_skill_id', microSkillId);
    const data = await apiClient.get<any>(`/subjects/skills/${skillId}/questions?${params}`);
    const items = (data?.items || []).map((q: any) => ({
      id: String(q.id),
      type: mapQuestionType(q.question_type || 'mcq'),
      prompt: q.text,
      options: Array.isArray(q.choices) ? q.choices : undefined,
      choices: q.choices,
      correctAnswer: q.correct_answer,
      explanation: q.explanation,
      hint: q.hint,
      hints: q.hints || (q.hint ? [q.hint] : undefined),
      imageUrl: q.media_url,
      points: q.points,
      timeLimitSeconds: q.time_limit_seconds,
      microSkillId: q.micro_skill_id ? String(q.micro_skill_id) : undefined,
      mediaReferences: q.media_references || undefined,
      interactiveConfig: q.interactive_config || undefined,
    }));
    return { items, total: data?.total || items.length, page: data?.page || 1, page_size: data?.page_size || pageSize, pages: data?.pages || 1 };
  },

  // ── Admin CRUD ──────────────────────────────────────────
  async createSubject(body: { name: string; slug: string; description?: string; grade_level_id?: string }): Promise<SubjectDTO> {
    const data = await apiClient.post<any>('/admin/content/subjects', body);
    const colors = getSubjectColors(data.slug);
    return { id: String(data.id), name: data.name, slug: data.slug, description: data.description, iconName: getIconName(data.slug), color: colors.bg, textColor: colors.text, gradient: colors.gradient, emoji: colors.emoji, order: data.order, gradeLevelId: data.grade_level_id ? String(data.grade_level_id) : undefined };
  },

  async createDomain(body: { name: string; slug: string; subject_id: string; description?: string }): Promise<DomainDTO> {
    const data = await apiClient.post<any>('/admin/content/domains', body);
    return { id: String(data.id), name: data.name, slug: data.slug, description: data.description, subjectId: String(data.subject_id), order: data.order };
  },

  async createSkill(body: { name: string; slug: string; domain_id: string; description?: string }): Promise<SkillDTO> {
    const data = await apiClient.post<any>('/admin/content/skills', body);
    return { id: String(data.id), name: data.name, slug: data.slug, description: data.description, domainId: String(data.domain_id), order: data.order };
  },

  async importQuestionsCsv(file: File): Promise<BulkImportReport> {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.upload('/admin/content/import/questions', formData);
  },

  async importQuestions(file: File): Promise<BulkImportReport> {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.upload('/admin/content/import/questions', formData);
  },

  // ── Curriculum Tree ─────────────────────────────────
  async getCurriculumTree(gradeLevelId?: string): Promise<TreeGradeDTO[]> {
    const params = gradeLevelId ? `?grade_level_id=${gradeLevelId}` : '';
    const data = await apiClient.get<TreeGradeDTO[]>(`/admin/content/curriculum/tree${params}`);
    return data || [];
  },

  // ── Curriculum Import ────────────────────────────────
  async importCurriculum(body: object): Promise<CurriculumImportResult> {
    const data = await apiClient.post<CurriculumImportResult>('/admin/content/curriculum/import', body);
    return data;
  },

  async importCurriculumFile(file: File): Promise<CurriculumImportResult> {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.upload('/admin/content/curriculum/import/file', formData);
  },

  // ── Content Workflow ─────────────────────────────────
  async listQuestionsByStatus(status: string, limit = 50, offset = 0): Promise<KanbanQuestionDTO[]> {
    const data = await apiClient.get<any[]>(`/admin/content/questions/by-status?status=${status}&limit=${limit}&offset=${offset}`);
    return (data || []).map((q: any) => ({
      id: q.id,
      text: q.text || '',
      questionType: q.question_type,
      difficulty: q.difficulty,
      status: q.status,
      reviewerNotes: q.reviewer_notes,
      skillId: q.skill_id,
      updatedAt: q.updated_at,
    }));
  },

  async transitionQuestion(questionId: string, targetStatus: string, reviewerNotes?: string): Promise<void> {
    await apiClient.post(`/admin/content/questions/${questionId}/transition`, {
      target_status: targetStatus,
      reviewer_notes: reviewerNotes || undefined,
    });
  },

  async previewQuestion(questionId: string): Promise<{
    id: string;
    questionType: string;
    difficulty: string;
    text: string;
    choices: any;
    correctAnswer: any;
    explanation: string | null;
    hint: string | null;
    mediaUrl: string | null;
    points: number;
    timeLimitSeconds: number | null;
    status: string;
  }> {
    const data = await apiClient.get<any>(`/admin/content/questions/${questionId}/preview`);
    return {
      id: data.id,
      questionType: data.question_type || 'mcq',
      difficulty: data.difficulty || 'medium',
      text: data.text,
      choices: data.choices,
      correctAnswer: data.correct_answer,
      explanation: data.explanation || null,
      hint: data.hint || null,
      mediaUrl: data.media_url || null,
      points: data.points,
      timeLimitSeconds: data.time_limit_seconds || null,
      status: data.status,
    };
  },

  async transitionLesson(lessonId: string, targetStatus: string, reviewerNotes?: string): Promise<void> {
    await apiClient.post(`/admin/content/lessons/${lessonId}/transition`, {
      target_status: targetStatus,
      reviewer_notes: reviewerNotes || undefined,
    });
  },

  // ── Question Comments ─────────────────────────────────
  async getQuestionComments(questionId: string): Promise<QuestionCommentDTO[]> {
    const data = await apiClient.get<any[]>(`/admin/content/questions/${questionId}/comments`);
    return (data || []).map((c: any) => ({
      id: c.id,
      questionId: c.question_id,
      authorId: c.author_id,
      authorName: c.author_name || '',
      text: c.text,
      createdAt: c.created_at,
    }));
  },

  async addQuestionComment(questionId: string, text: string): Promise<QuestionCommentDTO> {
    const c = await apiClient.post<any>(`/admin/content/questions/${questionId}/comments`, { text });
    return {
      id: c.id,
      questionId: c.question_id,
      authorId: c.author_id,
      authorName: c.author_name || '',
      text: c.text,
      createdAt: c.created_at,
    };
  },

  async deleteQuestionComment(questionId: string, commentId: string): Promise<void> {
    await apiClient.delete(`/admin/content/questions/${questionId}/comments/${commentId}`);
  },

  // ── Content Versioning ─────────────────────────────────
  async getQuestionVersions(questionId: string): Promise<ContentVersionDTO[]> {
    const data = await apiClient.get<ContentVersionDTO[]>(`/admin/content/questions/${questionId}/versions`);
    return data || [];
  },

  async getQuestionVersionDetail(questionId: string, version: number): Promise<ContentVersionDTO> {
    return apiClient.get<ContentVersionDTO>(`/admin/content/questions/${questionId}/versions/${version}`);
  },

  async rollbackQuestion(questionId: string, version: number): Promise<any> {
    return apiClient.post(`/admin/content/questions/${questionId}/rollback/${version}`, {});
  },

  async getLessonVersions(lessonId: string): Promise<ContentVersionDTO[]> {
    const data = await apiClient.get<ContentVersionDTO[]>(`/admin/content/lessons/${lessonId}/versions`);
    return data || [];
  },

  async rollbackLesson(lessonId: string, version: number): Promise<any> {
    return apiClient.post(`/admin/content/lessons/${lessonId}/rollback/${version}`, {});
  },

  // ── Search ──────────────────────────────────────────────
  async search(query: string, limit = 20): Promise<SearchResultDTO[]> {
    const data = await apiClient.get<any[]>(`/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    return (data || []).map((r: any) => ({
      type: r.type as 'skill' | 'question' | 'domain' | 'lesson',
      id: r.id,
      title: r.title,
      subtitle: r.subtitle || '',
      score: r.score,
      skillId: r.skill_id || undefined,
      domainId: r.domain_id || undefined,
    }));
  },

  // ── Prerequisites ───────────────────────────────────────
  async checkPrerequisites(skillId: string): Promise<PrerequisiteCheckDTO> {
    const data = await apiClient.get<any>(`/subjects/skills/${skillId}/prerequisites`);
    return {
      met: data?.met ?? true,
      prerequisites: (data?.prerequisites || []).map((p: any) => ({
        externalId: p.external_id,
        name: p.name,
        skillId: p.skill_id,
        smartScore: p.smart_score ?? 0,
        threshold: p.threshold ?? 70,
        met: p.met ?? true,
      })),
    };
  },

  // ── Formulas ─────────────────────────────────────────
  async listFormulas(): Promise<FormulaDTO[]> {
    const data = await apiClient.get<any[]>('/subjects/formulas');
    return (data || []).map((f: any) => ({
      id: String(f.id),
      title: f.title,
      formula: f.formula,
      retenons: f.retenons,
      summary: f.summary,
      skillId: String(f.skill_id),
      skillName: f.skill_name,
      domainId: String(f.domain_id),
      domainName: f.domain_name,
      subjectName: f.subject_name,
    }));
  },
};
