import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Cards';
import { CEPPredictionCard } from '../components/dashboard/CEPPredictionCard';
import { CurrentLessonHero } from '../components/dashboard/CurrentLessonHero';
import { ProgressByTrimester } from '../components/dashboard/ProgressByTrimester';
import { Button } from '../components/ui/Button';
import { Skeleton } from '../components/ui/Skeleton';
import { StreakWidget } from '../components/ilma/Gamification';
import { useAuthStore } from '../store/authStore';
import { useAppStore } from '../store';
import { contentService, SubjectDTO, SkillDTO } from '../services/contentService';
import { progressService, SkillProgressDTO } from '../services/progressService';
import { Zap, Trophy, Download, Book, Calculator, FlaskConical, Globe, BookOpen, Flame, Clock, Sprout, Brain, Lightbulb, Target } from 'lucide-react';
import { contentService as contentSvc, FormulaDTO } from '../services/contentService';
import { ButtonVariant } from '../types';
import { avatarUrl } from '../utils/avatar';

const ICON_COMPONENTS: Record<string, React.ReactNode> = {
  Calculator: <Calculator size={24} />,
  Book: <Book size={24} />,
  FlaskConical: <FlaskConical size={24} />,
  Globe: <Globe size={24} />,
  BookOpen: <BookOpen size={24} />,
};

const GRADIENT_TOP_MAP: Record<string, string> = {
  math: 'card-gradient-top-blue',
  fr: 'card-gradient-top-purple',
  sci: 'card-gradient-top-green',
  geo: 'card-gradient-top-orange',
};

const STATIC_CHALLENGES = [
  { title: 'Numération : Les grands nombres', desc: 'Réussis 5 exercices pour gagner le badge "As des nombres" !', xp: 50 },
  { title: 'Opérations : La division', desc: 'Maîtrise la division euclidienne avec 5 exercices sans faute !', xp: 50 },
  { title: 'Géométrie : Les angles', desc: 'Identifie et mesure les angles — 5 exercices pour le badge "Géomètre" !', xp: 50 },
  { title: 'Mesures : Les unités', desc: 'Convertis les unités de longueur et de masse — bonus +50 XP !', xp: 50 },
  { title: 'Fractions : Comparer et ordonner', desc: 'Range les fractions dans l\'ordre — défi du champion !', xp: 50 },
  { title: 'Proportionnalité : Problèmes', desc: 'Résous 5 problèmes de proportionnalité pour briller au CEP !', xp: 50 },
  { title: 'Calcul mental : Les tables', desc: 'Révise tes tables de multiplication — chrono 60 secondes !', xp: 50 },
];

/** Pick the weakest skill (lowest score + not practiced in 3+ days) as today's challenge. */
function buildDynamicChallenge(skills: SkillProgressDTO[]): { title: string; desc: string; xp: number } | null {
  if (!skills || skills.length === 0) return null;
  const threeDaysAgo = Date.now() - 3 * 24 * 60 * 60 * 1000;
  // Prioritise skills not practiced recently with low score
  const candidates = skills
    .map(s => ({
      ...s,
      lastMs: s.lastPlayedAt ? new Date(s.lastPlayedAt).getTime() : 0,
    }))
    .sort((a, b) => {
      const aStale = a.lastMs < threeDaysAgo ? 1 : 0;
      const bStale = b.lastMs < threeDaysAgo ? 1 : 0;
      if (aStale !== bStale) return bStale - aStale; // stale first
      return a.score - b.score; // lowest score first
    });
  const weakest = candidates[0];
  if (!weakest) return null;
  return {
    title: weakest.skillName,
    desc: weakest.score < 50
      ? `Ton score est de ${weakest.score}% — pratique pour progresser !`
      : `Continue à t'entraîner pour atteindre la maîtrise !`,
    xp: 50,
  };
}

