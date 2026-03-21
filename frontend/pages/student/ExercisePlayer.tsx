import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { QuestionRenderer } from '../../components/exercise/QuestionRenderer';
import { ButtonVariant, Question, SubscriptionTier } from '../../types';
import { X, CheckCircle2, AlertCircle, ArrowRight, RotateCcw, Award, HelpCircle, BookOpen, PenLine, Share2 } from 'lucide-react';
import { Breadcrumb } from '../../components/ui/Breadcrumb';
import { useAppStore } from '../../store';
import { SmartScoreMeter } from '../../components/ilma/Gamification';
import { PaywallModal } from '../../components/subscription/PaywallModal';
import { contentService, QuestionDTO } from '../../services/contentService';
import { sessionService, SessionDTO, NextQuestionDTO } from '../../services/sessionService';
import { useAuthStore } from '../../store/authStore';
import { useConfigStore } from '../../store/configStore';
import { telemetry } from '../../services/telemetry';

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

/** Map a NextQuestionDTO (from session engine) to a Question for QuestionRenderer */
function mapNextToRenderQuestion(nq: NextQuestionDTO, correctAnswer?: any, explanation?: string): Question {
  const QUESTION_TYPE_MAP: Record<string, string> = {
    mcq: 'MCQ', true_false: 'BOOLEAN', fill_blank: 'FILL_BLANK',
    numeric_input: 'NUMERIC_INPUT', short_answer: 'SHORT_ANSWER',
    ordering: 'ORDERING', matching: 'MATCHING', error_correction: 'ERROR_CORRECTION',
    contextual_problem: 'CONTEXTUAL_PROBLEM', guided_steps: 'GUIDED_STEPS',
    justification: 'JUSTIFICATION', tracing: 'TRACING',
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
          <button onClick={onClose} className="text-xs px-3 py-1.5 bg-ilma-primary text-white rounded-lg hover:bg-ilma-primary-dark transition-colors font-medium">Fermer</button>
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
    const [isValidating, setIsValidating] = useState(false);
    const [showScratchpad, setShowScratchpad] = useState(false);
    const [smartScoreBefore, setSmartScoreBefore] = useState<number | null>(null);
    const [smartScoreAfter, setSmartScoreAfter] = useState<number | null>(null);
    const [xpEarned, setXpEarned] = useState<number | null>(null);

    // Load intro data (question count + skill name)
    useEffect(() => {
        if (!id) return;
        Promise.all([
            contentService.listQuestions(id, microSkillId),
            contentService.getSkillWithLessons(id).catch(() => null),
        ]).then(([qs, skillData]) => {
            setQuestionCount(qs.length);
            if (skillData) setSkillName(skillData.skill.name);
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

            if (result.isCorrect) {
                setAnswerStatus('CORRECT');
                setScore(prev => prev + 1);
                setConsecutiveMistakes(0);
                setFeedbackMessage(getRandomMessage(CORRECT_MESSAGES));
            } else {
                setAnswerStatus('INCORRECT');
                setMistakes(prev => prev + 1);
                setConsecutiveMistakes(prev => prev + 1);
                setFeedbackMessage(getRandomMessage(INCORRECT_MESSAGES));
            }
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
            questionStartTime.current = Date.now();
        } catch {
            // If next question fails, finish session
            await handleFinish();
        }
    };

    const handleFinish = async () => {
        if (!session) return;
        try {
            const result = await sessionService.completeSession(session.id);
            // Use server-reported score if available
            if (result.score !== undefined) {
                setScore(result.correctAnswers || score);
                setTotalQuestions(result.totalQuestions || totalQuestions);
            }
            if (result.smartScoreBefore !== undefined) setSmartScoreBefore(result.smartScoreBefore);
            if (result.smartScoreAfter !== undefined) setSmartScoreAfter(result.smartScoreAfter);
            if (result.xpEarned !== undefined) setXpEarned(result.xpEarned);
        } catch {
            // Even if complete fails, show summary with local data
        }
        incrementDailyExercise();
        setPhase('SUMMARY');
    };

    const handleQuit = () => {
        if (window.confirm("Tu veux vraiment quitter ? Ta progression pour cet exercice sera perdue.")) {
            navigate(returnPath);
        }
    };

    const goToLesson = () => {
        navigate(`/app/student/lesson/${id}`, {
            state: { returnPath: location.pathname }
        });
    };

    // Build render question from current state
    const renderQuestion: Question | null = currentQuestion
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

                <Button fullWidth onClick={handleStart} className="mb-4 h-14 text-lg">&#128640; Commencer</Button>
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
                        <span className="block text-2xl font-bold text-ilma-primary">{score}/{displayTotal}</span>
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
                            <span className="text-lg font-bold text-ilma-primary">{smartScoreAfter}</span>
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
                            const text = `J'ai obtenu ${finalPercentage}% en ${skillName} sur ILMA ! \ud83c\udfc6 Tu veux essayer ?`;
                            const url = 'https://ilma.app';
                            telemetry.logEvent('Exercise', 'Share', skillName, finalPercentage);
                            if (navigator.share) {
                                navigator.share({ title: 'Mon score ILMA', text, url }).catch(() => {});
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
        <div className="min-h-screen bg-ilma-surface flex flex-col max-w-3xl mx-auto md:border-x md:border-gray-200 md:bg-white md:shadow-xl md:min-h-0 md:h-screen">
            <header className="p-4 border-b border-gray-100 bg-white sticky top-0 z-20">
                <div className="flex items-center justify-between mb-4">
                    <button onClick={handleQuit} className="p-2 rounded-full hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600" aria-label="Quitter l'exercice">
                        <X size={24} />
                    </button>
                    <div className="text-sm font-bold text-gray-500">
                        Question {currentQIndex + 1} / {totalQuestions || '?'}
                    </div>
                    <div className="flex items-center gap-1">
                        <button onClick={() => setShowScratchpad(!showScratchpad)} className="p-2 rounded-full hover:bg-gray-100 transition-colors" aria-label="Ouvrir le brouillon" title="Brouillon">
                            <PenLine size={20} className="text-gray-400" />
                        </button>
                    <button onClick={goToLesson} className="p-2 text-ilma-primary hover:bg-amber-50 rounded-full" title="Voir la le&ccedil;on">
                        <HelpCircle size={24} />
                    </button>
                    </div>
                </div>
                <div className="w-full bg-gray-100 h-3 rounded-full overflow-hidden">
                    <div className="gradient-xp h-full rounded-full transition-all duration-500 ease-out" style={{ width: `${progress}%` }} />
                </div>
            </header>

            <main className="flex-1 overflow-y-auto p-6 md:p-10 flex flex-col">
                {renderQuestion && (
                    <QuestionRenderer
                        key={currentQuestion?.questionId}
                        question={renderQuestion}
                        selectedAnswer={selectedAnswer}
                        onAnswerChange={setSelectedAnswer}
                        isFeedbackMode={answerStatus !== 'IDLE'}
                    />
                )}
            </main>

            <footer className={`p-4 md:p-6 border-t border-gray-100 sticky bottom-0 z-20 transition-colors duration-300 ${
                answerStatus === 'CORRECT' ? 'bg-green-50 border-green-200' :
                answerStatus === 'INCORRECT' ? 'bg-red-50 border-red-200' : 'bg-white'
            }`}>
                {answerStatus !== 'IDLE' && (
                    <div className="mb-4 animate-slide-up">
                        <div className="flex items-start mb-2">
                            {answerStatus === 'CORRECT' ? (
                                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                                    <CheckCircle2 className="text-ilma-green w-5 h-5" />
                                </div>
                            ) : (
                                <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                                    <AlertCircle className="text-ilma-red w-5 h-5" />
                                </div>
                            )}
                            <div>
                                <h3 className={`font-extrabold text-lg ${answerStatus === 'CORRECT' ? 'text-ilma-green' : 'text-ilma-red'}`}>
                                    {feedbackMessage.emoji} {feedbackMessage.text}
                                </h3>
                                {explanation && (
                                    <p className="text-gray-600 mt-1 text-sm md:text-base leading-relaxed">
                                        {explanation}
                                    </p>
                                )}
                            </div>
                        </div>

                        {answerStatus === 'INCORRECT' && consecutiveMistakes >= 2 && (
                            <div className="mt-3 ml-11">
                                <Button
                                    size="sm"
                                    variant={ButtonVariant.SECONDARY}
                                    onClick={goToLesson}
                                    className="bg-white border border-red-200 text-ilma-red hover:bg-red-50"
                                    leftIcon={<BookOpen size={16} />}
                                >
                                    Relire la le&ccedil;on
                                </Button>
                            </div>
                        )}
                    </div>
                )}

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
            </footer>

            <Scratchpad isOpen={showScratchpad} onClose={() => setShowScratchpad(false)} />
        </div>
    );
};
