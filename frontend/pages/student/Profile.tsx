import React, { useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import { useSync, useSyncStatus } from '../../contexts/SyncContext';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { XPBar, StreakWidget } from '../../components/ilma/Gamification';
import { RefreshCw, LogOut, Settings, Clock, CheckCircle2, Zap, WifiOff, GraduationCap } from 'lucide-react';
import { ButtonVariant, SyncStatus } from '../../types';
import { useNavigate } from 'react-router-dom';

export const ProfilePage: React.FC = () => {
  const { user, logout, activeProfile } = useAuthStore();
  const displayName = activeProfile?.displayName || user?.name;
  const displayAvatar = activeProfile?.avatarUrl || user?.avatarUrl;
  const { triggerSync, isOffline } = useSync();
  const syncStatus = useSyncStatus();
  const navigate = useNavigate();
  const [selectedGrade, setSelectedGrade] = useState('cm2');

  const handleGradeChange = (value: string) => {
    setSelectedGrade(value);
  };

  if (!user) return null;

  const isSyncing = syncStatus === SyncStatus.SYNCING;

  return (
    <div className="space-y-6">
       {/* 1. Header Profile Card */}
       <Card className="flex flex-col md:flex-row items-center md:items-start text-center md:text-left p-8 border-none bg-gradient-to-br from-white to-amber-50">
           <div className="relative mb-4 md:mb-0 md:mr-8">
               <img src={displayAvatar} alt="Avatar" loading="eager" decoding="async" width={96} height={96} className="w-24 h-24 md:w-32 md:h-32 rounded-full border-4 border-white shadow-lg object-cover bg-gray-200" />
               <div className="absolute bottom-0 right-0 bg-sitou-primary text-white text-sm font-bold px-3 py-1 rounded-full border-2 border-white">
                   Niv. {user.level}
               </div>
           </div>
           
           <div className="flex-1 w-full">
               <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4">
                   <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900">{displayName}</h1>
                   <div className="mt-2 md:mt-0 flex justify-center md:justify-end">
                        <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-wide">
                            {user.role}
                        </span>
                   </div>
               </div>
               
               <div className="mb-6">
                   <XPBar current={user.xp} max={user.xpToNextLevel} level={user.level} />
               </div>

               <div className="flex justify-center md:justify-start space-x-4">
                    <StreakWidget days={user.streak} active={true} />
               </div>
           </div>
       </Card>

       {/* 2. Stats Grid */}
       <div className="bento-grid grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatsCard icon={<CheckCircle2 size={24}/>} label="Exercices" value="42" color="bg-green-50 text-green-700" />
            <StatsCard icon={<Zap size={24}/>} label="Score Moyen" value="85%" color="bg-yellow-50 text-yellow-700" />
            <StatsCard icon={<Clock size={24}/>} label="Temps" value="3h 15m" color="bg-purple-50 text-purple-700" />
            <StatsCard icon={<Settings size={24}/>} label="Défis" value="12" color="bg-amber-50 text-amber-700" />
       </div>

       {/* 3. Grade Level Selector */}
       <Card>
           <div className="flex items-center mb-6">
               <div className="p-2 bg-indigo-100 rounded-lg mr-3 text-indigo-600">
                   <GraduationCap size={24} />
               </div>
               <div>
                   <h2 className="text-lg font-bold text-gray-900">Niveau scolaire</h2>
                   <p className="text-sm text-gray-500">Sélectionnez votre classe pour accéder au bon programme.</p>
               </div>
           </div>
           <select
             value={selectedGrade}
             onChange={(e) => handleGradeChange(e.target.value)}
             className="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm font-medium focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary bg-white"
             aria-label="Niveau scolaire"
           >
             <option value="cm2">CM2 (10-11 ans)</option>
             <option value="cm1" disabled>CM1 (9-10 ans) — Bientôt</option>
             <option value="6e" disabled>6ème (11-12 ans) — Bientôt</option>
           </select>
       </Card>

       {/* 4. Sync & Settings Actions */}
       <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
           {/* Sync Control */}
           <Card>
               <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                   <RefreshCw size={20} className="mr-2 text-gray-500" /> État de la synchronisation
               </h3>
               
               <div className="flex items-center justify-between mb-6 p-3 bg-gray-50 rounded-xl border border-gray-100">
                   <div className="flex items-center">
                       <div className={`w-3 h-3 rounded-full mr-3 ${isOffline ? 'bg-red-500' : 'bg-green-500'}`} />
                       <span className="text-sm font-medium text-gray-600">
                           {isOffline ? 'Hors ligne' : 'Connecté'}
                       </span>
                   </div>
                   <span className="text-xs font-bold text-gray-400 uppercase">{syncStatus}</span>
               </div>

               <Button 
                   fullWidth 
                   variant={ButtonVariant.SECONDARY}
                   onClick={() => triggerSync()}
                   disabled={isOffline || isSyncing}
                   leftIcon={isOffline ? <WifiOff size={18}/> : <RefreshCw size={18} className={isSyncing ? "animate-spin" : ""} />}
               >
                   {isOffline ? 'Mode hors-ligne actif' : isSyncing ? 'Synchronisation...' : 'Synchroniser maintenant'}
               </Button>
               {!isOffline && <p className="text-xs text-center text-gray-400 mt-2">Dernière synchro : Il y a 5 min</p>}
           </Card>

           {/* Account Actions */}
           <Card>
               <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                   <Settings size={20} className="mr-2 text-gray-500" /> Mon Compte
               </h3>
               <div className="space-y-3">
                   <Button fullWidth variant={ButtonVariant.GHOST} className="justify-start">
                       Modifier mon profil
                   </Button>
                   <Button 
                        fullWidth 
                        variant={ButtonVariant.GHOST} 
                        className="justify-start"
                        onClick={() => navigate('/app/student/settings')}
                    >
                       Paramètres de notification
                   </Button>
                   <div className="pt-2 border-t border-gray-100">
                        <Button fullWidth variant={ButtonVariant.DANGER} onClick={logout} leftIcon={<LogOut size={18} />}>
                            Se déconnecter
                        </Button>
                   </div>
               </div>
           </Card>
       </div>
    </div>
  );
};

const StatsCard = ({ icon, label, value, color }: { icon: any, label: string, value: string, color: string }) => (
    <Card className="clay-card flex flex-col items-center justify-center p-4">
        <div className={`p-3 rounded-full mb-3 ${color}`}>
            {icon}
        </div>
        <span className="text-2xl font-extrabold text-gray-800">{value}</span>
        <span className="text-xs font-bold text-gray-400 uppercase">{label}</span>
    </Card>
);