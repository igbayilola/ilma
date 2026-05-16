import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { QuestionRenderer } from '../../components/exercise/QuestionRenderer';
import { ButtonVariant, Question, SubscriptionTier } from '../../types';
import { X, CheckCircle2, AlertCircle, ArrowRight, RotateCcw, Award, HelpCircle, BookOpen, PenLine, Share2, Timer, Pause, Lightbulb, ChevronDown, ChevronUp, Volume2 } from 'lucide-react';
import { Breadcrumb } from '../../components/ui/Breadcrumb';
import { useAppStore } from '../../store';
import { SmartScoreMeter } from '../../components/ilma/Gamification';
import { PaywallModal } from '../../components/subscription/PaywallModal';
import { contentService, QuestionDTO, PrerequisiteCheckDTO } from '../../services/contentService';
import { sessionService, SessionDTO, NextQuestionDTO } from '../../services/sessionService';
import { useAuthStore } from '../../store/authStore';
import { useConfigStore } from '../../store/configStore';
import { telemetry } from '../../services/telemetry';
import { analytics } from '../../services/analytics';
import { saveDraft, loadDraft, clearDraft, ExerciseDraft } from '../../services/exerciseDraft';
import { SanitizedHTML } from '../../components/ui/SanitizedHTML';

type PlayerPhase = 'INTRO' | 'ACTIVE' | 'SUMMARY';
type AnswerStatus = 'IDLE' | 'CORRECT' | 'INCORRECT';

const CORRECT_MESSAGES = [
  { text: 'Bonne r\u00e9ponse !', emoji: '\ud83c\udf1f' },
  { text: 'Bravo !', emoji: '\ud83c\udf89' },
  { text: 'Excellent !', emoji: '\u2b50' },
  { text: 'Super !', emoji: '\ud83d\udcaa' },
];

const INCORRECT_MESSAGES = [
  { text: 'Oups, pas tout \u00e0 fait.', emoji: '\ud83e\uddd0' },
  { text: 'Presque ! Continue.', emoji: '\ud83c\udf31' },
  { text: 'Pas encore, r\u00e9essaie !', emoji: '\ud83d\udcaa' },
];

function getRandomMessage(messages: typeof CORRECT_MESSAGES) {
  return messages[Math.floor(Math.random() * messages.length)];
}

/** Strip HTML tags so Tiptap-authored explanations are spoken as plain text. */
function htmlToPlainText(html: string): string {
  if (!html) return '';
  if (!/<[a-z][^>]*>/i.test(html)) return html; // already plain
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return (tmp.textContent || tmp.innerText || '').trim();
}

/** Speak short feedback via Web Speech API (non-blocking, best effort) */
function speakFeedback(text: string) {
  try {
    if (!('speechSynthesis' in window)) return;
    const plain = htmlToPlainText(text);
    if (!plain) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(plain);
    u.lang = 'fr-FR';
    u.rate = 1.1;
    u.volume = 0.8;
    window.speechSynthesis.speak(u);
  } catch { /* ignore */ }
}

const PAUSE_SUGGESTION_MS = 5 * 60 * 1000; // 5 minutes

/** Map a NextQuestionDTO (from session engine) to a Question for QuestionRenderer */
function mapNextToRenderQuestion(nq: NextQuestionDTO, correctAnswer?: any, explanation?: string): Question {
  const QUESTION_TYPE_MAP: Record<string, string> = {
    mcq: 'MCQ', true_false: 'TRUE_FALSE', fill_blank: 'FILL_BLANK',
    numeric_input: 'NUMERIC_INPUT', short_answer: 'SHORT_ANSWER',
    ordering: 'ORDERING', matching: 'MATCHING', error_correction: 'ERROR_CORRECTION',
    contextual_problem: 'CONTEXTUAL_PROBLEM', guided_steps: 'GUIDED_STEPS',
    justification: 'JUSTIFICATION', tracing: 'TRACING',
    drag_drop: 'DRAG_DROP', interactive_draw: 'INTERACTIVE_DRAW',
    chart_input: 'CHART_INPUT', audio_comprehension: 'AUDIO_COMPREHENSION',
  };
  const mappedType = QUESTION_TYPE_MAP[(nq.questionType || '').toLowerCase()] || 'MCQ';

  return {
    id: nq.questionId,
    type: mappedType as any,
    prompt: nq.text,
    options: nq.choices,
    choices: nq.choices,
    correctAnswer: correctAnswer ?? '',
    explanation: explanation || '',
    hint: undefined,
    imageUrl: nq.mediaUrl,
  };
}

const Confetti: React.FC = () => (
  <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden" aria-hidden="true">
    {Array.from({ length: 20 }).map((_, i) => (
      <div
        key={i}
        className="absolute w-3 h-3 rounded-sm"
        style={{
          left: `${Math.random() * 100}%`,
          top: '-10px',
          backgroundColor: ['#D97706', '#F59E0B', '#22C55E', '#7C3AED', '#EC4899', '#0EA5E9'][i % 6],
          animation: `confetti-fall ${2 + Math.random() * 2}s ease-out ${Math.random() * 0.5}s forwards`,
        }}
      />
    ))}
  </div>
);

