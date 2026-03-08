
import React, { Suspense, useEffect } from 'react';
import { HashRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AppShell } from './components/layout/Shell';
import { useAuthStore } from './store/authStore'; // Changed from appStore
import { UserRole } from './types';
import { ProtectedRoute, RoleRoute, GuestRoute, RequireProfile } from './components/auth/Guards';
import { SyncProvider } from './contexts/SyncContext';
import { ToastProvider } from './components/ui/Toast';
import { Skeleton } from './components/ui/Skeleton';
import { PWAUpdatePrompt } from './components/pwa/UpdatePrompt';
import { ErrorBoundary } from './components/common/ErrorBoundary';

// Retry wrapper for lazy imports — reloads the page once on chunk load failure
function lazyWithRetry<T extends React.ComponentType<any>>(
  factory: () => Promise<{ default: T }>
): React.LazyExoticComponent<T> {
  return React.lazy(() =>
    factory().catch((err) => {
      const key = 'ilma_chunk_retry';
      const hasRetried = sessionStorage.getItem(key);
      if (!hasRetried) {
        sessionStorage.setItem(key, '1');
        window.location.reload();
        return new Promise(() => {}); // never resolves — page is reloading
      }
      sessionStorage.removeItem(key);
      throw err;
    })
  );
}

// Helper for named-export modules
function lazyNamed<M extends Record<string, any>, K extends keyof M>(
  factory: () => Promise<M>,
  name: K
): React.LazyExoticComponent<M[K]> {
  return lazyWithRetry(() => factory().then(m => ({ default: m[name] })));
}

// Lazy Load Pages to reduce initial bundle size
const Dashboard = lazyNamed(() => import('./pages/Dashboard'), 'Dashboard');
const StyleGuide = lazyNamed(() => import('./pages/StyleGuide'), 'StyleGuide');
const SplashPage = lazyNamed(() => import('./pages/public/Splash'), 'SplashPage');
const LoginPage = lazyNamed(() => import('./pages/auth/Login'), 'LoginPage');
const RegisterPage = lazyNamed(() => import('./pages/auth/Register'), 'RegisterPage');
const OTPPage = lazyNamed(() => import('./pages/auth/OTP'), 'OTPPage');

// Profile selection
const ProfileSelectorPage = lazyNamed(() => import('./pages/auth/ProfileSelector'), 'ProfileSelectorPage');
const ProfileCreatePage = lazyNamed(() => import('./pages/auth/ProfileCreate'), 'ProfileCreatePage');

// Student Pages
const SubjectsPage = lazyNamed(() => import('./pages/student/Subjects'), 'SubjectsPage');
const DomainsPage = lazyNamed(() => import('./pages/student/Domains'), 'DomainsPage');
const SkillsPage = lazyNamed(() => import('./pages/student/Skills'), 'SkillsPage');
const ExercisePlayerPage = lazyNamed(() => import('./pages/student/ExercisePlayer'), 'ExercisePlayerPage');
const MicroLessonPage = lazyNamed(() => import('./pages/student/MicroLesson'), 'MicroLessonPage');
const ProgressPage = lazyNamed(() => import('./pages/student/Progress'), 'ProgressPage');
const BadgesPage = lazyNamed(() => import('./pages/student/Badges'), 'BadgesPage');
const ProfilePage = lazyNamed(() => import('./pages/student/Profile'), 'ProfilePage');
const StudentSettingsPage = lazyNamed(() => import('./pages/student/Settings'), 'StudentSettingsPage');
const OfflineManagementPage = lazyNamed(() => import('./pages/student/OfflineManagement'), 'OfflineManagementPage');

// Parent Pages
const ParentDashboard = lazyNamed(() => import('./pages/parent/Dashboard'), 'ParentDashboard');
const ChildDetailPage = lazyNamed(() => import('./pages/parent/ChildDetail'), 'ChildDetailPage');
const ParentSettingsPage = lazyNamed(() => import('./pages/parent/Settings'), 'ParentSettingsPage');
const ParentGoalsPage = lazyNamed(() => import('./pages/parent/Goals'), 'ParentGoalsPage');

// Subscription
const PlansPage = lazyNamed(() => import('./pages/subscription/Plans'), 'PlansPage');

// Admin Pages
const AdminDashboard = lazyNamed(() => import('./pages/admin/Dashboard'), 'AdminDashboard');
const AdminContentPage = lazyNamed(() => import('./pages/admin/Content'), 'AdminContentPage');
const AdminUsersPage = lazyNamed(() => import('./pages/admin/Users'), 'AdminUsersPage');
const AdminSubsPage = lazyNamed(() => import('./pages/admin/Subscriptions'), 'AdminSubsPage');
const AdminAnalyticsPage = lazyNamed(() => import('./pages/admin/Analytics'), 'AdminAnalyticsPage');
const AdminConfigPage = lazyNamed(() => import('./pages/admin/Config'), 'AdminConfigPage');

// Other Pages
const DebugSyncPage = lazyNamed(() => import('./pages/DebugSync'), 'DebugSyncPage');
const UnauthorizedPage = lazyNamed(() => import('./pages/Placeholders'), 'UnauthorizedPage');

// Global Loading Fallback
const PageLoader = () => (
    <div className="w-full h-screen flex flex-col items-center justify-center space-y-4 p-8">
        <div className="w-12 h-12 border-4 border-ilma-primary-light border-t-ilma-primary rounded-full animate-spin"></div>
        <Skeleton variant="text" className="w-32 mx-auto" />
    </div>
);

