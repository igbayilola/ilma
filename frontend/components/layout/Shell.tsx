
import React, { useState, useCallback } from 'react';
import { useAuthStore } from '../../store/authStore';
import { useAppStore } from '../../store';
import { NavItem, UserRole, SubscriptionTier } from '../../types';
import { Link, useLocation } from 'react-router-dom';
import {
  Home, BookOpen, Award, User, Menu, Bell, Trophy,
  Settings, LogOut, X, ChevronRight, FileEdit,
  LayoutDashboard, Users, FileText, BarChart2, Shield, Target, AlertTriangle, Crown, Cloud, ArrowLeftRight,
  School, ClipboardList
} from 'lucide-react';
import { OfflineBanner, SyncCounter } from '../ilma/OfflineIndicators';
import { XPBar, StreakWidget, LEVEL_NAMES } from '../ilma/Gamification';
import { NotificationCenter } from '../notifications/NotificationCenter';
import { dbService } from '../../services/db';
import { syncManager } from '../../services/syncManager';

// Definitive Navigation Configuration
const NAV_ITEMS: NavItem[] = [
  // Student & Guest
  { label: 'Accueil', path: '/app/student/dashboard', icon: 'Home', allowedRoles: [UserRole.STUDENT, UserRole.GUEST] },
  { label: 'Mati\u00e8res', path: '/app/student/subjects', icon: 'BookOpen', allowedRoles: [UserRole.STUDENT, UserRole.GUEST] },
  { label: 'Classement', path: '/app/student/leaderboard', icon: 'Trophy', allowedRoles: [UserRole.STUDENT, UserRole.GUEST] },
  { label: 'Progression', path: '/app/student/progress', icon: 'Award', allowedRoles: [UserRole.STUDENT, UserRole.GUEST] },
  { label: 'Profil', path: '/app/student/profile', icon: 'User', allowedRoles: [UserRole.STUDENT, UserRole.GUEST] },

  // Parent
  { label: 'Dashboard', path: '/app/parent/dashboard', icon: 'LayoutDashboard', allowedRoles: [UserRole.PARENT] },
  { label: 'Enfants', path: '/app/parent/children', icon: 'Users', allowedRoles: [UserRole.PARENT] },
  { label: 'Objectifs', path: '/app/parent/goals', icon: 'Target', allowedRoles: [UserRole.PARENT] },
  { label: 'Alertes', path: '/app/parent/alerts', icon: 'AlertTriangle', allowedRoles: [UserRole.PARENT] },

  // Teacher
  { label: 'Dashboard', path: '/app/teacher/dashboard', icon: 'LayoutDashboard', allowedRoles: [UserRole.TEACHER] },
  { label: 'Mes Classes', path: '/app/teacher/dashboard', icon: 'School', allowedRoles: [UserRole.TEACHER] },
  { label: 'Alertes', path: '/app/teacher/dashboard', icon: 'AlertTriangle', allowedRoles: [UserRole.TEACHER] },

  // Admin
  { label: 'Dashboard', path: '/app/admin/dashboard', icon: 'LayoutDashboard', allowedRoles: [UserRole.ADMIN] },
  { label: 'Contenu', path: '/app/admin/content', icon: 'FileText', allowedRoles: [UserRole.ADMIN] },
  { label: 'Utilisateurs', path: '/app/admin/users', icon: 'Users', allowedRoles: [UserRole.ADMIN] },
  { label: 'Analytics', path: '/app/admin/analytics', icon: 'BarChart2', allowedRoles: [UserRole.ADMIN] },
  { label: 'Editorial', path: '/app/admin/editorial', icon: 'FileEdit', allowedRoles: [UserRole.ADMIN] },
  { label: 'Config', path: '/app/admin/config', icon: 'Shield', allowedRoles: [UserRole.ADMIN] },
];