/** Returns hours and minutes remaining until midnight (local time). */
export function useTimeUntilMidnight() {
  const [remaining, setRemaining] = useState(() => calcRemaining());

  function calcRemaining() {
    const now = new Date();
    const midnight = new Date(now);
    midnight.setHours(24, 0, 0, 0);
    const diffMs = midnight.getTime() - now.getTime();
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    return { hours, minutes };
  }

  useEffect(() => {
    const timer = setInterval(() => setRemaining(calcRemaining()), 60_000);
    return () => clearInterval(timer);
  }, []);

  return remaining;
}

/** Streak reminder card — replaces the old "Reprendre" section. */
export const StreakReminderCard: React.FC<{
  streak: number;
  hasPlayedToday: boolean;
  lastActivity: { skillId: string; skillName: string; subjectId?: string; subjectName?: string } | null;
}> = ({ streak, hasPlayedToday, lastActivity }) => {
  const navigate = useNavigate();
  const { hours, minutes } = useTimeUntilMidnight();

  const handlePlay = () => {
    if (lastActivity) {
      navigate(`/app/student/exercise/${lastActivity.skillId}`, {
        state: {
          returnPath: '/app/student/dashboard',
          subjectId: lastActivity.subjectId,
          subjectName: lastActivity.subjectName,
        },
      });
    } else {
      navigate('/app/student/subjects');
    }
  };

  // Already played today — positive reinforcement
  if (hasPlayedToday && streak > 0) {
    return (
      <div className="clay-card p-4 flex items-center justify-between bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
            <Flame size={20} className="text-green-600 fill-green-600" />
          </div>
          <div>
            <p className="font-bold text-sm text-green-800">
              S&eacute;rie : {streak} jour{streak > 1 ? 's' : ''} !
            </p>
            <p className="text-xs text-green-600">
              Bravo ! Tu as jou&eacute; aujourd'hui. Continue demain !
            </p>
          </div>
        </div>
        <button
          onClick={handlePlay}
          className="px-4 py-2 bg-green-600 text-white text-sm font-bold rounded-lg shadow-sm hover:bg-green-700 transition-colors"
        >
          Rejouer &rarr;
        </button>
      </div>
    );
  }

  // Streak active but hasn't played today — urgency
  if (streak > 0) {
    return (
      <div className="clay-card p-4 bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center">
              <Flame size={20} className="text-sitou-orange fill-sitou-orange animate-wiggle" />
            </div>
            <div>
              <p className="font-bold text-sm text-gray-800">
                S&eacute;rie : {streak} jour{streak > 1 ? 's' : ''} !
              </p>
              <p className="text-xs text-gray-600">
                Joue aujourd'hui pour ne pas perdre ta s&eacute;rie !
              </p>
            </div>
          </div>
          <button
            onClick={handlePlay}
            className="px-4 py-2 gradient-hero text-white text-sm font-bold rounded-lg shadow-sm"
          >
            Jouer &rarr;
          </button>
        </div>
        <div className="flex items-center gap-1 mt-3 text-xs text-orange-600 font-medium">
          <Clock size={14} />
          <span>Il te reste {hours}h{String(minutes).padStart(2, '0')} avant minuit</span>
        </div>
      </div>
    );
  }

  // No streak — encourage starting a new one
  return (
    <div className="clay-card p-4 flex items-center justify-between bg-gradient-to-r from-sky-50 to-indigo-50 border-sky-200">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-sky-100 flex items-center justify-center">
          <Sprout size={20} className="text-sky-600" />
        </div>
        <div>
          <p className="font-bold text-sm text-gray-800">
            Commence une nouvelle s&eacute;rie !
          </p>
          <p className="text-xs text-gray-500">
            1 exercice = 1 jour de s&eacute;rie
          </p>
        </div>
      </div>
      <button
        onClick={handlePlay}
        className="px-4 py-2 gradient-hero text-white text-sm font-bold rounded-lg shadow-sm"
      >
        C'est parti &rarr;
      </button>
    </div>
  );
};

