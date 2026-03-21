import { create } from 'zustand';
import { SyncStatus, SyncItem, AppNotification } from './types';
import { apiClient } from './services/apiClient';

// NOTE: Auth state (User, Login, Logout) has been moved to `store/authStore.ts`
// This store now manages UI state and Business Logic (Offline, Sync, Notifications)

// --- Freemium daily exercise counter (localStorage-backed, works offline) ---
const DAILY_EXERCISES_KEY = 'ilma_daily_exercises';
const LAST_ACTIVITY_KEY = 'ilma_last_activity';

export interface LastActivity {
  skillId: string;
  skillName: string;
  subjectId?: string;
  subjectName?: string;
}

const getStoredLastActivity = (): LastActivity | null => {
  try {
    const stored = localStorage.getItem(LAST_ACTIVITY_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch { return null; }
};

const storeLastActivity = (activity: LastActivity | null): void => {
  try {
    if (activity) {
      localStorage.setItem(LAST_ACTIVITY_KEY, JSON.stringify(activity));
    } else {
      localStorage.removeItem(LAST_ACTIVITY_KEY);
    }
  } catch { /* ignore */ }
};

const getDailyCount = (): number => {
  const today = new Date().toISOString().split('T')[0];
  try {
    const stored = localStorage.getItem(DAILY_EXERCISES_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (parsed.date === today) return parsed.count;
    }
  } catch {
    // Corrupted data — treat as zero
  }
  return 0;
};

const incrementDailyCount = (): number => {
  const today = new Date().toISOString().split('T')[0];
  const current = getDailyCount();
  const next = current + 1;
  localStorage.setItem(DAILY_EXERCISES_KEY, JSON.stringify({ date: today, count: next }));
  return next;
};

const resetDailyCount = (): void => {
  localStorage.removeItem(DAILY_EXERCISES_KEY);
};

interface AppState {
  // UI State
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  isMobileDrawerOpen: boolean;
  setMobileDrawerOpen: (isOpen: boolean) => void;
  isNotificationOpen: boolean;
  setNotificationOpen: (isOpen: boolean) => void;

  // Network/Offline State
  isOffline: boolean;
  setOffline: (status: boolean) => void;
  syncStatus: SyncStatus;
  setSyncStatus: (status: SyncStatus) => void;
  pendingSyncItems: SyncItem[];
  setPendingSyncItems: (items: SyncItem[]) => void;

  // Subscription & Usage
  dailyExerciseCount: number;
  incrementDailyExercise: () => void;
  resetDailyExercise: () => void;

  // Last Activity (resume feature)
  lastActivity: LastActivity | null;
  setLastActivity: (activity: LastActivity | null) => void;

  // Notifications
  notifications: AppNotification[];
  fetchNotifications: () => Promise<void>;
  markNotificationAsRead: (id: string) => void;
  markAllNotificationsAsRead: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  // UI
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  isMobileDrawerOpen: false,
  setMobileDrawerOpen: (isOpen) => set({ isMobileDrawerOpen: isOpen }),
  isNotificationOpen: false,
  setNotificationOpen: (isOpen) => set({ isNotificationOpen: isOpen }),

  // Offline
  isOffline: false,
  setOffline: (status) => set({ isOffline: status }),
  syncStatus: SyncStatus.SYNCED,
  setSyncStatus: (status) => set({ syncStatus: status }),
  pendingSyncItems: [],
  setPendingSyncItems: (items) => set({ pendingSyncItems: items }),

  // Subscription & Usage (backed by localStorage for offline persistence)
  dailyExerciseCount: getDailyCount(),
  incrementDailyExercise: () => {
    const newCount = incrementDailyCount();
    set({ dailyExerciseCount: newCount });
  },
  resetDailyExercise: () => {
    resetDailyCount();
    set({ dailyExerciseCount: 0 });
  },
  
  // Last Activity
  lastActivity: getStoredLastActivity(),
  setLastActivity: (activity) => {
    storeLastActivity(activity);
    set({ lastActivity: activity });
  },

  // Notifications
  notifications: [],
  fetchNotifications: async () => {
    try {
      const data = await apiClient.get<any[]>('/notifications');
      const items: AppNotification[] = (data || []).map((n: any) => ({
        id: String(n.id),
        type: (n.type || n.notification_type || 'SYSTEM').toUpperCase(),
        title: n.title,
        message: n.message || n.body || '',
        timestamp: n.created_at || n.timestamp || new Date().toISOString(),
        read: n.read ?? n.is_read ?? false,
        actionUrl: n.action_url,
      }));
      set({ notifications: items });
    } catch {
      // Silently fail — notifications are non-critical
    }
  },
  markNotificationAsRead: (id) => {
    set((state) => ({
      notifications: state.notifications.map(n => n.id === id ? { ...n, read: true } : n)
    }));
    apiClient.post(`/notifications/${id}/read`, {}).catch(() => {});
  },
  markAllNotificationsAsRead: () => {
    set((state) => ({
      notifications: state.notifications.map(n => ({ ...n, read: true }))
    }));
    apiClient.post('/notifications/read-all', {}).catch(() => {});
  }
}));