const IconMap: Record<string, React.ReactNode> = {
  Home: <Home size={24} />,
  BookOpen: <BookOpen size={24} />,
  Trophy: <Trophy size={24} />,
  Award: <Award size={24} />,
  User: <User size={24} />,
  LayoutDashboard: <LayoutDashboard size={24} />,
  Users: <Users size={24} />,
  Target: <Target size={24} />,
  AlertTriangle: <AlertTriangle size={24} />,
  FileText: <FileText size={24} />,
  BarChart2: <BarChart2 size={24} />,
  Shield: <Shield size={24} />,
  FileEdit: <FileEdit size={24} />,
  School: <School size={24} />,
  ClipboardList: <ClipboardList size={24} />,
};

// --- Sync-aware logout guard ---

interface LogoutGuardState {
  showModal: boolean;
  pendingCount: number;
  syncing: boolean;
}

const LogoutGuardModal: React.FC<{
  pendingCount: number;
  onCancel: () => void;
  onForceLogout: () => void;
}> = ({ pendingCount, onCancel, onForceLogout }) => (
  <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-sm w-full mx-4 p-6">
      <div className="flex items-center mb-4">
        <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg mr-3">
          <AlertTriangle size={24} className="text-red-500" />
        </div>
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
          Données non synchronisées
        </h3>
      </div>
      <p className="text-gray-600 dark:text-gray-300 text-sm mb-6">
        {pendingCount} événement{pendingCount > 1 ? 's' : ''} non synchronisé{pendingCount > 1 ? 's' : ''}.
        Si vous vous déconnectez, ces données seront perdues.
        Connectez-vous à internet pour synchroniser avant de vous déconnecter.
      </p>
      <div className="flex space-x-3">
        <button
          onClick={onCancel}
          className="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          Annuler
        </button>
        <button
          onClick={onForceLogout}
          className="flex-1 px-4 py-2.5 rounded-xl bg-red-500 text-white font-medium hover:bg-red-600 transition-colors"
        >
          Déconnexion forcée
        </button>
      </div>
    </div>
  </div>
);

const SyncingOverlay: React.FC = () => (
  <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-xs w-full mx-4 p-6 text-center">
      <div className="animate-spin w-8 h-8 border-4 border-ilma-primary border-t-transparent rounded-full mx-auto mb-4"></div>
      <p className="text-gray-700 dark:text-gray-300 font-medium">Synchronisation en cours...</p>
      <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Veuillez patienter</p>
    </div>
  </div>
);

function useSafeLogout() {
  const { logout } = useAuthStore();
  const [guard, setGuard] = useState<LogoutGuardState>({
    showModal: false,
    pendingCount: 0,
    syncing: false,
  });

  const attemptLogout = useCallback(async () => {
    try {
      const count = await dbService.getPendingSyncCount();

      if (count === 0) {
        await logout();
        return;
      }

      if (navigator.onLine) {
        // Online with pending events: sync first, then logout
        setGuard({ showModal: false, pendingCount: count, syncing: true });
        try {
          await syncManager.processQueue();
        } catch {
          // Sync failed — check remaining count
        }
        const remaining = await dbService.getPendingSyncCount();
        if (remaining === 0) {
          setGuard({ showModal: false, pendingCount: 0, syncing: false });
          await logout();
        } else {
          // Some items failed to sync, show modal
          setGuard({ showModal: true, pendingCount: remaining, syncing: false });
        }
      } else {
        // Offline with pending events: warn user
        setGuard({ showModal: true, pendingCount: count, syncing: false });
      }
    } catch {
      // If we can't even check, just logout
      await logout();
    }
  }, [logout]);

  const forceLogout = useCallback(async () => {
    setGuard({ showModal: false, pendingCount: 0, syncing: false });
    await logout();
  }, [logout]);

  const cancelLogout = useCallback(() => {
    setGuard({ showModal: false, pendingCount: 0, syncing: false });
  }, []);

  return { guard, attemptLogout, forceLogout, cancelLogout };
}