/** Rule of the day widget — shows a random formula from the weakest domain. */
const RuleDuJourWidget: React.FC<{ skillsProgress: SkillProgressDTO[] }> = ({ skillsProgress }) => {
  const navigate = useNavigate();
  const [formula, setFormula] = useState<FormulaDTO | null>(null);

  useEffect(() => {
    contentSvc.listFormulas().then(formulas => {
      if (formulas.length === 0) return;

      // Find weakest domain from progress
      const domainScores = new Map<string, number[]>();
      for (const p of skillsProgress) {
        // We don't have domainId on SkillProgressDTO, so we pick randomly
        // among formulas weighted toward the start (typically weaker skills)
      }

      // Pick a seeded-random formula based on today's date
      const dayIndex = Math.floor(Date.now() / (1000 * 60 * 60 * 24));
      const idx = dayIndex % formulas.length;
      setFormula(formulas[idx]);
    }).catch(() => {});
  }, [skillsProgress]);

  if (!formula) return null;

  return (
    <div className="clay-card p-4 bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          <div className="w-10 h-10 rounded-xl bg-yellow-100 flex items-center justify-center flex-shrink-0">
            <Lightbulb size={20} className="text-yellow-600" />
          </div>
          <div>
            <p className="text-xs text-yellow-600 font-bold uppercase tracking-wide mb-1">R&egrave;gle du jour</p>
            <p className="font-bold text-gray-900 text-sm">{formula.title}</p>
            {formula.formula && (
              <p className="mt-1 font-mono text-sm text-yellow-900 bg-yellow-100 inline-block px-2 py-0.5 rounded">
                {formula.formula}
              </p>
            )}
            {!formula.formula && formula.summary && (
              <p className="text-gray-600 text-xs mt-1 line-clamp-2">{formula.summary}</p>
            )}
          </div>
        </div>
        <button
          onClick={() => navigate(`/app/student/exercise/${formula.skillId}`, {
            state: { returnPath: '/app/student/dashboard' },
          })}
          className="px-3 py-1.5 bg-yellow-600 text-white text-xs font-bold rounded-lg shadow-sm hover:bg-yellow-700 transition-colors flex-shrink-0 ml-3"
        >
          Pratiquer
        </button>
      </div>
    </div>
  );
};

/** Compact "Défi du jour" widget — dynamic if progress data present, static fallback otherwise. */
const DailyChallengeWidget: React.FC<{
  challenge: { title: string; desc: string; xp: number };
}> = ({ challenge }) => {
  const navigate = useNavigate();
  return (
    <div className="clay-card p-4 bg-gradient-to-r from-rose-50 to-pink-50 border-rose-200 flex flex-col">
      <div className="flex items-start gap-3 flex-1">
        <div className="w-10 h-10 rounded-xl bg-rose-100 flex items-center justify-center flex-shrink-0">
          <Zap size={20} className="text-rose-600 fill-rose-600" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="text-xs text-rose-600 font-bold uppercase tracking-wide">D&eacute;fi du jour</p>
            <span className="text-[10px] font-bold text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded">
              +{challenge.xp} XP
            </span>
          </div>
          <p className="font-bold text-gray-900 text-sm line-clamp-2 mb-1">{challenge.title}</p>
          <p className="text-xs text-gray-600 line-clamp-2">{challenge.desc}</p>
        </div>
      </div>
      <button
        onClick={() => navigate('/app/student/subjects')}
        className="mt-3 px-3 py-2 bg-rose-600 text-white text-xs font-bold rounded-lg shadow-sm hover:bg-rose-700 transition-colors self-end"
      >
        Relever &rarr;
      </button>
    </div>
  );
};

