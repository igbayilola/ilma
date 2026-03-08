import { apiClient } from './apiClient';
import type { QuestionType } from '../types';

/** Map backend question_type (snake_case lowercase) to frontend QuestionType */
const QUESTION_TYPE_MAP: Record<string, QuestionType> = {
  mcq: 'MCQ',
  true_false: 'BOOLEAN',
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

export interface LessonDTO {
  id: string;
  title: string;
  contentHtml: string;
  summary?: string;
  durationMinutes: number;
  skillId: string;
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

  async listSkills(subjectId: string, domainId?: string): Promise<SkillDTO[]> {
    const url = domainId
      ? `/subjects/${subjectId}/chapters/${domainId}/skills`
      : `/subjects/${subjectId}/skills`;
    const data = await apiClient.get<any[]>(url);
    return (data || []).map((s: any) => ({
      id: String(s.id),
      name: s.name,
      slug: s.slug,
      description: s.description,
      domainId: String(s.domain_id),
      domainName: s.domain_name,
      order: s.order,
    }));
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

  async listQuestions(skillId: string, microSkillId?: string): Promise<QuestionDTO[]> {
    const params = microSkillId ? `?micro_skill_id=${microSkillId}` : '';
    const data = await apiClient.get<any[]>(`/subjects/skills/${skillId}/questions${params}`);
    return (data || []).map((q: any) => ({
      id: String(q.id),
      type: mapQuestionType(q.question_type || 'mcq'),
      prompt: q.text,
      options: Array.isArray(q.choices) ? q.choices : undefined,
      choices: q.choices,
      correctAnswer: q.correct_answer,
      explanation: q.explanation,
      hint: q.hint,
      imageUrl: q.media_url,
      points: q.points,
      timeLimitSeconds: q.time_limit_seconds,
      microSkillId: q.micro_skill_id ? String(q.micro_skill_id) : undefined,
    }));
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

  async importQuestionsCsv(file: File): Promise<{ created: number; errors: Array<{ row: number; error: string }> }> {
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
};
