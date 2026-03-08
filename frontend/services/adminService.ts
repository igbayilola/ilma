import { apiClient } from './apiClient';

export interface AdminUserDTO {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: string;
  isActive: boolean;
  lastLogin?: string;
}

export interface KpiDTO {
  totalUsers: number;
  totalStudents: number;
  dau: number;
  mau: number;
  mrrXof: number;
  activeSubscriptions: number;
  sessionsToday: number;
  avgSessionScore: number;
}

export interface PaymentDTO {
  id: string;
  userName: string;
  userEmail: string;
  provider: string;
  providerTxId?: string;
  amountXof: number;
  status: string;
  createdAt?: string;
}

export interface QuestionStatDTO {
  questionId: string;
  prompt: string;
  skillName: string;
  successRate: number;
  avgTimeSeconds: number;
  totalAttempts: number;
}

export const adminService = {
  async listUsers(page = 1, pageSize = 50, role?: string, search?: string): Promise<{ items: AdminUserDTO[]; total: number; page: number; totalPages: number }> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (role) params.set('role', role);
    if (search) params.set('search', search);
    const data = await apiClient.get<any>(`/admin/users?${params}`);
    // Backend returns paginated() envelope: {items, total, page, page_size}
    const items = (data.items || data || []).map((u: any) => ({
      id: String(u.id),
      name: u.full_name || u.name || '',
      email: u.email || '',
      phone: u.phone,
      role: (u.role || '').toUpperCase(),
      isActive: u.is_active ?? true,
      lastLogin: u.last_login,
    }));
    return {
      items,
      total: data.total || items.length,
      page: data.page || page,
      totalPages: Math.ceil((data.total || items.length) / pageSize),
    };
  },

  async suspendUser(userId: string): Promise<void> {
    await apiClient.post(`/admin/users/${userId}/suspend`, {});
  },

  async reactivateUser(userId: string): Promise<void> {
    await apiClient.post(`/admin/users/${userId}/reactivate`, {});
  },

  async getKpis(): Promise<KpiDTO> {
    const data = await apiClient.get<any>('/admin/analytics/kpis');
    return {
      totalUsers: data.total_users ?? 0,
      totalStudents: data.total_students ?? 0,
      dau: data.dau ?? 0,
      mau: data.mau ?? 0,
      mrrXof: data.mrr_xof ?? 0,
      activeSubscriptions: data.active_subscriptions ?? 0,
      sessionsToday: data.sessions_today ?? 0,
      avgSessionScore: data.avg_session_score ?? 0,
    };
  },

  async listPayments(page = 1, pageSize = 50, status?: string): Promise<{ items: PaymentDTO[]; total: number; page: number; totalPages: number }> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (status) params.set('status', status);
    const data = await apiClient.get<any>(`/admin/payments?${params}`);
    const items = (data.items || data || []).map((p: any) => ({
      id: String(p.id),
      userName: p.user_name || '',
      userEmail: p.user_email || '',
      provider: p.provider || 'mock',
      providerTxId: p.provider_tx_id,
      amountXof: p.amount_xof ?? 0,
      status: p.status || 'pending',
      createdAt: p.created_at,
    }));
    return {
      items,
      total: data.total || items.length,
      page: data.page || page,
      totalPages: Math.ceil((data.total || items.length) / pageSize),
    };
  },

  async getQuestionStats(limit = 50): Promise<QuestionStatDTO[]> {
    const data = await apiClient.get<any>(`/admin/analytics/questions?limit=${limit}`);
    return (Array.isArray(data) ? data : []).map((q: any) => ({
      questionId: q.question_id || '',
      prompt: q.prompt || '',
      skillName: q.skill_name || '',
      successRate: q.success_rate ?? 0,
      avgTimeSeconds: q.avg_time_seconds ?? 0,
      totalAttempts: q.total_attempts ?? 0,
    }));
  },

  async exportUsersCsv(): Promise<void> {
    window.open('/api/v1/admin/export/users.csv', '_blank');
  },
};
