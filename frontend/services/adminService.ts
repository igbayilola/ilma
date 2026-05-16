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

export interface DigestStatsDTO {
  totalAllTime: number;
  digestsThisWeek: number;
  digestsLastWeek: number;
  uniqueParentsReached: number;
  avgChildrenPerDigest: number;
}

export interface EngagementTimeSeriesPoint {
  date: string;
  dau: number;
}

export interface EngagementDTO {
  dau: number;
  wau: number;
  mau: number;
  stickiness: number;
  timeSeries: EngagementTimeSeriesPoint[];
}

export interface RetentionCohortDTO {
  cohortWeek: string;
  cohortSize: number;
  d1: number | null;
  d7: number | null;
  d14: number | null;
  d30: number | null;
}

export interface ConversionStageDTO {
  stage: string;
  count: number;
  conversionRate: number;
}

export interface ConversionDTO {
  stages: ConversionStageDTO[];
}

export interface NotificationChannelStatDTO {
  channel: string;
  sentCount: number;
  deliveredCount: number;
  failedCount: number;
  failureRate: number;
}

export interface NotificationDailyDTO {
  date: string;
  total: number;
  delivered: number;
  deliveryRate: number;
}

export interface NotificationErrorDTO {
  error: string;
  count: number;
}

export interface NotificationStatsDTO {
  total24h: number;
  total7d: number;
  total30d: number;
  byChannel: NotificationChannelStatDTO[];
  topErrors: NotificationErrorDTO[];
  dailySeries: NotificationDailyDTO[];
}

export type AtRiskLevel = 'medium' | 'high';

export interface AtRiskFunnelDTO {
  periodDays: number;
  detectedNow: number;
  smsSent: number;
  smsWithReactivation: number;
  reactivationRate: number; // 0..1
}

export interface AtRiskStudentDTO {
  profileId: string;
  displayName: string;
  gradeLevel: string | null;
  parentUserId: string | null;
  parentPhone: string | null;
  lastCompletedAt: string | null;
  daysInactive: number;
  avgScore: number;
  riskLevel: 'low' | 'medium' | 'high';
  suggestedAction: string;
}

export interface ViralityDTO {
  totalChallenges: number;
  challengesThisMonth: number;
  activeChallengers: number;
  mau: number;
  newUsersThisMonth: number;
  invitationsPerUser: number;
  inviteConversionRate: number;
  kFactor: number;
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

  async getDigestStats(): Promise<DigestStatsDTO> {
    const data = await apiClient.get<any>('/admin/analytics/digest-stats');
    return {
      totalAllTime: data.total_all_time ?? 0,
      digestsThisWeek: data.digests_this_week ?? 0,
      digestsLastWeek: data.digests_last_week ?? 0,
      uniqueParentsReached: data.unique_parents_reached ?? 0,
      avgChildrenPerDigest: data.avg_children_per_digest ?? 0,
    };
  },

  async getEngagement(): Promise<EngagementDTO> {
    const data = await apiClient.get<any>('/admin/analytics/engagement');
    return {
      dau: data.dau ?? 0,
      wau: data.wau ?? 0,
      mau: data.mau ?? 0,
      stickiness: data.stickiness ?? 0,
      timeSeries: (data.time_series || []).map((p: any) => ({
        date: p.date,
        dau: p.dau ?? 0,
      })),
    };
  },

  async getRetention(): Promise<RetentionCohortDTO[]> {
    const data = await apiClient.get<any>('/admin/analytics/retention');
    return (Array.isArray(data) ? data : []).map((c: any) => ({
      cohortWeek: c.cohort_week || '',
      cohortSize: c.cohort_size ?? 0,
      d1: c.d1,
      d7: c.d7,
      d14: c.d14,
      d30: c.d30,
    }));
  },

  async getConversion(): Promise<ConversionDTO> {
    const data = await apiClient.get<any>('/admin/analytics/conversion');
    return {
      stages: (data.stages || []).map((s: any) => ({
        stage: s.stage || '',
        count: s.count ?? 0,
        conversionRate: s.conversion_rate ?? 0,
      })),
    };
  },

  async getVirality(): Promise<ViralityDTO> {
    const data = await apiClient.get<any>('/admin/analytics/virality');
    return {
      totalChallenges: data.total_challenges ?? 0,
      challengesThisMonth: data.challenges_this_month ?? 0,
      activeChallengers: data.active_challengers ?? 0,
      mau: data.mau ?? 0,
      newUsersThisMonth: data.new_users_this_month ?? 0,
      invitationsPerUser: data.invitations_per_user ?? 0,
      inviteConversionRate: data.invite_conversion_rate ?? 0,
      kFactor: data.k_factor ?? 0,
    };
  },

  async getNotificationStats(): Promise<NotificationStatsDTO> {
    const data = await apiClient.get<any>('/admin/analytics/notifications');
    return {
      total24h: data.total_24h ?? 0,
      total7d: data.total_7d ?? 0,
      total30d: data.total_30d ?? 0,
      byChannel: (data.by_channel || []).map((c: any) => ({
        channel: c.channel || '',
        sentCount: c.sent_count ?? 0,
        deliveredCount: c.delivered_count ?? 0,
        failedCount: c.failed_count ?? 0,
        failureRate: c.failure_rate ?? 0,
      })),
      topErrors: (data.top_errors || []).map((e: any) => ({
        error: e.error || '',
        count: e.count ?? 0,
      })),
      dailySeries: (data.daily_series || []).map((d: any) => ({
        date: d.date || '',
        total: d.total ?? 0,
        delivered: d.delivered ?? 0,
        deliveryRate: d.delivery_rate ?? 0,
      })),
    };
  },

  async exportUsersCsv(): Promise<void> {
    window.open('/api/v1/admin/export/users.csv', '_blank');
  },

  async getAtRiskFunnel(periodDays = 30): Promise<AtRiskFunnelDTO> {
    const data = await apiClient.get<any>(`/admin/analytics/at-risk-funnel?period_days=${periodDays}`);
    return {
      periodDays: data.period_days ?? periodDays,
      detectedNow: data.detected_now ?? 0,
      smsSent: data.sms_sent ?? 0,
      smsWithReactivation: data.sms_with_reactivation ?? 0,
      reactivationRate: data.reactivation_rate ?? 0,
    };
  },

  async listAtRisk(
    minLevel: AtRiskLevel = 'medium',
    page = 1,
    pageSize = 50,
  ): Promise<{ items: AtRiskStudentDTO[]; total: number; page: number; totalPages: number }> {
    const params = new URLSearchParams({
      min_level: minLevel,
      page: String(page),
      page_size: String(pageSize),
    });
    const data = await apiClient.get<any>(`/admin/students/at-risk?${params}`);
    const items: AtRiskStudentDTO[] = (data.items || []).map((r: any) => ({
      profileId: String(r.profile_id),
      displayName: r.display_name || '',
      gradeLevel: r.grade_level ?? null,
      parentUserId: r.parent_user_id ?? null,
      parentPhone: r.parent_phone ?? null,
      lastCompletedAt: r.last_completed_at ?? null,
      daysInactive: r.days_inactive ?? 0,
      avgScore: r.avg_score ?? 0,
      riskLevel: r.risk_level || 'low',
      suggestedAction: r.suggested_action || '',
    }));
    return {
      items,
      total: data.total ?? items.length,
      page: data.page ?? page,
      totalPages: Math.ceil((data.total ?? items.length) / pageSize),
    };
  },
};
