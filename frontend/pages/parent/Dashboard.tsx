import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { Plus, Clock, TrendingUp, ChevronRight } from 'lucide-react';
import { StreakWidget } from '../../components/ilma/Gamification';
import { parentService, ChildDTO } from '../../services/parentService';

const onboardingSteps = [
  { title: 'Bienvenue !', desc: "Suivez les progr\u00e8s de vos enfants en un coup d'\u0153il. Commencez par ajouter votre premier profil enfant.", icon: '\uD83D\uDC4B' },
  { title: 'Créer un profil', desc: 'Ajoutez un profil pour chaque enfant avec son prénom, sa classe et un avatar. Vous pouvez protéger chaque profil avec un code PIN.', icon: '\uD83D\uDC66' },
  { title: 'Fixez un objectif', desc: 'D\u00e9finissez un objectif hebdomadaire pour motiver votre enfant. Vous recevrez des alertes de progression.', icon: '\uD83C\uDFAF' },
];

export const ParentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [childrenList, setChildrenList] = useState<ChildDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [childProgress, setChildProgress] = useState<Record<string, any>>({});
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [onboardingStep, setOnboardingStep] = useState(0);

  useEffect(() => {
    parentService.listChildren()
      .then(setChildrenList)
      .catch(() => setChildrenList([]))
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    // After children are loaded, fetch progress for each
    childrenList.forEach(async (child) => {
      try {
        const progress = await parentService.getChildProgress(child.id);
        setChildProgress(prev => ({ ...prev, [child.id]: progress }));
      } catch { /* silently fail, show 0 */ }
    });
  }, [childrenList]);

  useEffect(() => {
    if (!isLoading && childrenList.length === 0) {
      const alreadyOnboarded = localStorage.getItem('ilma_parent_onboarded');
      if (!alreadyOnboarded) {
        setShowOnboarding(true);
      }
    }
  }, [isLoading, childrenList]);

  const handleOnboardingNext = () => {
    if (onboardingStep < onboardingSteps.length - 1) {
      setOnboardingStep(prev => prev + 1);
    } else {
      localStorage.setItem('ilma_parent_onboarded', 'true');
      setShowOnboarding(false);
    }
  };

  const handleAddChild = () => {
    navigate('/select-profile/create');
  };

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Skeleton variant="text" className="w-64 h-8" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2].map(i => <Skeleton key={i} variant="rect" className="h-64" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900">Tableau de bord Parents</h1>
            <p className="text-gray-500">Suivez les progrès de vos enfants en un coup d'œil.</p>
        </div>
        <Button onClick={handleAddChild} leftIcon={<Plus size={20} />}>
            Ajouter un profil
        </Button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {childrenList.map((child) => (
            <Card key={child.id} interactive onClick={() => navigate(`/app/parent/children/${child.id}`)} className="group relative overflow-hidden">
                <div className="flex items-start justify-between mb-6 relative z-10">
                    <div className="flex items-center space-x-4">
                        <img src={child.avatar} alt={child.name} className="w-16 h-16 rounded-2xl object-cover border-2 border-gray-100" />
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">{child.name}</h3>
                            <span className="text-sm text-gray-500 font-medium">Niveau {child.level}</span>
                        </div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded-full group-hover:bg-ilma-primary group-hover:text-white transition-colors">
                        <ChevronRight size={20} />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-6 relative z-10">
                    <div className="bg-blue-50 rounded-xl p-3 text-center">
                        <Clock className="w-5 h-5 text-blue-500 mx-auto mb-1" />
                        <span className="block font-bold text-blue-900">
                          {childProgress[child.id]?.total_time_minutes ?? childProgress[child.id]?.totalTimeMinutes ?? 0} min
                        </span>
                        <span className="text-[10px] uppercase font-bold text-blue-400">Cette sem.</span>
                    </div>
                    <div className="bg-green-50 rounded-xl p-3 text-center">
                        <TrendingUp className="w-5 h-5 text-green-500 mx-auto mb-1" />
                        <span className="block font-bold text-green-900">
                          {Math.round(childProgress[child.id]?.average_score ?? childProgress[child.id]?.averageScore ?? 0)}%
                        </span>
                        <span className="text-[10px] uppercase font-bold text-green-400">Moyenne</span>
                    </div>
                </div>

                <div className="relative z-10">
                    <div className="flex justify-between text-xs font-bold mb-1">
                        <span className="text-gray-500">Objectif Hebdo</span>
                        <span className="text-ilma-primary">{childProgress[child.id]?.total_time_minutes ?? childProgress[child.id]?.totalTimeMinutes ?? 0}/{child.weeklyGoalMinutes}m</span>
                    </div>
                    <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                        <div className="h-full rounded-full bg-ilma-primary" style={{ width: `${Math.min(100, Math.round(((childProgress[child.id]?.total_time_minutes ?? childProgress[child.id]?.totalTimeMinutes ?? 0) / child.weeklyGoalMinutes) * 100))}%` }} />
                    </div>
                </div>
            </Card>
        ))}

        <button
            onClick={handleAddChild}
            className="border-2 border-dashed border-gray-300 rounded-3xl p-8 flex flex-col items-center justify-center text-gray-400 hover:border-ilma-primary hover:text-ilma-primary hover:bg-amber-50 transition-all min-h-[250px]"
        >
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mb-4 shadow-sm">
                <Plus size={32} />
            </div>
            <span className="font-bold text-lg">Ajouter un profil</span>
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

            {/* Step indicators */}
            <div className="flex justify-center gap-2 mb-6">
              {onboardingSteps.map((_, i) => (
                <div
                  key={i}
                  className={`h-2 rounded-full transition-all ${i === onboardingStep ? 'w-8 bg-ilma-primary' : 'w-2 bg-gray-200'}`}
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