// Layout wrapper for authenticated routes to ensure Shell is always present
const AppLayout = () => {
    return (
        <AppShell>
            <Suspense fallback={<PageLoader />}>
                <Outlet />
            </Suspense>
        </AppShell>
    );
};

// Auth Initializer Component
const AuthInitializer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { checkAuth, isLoading } = useAuthStore();

    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    if (isLoading) {
        return <PageLoader />;
    }

    return <>{children}</>;
};

const App: React.FC = () => {
  const { user, profiles, activeProfile } = useAuthStore();

  // Root redirect logic
  const getHomeRoute = () => {
      if (!user) return '/login';

      // If user has multiple profiles and no active one → profile selector
      if (profiles.length > 1 && !activeProfile) {
          return '/select-profile';
      }

      switch(user.role) {
          case UserRole.PARENT:
            // Parents with profiles go to selector, without go to dashboard
            return profiles.length > 0 && !activeProfile ? '/select-profile' : '/app/parent/dashboard';
          case UserRole.ADMIN: return '/app/admin/dashboard';
          case UserRole.STUDENT:
          case UserRole.GUEST:
            return '/app/student/dashboard';
          default: return '/app/student/dashboard';
      }
  };

  return (
    <ToastProvider>
        <SyncProvider>
            <AuthInitializer>
                <HashRouter>
                <ErrorBoundary>
                <Suspense fallback={<PageLoader />}>
                    <Routes>
                        {/* Public Routes */}
                        <Route element={<GuestRoute />}>
                            <Route path="/" element={<SplashPage />} />
                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/register" element={<RegisterPage />} />
                            <Route path="/otp" element={<OTPPage />} />
                        </Route>

                        <Route path="/styleguide" element={<AppShell><StyleGuide /></AppShell>} />
                        <Route path="/unauthorized" element={<UnauthorizedPage />} />

                        {/* Profile Selection (requires auth but not profile) */}
                        <Route path="/select-profile" element={<ProtectedRoute />}>
                            <Route index element={<ProfileSelectorPage />} />
                            <Route path="create" element={<ProfileCreatePage />} />
                        </Route>

                        {/* Protected Application Routes */}
                        <Route path="/app" element={<ProtectedRoute />}>
                            <Route element={<AppLayout />}>

                                {/* Redirect /app to specific role dashboard */}
                                <Route index element={<Navigate to={getHomeRoute()} replace />} />

                                {/* Shared Debug Route */}
                                <Route path="debug/sync" element={<DebugSyncPage />} />
                                <Route path="subscription/plans" element={<PlansPage />} />

                                {/* STUDENT & GUEST ROUTES — wrapped with RequireProfile */}
                                <Route path="student" element={<RoleRoute allowedRoles={[UserRole.STUDENT, UserRole.GUEST]} />}>
                                    <Route element={<RequireProfile />}>
                                        <Route path="dashboard" element={<Dashboard />} />

                                        {/* Educational Flow */}
                                        <Route path="subjects" element={<SubjectsPage />} />
                                        <Route path="subjects/:subjectId" element={<DomainsPage />} />
                                        <Route path="subjects/:subjectId/domains/:domainId" element={<SkillsPage />} />

                                        <Route path="exercise/:id" element={<ExercisePlayerPage />} />
                                        <Route path="lesson/:id" element={<MicroLessonPage />} />

                                        <Route path="progress" element={<ProgressPage />} />
                                        <Route path="badges" element={<BadgesPage />} />
                                        <Route path="profile" element={<ProfilePage />} />
                                        <Route path="settings" element={<StudentSettingsPage />} />
                                        <Route path="offline-management" element={<OfflineManagementPage />} />
                                    </Route>
                                </Route>

                                {/* PARENT ROUTES — no RequireProfile needed */}
                                <Route path="parent" element={<RoleRoute allowedRoles={[UserRole.PARENT]} />}>
                                    <Route path="dashboard" element={<ParentDashboard />} />
                                    <Route path="children" element={<ParentDashboard />} /> {/* Fallback to dashboard for list */}
                                    <Route path="children/:childId" element={<ChildDetailPage />} />
                                    <Route path="goals" element={<ParentGoalsPage />} />
                                    <Route path="alerts" element={<ParentSettingsPage />} /> {/* Alerts are inside settings now */}
                                    <Route path="settings" element={<ParentSettingsPage />} />
                                </Route>

                                {/* ADMIN ROUTES */}
                                <Route path="admin" element={<RoleRoute allowedRoles={[UserRole.ADMIN]} />}>
                                    <Route path="dashboard" element={<AdminDashboard />} />
                                    <Route path="content" element={<AdminContentPage />} />
                                    <Route path="users" element={<AdminUsersPage />} />
                                    <Route path="subs" element={<AdminSubsPage />} />
                                    <Route path="analytics" element={<AdminAnalyticsPage />} />
                                    <Route path="config" element={<AdminConfigPage />} />
                                </Route>

                            </Route>
                        </Route>

                        {/* Catch all - Redirect to root (which handles auth redirect) */}
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </Suspense>
                </ErrorBoundary>
                </HashRouter>
            </AuthInitializer>
        </SyncProvider>
    <PWAUpdatePrompt />
    </ToastProvider>
  );
};

export default App;