const Scratchpad: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = React.useState(false);

  const getPos = (e: React.TouchEvent | React.MouseEvent) => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    if ('touches' in e) {
      return { x: e.touches[0].clientX - rect.left, y: e.touches[0].clientY - rect.top };
    }
    return { x: (e as React.MouseEvent).clientX - rect.left, y: (e as React.MouseEvent).clientY - rect.top };
  };

  const startDraw = (e: React.TouchEvent | React.MouseEvent) => {
    setIsDrawing(true);
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;
    const pos = getPos(e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
  };

  const draw = (e: React.TouchEvent | React.MouseEvent) => {
    if (!isDrawing) return;
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;
    const pos = getPos(e);
    ctx.lineTo(pos.x, pos.y);
    ctx.strokeStyle = '#1F2937';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.stroke();
  };

  const stopDraw = () => setIsDrawing(false);

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 bg-white border-t-2 border-gray-200 shadow-2xl animate-slide-up" style={{ height: '50vh' }}>
      <div className="flex items-center justify-between p-3 border-b border-gray-100">
        <h3 className="font-bold text-sm text-gray-700">📝 Brouillon</h3>
        <div className="flex gap-2">
          <button onClick={clearCanvas} className="text-xs px-3 py-1.5 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors font-medium">Effacer</button>
          <button onClick={onClose} className="text-xs px-3 py-1.5 bg-sitou-primary text-white rounded-lg hover:bg-sitou-primary-dark transition-colors font-medium">Fermer</button>
        </div>
      </div>
      <canvas
        ref={canvasRef}
        width={window.innerWidth}
        height={window.innerHeight * 0.5 - 60}
        className="bg-white touch-none cursor-crosshair w-full"
        onMouseDown={startDraw}
        onMouseMove={draw}
        onMouseUp={stopDraw}
        onMouseLeave={stopDraw}
        onTouchStart={startDraw}
        onTouchMove={draw}
        onTouchEnd={stopDraw}
      />
    </div>
  );
};

