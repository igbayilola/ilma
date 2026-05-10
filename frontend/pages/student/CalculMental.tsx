import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Cards';
import { ButtonVariant } from '../../types';
import { ArrowLeft, Zap, Trophy, Clock, RotateCcw, Home, Delete } from 'lucide-react';
import { sessionService, SessionDTO, NextQuestionDTO } from '../../services/sessionService';
import { contentService } from '../../services/contentService';

type Phase = 'ready' | 'playing' | 'finished';

const TOTAL_TIME_SECONDS = 60;
const PER_QUESTION_TIMEOUT = 8;

interface QuestionResult {
  questionId: string;
  answer: string;
  isCorrect: boolean;
  timeSpent: number;
}

export const CalculMentalPage: React.FC = () => {
  const navigate = useNavigate();

  // State
  const [phase, setPhase] = useState<Phase>('ready');
  const [session, setSession] = useState<SessionDTO | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<NextQuestionDTO | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [globalTimeLeft, setGlobalTimeLeft] = useState(TOTAL_TIME_SECONDS);
  const [questionTimeLeft, setQuestionTimeLeft] = useState(PER_QUESTION_TIMEOUT);
  const [results, setResults] = useState<QuestionResult[]>([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [skillId, setSkillId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [bestScore, setBestScore] = useState<number>(0);

  const questionStartRef = useRef<number>(Date.now());
  const globalTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const questionTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Load best score from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('sitou_calcul_mental_best');
    if (saved) setBestScore(parseInt(saved, 10));
  }, []);

  // Find the math skill that has calcul_mental questions
  useEffect(() => {
    const findSkill = async () => {
      try {
        const subjects = await contentService.listSubjects();
        // Find math subject (slug contains 'math')
        const mathSubject = subjects.find(s =>
          s.slug?.includes('math') || s.name?.toLowerCase().includes('math')
        );
        if (!mathSubject) {
          setIsLoading(false);
          return;
        }
        // Get first skill from first domain (the exercises are tagged, not skill-specific)
        const domains = await contentService.listDomains(mathSubject.id);
        if (domains.length > 0) {
          const { items: skills } = await contentService.listSkills(mathSubject.id, domains[0].id);
          if (skills.length > 0) {
            setSkillId(skills[0].id);
          }
        }
      } catch {
        // Fallback handled in UI
      } finally {
        setIsLoading(false);
      }
    };
    findSkill();
  }, []);

  // Global countdown
  useEffect(() => {
    if (phase !== 'playing') return;
    globalTimerRef.current = setInterval(() => {
      setGlobalTimeLeft(prev => {
        if (prev <= 1) {
          finishGame();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => { if (globalTimerRef.current) clearInterval(globalTimerRef.current); };
  }, [phase]);

  // Per-question countdown
  useEffect(() => {
    if (phase !== 'playing' || !currentQuestion) return;
    setQuestionTimeLeft(PER_QUESTION_TIMEOUT);
    questionTimerRef.current = setInterval(() => {
      setQuestionTimeLeft(prev => {
        if (prev <= 1) {
          handleTimeout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => { if (questionTimerRef.current) clearInterval(questionTimerRef.current); };
  }, [currentQuestion?.questionId, phase]);

  const finishGame = useCallback(async () => {
    if (globalTimerRef.current) clearInterval(globalTimerRef.current);
    if (questionTimerRef.current) clearInterval(questionTimerRef.current);
    setPhase('finished');

    if (session) {
      try {
        await sessionService.completeSession(session.id);
      } catch { /* session may already be completed */ }
    }
  }, [session]);

  const startGame = async () => {
    if (!skillId) return;
    try {
      const sess = await sessionService.startSession(skillId, 'calcul_mental');
      setSession(sess);
      setResults([]);
      setQuestionIndex(0);
      setGlobalTimeLeft(TOTAL_TIME_SECONDS);
      setPhase('playing');

      const q = await sessionService.getNextQuestion(sess.id);
      setCurrentQuestion(q);
      questionStartRef.current = Date.now();
    } catch {
      // No questions available
      setPhase('ready');
    }
  };

  const handleTimeout = useCallback(async () => {
    if (!session || !currentQuestion || isSubmitting) return;
    setIsSubmitting(true);

    const timeSpent = PER_QUESTION_TIMEOUT;
    try {
      const result = await sessionService.recordAttempt(
        session.id, currentQuestion.questionId, '', timeSpent
      );
      setResults(prev => [...prev, {
        questionId: currentQuestion.questionId,
        answer: '',
        isCorrect: false,
        timeSpent,
      }]);
    } catch { /* continue */ }

    await advanceQuestion();
    setIsSubmitting(false);
  }, [session, currentQuestion, isSubmitting]);

  const submitAnswer = async () => {
    if (!session || !currentQuestion || isSubmitting || !inputValue.trim()) return;
    setIsSubmitting(true);

    if (questionTimerRef.current) clearInterval(questionTimerRef.current);

    const timeSpent = Math.round((Date.now() - questionStartRef.current) / 1000);

    // Parse numeric answer
    let answer: any = inputValue.trim();
    const parsed = parseFloat(answer);
    if (!isNaN(parsed)) answer = parsed;

    try {
      const result = await sessionService.recordAttempt(
        session.id, currentQuestion.questionId, answer, timeSpent
      );
      setResults(prev => [...prev, {
        questionId: currentQuestion.questionId,
        answer: inputValue,
        isCorrect: result.isCorrect,
        timeSpent,
      }]);
    } catch { /* continue */ }

    await advanceQuestion();
    setIsSubmitting(false);
  };

  const advanceQuestion = async () => {
    if (!session) return;
    setInputValue('');
    setQuestionIndex(prev => prev + 1);

    const next = await sessionService.getNextQuestion(session.id);
    if (!next) {
      finishGame();
      return;
    }
    setCurrentQuestion(next);
    questionStartRef.current = Date.now();
  };

  const handleNumpadPress = (key: string) => {
    if (key === 'delete') {
      setInputValue(prev => prev.slice(0, -1));
    } else if (key === 'submit') {
      submitAnswer();
    } else {
      setInputValue(prev => prev + key);
    }
  };

  // Save best score
  useEffect(() => {
    if (phase === 'finished') {
      const correct = results.filter(r => r.isCorrect).length;
      if (correct > bestScore) {
        setBestScore(correct);
        localStorage.setItem('sitou_calcul_mental_best', String(correct));
      }
    }
  }, [phase]);

  const correctCount = results.filter(r => r.isCorrect).length;
  const avgTime = results.length > 0
    ? (results.reduce((sum, r) => sum + r.timeSpent, 0) / results.length).toFixed(1)
    : '0';

  // ── READY SCREEN ──
  if (phase === 'ready') {
    if (isLoading) return <div className="p-8 text-center text-gray-400">Chargement...</div>;

    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-white flex flex-col items-center justify-center p-6 text-center">
        <div className="w-20 h-20 bg-amber-100 rounded-full flex items-center justify-center mb-6">
          <Zap size={40} className="text-amber-600" />
        </div>
        <h1 className="text-3xl font-extrabold text-gray-900 mb-2">Calcul Mental</h1>
        <p className="text-gray-500 mb-2 max-w-md">
          R&eacute;ponds au maximum de questions en {TOTAL_TIME_SECONDS} secondes.
          Chaque question a un chrono de {PER_QUESTION_TIMEOUT}s.
        </p>

        {bestScore > 0 && (
          <div className="flex items-center text-amber-600 font-bold mb-6">
            <Trophy size={18} className="mr-2" /> Record : {bestScore} bonnes r&eacute;ponses
          </div>
        )}

        <Button
          size="lg"
          className="h-14 px-10 text-lg shadow-lg"
          onClick={startGame}
          disabled={!skillId}
        >
          <Zap size={20} className="mr-2" /> C'est parti !
        </Button>

        <button
          onClick={() => navigate('/app/student/dashboard')}
          className="mt-4 text-gray-400 text-sm hover:text-gray-600"
        >
          Retour au tableau de bord
        </button>
      </div>
    );
  }

  // ── FINISHED SCREEN ──
  if (phase === 'finished') {
    const isNewRecord = correctCount >= bestScore && correctCount > 0;

    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-white flex flex-col items-center justify-center p-6 text-center">
        {isNewRecord && (
          <div className="mb-4 text-amber-500 font-bold animate-bounce text-lg">
            Nouveau record !
          </div>
        )}

        <div className="w-24 h-24 bg-amber-100 rounded-full flex items-center justify-center mb-6">
          <Trophy size={48} className="text-amber-600" />
        </div>

        <h1 className="text-3xl font-extrabold text-gray-900 mb-6">Termin&eacute; !</h1>

        <div className="grid grid-cols-3 gap-4 mb-8 w-full max-w-sm">
          <Card className="text-center bg-green-50 border-green-200">
            <p className="text-3xl font-extrabold text-green-700">{correctCount}</p>
            <p className="text-xs text-green-600 font-medium">Bonnes r&eacute;ponses</p>
          </Card>
          <Card className="text-center bg-blue-50 border-blue-200">
            <p className="text-3xl font-extrabold text-blue-700">{results.length}</p>
            <p className="text-xs text-blue-600 font-medium">Questions</p>
          </Card>
          <Card className="text-center bg-purple-50 border-purple-200">
            <p className="text-3xl font-extrabold text-purple-700">{avgTime}s</p>
            <p className="text-xs text-purple-600 font-medium">Temps moyen</p>
          </Card>
        </div>

        {bestScore > 0 && (
          <p className="text-amber-600 font-bold mb-6 flex items-center">
            <Trophy size={16} className="mr-1" /> Record personnel : {bestScore}
          </p>
        )}

        <div className="flex flex-col gap-3 w-full max-w-xs">
          <Button fullWidth size="lg" onClick={startGame}>
            <RotateCcw size={18} className="mr-2" /> Rejouer
          </Button>
          <Button fullWidth variant={ButtonVariant.SECONDARY} onClick={() => navigate('/app/student/dashboard')}>
            <Home size={18} className="mr-2" /> Tableau de bord
          </Button>
        </div>
      </div>
    );
  }

  // ── PLAYING SCREEN ──
  const globalPercent = (globalTimeLeft / TOTAL_TIME_SECONDS) * 100;
  const questionPercent = (questionTimeLeft / PER_QUESTION_TIMEOUT) * 100;

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Top bar: global timer + score */}
      <header className="p-3 bg-white border-b border-gray-100 flex items-center justify-between">
        <button onClick={finishGame} className="text-gray-400 hover:text-gray-600">
          <ArrowLeft size={20} />
        </button>
        <div className="flex items-center space-x-4">
          <div className="flex items-center text-sm font-bold text-green-600">
            <Zap size={16} className="mr-1" /> {correctCount}/{results.length}
          </div>
          <div className={`flex items-center text-sm font-bold ${globalTimeLeft <= 10 ? 'text-red-600 animate-pulse' : 'text-gray-700'}`}>
            <Clock size={16} className="mr-1" /> {globalTimeLeft}s
          </div>
        </div>
      </header>

      {/* Global timer bar */}
      <div className="w-full h-1.5 bg-gray-100">
        <div
          className={`h-full transition-all duration-1000 rounded-r-full ${globalTimeLeft <= 10 ? 'bg-red-500' : 'bg-sitou-primary'}`}
          style={{ width: `${globalPercent}%` }}
        />
      </div>

      {/* Question area */}
      <main className="flex-1 flex flex-col items-center justify-center p-6">
        {currentQuestion && (
          <>
            {/* Question timer ring */}
            <div className="relative w-16 h-16 mb-4">
              <svg className="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="3"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke={questionTimeLeft <= 3 ? '#ef4444' : '#f59e0b'}
                  strokeWidth="3"
                  strokeDasharray={`${questionPercent}, 100`}
                  className="transition-all duration-1000"
                />
              </svg>
              <span className={`absolute inset-0 flex items-center justify-center text-sm font-bold ${questionTimeLeft <= 3 ? 'text-red-600' : 'text-gray-700'}`}>
                {questionTimeLeft}
              </span>
            </div>

            {/* Question number */}
            <p className="text-sm text-gray-400 font-medium mb-2">
              Question {questionIndex + 1}
            </p>

            {/* Question text */}
            <h2 className="text-2xl md:text-3xl font-extrabold text-gray-900 text-center mb-8 max-w-md">
              {currentQuestion.text}
            </h2>

            {/* Answer display */}
            <div className="w-full max-w-xs mb-6">
              <div className="bg-gray-50 border-2 border-gray-200 rounded-2xl px-6 py-4 text-center text-3xl font-bold text-gray-900 min-h-[60px] flex items-center justify-center">
                {inputValue || <span className="text-gray-300">?</span>}
              </div>
            </div>

            {/* Numpad */}
            <div className="grid grid-cols-3 gap-2 w-full max-w-xs">
              {['7', '8', '9', '4', '5', '6', '1', '2', '3'].map(key => (
                <button
                  key={key}
                  onClick={() => handleNumpadPress(key)}
                  className="h-14 bg-gray-100 hover:bg-gray-200 active:bg-gray-300 rounded-xl text-xl font-bold text-gray-800 transition-colors"
                >
                  {key}
                </button>
              ))}
              <button
                onClick={() => handleNumpadPress('delete')}
                className="h-14 bg-red-50 hover:bg-red-100 active:bg-red-200 rounded-xl flex items-center justify-center transition-colors"
              >
                <Delete size={24} className="text-red-500" />
              </button>
              <button
                onClick={() => handleNumpadPress('0')}
                className="h-14 bg-gray-100 hover:bg-gray-200 active:bg-gray-300 rounded-xl text-xl font-bold text-gray-800 transition-colors"
              >
                0
              </button>
              <button
                onClick={() => handleNumpadPress('submit')}
                disabled={!inputValue.trim() || isSubmitting}
                className="h-14 bg-sitou-primary hover:bg-sitou-primary/90 active:bg-sitou-primary/80 text-white rounded-xl text-lg font-bold transition-colors disabled:opacity-40"
              >
                OK
              </button>
            </div>

            {/* Decimal / negative row */}
            <div className="grid grid-cols-2 gap-2 w-full max-w-xs mt-2">
              <button
                onClick={() => handleNumpadPress(',')}
                className="h-12 bg-gray-100 hover:bg-gray-200 rounded-xl text-xl font-bold text-gray-800 transition-colors"
              >
                ,
              </button>
              <button
                onClick={() => handleNumpadPress('-')}
                className="h-12 bg-gray-100 hover:bg-gray-200 rounded-xl text-xl font-bold text-gray-800 transition-colors"
              >
                &minus;
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
};
