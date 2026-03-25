import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { Plus, Flame, Clock, TrendingUp, ChevronRight, Lightbulb, Zap, MessageSquare } from 'lucide-react';
import { parentService, ChildDTO, ChildHealthDTO } from '../../services/parentService';

const STATUS_CONFIG = {
  green: {
    bg: 'bg-green-500',
    ring: 'ring-green-200',
    label: 'En forme',
  },
  orange: {
    bg: 'bg-orange-400',
    ring: 'ring-orange-200',
    label: 'Attention',
  },
  red: {
    bg: 'bg-red-500',
    ring: 'ring-red-200',
    label: 'Alerte',
  },
};

const onboardingSteps = [
  { title: 'Bienvenue !', desc: "Suivez les progr\u00e8s de vos enfants en un coup d'\u0153il. Commencez par ajouter votre premier profil enfant.", icon: '\uD83D\uDC4B' },
  { title: 'Cr\u00e9er un profil', desc: 'Ajoutez un profil pour chaque enfant avec son pr\u00e9nom, sa classe et un avatar. Vous pouvez prot\u00e9ger chaque profil avec un code PIN.', icon: '\uD83D\uDC66' },
  { title: 'Fixez un objectif', desc: 'D\u00e9finissez un objectif hebdomadaire pour motiver votre enfant. Vous recevrez des alertes de progression.', icon: '\uD83C\uDFAF' },
];

