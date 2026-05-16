import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { Plus, Flame, Clock, TrendingUp, ChevronRight, Lightbulb, Zap, MessageSquare, Volume2, Share2, AlertCircle, AlertTriangle, School } from 'lucide-react';
import { Modal } from '../../components/ui/Modal';
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
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [joinChildId, setJoinChildId] = useState<string>('');
  const [joinCode, setJoinCode] = useState('');
  const [joining, setJoining] = useState(false);
  const [joinMessage, setJoinMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

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

  const openJoinModal = () => {
    setJoinCode('');
    setJoinMessage(null);
    // Default to first child if any; user can change.
    setJoinChildId(healthData[0]?.profileId || '');
    setShowJoinModal(true);
  };

  const handleJoinClassroom = async () => {
    setJoinMessage(null);
    if (!joinChildId) {
      setJoinMessage({ type: 'error', text: 'Sélectionnez un enfant.' });
      return;
    }
    const code = joinCode.trim().toUpperCase();
    if (code.length < 4 || code.length > 8) {
      setJoinMessage({ type: 'error', text: 'Le code doit faire entre 4 et 8 caractères.' });
      return;
    }
    setJoining(true);
    try {
      const result = await parentService.joinClassroomForChild(joinChildId, code);
      const childName = healthData.find(c => c.profileId === joinChildId)?.displayName || 'L\'enfant';
      setJoinMessage({
        type: 'success',
        text: `${childName} a rejoint la classe « ${result.classroom_name} ».`,
      });
      setJoinCode('');
    } catch (err: any) {
      const msg = err?.message?.includes('introuvable')
        ? 'Code invalide. Vérifiez avec l\'enseignant.'
        : err?.message?.includes('déjà')
        ? 'Cet enfant est déjà inscrit dans cette classe.'
        : err?.message?.includes('pleine')
        ? 'La classe est pleine.'
        : err?.message || 'Erreur lors de l\'inscription.';
      setJoinMessage({ type: 'error', text: msg });
    } finally {
      setJoining(false);
    }
  };

  const speakHealthSummary = (children: ChildHealthDTO[]) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const lines = children.map(child => {
      const status = child.status === 'green' ? 'va bien'
        : child.status === 'orange' ? 'a besoin d\'encouragement'
        : 'risque de prendre du retard';
      const score = `Score moyen : ${Math.round(child.averageScore)} pour cent.`;
      const time = `Temps cette semaine : ${child.timeThisWeekMinutes} minutes.`;
      const advice = child.advice ? child.advice : '';
      return `${child.displayName} ${status}. ${score} ${time} ${advice}`;
    });
    const text = `Bonjour ! Voici le résumé de vos enfants. ${lines.join('. ')}`;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  };

  const shareOnWhatsApp = (children: ChildHealthDTO[]) => {
    const lines = children.map(child => {
      const emoji = child.status === 'green' ? '🟢' : child.status === 'orange' ? '🟡' : '🔴';
      return `${emoji} ${child.displayName} — Score: ${Math.round(child.averageScore)}%, Temps: ${child.timeThisWeekMinutes}min`;
    });
    const text = `📚 Résumé Sitou\n\n${lines.join('\n')}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
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
                      loading="lazy"
                      decoding="async"
                      width={56}
                      height={56}
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

              {/* Action suggérée — basée sur risk_level unifié (même formule
                  que l'admin at-risk + le cron SMS parent). S'affiche au-dessus
                  du conseil pédagogique car c'est une intervention parent, pas
                  un commentaire sur le score. */}
              {child.suggestedAction && child.riskLevel !== 'low' && (
                <div className={`flex items-start gap-2 p-3 rounded-xl text-xs font-bold mb-2 border ${
                  child.riskLevel === 'high'
                    ? 'bg-red-50 text-red-800 border-red-200'
                    : 'bg-amber-50 text-amber-800 border-amber-200'
                }`}>
                  {child.riskLevel === 'high'
                    ? <AlertCircle size={14} className="flex-shrink-0 mt-0.5" />
                    : <AlertTriangle size={14} className="flex-shrink-0 mt-0.5" />}
                  <span>
                    <span className="uppercase tracking-wide text-[10px] opacity-80">Action suggérée</span>
                    <br />{child.suggestedAction}
                  </span>
                </div>
              )}

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

        {/* Action buttons */}
        {healthData.length > 0 && (
          <div className="space-y-2">
            {'speechSynthesis' in window && (
              <button
                onClick={() => speakHealthSummary(healthData)}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white font-bold rounded-2xl hover:bg-indigo-700 transition-all"
              >
                <Volume2 size={18} />
                Écouter le résumé
              </button>
            )}
            <button
              onClick={() => shareOnWhatsApp(healthData)}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white font-bold rounded-2xl hover:bg-green-700 transition-all"
            >
              <Share2 size={18} />
              Partager sur WhatsApp
            </button>
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

        {/* Join classroom CTA — only show when at least one child exists */}
        {healthData.length > 0 && (
          <button
            onClick={openJoinModal}
            className="w-full border-2 border-dashed border-gray-300 rounded-3xl p-5 flex items-center justify-center gap-3 text-gray-500 hover:border-sitou-primary hover:text-sitou-primary hover:bg-amber-50 transition-all"
          >
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm">
              <School size={20} />
            </div>
            <span className="font-bold">Rejoindre une classe enseignant</span>
          </button>
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

      {/* Join classroom modal */}
      <Modal
        isOpen={showJoinModal}
        onClose={() => setShowJoinModal(false)}
        title="Rejoindre une classe"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Entrez le code à 8 caractères fourni par l'enseignant pour inscrire un enfant à sa classe.
          </p>

          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Enfant à inscrire</label>
            <select
              value={joinChildId}
              onChange={e => setJoinChildId(e.target.value)}
              disabled={healthData.length <= 1}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm bg-white disabled:bg-gray-50"
            >
              {healthData.map(c => (
                <option key={c.profileId} value={c.profileId}>{c.displayName}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Code d'invitation</label>
            <input
              type="text"
              value={joinCode}
              onChange={e => setJoinCode(e.target.value.toUpperCase())}
              placeholder="EX. XK4Z8P2T"
              maxLength={8}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-lg font-mono font-bold tracking-widest text-center uppercase"
            />
          </div>

          {joinMessage && (
            <p className={`text-sm font-medium ${joinMessage.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
              {joinMessage.text}
            </p>
          )}

          <div className="flex gap-2 pt-2">
            <button
              onClick={() => setShowJoinModal(false)}
              className="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-bold text-sm hover:bg-gray-50"
            >
              Fermer
            </button>
            <button
              onClick={handleJoinClassroom}
              disabled={joining}
              className="flex-1 px-4 py-2.5 rounded-xl bg-sitou-primary text-white font-bold text-sm hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {joining ? 'Inscription…' : 'Rejoindre'}
            </button>
          </div>
        </div>
      </Modal>

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