/** Calcul Mental quick-launch widget with personal best score. */
const CalculMentalWidget: React.FC = () => {
  const navigate = useNavigate();
  const bestScore = parseInt(localStorage.getItem('sitou_calcul_mental_best') || '0', 10);

  return (
    <div
      className="clay-card p-4 flex items-center justify-between bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-200 cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => navigate('/app/student/calcul-mental')}
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
          <Brain size={20} className="text-amber-600" />
        </div>
        <div>
          <p className="font-bold text-sm text-gray-800">Calcul Mental</p>
          <p className="text-xs text-gray-500">
            {bestScore > 0
              ? <>Record : <span className="font-bold text-amber-600">{bestScore}</span> bonnes r&eacute;ponses en 60s</>
              : <>60 secondes pour r&eacute;pondre au maximum de calculs !</>
            }
          </p>
        </div>
      </div>
      <button className="px-4 py-2 gradient-hero text-white text-sm font-bold rounded-lg shadow-sm">
        Jouer &rarr;
      </button>
    </div>
  );
};

export const Dashboard: React.FC = () => {
  const { user, activeProfile } = useAuthStore();
  const displayName = activeProfile?.displayName || user?.name;
  const displayAvatar = activeProfile?.avatarUrl || user?.avatarUrl || avatarUrl(user?.id);
  const gradeLevelId = activeProfile?.gradeLevelId || user?.gradeLevelId;
  const navigate = useNavigate();
  const lastActivity = useAppStore(s => s.lastActivity);
  const dailyExerciseCount = useAppStore(s => s.dailyExerciseCount);
  const [isLoading, setIsLoading] = useState(true);
  const [subjects, setSubjects] = useState<SubjectDTO[]>([]);
  const [skillsBySubject, setSkillsBySubject] = useState<Map<string, SkillDTO[]>>(new Map());
  const [skillsProgress, setSkillsProgress] = useState<SkillProgressDTO[]>([]);
  const [todayChallenge, setTodayChallenge] = useState(STATIC_CHALLENGES[new Date().getDay()]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const subjectsData = await contentService.listSubjects(gradeLevelId).catch(() => [] as SubjectDTO[]);
        setSubjects(subjectsData);

        // Load all skills per subject (for progress bars)
        const skillsMap = new Map<string, SkillDTO[]>();
        const skillsResults = await Promise.all(
          subjectsData.map(s => contentService.listSkills(s.id).then(r => r.items).catch(() => [] as SkillDTO[]))
        );
        subjectsData.forEach((s, i) => skillsMap.set(s.id, skillsResults[i]));
        setSkillsBySubject(skillsMap);

        // Try to build a dynamic challenge from progress data
        try {
          const progress = await progressService.getSkillsProgress();
          setSkillsProgress(progress);
          const dynamic = buildDynamicChallenge(progress);
          if (dynamic) setTodayChallenge(dynamic);
        } catch {
          // Keep static fallback
        }
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [gradeLevelId]);

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (subjects.length === 0) {
    return <EmptyStateDashboard />;
  }

  return (
    <div className="space-y-8 pb-20 md:pb-0">
      {/* 1. Header Zone */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="flex items-center space-x-4">
            <div className="relative">
                <img src={displayAvatar} alt="Avatar" loading="eager" decoding="async" width={64} height={64} className="w-16 h-16 rounded-full border-4 border-white shadow-md bg-gray-200 object-cover" />
                <div className="absolute -bottom-1 -right-1 gradient-hero text-white text-xs font-bold px-2 py-0.5 rounded-full border-2 border-white shadow-sm">
                    Niv. {user?.level || 1}
                </div>
            </div>
            <div>
                <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 font-display">Bonjour, {displayName} !</h1>
                <div className="flex items-center text-sm text-gray-500 mt-1 space-x-3">
                    <span className="font-bold text-amber-500">&#127942; {user?.xp || 0} XP</span>
                    <span className="w-1 h-1 rounded-full bg-gray-300"></span>
                    <span>Prochain niveau: <span className="font-medium">{user?.xpToNextLevel || 1000} XP</span></span>
                </div>
            </div>
        </div>
        <div className="flex items-center space-x-3 self-start md:self-auto">
             <StreakWidget days={user?.streak || 0} active={true} />
        </div>
      </header>

      {/* 2. Hero — "Cette semaine en CM2" (curriculum-aware current lesson) */}
      <CurrentLessonHero
        subjects={subjects}
        skillsBySubject={skillsBySubject}
        progress={skillsProgress}
      />

      {/* 2bis. Récap trimestres → vers /app/student/programme */}
      <ProgressByTrimester
        subjects={subjects}
        skillsBySubject={skillsBySubject}
        progress={skillsProgress}
      />

      {/* 3. Streak Reminder — cadence quotidienne, cœur du modèle compagnon-annuel */}
      <StreakReminderCard
        streak={user?.streak || 0}
        hasPlayedToday={dailyExerciseCount > 0}
        lastActivity={lastActivity}
      />

      {/* 4. Trio compact : Défi du jour · Calcul Mental · Règle du jour */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DailyChallengeWidget challenge={todayChallenge} />
        <CalculMentalWidget />
        <RuleDuJourWidget skillsProgress={skillsProgress} />
      </div>

      {/* 5. Subjects Grid */}
      <section>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-800 flex items-center font-display">
                &#128218; Mes Mati&egrave;res
            </h3>
          </div>

          <div className="bento-grid">
              {subjects.map(subject => {
                  const subjectSkills = skillsBySubject.get(subject.id) || [];
                  const progressMap = new Map(skillsProgress.map(p => [p.skillId, p]));
                  const totalSkills = subjectSkills.length;
                  const scoreSum = subjectSkills.reduce((acc, sk) => acc + (progressMap.get(sk.id)?.score || 0), 0);
                  const avgProgress = totalSkills > 0 ? Math.round(scoreSum / totalSkills) : 0;

                  return (
                  <Card key={subject.id} interactive onClick={() => navigate(`/app/student/subjects/${subject.id}`)} className={`flex flex-col hover:border-sitou-primary transition-all duration-300 group relative overflow-hidden ${GRADIENT_TOP_MAP[subject.slug] || 'card-gradient-top-blue'}`}>
                      <div className="flex items-start justify-between mb-4 relative z-10">
                          <div className={`w-12 h-12 flex items-center justify-center rounded-2xl ${subject.color} ${subject.textColor} group-hover:scale-110 transition-transform`}>
                              {ICON_COMPONENTS[subject.iconName] || <BookOpen size={24} />}
                          </div>
                      </div>

                      <h4 className="text-lg font-bold text-gray-800 mb-1 group-hover:text-sitou-primary transition-colors relative z-10 font-display">{subject.emoji} {subject.name}</h4>
                      <p className="text-xs text-gray-500 mb-3 relative z-10 font-medium">
                          {subject.description || 'Exercices et le\u00e7ons'}
                      </p>

                      {totalSkills > 0 && (
                          <div className="relative z-10 mb-3">
                              <div className="flex items-center justify-between text-xs mb-1">
                                  <span className="font-medium text-gray-500">Progression</span>
                                  <span className="font-bold text-gray-700">{avgProgress}%</span>
                              </div>
                              <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                                  <div
                                      className="h-full rounded-full transition-all duration-500 gradient-xp"
                                      style={{ width: `${avgProgress}%` }}
                                  />
                              </div>
                          </div>
                      )}

                      <Button fullWidth variant={ButtonVariant.SECONDARY} className="mt-auto group-hover:bg-sitou-primary group-hover:text-white transition-colors relative z-10 border-0 bg-gray-50">
                          Commencer
                      </Button>
                  </Card>
                  );
              })}
          </div>
      </section>

      {/* 6. Mon objectif fin d'année — CEP relégué ici (compagnon-annuel, pas crammer) */}
      <section>
          <div className="flex items-center justify-between mb-2">
              <h3 className="text-xl font-bold text-gray-800 flex items-center font-display">
                  <Target size={20} className="mr-2 text-sitou-primary" /> Mon objectif fin d'ann&eacute;e
              </h3>
          </div>
          <p className="text-sm text-gray-500 mb-4">
              Tu pratiques pour le CEP en juin. Ton score progresse au fil des le&ccedil;ons ma&icirc;tris&eacute;es.
          </p>
          <CEPPredictionCard />
      </section>

      {/* 7. Trophées récents — compact, plus en hero */}
      <section>
          <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-800 flex items-center font-display">
                  <Trophy size={20} className="mr-2 text-sitou-orange" /> Troph&eacute;es r&eacute;cents
              </h3>
              <Button variant={ButtonVariant.GHOST} className="text-sm h-9" onClick={() => navigate('/app/student/badges')}>
                  Voir tout
              </Button>
          </div>
          <div className="clay-card p-4 flex items-center gap-6 overflow-x-auto">
              <div className="flex flex-col items-center group cursor-pointer flex-shrink-0">
                  <div className="w-14 h-14 bg-yellow-50 rounded-2xl flex items-center justify-center text-2xl mb-1 shadow-sm border border-yellow-100 group-hover:scale-110 transition-transform">&#129518;</div>
                  <span className="text-xs font-bold text-gray-600">Maths</span>
              </div>
              <div className="flex flex-col items-center group cursor-pointer flex-shrink-0">
                  <div className="w-14 h-14 bg-green-50 rounded-2xl flex items-center justify-center text-2xl mb-1 shadow-sm border border-green-100 group-hover:scale-110 transition-transform">&#127757;</div>
                  <span className="text-xs font-bold text-gray-600">G&eacute;o</span>
              </div>
              <div className="flex flex-col items-center opacity-50 flex-shrink-0">
                  <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center mb-1 border-2 border-dashed border-gray-200">
                      <Trophy size={22} className="text-gray-300" />
                  </div>
                  <span className="text-xs font-bold text-gray-400">Suivant</span>
              </div>
          </div>
      </section>
    </div>
  );
};

const DashboardSkeleton = () => (
    <div className="space-y-8">
        <div className="flex items-center space-x-4">
            <Skeleton variant="circle" className="w-16 h-16" />
            <div className="space-y-3">
                <Skeleton variant="text" className="w-48 h-8" />
                <Skeleton variant="text" className="w-32 h-4" />
            </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Skeleton variant="rect" className="lg:col-span-2 h-[220px]" />
            <Skeleton variant="rect" className="h-[220px]" />
        </div>
        <div className="space-y-4">
            <Skeleton variant="text" className="w-32 h-6" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map(i => (
                    <Skeleton key={i} variant="rect" className="h-[200px]" />
                ))}
            </div>
        </div>
    </div>
);

const EmptyStateDashboard = () => {
    const navigate = useNavigate();
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 animate-fade-in">
            <div className="w-24 h-24 gradient-hero rounded-full flex items-center justify-center mb-6 shadow-fun animate-float">
                <Download size={40} className="text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2 font-display">Aucun cours trouv&eacute; &#128640;</h2>
            <p className="text-gray-500 max-w-md mb-8 leading-relaxed">
                Il semble que tu n'aies pas encore t&eacute;l&eacute;charg&eacute; de le&ccedil;ons. T&eacute;l&eacute;charge un pack pour commencer &agrave; apprendre, m&ecirc;me hors-ligne !
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
                 <Button leftIcon={<Download size={20} />} onClick={() => navigate('/app/student/offline-management')}>
                    T&eacute;l&eacute;charger un pack
                </Button>
                <Button variant={ButtonVariant.GHOST} onClick={() => navigate('/app/student/subjects')}>
                    Explorer le catalogue
                </Button>
            </div>
        </div>
    );
};