// Sidebar Component (Desktop)
const Sidebar: React.FC = () => {
  const { pathname } = useLocation();
  const { user, activeProfile, profiles } = useAuthStore();
  const { guard, attemptLogout, forceLogout, cancelLogout } = useSafeLogout();

  // When a parent has selected a child profile, show student nav items
  const effectiveRole = (user?.role === UserRole.PARENT && activeProfile) ? UserRole.STUDENT : user?.role;
  const filteredItems = NAV_ITEMS.filter(item => effectiveRole && item.allowedRoles.includes(effectiveRole));
  const isPremium = activeProfile?.subscriptionTier === SubscriptionTier.PREMIUM || user?.subscriptionTier === SubscriptionTier.PREMIUM;
  const displayName = activeProfile?.displayName || user?.name;
  const displayAvatar = activeProfile?.avatarUrl || user?.avatarUrl;

  return (
    <aside className="hidden md:flex flex-col w-64 gradient-sidebar dark:bg-gray-900 border-r border-ilma-border dark:border-gray-700 h-screen fixed left-0 top-0 z-30">
      <div className="p-6 flex items-center justify-start border-b border-ilma-border h-20">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-xl mr-3 shadow-lg gradient-hero">
          I
        </div>
        <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-amber-600 via-orange-500 to-yellow-500 bg-clip-text text-transparent font-display">ILMA</span>
      </div>

      <div className="p-6">
        <div className="mb-6 relative">
            <div className="flex items-center space-x-3 mb-2">
                <div className="relative">
                    <img src={displayAvatar} alt="Avatar" className={`w-10 h-10 rounded-full bg-gray-200 object-cover ${isPremium ? 'border-2 border-yellow-400' : ''}`} />
                    {isPremium && (
                        <div className="absolute -top-2 -right-1 bg-yellow-400 text-white rounded-full p-0.5 border border-white">
                            <Crown size={10} fill="currentColor"/>
                        </div>
                    )}
                </div>
                <div className="flex-1 min-w-0">
                    <p className="font-bold text-sm text-gray-900 line-clamp-1">{displayName}</p>
                    {(effectiveRole === UserRole.STUDENT || effectiveRole === UserRole.GUEST) && <p className="text-xs text-gray-500">Niv. {user?.level} — {LEVEL_NAMES[user?.level ?? 1] || 'Apprenti'}</p>}
                    {effectiveRole !== UserRole.STUDENT && effectiveRole !== UserRole.GUEST && <p className="text-xs text-gray-500 capitalize">{effectiveRole?.toLowerCase()}</p>}
                </div>
                {(profiles.length > 1 || user?.role === UserRole.PARENT) && (
                    <Link to="/select-profile" className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors" title="Changer de profil">
                        <ArrowLeftRight size={16} className="text-gray-400" />
                    </Link>
                )}
            </div>
            {(effectiveRole === UserRole.STUDENT || effectiveRole === UserRole.GUEST) && <XPBar current={user.xp} max={user.xpToNextLevel} level={user.level} />}
        </div>

        <nav className="space-y-2" aria-label="Navigation principale">
          {filteredItems.map((item) => {
            const isActive = pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? 'gradient-hero text-white shadow-clay-sm'
                    : 'text-gray-600 hover:bg-ilma-primary-light hover:text-ilma-primary'
                }`}
              >
                <span className={`mr-3 ${isActive ? 'text-white' : 'text-gray-400 group-hover:text-ilma-primary'}`}>
                  {IconMap[item.icon]}
                </span>
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="mt-auto p-6 border-t border-ilma-border">
         {(effectiveRole === UserRole.STUDENT || effectiveRole === UserRole.GUEST) && !isPremium && (
             <div className="bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 rounded-2xl p-4 border border-yellow-200 shadow-sm">
                 <div className="flex items-center mb-1">
                     <Crown size={16} className="text-yellow-500 mr-2 fill-yellow-500" />
                     <h4 className="font-bold text-gray-800 text-sm">Premium</h4>
                 </div>
                 <p className="text-xs text-gray-500 mb-3">D&eacute;bloque tous les cours et le mode hors-ligne illimit&eacute;.</p>
                 <Link to="/app/subscription/plans">
                     <button className="w-full gradient-hero text-white text-xs font-bold py-2 rounded-lg shadow-clay-sm hover:shadow-clay-hover transition-shadow">
                         Voir les offres
                     </button>
                 </Link>
             </div>
         )}
         {isPremium && (
             <div className="text-center">
                 <span className="text-xs font-bold text-yellow-600 bg-yellow-100 px-3 py-1 rounded-full flex items-center justify-center">
                     <Crown size={12} className="mr-1 fill-current" /> Membre Premium
                 </span>
             </div>
         )}
         <button
           onClick={attemptLogout}
           className="w-full flex items-center px-4 py-3 mt-4 rounded-xl text-gray-500 hover:bg-red-50 hover:text-ilma-red transition-colors group"
         >
           <LogOut size={20} className="mr-3 text-gray-400 group-hover:text-ilma-red" />
           <span className="font-medium">D&eacute;connexion</span>
         </button>
      </div>
      {guard.syncing && <SyncingOverlay />}
      {guard.showModal && (
        <LogoutGuardModal
          pendingCount={guard.pendingCount}
          onCancel={cancelLogout}
          onForceLogout={forceLogout}
        />
      )}
    </aside>
  );
};

// Mobile Bottom Nav
const MobileNav: React.FC = () => {
  const { pathname } = useLocation();
  const { user, activeProfile } = useAuthStore();
  const effectiveRole = (user?.role === UserRole.PARENT && activeProfile) ? UserRole.STUDENT : user?.role;

  // Show max 4 items on mobile
  const filteredItems = NAV_ITEMS
    .filter(item => effectiveRole && item.allowedRoles.includes(effectiveRole))
    .slice(0, 4);

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 pb-safe z-40 h-[72px] flex items-center justify-around px-2 shadow-clay" aria-label="Navigation mobile">
      {filteredItems.map((item) => {
        const isActive = pathname.startsWith(item.path);
        return (
          <Link
            key={item.path}
            to={item.path}
            className={`flex flex-col items-center justify-center w-full h-full p-2`}
          >
            <div className={`p-1.5 rounded-full mb-1 transition-all ${isActive ? 'gradient-hero text-white scale-110 shadow-md' : 'text-gray-400'}`}>
               {React.cloneElement(IconMap[item.icon] as React.ReactElement<any>, { size: 20 })}
            </div>
            <span className={`text-[10px] font-bold ${isActive ? 'text-ilma-primary' : 'text-gray-500'}`}>
              {item.label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
};

// Drawer for Mobile Menu
const MobileDrawer: React.FC = () => {
    const { isMobileDrawerOpen, setMobileDrawerOpen } = useAppStore();
    const { user, activeProfile } = useAuthStore();
    const { guard, attemptLogout, forceLogout, cancelLogout } = useSafeLogout();
    const effectiveRole = (user?.role === UserRole.PARENT && activeProfile) ? UserRole.STUDENT : user?.role;
    const isPremium = activeProfile?.subscriptionTier === SubscriptionTier.PREMIUM || user?.subscriptionTier === SubscriptionTier.PREMIUM;
    const displayName = activeProfile?.displayName || user?.name;
    const displayAvatar = activeProfile?.avatarUrl || user?.avatarUrl;

    if (!isMobileDrawerOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex justify-end">
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setMobileDrawerOpen(false)}></div>
            <div className="relative w-4/5 max-w-xs bg-white h-full shadow-2xl animate-slide-in-right flex flex-col">
                <div className="p-5 border-b border-gray-100 flex items-center justify-between">
                    <h2 className="font-bold text-lg text-gray-800 font-display">Menu</h2>
                    <button onClick={() => setMobileDrawerOpen(false)} className="p-2 bg-gray-100 rounded-full">
                        <X size={20} />
                    </button>
                </div>

                <div className="p-5 flex-1 overflow-y-auto">
                    <div className="mb-6 flex items-center space-x-3">
                         <img src={displayAvatar} className="w-12 h-12 rounded-full" alt="profile" />
                         <div>
                             <p className="font-bold">{displayName}</p>
                             <div className="flex items-center space-x-2">
                                 <div className="text-xs text-gray-500 flex items-center capitalize">
                                     {effectiveRole?.toLowerCase()}
                                 </div>
                                 {isPremium && <span className="text-[10px] bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded font-bold border border-yellow-200">PRO</span>}
                             </div>
                         </div>
                    </div>

                    <div className="space-y-1">
                        {!isPremium && (
                            <Link to="/app/subscription/plans" className="flex items-center justify-between p-3 rounded-xl gradient-hero text-white shadow-lg mb-4">
                                <div className="flex items-center font-bold"><Crown size={20} className="mr-3 fill-white"/> Passer Premium</div>
                                <ChevronRight size={16} />
                            </Link>
                        )}

                        {(effectiveRole === UserRole.STUDENT || effectiveRole === UserRole.GUEST) && (
                            <Link to="/app/student/offline-management" onClick={() => setMobileDrawerOpen(false)} className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 text-gray-700">
                                <div className="flex items-center"><Cloud size={20} className="mr-3 text-gray-400"/> Gestion Hors-Ligne</div>
                                <ChevronRight size={16} className="text-gray-300" />
                            </Link>
                        )}

                        <Link to="/app/student/settings" onClick={() => setMobileDrawerOpen(false)} className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 text-gray-700">
                            <div className="flex items-center"><Settings size={20} className="mr-3 text-gray-400"/> Param&egrave;tres</div>
                            <ChevronRight size={16} className="text-gray-300" />
                        </Link>
                         <button
                            onClick={async () => {
                                setMobileDrawerOpen(false);
                                await attemptLogout();
                            }}
                            className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-red-50 text-ilma-red mt-4"
                         >
                             <div className="flex items-center"><LogOut size={20} className="mr-3"/> D&eacute;connexion</div>
                        </button>
                    </div>
                </div>
                {guard.syncing && <SyncingOverlay />}
                {guard.showModal && (
                  <LogoutGuardModal
                    pendingCount={guard.pendingCount}
                    onCancel={cancelLogout}
                    onForceLogout={forceLogout}
                  />
                )}
            </div>
        </div>
    );
};

// Header (Adaptive)
const Header: React.FC = () => {
  const { setMobileDrawerOpen, setNotificationOpen, notifications } = useAppStore();
  const { user, activeProfile } = useAuthStore();
  const effectiveRole = (user?.role === UserRole.PARENT && activeProfile) ? UserRole.STUDENT : user?.role;

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-ilma-border dark:border-gray-700 h-16 md:h-20 flex items-center justify-between px-4 md:px-8 sticky top-0 z-20">
      <div className="flex items-center md:hidden">
          <div className="w-8 h-8 gradient-hero rounded-lg flex items-center justify-center text-white font-bold mr-3">I</div>
      </div>


      <div className="flex items-center space-x-3 md:space-x-6">
        <SyncCounter />
        {(effectiveRole === UserRole.STUDENT || effectiveRole === UserRole.GUEST) && <StreakWidget days={user?.streak ?? 0} active={true} />}

        <button
            className="relative p-2 rounded-full hover:bg-gray-100 transition-colors"
            onClick={() => setNotificationOpen(true)}
            aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} non lues)` : ''}`}
        >
            <Bell className={`w-6 h-6 ${unreadCount > 0 ? 'text-gray-800' : 'text-gray-500'}`} />
            {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-ilma-red rounded-full border-2 border-white flex items-center justify-center text-[8px] text-white font-bold">
                    {unreadCount}
                </span>
            )}
        </button>

        {/* Mobile Menu Trigger */}
        <button onClick={() => setMobileDrawerOpen(true)} className="md:hidden p-2" aria-label="Ouvrir le menu">
            <Menu className="w-6 h-6 text-gray-800" />
        </button>
      </div>
    </header>
  );
};

// Main Layout Wrapper
export const AppShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-ilma-surface dark:bg-gray-950 flex flex-col">
      {/* Skip to content link for keyboard users */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[100] focus:bg-ilma-primary focus:text-white focus:px-4 focus:py-2 focus:rounded-lg focus:text-sm focus:font-bold"
      >
        Aller au contenu principal
      </a>
      <OfflineBanner />
      <NotificationCenter />
      <Sidebar />
      <MobileDrawer />

      <div className="flex-1 md:ml-64 flex flex-col pb-20 md:pb-0">
        <Header />
        <main id="main-content" className="flex-1 p-4 md:p-8 max-w-6xl mx-auto w-full animate-fade-in" role="main">
            {children}
        </main>
      </div>

      <MobileNav />
    </div>
  );
};