export const ExercisePlayerPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [searchParams] = useSearchParams();
    const microSkillId = searchParams.get('micro_skill_id') || undefined;
    const navigate = useNavigate();
    const location = useLocation();
    const { dailyExerciseCount, incrementDailyExercise, setLastActivity } = useAppStore();
    const { user, activeProfile } = useAuthStore();
    const effectiveTier = activeProfile?.subscriptionTier || user?.subscriptionTier;
    const freemiumDailyLimit = useConfigStore(s => s.freemiumDailyLimit);

    // Navigation context from location.state
    const navState = (location.state || {}) as {
      returnPath?: string;
      subjectId?: string;
      subjectName?: string;
      domainName?: string;
    };
    const returnPath = navState.returnPath || '/app/student/subjects';

    // Intro data (loaded from content API for display)
    const [questionCount, setQuestionCount] = useState(0);
    const [skillName, setSkillName] = useState('Exercice');
    const [isLoading, setIsLoading] = useState(true);

    // Session engine state
    const [session, setSession] = useState<SessionDTO | null>(null);
    const [currentQuestion, setCurrentQuestion] = useState<NextQuestionDTO | null>(null);
    const questionStartTime = useRef<number>(Date.now());

    // UI state
    const [phase, setPhase] = useState<PlayerPhase>('INTRO');
    const [currentQIndex, setCurrentQIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<any>(null);
    const [answerStatus, setAnswerStatus] = useState<AnswerStatus>('IDLE');
    const [score, setScore] = useState(0);
    const [totalQuestions, setTotalQuestions] = useState(0);
    const [mistakes, setMistakes] = useState(0);
    const [isPaywallOpen, setIsPaywallOpen] = useState(false);
    const [consecutiveMistakes, setConsecutiveMistakes] = useState(0);
    const [feedbackMessage, setFeedbackMessage] = useState({ text: '', emoji: '' });
    const [correctAnswer, setCorrectAnswer] = useState<any>(null);
    const [explanation, setExplanation] = useState('');
    const [showExplanation, setShowExplanation] = useState(false);
    const [criteriaFeedback, setCriteriaFeedback] = useState<import('../../services/sessionService').CriterionFeedback[] | null>(null);
    const [isValidating, setIsValidating] = useState(false);
    const [showScratchpad, setShowScratchpad] = useState(false);
    const [showRetenonsSheet, setShowRetenonsSheet] = useState(false);
    const [retenonsData, setRetenonsData] = useState<{ bodyHtml: string; rules: string[]; formula?: string } | null>(null);

    // Question history for non-linear navigation
    interface AnsweredQuestion {
        question: NextQuestionDTO;
        answer: any;
        isCorrect: boolean;
        correctAnswer: any;
        explanation: string;
    }
    const [questionHistory, setQuestionHistory] = useState<AnsweredQuestion[]>([]);
    const [reviewIndex, setReviewIndex] = useState<number | null>(null); // null = viewing current question

    const hintsUsedRef = useRef(0);
    const totalHintsRef = useRef(0);
    const sessionStartRef = useRef<number>(Date.now());
    const [smartScoreBefore, setSmartScoreBefore] = useState<number | null>(null);
    const [smartScoreAfter, setSmartScoreAfter] = useState<number | null>(null);
    const [xpEarned, setXpEarned] = useState<number | null>(null);
    const [pendingDraft, setPendingDraft] = useState<ExerciseDraft | null>(null);
    const [prereqCheck, setPrereqCheck] = useState<PrerequisiteCheckDTO | null>(null);
    const [showPauseSuggestion, setShowPauseSuggestion] = useState(false);
    const [elapsedSeconds, setElapsedSeconds] = useState(0);
    const pauseSuggestedRef = useRef(false);

    // Session timer + pause suggestion after 5min
    useEffect(() => {
        if (phase !== 'ACTIVE') return;
        const interval = setInterval(() => {
            setElapsedSeconds(Math.floor((Date.now() - sessionStartRef.current) / 1000));
            if (!pauseSuggestedRef.current && (Date.now() - sessionStartRef.current) >= PAUSE_SUGGESTION_MS) {
                pauseSuggestedRef.current = true;
                setShowPauseSuggestion(true);
            }
        }, 1000);
        return () => clearInterval(interval);
    }, [phase]);

    // Load intro data + check for a resumable draft + check prerequisites
    useEffect(() => {
        if (!id) return;
        Promise.all([
            contentService.listQuestions(id, microSkillId),
            contentService.getSkillWithLessons(id).catch(() => null),
            contentService.checkPrerequisites(id).catch(() => null),
        ]).then(([qsResult, skillData, prereqs]) => {
            setQuestionCount(qsResult.total);
            if (skillData) {
                setSkillName(skillData.skill.name);
                // Extract retenons from the first structured lesson
                const lesson = skillData.lessons?.[0];
                if (lesson?.sections?.retenons) {
                    setRetenonsData({
                        bodyHtml: lesson.sections.retenons.body_html,
                        rules: lesson.sections.retenons.rules || [],
                        formula: lesson.formula,
                    });
                } else if (lesson?.formula) {
                    setRetenonsData({ bodyHtml: '', rules: [], formula: lesson.formula });
                }
            }
            if (prereqs) setPrereqCheck(prereqs);
            const draft = loadDraft(id);
            if (draft) setPendingDraft(draft);
        }).catch(() => setQuestionCount(0))
          .finally(() => setIsLoading(false));
    }, [id, microSkillId]);

    const xpReward = questionCount * 10;
    const progress = totalQuestions > 0 ? (currentQIndex / totalQuestions) * 100 : 0;

    const handleStart = async () => {
        if (effectiveTier === SubscriptionTier.FREE && dailyExerciseCount >= freemiumDailyLimit) {
            setIsPaywallOpen(true);
            return;
        }

        if (!id) return;
        setIsLoading(true);
        try {
            // Start a real session via the backend engine
            const sess = await sessionService.startSession(id, 'practice', microSkillId);
            setSession(sess);
            setTotalQuestions(sess.totalQuestions || questionCount);
            sessionStartRef.current = Date.now();
            hintsUsedRef.current = 0;
            totalHintsRef.current = 0;

            analytics.exerciseStart(sess.id, {
                skill_id: id,
                micro_skill_id: microSkillId,
                source: navState.returnPath ? 'browse' : 'dashboard_resume',
            });

            // Fetch first question
            const nq = await sessionService.getNextQuestion(sess.id);
            if (!nq) {
                setPhase('SUMMARY');
                setIsLoading(false);
                return;
            }
            setCurrentQuestion(nq);
            questionStartTime.current = Date.now();
            setPhase('ACTIVE');

            // Save last activity for "Resume" on Dashboard
            if (id) {
                setLastActivity({
                    skillId: id,
                    skillName,
                    subjectId: navState.subjectId,
                    subjectName: navState.subjectName,
                });
            }
        } catch (err: any) {
            // Fallback: if session engine fails (e.g. no questions in DB), show error
            console.error('Session start failed:', err);
            setQuestionCount(0);
        } finally {
            setIsLoading(false);
        }
    };

    /** Resume from a saved draft */
    const handleResumeDraft = (draft: ExerciseDraft) => {
        const sess: SessionDTO = {
            id: draft.sessionId,
            skillId: draft.skillId,
            status: 'in_progress',
            totalQuestions: draft.totalQuestions,
        };
        setSession(sess);
        setCurrentQuestion({
            questionId: draft.currentQuestion.questionId,
            text: draft.currentQuestion.text,
            questionType: draft.currentQuestion.questionType,
            difficulty: draft.currentQuestion.difficulty,
            choices: draft.currentQuestion.choices,
            mediaUrl: draft.currentQuestion.mediaUrl,
            timeLimitSeconds: draft.currentQuestion.timeLimitSeconds,
            points: draft.currentQuestion.points,
            microSkillId: draft.currentQuestion.microSkillId,
        });
        setSelectedAnswer(draft.selectedAnswer);
        setCurrentQIndex(draft.currentQIndex);
        setScore(draft.score);
        setMistakes(draft.mistakes);
        setTotalQuestions(draft.totalQuestions);
        setSkillName(draft.skillName);
        sessionStartRef.current = new Date(draft.sessionStartedAt).getTime();
        questionStartTime.current = Date.now();
        setPhase('ACTIVE');
        setPendingDraft(null);
    };

    /** Persist current exercise state to localStorage */
    const persistDraft = () => {
        if (!session || !currentQuestion || !id || phase !== 'ACTIVE') return;
        saveDraft({
            sessionId: session.id,
            skillId: id,
            skillName,
            microSkillId,
            currentQuestion: {
                questionId: currentQuestion.questionId,
                text: currentQuestion.text,
                questionType: currentQuestion.questionType,
                difficulty: currentQuestion.difficulty,
                choices: currentQuestion.choices,
                mediaUrl: currentQuestion.mediaUrl,
                timeLimitSeconds: currentQuestion.timeLimitSeconds,
                points: currentQuestion.points,
                microSkillId: currentQuestion.microSkillId,
            },
            selectedAnswer,
            currentQIndex,
            score,
            mistakes,
            totalQuestions,
            sessionStartedAt: new Date(sessionStartRef.current).toISOString(),
            savedAt: new Date().toISOString(),
            navState: {
                returnPath: navState.returnPath,
                subjectId: navState.subjectId,
                subjectName: navState.subjectName,
            },
        });
    };

    // Auto-save draft whenever the answer or question changes during ACTIVE phase
    useEffect(() => {
        persistDraft();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedAnswer, currentQIndex, score, mistakes, phase]);

    const handleValidate = async () => {
        if (!currentQuestion || !session || selectedAnswer === null || selectedAnswer === '' || isValidating) return;

        setIsValidating(true);
        const timeSpent = Math.round((Date.now() - questionStartTime.current) / 1000);

        try {
            // Record attempt via backend — backend validates correctness
            const result = await sessionService.recordAttempt(
                session.id,
                currentQuestion.questionId,
                selectedAnswer,
                timeSpent,
            );

            setCorrectAnswer(result.correctAnswer);
            setExplanation(result.explanation || '');
            setCriteriaFeedback(result.criteriaFeedback || null);

            if (result.isCorrect) {
                setAnswerStatus('CORRECT');
                setScore(prev => prev + 1);
                setConsecutiveMistakes(0);
                const msg = getRandomMessage(CORRECT_MESSAGES);
                setFeedbackMessage(msg);
                speakFeedback(msg.text);
            } else {
                setAnswerStatus('INCORRECT');
                setMistakes(prev => prev + 1);
                setConsecutiveMistakes(prev => prev + 1);
                const msg = getRandomMessage(INCORRECT_MESSAGES);
                setFeedbackMessage(msg);
                speakFeedback(msg.text);
            }

            // Store in history for non-linear review
            setQuestionHistory(prev => [...prev, {
                question: currentQuestion,
                answer: selectedAnswer,
                isCorrect: result.isCorrect,
                correctAnswer: result.correctAnswer,
                explanation: result.explanation || '',
            }]);

            analytics.exerciseStepCompleted(session.id, {
                question_number: currentQIndex + 1,
                question_id: currentQuestion.questionId,
                question_type: currentQuestion.questionType,
                is_correct: result.isCorrect,
                time_spent_seconds: timeSpent,
                hints_used: hintsUsedRef.current,
            });
            totalHintsRef.current += hintsUsedRef.current;
            hintsUsedRef.current = 0;
        } catch (err: any) {
            console.error('Attempt recording failed:', err);
            // On error, show as incorrect to let user continue
            setAnswerStatus('INCORRECT');
            setMistakes(prev => prev + 1);
            setConsecutiveMistakes(prev => prev + 1);
            setFeedbackMessage({ text: 'Erreur de connexion.', emoji: '\u26a0\ufe0f' });
        } finally {
            setIsValidating(false);
        }
    };

    const handleNext = async () => {
        if (!session) return;

        try {
            const nq = await sessionService.getNextQuestion(session.id);
            if (!nq) {
                // No more questions — complete session
                await handleFinish();
                return;
            }
            setCurrentQuestion(nq);
            setCurrentQIndex(prev => prev + 1);
            setSelectedAnswer(null);
            setAnswerStatus('IDLE');
            setCorrectAnswer(null);
            setExplanation('');
            setShowExplanation(false);
            setCriteriaFeedback(null);
            questionStartTime.current = Date.now();
        } catch {
            // If next question fails, finish session
            await handleFinish();
        }
    };

    const handleFinish = async () => {
        if (!session) return;
        const totalTimeSec = Math.round((Date.now() - sessionStartRef.current) / 1000);
        try {
            const result = await sessionService.completeSession(session.id);
            const finalCorrect = result.correctAnswers ?? score;
            const finalTotal = result.totalQuestions ?? totalQuestions;
            if (result.score !== undefined) {
                setScore(finalCorrect);
                setTotalQuestions(finalTotal);
            }
            if (result.smartScoreBefore !== undefined) setSmartScoreBefore(result.smartScoreBefore);
            if (result.smartScoreAfter !== undefined) setSmartScoreAfter(result.smartScoreAfter);
            if (result.xpEarned !== undefined) setXpEarned(result.xpEarned);

            analytics.exerciseCompleted(session.id, {
                score_percent: finalTotal > 0 ? Math.round(finalCorrect / finalTotal * 100) : 0,
                time_total_seconds: totalTimeSec,
                total_questions: finalTotal,
                correct_answers: finalCorrect,
                total_hints_used: totalHintsRef.current,
                status: 'success',
                smart_score_delta: (result.smartScoreAfter ?? 0) - (result.smartScoreBefore ?? 0),
            });
        } catch {
            analytics.exerciseCompleted(session.id, {
                score_percent: totalQuestions > 0 ? Math.round(score / totalQuestions * 100) : 0,
                time_total_seconds: totalTimeSec,
                total_questions: totalQuestions,
                correct_answers: score,
                total_hints_used: totalHintsRef.current,
                status: 'success',
            });
        }
        clearDraft();
        incrementDailyExercise();
        setPhase('SUMMARY');
    };

    const handleQuit = () => {
        if (window.confirm("Tu veux vraiment quitter ? Ta progression pour cet exercice sera perdue.")) {
            if (session && phase === 'ACTIVE') {
                analytics.dropOff(session.id, {
                    question_number: currentQIndex + 1,
                    time_on_question_seconds: Math.round((Date.now() - questionStartTime.current) / 1000),
                    total_time_seconds: Math.round((Date.now() - sessionStartRef.current) / 1000),
                });
                analytics.flush();
            }
            clearDraft();
            navigate(returnPath);
        }
    };

    // Track drop_off on unmount if exercise is still active
    useEffect(() => {
        return () => {
            const sess = session;
            if (sess && phase === 'ACTIVE') {
                analytics.dropOff(sess.id, {
                    question_number: currentQIndex + 1,
                    time_on_question_seconds: Math.round((Date.now() - questionStartTime.current) / 1000),
                    total_time_seconds: Math.round((Date.now() - sessionStartRef.current) / 1000),
                });
            }
        };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [session, phase, currentQIndex]);

    const goToLesson = () => {
        if (retenonsData && !showRetenonsSheet) {
            // First click: show inline retenons bottom sheet
            setShowRetenonsSheet(true);
        } else {
            // Second click or no retenons: navigate to full lesson
            setShowRetenonsSheet(false);
            navigate(`/app/student/lesson/${id}`, {
                state: { returnPath: location.pathname }
            });
        }
    };

    // Build render question — either current or from history review
    const isReviewing = reviewIndex !== null;
    const reviewedItem = isReviewing ? questionHistory[reviewIndex] : null;

    const renderQuestion: Question | null = isReviewing && reviewedItem
        ? mapNextToRenderQuestion(reviewedItem.question, reviewedItem.correctAnswer, reviewedItem.explanation)
        : currentQuestion
            ? mapNextToRenderQuestion(currentQuestion, correctAnswer, explanation)
            : null;

    if (isLoading) return <div className="p-8 text-center">Chargement...</div>;
    if (questionCount === 0 && phase === 'INTRO') return <div className="p-8 text-center">Aucune question trouv&eacute;e pour cette comp&eacute;tence.</div>;

    if (phase === 'INTRO') {
        const breadcrumbItems = [
            { label: 'Mati\u00e8res', to: '/app/student/subjects' },
            ...(navState.subjectName && navState.subjectId
                ? [{ label: navState.subjectName, to: `/app/student/subjects/${navState.subjectId}` }]
                : []),
            { label: skillName },
        ];

        return (
            <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center max-w-lg mx-auto">
                <div className="mb-6 self-start w-full text-left">
                    <Breadcrumb items={breadcrumbItems} />
                </div>
                <div className="w-20 h-20 gradient-hero rounded-3xl flex items-center justify-center text-white mb-6 animate-bounce-in shadow-glow-amber">
                    <Award size={40} />
                </div>
                <h1 className="text-3xl font-extrabold text-gray-900 mb-2 font-display">{skillName}</h1>
                <p className="text-gray-500 mb-8">{questionCount} questions &bull; <span className="text-amber-500 font-bold">&#127942; {xpReward} XP</span> &agrave; gagner</p>

                {effectiveTier === SubscriptionTier.FREE && (
                    <div className="mb-8 text-xs font-bold text-gray-500 bg-gray-100 py-1 px-3 rounded-full inline-block">
                        Exercice {dailyExerciseCount}/{freemiumDailyLimit} (Gratuit)
                    </div>
                )}

                {prereqCheck && !prereqCheck.met && (
                    <div className="mb-6 w-full p-4 bg-amber-50 border border-amber-200 rounded-xl text-left" role="alert">
                        <p className="text-sm font-semibold text-amber-800 mb-2">Comp&eacute;tences recommand&eacute;es avant de commencer :</p>
                        <ul className="space-y-1.5">
                            {prereqCheck.prerequisites.filter(p => !p.met).map(p => (
                                <li key={p.externalId} className="flex items-center justify-between text-sm">
                                    <button
                                        onClick={() => navigate(`/app/student/exercise/${p.skillId}`, { state: navState })}
                                        className="text-amber-700 hover:text-amber-900 underline underline-offset-2 text-left"
                                    >
                                        {p.name}
                                    </button>
                                    <span className="text-xs text-amber-600 font-medium ml-2 flex-shrink-0">
                                        {Math.round(p.smartScore)}% / {p.threshold}%
                                    </span>
                                </li>
                            ))}
                        </ul>
                        <p className="text-xs text-amber-600 mt-2">Tu peux quand m&ecirc;me commencer si tu le souhaites.</p>
                    </div>
                )}

                {pendingDraft && (
                    <div className="mb-4 w-full">
                        <Button fullWidth onClick={() => handleResumeDraft(pendingDraft)} className="h-14 text-lg mb-2 bg-green-600 hover:bg-green-700">
                            Reprendre (question {pendingDraft.currentQIndex + 1}/{pendingDraft.totalQuestions})
                        </Button>
                        <button
                            onClick={() => { clearDraft(); setPendingDraft(null); }}
                            className="text-xs text-gray-400 hover:text-gray-600 transition-colors w-full text-center"
                        >
                            Ignorer et recommencer
                        </button>
                    </div>
                )}
                {!pendingDraft && (
                    <Button fullWidth onClick={handleStart} className="mb-4 h-14 text-lg">&#128640; Commencer</Button>
                )}
                <Button fullWidth variant={ButtonVariant.GHOST} onClick={() => navigate(-1)}>Retour</Button>
                <PaywallModal isOpen={isPaywallOpen} onClose={() => setIsPaywallOpen(false)} />
            </div>
        );
    }

    if (phase === 'SUMMARY') {
        const displayTotal = totalQuestions || questionCount || 1;
        const finalPercentage = Math.round((score / displayTotal) * 100);
        const isSuccess = finalPercentage >= 70;
        const hasSmartScoreDelta = smartScoreBefore !== null && smartScoreAfter !== null;
        const smartScoreDelta = hasSmartScoreDelta ? smartScoreAfter! - smartScoreBefore! : null;
        const pointsToMastery = smartScoreAfter !== null ? Math.max(0, 100 - smartScoreAfter) : null;
        const displayXp = xpEarned ?? xpReward;

        return (
            <div className={`min-h-screen flex flex-col items-center justify-center p-6 text-center max-w-lg mx-auto animate-fade-in ${isSuccess ? 'bg-gradient-to-b from-green-50 to-white' : 'bg-white'}`}>
                {isSuccess && <Confetti />}
                <div className="mb-8 relative">
                    <SmartScoreMeter score={finalPercentage} />
                    {isSuccess && (
                        <div className="absolute -top-2 -right-2 text-yellow-400 animate-celebrate">
                            <Award size={32} fill="currentColor" />
                        </div>
                    )}
                </div>

                <h2 className="text-3xl font-extrabold text-gray-900 mb-2 font-display">
                    {isSuccess ? '\ud83c\udf89 Bravo !' : 'Bien jou\u00e9 !'}
                </h2>
                <p className="text-gray-500 mb-4">
                    {isSuccess
                        ? `Tu as ma\u00eetris\u00e9 cette comp\u00e9tence. Tu gagnes +${displayXp} XP.`
                        : "Tu as fait quelques erreurs, mais c'est en forgeant qu'on devient forgeron !"}
                </p>

                <div className="grid grid-cols-2 gap-4 w-full mb-6">
                    <div className="bg-gradient-to-br from-amber-50 to-orange-50 p-4 rounded-2xl">
                        <span className="block text-2xl font-bold text-sitou-primary">{score}/{displayTotal}</span>
                        <span className="text-xs text-gray-400 uppercase font-bold">Score</span>
                    </div>
                    <div className={`p-4 rounded-2xl ${mistakes === 0 ? 'bg-gradient-to-br from-green-50 to-teal-50' : 'bg-gradient-to-br from-orange-50 to-red-50'}`}>
                        <span className="block text-2xl font-bold text-gray-800">{mistakes}</span>
                        <span className="text-xs text-gray-400 uppercase font-bold">Erreurs</span>
                    </div>
                </div>

                {/* Progression SmartScore */}
                {hasSmartScoreDelta && (
                    <div className="w-full bg-gradient-to-br from-indigo-50 to-purple-50 p-4 rounded-2xl mb-6">
                        <p className="text-xs text-gray-500 uppercase font-bold mb-2">Ta progression</p>
                        <div className="flex items-center justify-center gap-2 mb-3">
                            <span className="text-lg font-bold text-gray-400">{smartScoreBefore}</span>
                            <ArrowRight size={16} className="text-gray-400" />
                            <span className="text-lg font-bold text-sitou-primary">{smartScoreAfter}</span>
                            {smartScoreDelta !== null && smartScoreDelta !== 0 && (
                                <span className={`text-sm font-bold px-2 py-0.5 rounded-full ${smartScoreDelta > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                    {smartScoreDelta > 0 ? '+' : ''}{smartScoreDelta}
                                </span>
                            )}
                        </div>
                        <div className="w-full bg-gray-200 h-2.5 rounded-full overflow-hidden">
                            <div
                                className="h-full rounded-full gradient-xp transition-all duration-1000 ease-out"
                                style={{ width: `${smartScoreAfter}%` }}
                            />
                        </div>
                        {pointsToMastery !== null && pointsToMastery > 0 && (
                            <p className="text-xs text-gray-500 mt-2">
                                Encore {pointsToMastery} point{pointsToMastery > 1 ? 's' : ''} pour ma&icirc;triser cette comp&eacute;tence !
                            </p>
                        )}
                        {pointsToMastery === 0 && (
                            <p className="text-xs text-green-600 font-bold mt-2">
                                Comp&eacute;tence ma&icirc;tris&eacute;e !
                            </p>
                        )}
                    </div>
                )}

                <div className="space-y-3 w-full">
                    <Button fullWidth onClick={() => navigate(returnPath)}>Retour</Button>
                    {!isSuccess && (
                        <Button fullWidth variant={ButtonVariant.SECONDARY} leftIcon={<RotateCcw size={18}/>} onClick={() => window.location.reload()}>R&eacute;essayer</Button>
                    )}
                    <Button
                        fullWidth
                        variant={ButtonVariant.GHOST}
                        leftIcon={<Share2 size={18}/>}
                        onClick={() => {
                            const text = `J'ai obtenu ${finalPercentage}% en ${skillName} sur Sitou ! \ud83c\udfc6 Tu veux essayer ?`;
                            const url = 'https://sitou.app';
                            telemetry.logEvent('Exercise', 'Share', skillName, finalPercentage);
                            if (navigator.share) {
                                navigator.share({ title: 'Mon score Sitou', text, url }).catch(() => {});
                            } else {
                                navigator.clipboard.writeText(`${text} ${url}`).then(() => {
                                    alert('Score copi\u00e9 dans le presse-papier !');
                                }).catch(() => {});
                            }
                        }}
                    >
                        Partager mon score
                    </Button>
                </div>
            </div>
        );
    }

    // ACTIVE PHASE
    return (
        <div className="min-h-screen bg-sitou-surface flex flex-col max-w-3xl mx-auto md:border-x md:border-gray-200 md:bg-white md:shadow-xl md:min-h-0 md:h-screen">
            <header className="p-4 border-b border-gray-100 bg-white sticky top-0 z-20">
                <div className="flex items-center justify-between mb-3">
                    <button onClick={handleQuit} className="p-2 rounded-full hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600" aria-label="Quitter l'exercice">
                        <X size={24} />
                    </button>
                    <div className="text-sm font-bold text-gray-500 flex items-center gap-2">
                        <span>{isReviewing
                            ? `Revue question ${reviewIndex! + 1}`
                            : `Question ${currentQIndex + 1} / ${totalQuestions || '?'}`}</span>
                        {phase === 'ACTIVE' && elapsedSeconds > 0 && (
                            <span className="flex items-center gap-1 text-xs text-gray-400">
                                <Timer size={12} />
                                {Math.floor(elapsedSeconds / 60)}:{String(elapsedSeconds % 60).padStart(2, '0')}
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-1">
                        <button onClick={() => setShowScratchpad(!showScratchpad)} className="p-2 rounded-full hover:bg-gray-100 transition-colors" aria-label="Ouvrir le brouillon" title="Brouillon">
                            <PenLine size={20} className="text-gray-400" />
                        </button>
                    <button onClick={goToLesson} className="p-2 text-sitou-primary hover:bg-amber-50 rounded-full" title="Voir la le&ccedil;on">
                        <HelpCircle size={24} />
                    </button>
                    </div>
                </div>

                {/* Question map — numbered dots for non-linear navigation */}
                {totalQuestions > 0 && (
                    <div className="flex items-center gap-1.5 mb-3 overflow-x-auto pb-1 scrollbar-none" role="tablist" aria-label="Navigation entre les questions">
                        {Array.from({ length: totalQuestions }).map((_, i) => {
                            const answered = questionHistory[i];
                            const isCurrent = !isReviewing && i === currentQIndex;
                            const isReviewTarget = isReviewing && i === reviewIndex;
                            const canNavigate = i < questionHistory.length; // only answered questions

                            let dotClass = 'bg-gray-200 text-gray-400'; // future/unanswered
                            if (answered?.isCorrect) dotClass = 'bg-green-100 text-green-700 border-green-300';
                            else if (answered && !answered.isCorrect) dotClass = 'bg-red-100 text-red-700 border-red-300';
                            if (isCurrent) dotClass = 'bg-amber-100 text-amber-700 border-amber-400 ring-2 ring-amber-200';
                            if (isReviewTarget) dotClass += ' ring-2 ring-indigo-300';

                            return (
                                <button
                                    key={i}
                                    role="tab"
                                    aria-selected={isCurrent || isReviewTarget}
                                    aria-label={`Question ${i + 1}${answered ? (answered.isCorrect ? ', correcte' : ', incorrecte') : ''}`}
                                    disabled={!canNavigate && !isCurrent}
                                    onClick={() => {
                                        if (canNavigate) {
                                            setReviewIndex(i);
                                        } else if (isCurrent) {
                                            setReviewIndex(null);
                                        }
                                    }}
                                    className={`min-w-[28px] h-7 rounded-lg text-xs font-bold border transition-all flex-shrink-0 ${dotClass} ${canNavigate ? 'cursor-pointer hover:scale-110' : !isCurrent ? 'cursor-default opacity-50' : 'cursor-pointer'}`}
                                >
                                    {i + 1}
                                </button>
                            );
                        })}
                    </div>
                )}

                <div className="w-full bg-gray-100 h-2.5 rounded-full overflow-hidden">
                    <div className="gradient-xp h-full rounded-full transition-all duration-500 ease-out" style={{ width: `${progress}%` }} />
                </div>
            </header>

            <main className="flex-1 overflow-y-auto p-6 md:p-10 flex flex-col">
                {isReviewing && reviewedItem ? (
                    <QuestionRenderer
                        key={`review-${reviewIndex}`}
                        question={renderQuestion!}
                        selectedAnswer={reviewedItem.answer}
                        onAnswerChange={() => {}} // read-only in review
                        isFeedbackMode={true}
                    />
                ) : renderQuestion && (
                    <QuestionRenderer
                        key={currentQuestion?.questionId}
                        question={renderQuestion}
                        selectedAnswer={selectedAnswer}
                        onAnswerChange={setSelectedAnswer}
                        isFeedbackMode={answerStatus !== 'IDLE'}
                        onHintRequested={() => {
                            hintsUsedRef.current += 1;
                            if (session && currentQuestion) {
                                analytics.hintRequested(session.id, {
                                    question_number: currentQIndex + 1,
                                    question_id: currentQuestion.questionId,
                                    time_before_hint_seconds: Math.round((Date.now() - questionStartTime.current) / 1000),
                                });
                            }
                        }}
                    />
                )}
            </main>

            {/* Retenons inline bottom sheet */}
            {showRetenonsSheet && retenonsData && (
                <div className="border-t-2 border-yellow-300 bg-yellow-50 p-4 md:p-6 animate-slide-up max-h-[40vh] overflow-y-auto">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="font-bold text-yellow-800 flex items-center text-base">
                            <Lightbulb size={18} className="mr-2 text-yellow-600" /> Retenons
                        </h3>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => { setShowRetenonsSheet(false); navigate(`/app/student/lesson/${id}`, { state: { returnPath: location.pathname } }); }}
                                className="text-xs text-sitou-primary font-semibold hover:underline"
                            >
                                Le&ccedil;on compl&egrave;te &rarr;
                            </button>
                            <button
                                onClick={() => setShowRetenonsSheet(false)}
                                className="text-gray-400 hover:text-gray-600 text-lg font-bold"
                            >
                                &times;
                            </button>
                        </div>
                    </div>
                    {retenonsData.formula && (
                        <div className="inline-block bg-yellow-100 border border-yellow-200 rounded-lg px-3 py-1.5 mb-3">
                            <span className="font-mono text-sm text-yellow-900 font-semibold">{retenonsData.formula}</span>
                        </div>
                    )}
                    {retenonsData.bodyHtml && (
                        <div className="prose prose-sm max-w-none text-gray-700 mb-3" dangerouslySetInnerHTML={{ __html: retenonsData.bodyHtml }} />
                    )}
                    {retenonsData.rules.length > 0 && (
                        <div className="space-y-1.5">
                            {retenonsData.rules.map((rule, idx) => (
                                <div key={idx} className="flex items-start space-x-2 bg-yellow-100 rounded-lg px-3 py-2">
                                    <Lightbulb size={14} className="text-yellow-600 mt-0.5 flex-shrink-0" />
                                    <span className="text-yellow-900 text-sm font-medium">{rule}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            <footer className={`p-4 md:p-6 border-t border-gray-100 sticky bottom-0 z-20 transition-colors duration-300 ${
                isReviewing ? 'bg-indigo-50 border-indigo-200' :
                answerStatus === 'CORRECT' ? 'bg-green-50 border-green-200' :
                answerStatus === 'INCORRECT' ? 'bg-red-50 border-red-200' : 'bg-white'
            }`}>
                {isReviewing ? (
                    <div className="w-full md:max-w-xs md:ml-auto">
                        <Button
                            fullWidth
                            onClick={() => setReviewIndex(null)}
                            className="h-12 text-lg"
                            leftIcon={<ArrowRight size={20} />}
                        >
                            Retour à la question en cours
                        </Button>
                    </div>
                ) : answerStatus !== 'IDLE' && (
                    <div className="mb-4 animate-slide-up">
                        <div className="flex items-start mb-2">
                            {answerStatus === 'CORRECT' ? (
                                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                                    <CheckCircle2 className="text-sitou-green w-5 h-5" />
                                </div>
                            ) : (
                                <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                                    <AlertCircle className="text-sitou-red w-5 h-5" />
                                </div>
                            )}
                            <div>
                                <h3 className={`font-extrabold text-lg ${answerStatus === 'CORRECT' ? 'text-sitou-green' : 'text-sitou-red'}`}>
                                    {feedbackMessage.emoji} {feedbackMessage.text}
                                </h3>
                                {explanation && answerStatus === 'CORRECT' && (
                                    <SanitizedHTML
                                        html={explanation}
                                        className="text-gray-600 mt-1 text-sm md:text-base leading-relaxed prose prose-sm max-w-none"
                                    />
                                )}

                                {explanation && answerStatus === 'INCORRECT' && (
                                    <div className="mt-2">
                                        <button
                                            type="button"
                                            onClick={() => {
                                                const next = !showExplanation;
                                                setShowExplanation(next);
                                                if (next) {
                                                    speakFeedback(explanation);
                                                } else if ('speechSynthesis' in window) {
                                                    window.speechSynthesis.cancel();
                                                }
                                            }}
                                            aria-expanded={showExplanation}
                                            aria-controls="worked-solution-panel"
                                            className="inline-flex items-center gap-2 text-sm font-bold text-sitou-red bg-white border border-red-200 hover:bg-red-50 px-3 py-1.5 rounded-xl transition-all"
                                        >
                                            <Lightbulb size={16} />
                                            {showExplanation ? "Masquer l'explication" : "Voir l'explication"}
                                            {showExplanation ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                                        </button>
                                        {showExplanation && (
                                            <div
                                                id="worked-solution-panel"
                                                className="mt-2 p-3 bg-white border border-red-100 rounded-xl"
                                            >
                                                <SanitizedHTML
                                                    html={explanation}
                                                    className="text-gray-700 text-sm md:text-base leading-relaxed prose prose-sm max-w-none"
                                                />
                                                {'speechSynthesis' in window && (
                                                    <button
                                                        type="button"
                                                        onClick={() => speakFeedback(explanation)}
                                                        aria-label="Réécouter l'explication"
                                                        className="mt-2 inline-flex items-center gap-1 text-xs font-bold text-sitou-primary hover:underline"
                                                    >
                                                        <Volume2 size={14} />
                                                        Réécouter
                                                    </button>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* C1/C2/C3 criteria feedback for contextual problems */}
                                {criteriaFeedback && criteriaFeedback.length > 0 && answerStatus === 'INCORRECT' && (
                                    <div className="mt-3 space-y-2">
                                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wide">Crit&egrave;res d'&eacute;valuation CEP</p>
                                        {criteriaFeedback.map((c) => (
                                            <div key={c.code} className="bg-red-50 border border-red-100 rounded-xl p-3">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="text-xs font-bold bg-red-200 text-red-800 px-2 py-0.5 rounded-full">{c.code}</span>
                                                    <span className="text-sm font-bold text-gray-800">{c.label}</span>
                                                </div>
                                                <p className="text-sm text-gray-600">{c.description}</p>
                                                {c.guide && (
                                                    <p className="text-sm text-sitou-primary font-medium mt-1">{c.guide}</p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>

                        {answerStatus === 'INCORRECT' && (
                            <div className="mt-3 ml-11 flex items-center gap-3">
                                <Button
                                    size="sm"
                                    variant={ButtonVariant.SECONDARY}
                                    onClick={goToLesson}
                                    className="bg-white border border-red-200 text-sitou-red hover:bg-red-50"
                                    leftIcon={<BookOpen size={16} />}
                                >
                                    {consecutiveMistakes >= 2 ? 'Relire la le\u00e7on' : 'Voir la le\u00e7on'}
                                </Button>
                                {consecutiveMistakes >= 2 && (
                                    <span className="text-xs text-red-400">La le&ccedil;on peut t&rsquo;aider !</span>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {!isReviewing && (
                    <div className="w-full md:max-w-xs md:ml-auto">
                        {answerStatus === 'IDLE' ? (
                            <Button fullWidth onClick={handleValidate} disabled={!selectedAnswer || isValidating} isLoading={isValidating} className="h-12 text-lg shadow-xl">
                                Valider
                            </Button>
                        ) : (
                            <Button
                                fullWidth
                                onClick={handleNext}
                                variant={answerStatus === 'CORRECT' ? ButtonVariant.SUCCESS : ButtonVariant.DANGER}
                                className="h-12 text-lg shadow-xl"
                                leftIcon={<ArrowRight size={20} />}
                            >
                                Continuer
                            </Button>
                        )}
                    </div>
                )}
            </footer>

            <Scratchpad isOpen={showScratchpad} onClose={() => setShowScratchpad(false)} />

            {/* Pause suggestion after 5 minutes */}
            {showPauseSuggestion && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
                    <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full p-8 text-center animate-fade-in">
                        <div className="text-5xl mb-4"><Pause size={48} className="mx-auto text-indigo-500" /></div>
                        <h2 className="text-xl font-extrabold text-gray-900 mb-2">Tu mérites une pause !</h2>
                        <p className="text-gray-500 text-sm mb-6">
                            Tu travailles depuis plus de 5 minutes. Étire-toi, respire, et reviens en pleine forme.
                        </p>
                        <Button fullWidth onClick={() => setShowPauseSuggestion(false)}>
                            Je continue
                        </Button>
                    </div>
                </div>
            )}
        </div>
    );
};
