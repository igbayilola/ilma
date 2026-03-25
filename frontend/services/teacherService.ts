import { apiClient } from './apiClient';

export interface ClassroomDTO {
  id: string;
  name: string;
  invite_code: string;
  grade_level_id?: string;
  student_count: number;
  created_at: string;
  is_active: boolean;
}

export interface ClassroomDetailDTO extends ClassroomDTO {
  students: ClassroomStudentDTO[];
}

export interface ClassroomStudentDTO {
  profile_id: string;
  display_name: string;
  avatar_url?: string;
  joined_at: string;
}

export interface AssignmentDTO {
  id: string;
  title: string;
  skill_id: string;
  skill_name?: string;
  deadline?: string;
  question_count?: number;
  created_at: string;
}

export interface AssignmentResultDTO {
  id: string;
  title: string;
  skill_name?: string;
  deadline?: string;
  results: StudentResultDTO[];
}

export interface StudentResultDTO {
  profile_id: string;
  display_name: string;
  best_score: number;
  avg_score: number;
  attempts: number;
}

export interface ClassroomOverviewDTO {
  avg_score: number;
  active_students: number;
  total_students: number;
  students_in_difficulty: AlertStudentDTO[];
}

export interface AlertStudentDTO {
  profile_id: string;
  display_name: string;
  classroom_name?: string;
  classroom_id?: string;
  avg_score: number;
  skill_name?: string;
}

export interface CreateAssignmentData {
  title: string;
  skill_id: string;
  deadline?: string;
  question_count?: number;
}

export const teacherService = {
  listClassrooms: () => apiClient.get<ClassroomDTO[]>('/teacher/classrooms'),
  createClassroom: (data: { name: string; grade_level_id?: string }) =>
    apiClient.post<ClassroomDTO>('/teacher/classrooms', data),
  getClassroom: (id: string) => apiClient.get<ClassroomDetailDTO>(`/teacher/classrooms/${id}`),
  deleteClassroom: (id: string) => apiClient.delete(`/teacher/classrooms/${id}`),
  joinClassroom: (inviteCode: string) =>
    apiClient.post('/teacher/classrooms/join', { invite_code: inviteCode }),
  removeStudent: (classroomId: string, profileId: string) =>
    apiClient.delete(`/teacher/classrooms/${classroomId}/students/${profileId}`),
  createAssignment: (classroomId: string, data: CreateAssignmentData) =>
    apiClient.post<AssignmentDTO>(`/teacher/classrooms/${classroomId}/assignments`, data),
  listAssignments: (classroomId: string) =>
    apiClient.get<AssignmentDTO[]>(`/teacher/classrooms/${classroomId}/assignments`),
  getAssignmentResults: (id: string) =>
    apiClient.get<AssignmentResultDTO>(`/teacher/assignments/${id}/results`),
  getOverview: (classroomId: string) =>
    apiClient.get<ClassroomOverviewDTO>(`/teacher/classrooms/${classroomId}/overview`),
  getReport: (classroomId: string) => apiClient.get(`/teacher/classrooms/${classroomId}/report`),
  getAlerts: () => apiClient.get<AlertStudentDTO[]>('/teacher/alerts'),
};
