import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { Target, Sparkles, CheckCircle2, ChevronRight, Clock } from 'lucide-react';
import {
  diagnosticService,
  DiagnosticQuestionDTO,
  DiagnosticSummary,
  DiagnosticAnswer,
} from '../../services/diagnosticService';
import { useAuthStore } from '../../store/authStore';

type Phase = 'LOADING' | 'INTRO' | 'QUIZ' | 'SUBMITTING' | 'RESULTS' | 'ERROR';

export const DiagnosticPage: React.FC = () => {
  const navigate = useNavigate();

  const [phase, setPhase] = useState<Phase>('LOADING');
  const [questions, setQuestions] = useState<DiagnosticQuestionDTO[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<DiagnosticAnswer[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [summary, setSummary] = useState<DiagnosticSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const resp = await diagnosticService.getQuestions();
        if (cancelled) return;
        if (resp.completed_at) {
          navigate('/app/student/dashboard', { replace: true });
          return;
        }
        if (!resp.questions || resp.questions.length === 0) {
          setError("Aucune question disponible pour le diagnostic.");
          setPhase('ERROR');
          return;
        }
        setQuestions(resp.questions);
        setPhase('INTRO');
      } catch {
        if (!cancelled) {
          setError('Impossible de charger le diagnostic.');
          setPhase('ERROR');
        }
      }
    })();
    return () => { cancelled = true; };
  }, [navigate]);

  const total = questions.length;
  const currentQ = questions[currentIdx];

  const handleNext = () => {
    if (!currentQ || selected === null) return;
    const newAnswers = [...answers, { question_id: currentQ.question_id, answer: selected }];
    setAnswers(newAnswers);
    setSelected(null);

    if (currentIdx + 1 >= total) {
      handleSubmit(newAnswers);
    } else {
      setCurrentIdx(currentIdx + 1);
    }
  };

  const handleSubmit = async (finalAnswers: DiagnosticAnswer[]) => {
    setPhase('SUBMITTING');
    try {
      const resp = await diagnosticService.submit(finalAnswers);
      setSummary(resp);
      useAuthStore.setState((s: any) => ({
        activeProfile: s.activeProfile
          ? { ...s.activeProfile, diagnosticCompletedAt: new Date().toISOString() }
          : null,
      }));
      setPhase('RESULTS');
    } catch {
      setError("L'enregistrement du diagnostic a échoué.");
      setPhase('ERROR');
    }
  };

  if (phase === 'LOADING' || phase === 'SUBMITTING') {
    return (
      <div className="max-w-2xl mx-auto p-6 space-y-4">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-12 w-1/3" />
      </div>
    );
  }

  if (phase === 'ERROR') {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <Card>
          <h2 className="text-xl font-bold mb-2">Oups…</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => navigate('/app/student/dashboard')}>Aller au tableau de bord</Button>
        </Card>
      </div>
    );
  }

  if (phase === 'INTRO') {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <Card>
          <div className="w-16 h-16 rounded-2xl bg-amber-100 flex items-center justify-center mb-4">
            <Sparkles size={32} className="text-sitou-primary" />
          </div>
          <h1 className="text-3xl font-extrabold font-display mb-2">Faisons connaissance !</h1>
          <p className="text-gray-600 mb-4 leading-relaxed">
            En <span className="font-bold">5 minutes</span> et <span className="font-bold">{total} questions</span>,
            on situe ton niveau pour te proposer le bon parcours CEP.
          </p>
          <ul className="text-sm text-gray-600 space-y-2 mb-6">
            <li className="flex items-center gap-2"><Clock size={16} className="text-sitou-primary" /> Environ 30 sec par question</li>
            <li className="flex items-center gap-2"><Target size={16} className="text-sitou-primary" /> Réponds du mieux que tu peux — pas grave si tu te trompes</li>
            <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-sitou-primary" /> Tes réponses servent à adapter ta suite</li>
          </ul>
          <div className="flex gap-3">
            <Button onClick={() => setPhase('QUIZ')} fullWidth>C'est parti</Button>
            <Button onClick={() => navigate('/app/student/dashboard')} className="bg-gray-100 text-gray-600 hover:bg-gray-200">
              Plus tard
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (phase === 'RESULTS' && summary) {
    const passing = summary.predicted >= 10;
    return (
      <div className="max-w-2xl mx-auto p-6">
        <Card>
          <div className="w-16 h-16 rounded-2xl bg-green-100 flex items-center justify-center mb-4">
            <CheckCircle2 size={32} className="text-sitou-green" />
          </div>
          <h1 className="text-3xl font-extrabold font-display mb-2">Bravo, c'est fait !</h1>
          <p className="text-gray-600 mb-6">
            Voici une première estimation. Elle s'affinera à mesure que tu pratiques.
          </p>

          <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl p-6 mb-6 text-center">
            <p className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-1">Score CEP estimé</p>
            <p className={`text-6xl font-black ${passing ? 'text-sitou-green' : 'text-sitou-red'}`}>
              {summary.predicted.toFixed(1)}
            </p>
            <p className="text-lg font-bold text-gray-400">/20</p>
            <p className="text-sm text-gray-500 mt-2">
              {summary.questions_answered} questions · {Math.round(summary.overall_accuracy * 100)} % de bonnes réponses
            </p>
          </div>

          <Button fullWidth onClick={() => navigate('/app/student/dashboard')}>
            Aller à mon tableau de bord
          </Button>
        </Card>
      </div>
    );
  }

  // QUIZ phase
  if (!currentQ) return null;
  const progress = ((currentIdx) / total) * 100;

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-bold text-gray-600">Question {currentIdx + 1} / {total}</span>
          <span className="text-xs text-gray-400">{Math.round(progress)} %</span>
        </div>
        <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
          <div className="h-full bg-sitou-primary transition-all duration-300" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <Card>
        <p className="text-lg font-medium text-gray-800 mb-6 leading-relaxed">{currentQ.text}</p>

        <div className="space-y-2" role="radiogroup" aria-label="Choix de réponse">
          {currentQ.choices.map((choice, i) => {
            const isSelected = selected === choice;
            return (
              <button
                key={i}
                type="button"
                role="radio"
                aria-checked={isSelected}
                onClick={() => setSelected(choice)}
                className={`w-full text-left px-4 py-3 rounded-xl border-2 transition-all ${
                  isSelected
                    ? 'bg-amber-50 border-sitou-primary text-gray-900 font-bold'
                    : 'bg-white border-gray-200 hover:border-amber-200 text-gray-700'
                }`}
              >
                {choice}
              </button>
            );
          })}
        </div>

        <div className="mt-6 flex justify-end">
          <Button
            onClick={handleNext}
            disabled={selected === null}
          >
            {currentIdx + 1 >= total ? 'Terminer' : 'Suivant'}
            <ChevronRight size={18} className="ml-2 -mr-1" />
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default DiagnosticPage;