export const ParentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [healthData, setHealthData] = useState<ChildHealthDTO[]>([]);
  const [childrenList, setChildrenList] = useState<ChildDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [onboardingStep, setOnboardingStep] = useState(0);
  const [digestSending, setDigestSending] = useState(false);
  const [digestMessage, setDigestMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        // Try health summary first (new endpoint)
        const health = await parentService.getHealthSummary().catch(() => []);
        setHealthData(health);

        // Fallback: also load children list for the "add profile" card
        const children = await parentService.listChildren().catch(() => []);
        setChildrenList(children);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (!isLoading && healthData.length === 0 && childrenList.length === 0) {
      const alreadyOnboarded = localStorage.getItem('sitou_parent_onboarded');
      if (!alreadyOnboarded) {
        setShowOnboarding(true);
      }
    }
  }, [isLoading, healthData, childrenList]);

  const handleOnboardingNext = () => {
    if (onboardingStep < onboardingSteps.length - 1) {
      setOnboardingStep(prev => prev + 1);
    } else {
      localStorage.setItem('sitou_parent_onboarded', 'true');
      setShowOnboarding(false);
    }
  };

  const handleAddChild = () => {
    navigate('/select-profile/create');
  };

  const handleTriggerDigest = async () => {
    setDigestSending(true);
    setDigestMessage(null);
    try {
      await parentService.triggerDigest();
      setDigestMessage({ type: 'success', text: 'Digest SMS envoyé avec succès !' });
    } catch {
      setDigestMessage({ type: 'error', text: "Erreur lors de l'envoi du digest." });
    } finally {
      setDigestSending(false);
      setTimeout(() => setDigestMessage(null), 4000);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Skeleton variant="text" className="w-64 h-8" />
        <div className="grid grid-cols-1 gap-6">
          {[1, 2].map(i => <Skeleton key={i} variant="rect" className="h-48" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-20 md:pb-0">
      <header>
        <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 font-display">Sant&eacute; scolaire</h1>
        <p className="text-gray-500 text-sm mt-1">Vue d'ensemble de vos enfants</p>
      </header>

      <div className="space-y-4">
        {healthData.map((child) => {
          const cfg = STATUS_CONFIG[child.status];
          const progressPct = child.weeklyGoalMinutes > 0
            ? Math.min(100, Math.round((child.timeThisWeekMinutes / child.weeklyGoalMinutes) * 100))
            : 0;

          return (
            <Card
              key={child.profileId}
              interactive
              onClick={() => navigate(`/app/parent/children/${child.profileId}`)}
              className="relative overflow-hidden"
            >
              {/* Status indicator + child info */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <img
                      src={child.avatarUrl}
                      alt={child.displayName}
                      className="w-14 h-14 rounded-2xl object-cover border-2 border-gray-100"
                    />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{child.displayName}</h3>
                    {child.streak > 0 ? (
                      <div className="flex items-center gap-1 text-sm text-orange-500 font-medium">
                        <Flame size={14} className="fill-orange-400" />
                        <span>S&eacute;rie : {child.streak} jour{child.streak > 1 ? 's' : ''}</span>
                      </div>
                    ) : child.daysInactive >= 3 ? (
                      <span className="text-sm text-gray-400">Inactif depuis {child.daysInactive} jours</span>
                    ) : (
                      <span className="text-sm text-gray-400">Actif r&eacute;cemment</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-4 h-4 rounded-full ${cfg.bg} ring-4 ${cfg.ring}`} title={cfg.label} />
                  <ChevronRight size={20} className="text-gray-300" />
                </div>
              </div>

              {/* Score bar */}
              <div className="mb-3">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-medium text-gray-500">Score moyen</span>
                  <span className="font-bold text-gray-700">{Math.round(child.averageScore)}%</span>
                </div>
                <div className="w-full bg-gray-100 h-2.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      child.averageScore >= 70 ? 'bg-green-500' :
                      child.averageScore >= 40 ? 'bg-orange-400' : 'bg-red-400'
                    }`}
                    style={{ width: `${Math.min(100, child.averageScore)}%` }}
                  />
                </div>
              </div>

              {/* Stats row */}
              <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                <div className="flex items-center gap-1">
                  <Clock size={12} />
                  <span className="font-medium">
                    {child.timeThisWeekMinutes > 60
                      ? `${Math.floor(child.timeThisWeekMinutes / 60)}h${String(child.timeThisWeekMinutes % 60).padStart(2, '0')}`
                      : `${child.timeThisWeekMinutes} min`
                    }
                  </span>
                  {child.timeDeltaMinutes !== 0 && (
                    <span className={`font-bold ${child.timeDeltaMinutes > 0 ? 'text-green-600' : 'text-red-500'}`}>
                      ({child.timeDeltaMinutes > 0 ? '+' : ''}{child.timeDeltaMinutes} min)
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  <TrendingUp size={12} />
                  <span className="font-medium">{progressPct}% de l'objectif</span>
                </div>
              </div>

              {/* Contextual advice */}
              {child.advice && (
                <div className={`flex items-start gap-2 p-3 rounded-xl text-xs font-medium ${
                  child.status === 'green' ? 'bg-green-50 text-green-700' :
                  child.status === 'red' ? 'bg-red-50 text-red-700' :
                  'bg-amber-50 text-amber-700'
                }`}>
                  {child.status === 'red' ? <Zap size={14} className="flex-shrink-0 mt-0.5" /> : <Lightbulb size={14} className="flex-shrink-0 mt-0.5" />}
                  <span>{child.advice}</span>
                </div>
              )}
            </Card>
          );
        })}

        {/* Digest SMS button */}
        {healthData.length > 0 && (
          <div className="space-y-2">
            <button
              onClick={handleTriggerDigest}
              disabled={digestSending}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-sitou-primary text-white font-bold rounded-2xl hover:bg-amber-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <MessageSquare size={18} />
              {digestSending ? 'Envoi en cours…' : 'Recevoir le digest SMS'}
            </button>
            {digestMessage && (
              <p className={`text-sm text-center font-medium ${digestMessage.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                {digestMessage.text}
              </p>
            )}
          </div>
        )}

        {/* Add child card */}
        <button
          onClick={handleAddChild}
          className="w-full border-2 border-dashed border-gray-300 rounded-3xl p-6 flex items-center justify-center gap-3 text-gray-400 hover:border-sitou-primary hover:text-sitou-primary hover:bg-amber-50 transition-all"
        >
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm">
            <Plus size={24} />
          </div>
          <span className="font-bold">Ajouter un profil</span>
        </button>
      </div>

      {/* Onboarding modal for first-time parents */}
      {showOnboarding && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 text-center animate-fade-in">
            <div className="text-5xl mb-4">{onboardingSteps[onboardingStep].icon}</div>
            <h2 className="text-2xl font-extrabold text-gray-900 mb-2">
              {onboardingSteps[onboardingStep].title}
            </h2>
            <p className="text-gray-500 text-sm leading-relaxed mb-6">
              {onboardingSteps[onboardingStep].desc}
            </p>

            <div className="flex justify-center gap-2 mb-6">
              {onboardingSteps.map((_, i) => (
                <div
                  key={i}
                  className={`h-2 rounded-full transition-all ${i === onboardingStep ? 'w-8 bg-sitou-primary' : 'w-2 bg-gray-200'}`}
                />
              ))}
            </div>

            <Button fullWidth onClick={handleOnboardingNext}>
              {onboardingStep < onboardingSteps.length - 1 ? 'Suivant' : 'Commencer'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
