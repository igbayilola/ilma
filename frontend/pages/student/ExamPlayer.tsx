import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { ButtonVariant } from '../../types';
import { X, ChevronLeft, ChevronRight, Clock, AlertTriangle, Link2 } from 'lucide-react';
import {
  examService,
  ExamQuestionDTO,
  ExamSessionDTO,
  ExamItemDTO,
  ExamSubQuestionDTO,
} from '../../services/examService';

type PlayerState = 'LOADING' | 'ACTIVE' | 'COMPLETING';

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

const DOMAIN_LABELS: Record<string, string> = {
  data_proportionality: 'Données & Proportionnalité',
  measures_operations: 'Mesures & Opérations',
  geometry: 'Géométrie',
};

export const ExamPlayerPage: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  // Session can be passed via location.state from ExamList
  const passedSession = (location.state as { session?: ExamSessionDTO })?.session;

  const [state, setState] = useState<PlayerState>(passedSession ? 'ACTIVE' : 'LOADING');
  const [sessionId, setSessionId] = useState<string>(passedSession?.session_id || '');
  const [examType, setExamType] = useState<'cep' | 'qcm'>(passedSession?.exam_type || 'qcm');

  // QCM state
  const [questions, setQuestions] = useState<ExamQuestionDTO[]>(
    passedSession?.questions || []
  );
  const [currentIndex, setCurrentIndex] = useState(0);

  // CEP state
  const [items, setItems] = useState<ExamItemDTO[]>(passedSession?.items || []);
  const [contextText, setContextText] = useState<string>(passedSession?.context_text || '');
  const [currentItemIndex, setCurrentItemIndex] = useState(0);

  // Shared state
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showTimeWarning, setShowTimeWarning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const hasAutoCompleted = useRef(false);

  // Start exam if not passed via state
  useEffect(() => {
    if (passedSession) {
      setTimeLeft((passedSession.duration_minutes || 60) * 60);
      return;
    }
    if (!examId) return;

    examService
      .startExam(examId)
      .then((session) => {
        setSessionId(session.session_id);
        setExamType(session.exam_type || 'qcm');
        if (session.exam_type === 'cep') {
          setItems(session.items || []);
          setContextText(session.context_text || '');
        } else {
          setQuestions(session.questions || []);
        }
        setTimeLeft((session.duration_minutes || 60) * 60);
        setState('ACTIVE');
      })
      .catch((err) => {
        console.error('Failed to start exam:', err);
        navigate('/app/student/exams');
      });
  }, [examId, passedSession, navigate]);

  // Update timer from exam metadata
  useEffect(() => {
    if (!examId || !passedSession) return;
    examService
      .listExams()
      .then((exams) => {
        const exam = exams.find((e) => e.id === examId);
        if (exam?.duration_minutes) {
          setTimeLeft(exam.duration_minutes * 60);
        }
      })
      .catch(() => {});
  }, [examId, passedSession]);

  // Complete exam handler
  const handleComplete = useCallback(async () => {
    if (!sessionId || state === 'COMPLETING') return;
    setState('COMPLETING');
    setShowConfirmModal(false);

    try {
      await examService.completeExam(sessionId);
      navigate(`/app/student/exams/${sessionId}/correction`, { replace: true });
    } catch (err) {
      console.error('Failed to complete exam:', err);
      navigate(`/app/student/exams/${sessionId}/correction`, { replace: true });
    }
  }, [sessionId, state, navigate]);

  // Timer countdown
  useEffect(() => {
    if (state !== 'ACTIVE') return;

    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          if (!hasAutoCompleted.current) {
            hasAutoCompleted.current = true;
            handleComplete();
          }
          return 0;
        }
        if (prev === 5 * 60 + 1) {
          setShowTimeWarning(true);
          setTimeout(() => setShowTimeWarning(false), 5000);
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [state, handleComplete]);

  // QCM answer submit
  const submitQcmAnswer = useCallback(
    async (questionId: string, answer: string) => {
      if (!sessionId) return;
      try {
        await examService.submitAnswer(sessionId, questionId, answer);
      } catch (err) {
        console.error('Failed to submit answer:', err);
      }
    },
    [sessionId]
  );

  // CEP answer submit
  const submitCepAnswer = useCallback(
    async (itemNumber: number, subLabel: string, answer: string) => {
      if (!sessionId) return;
      try {
        await examService.submitCepAnswer(sessionId, itemNumber, subLabel, answer);
      } catch (err) {
        console.error('Failed to submit CEP answer:', err);
      }
    },
    [sessionId]
  );

  const handleSelectAnswer = (questionId: string, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
    submitQcmAnswer(questionId, answer);

    const q = questions[currentIndex];
    if (q && (q.question_type === 'mcq' || q.question_type === 'true_false')) {
      setTimeout(() => {
        if (currentIndex < questions.length - 1) {
          setCurrentIndex((i) => i + 1);
        }
      }, 400);
    }
  };

  const handleFillBlankSubmit = (questionId: string, answer: string) => {
    if (!answer.trim()) return;
    setAnswers((prev) => ({ ...prev, [questionId]: answer.trim() }));
    submitQcmAnswer(questionId, answer.trim());
    if (currentIndex < questions.length - 1) {
      setTimeout(() => setCurrentIndex((i) => i + 1), 400);
    }
  };

  // CEP answer handlers
  const handleCepAnswer = (itemNumber: number, subLabel: string, answer: string) => {
    const key = `${itemNumber}-${subLabel}`;
    setAnswers((prev) => ({ ...prev, [key]: answer }));
    submitCepAnswer(itemNumber, subLabel, answer);
  };

  const handleCepSelectAnswer = (itemNumber: number, subLabel: string, answer: string) => {
    handleCepAnswer(itemNumber, subLabel, answer);
  };

  const handleCepFillBlankSubmit = (itemNumber: number, subLabel: string, answer: string) => {
    if (!answer.trim()) return;
    handleCepAnswer(itemNumber, subLabel, answer.trim());
  };

  const handleCepNumericSubmit = (itemNumber: number, subLabel: string, answer: string) => {
    if (!answer.trim()) return;
    handleCepAnswer(itemNumber, subLabel, answer.trim());
  };

  const handleQuit = () => {
    if (
      window.confirm(
        'Tu veux vraiment quitter ? Tes réponses seront perdues.'
      )
    ) {
      navigate('/app/student/exams');
    }
  };

  // Count answers
  const answeredCount = Object.keys(answers).length;
  const totalQuestions = examType === 'cep'
    ? items.reduce((sum, item) => sum + item.sub_questions.length, 0)
    : questions.length;
  const isLowTime = timeLeft <= 5 * 60;

  if (state === 'LOADING' || state === 'COMPLETING') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        <div className="w-12 h-12 border-4 border-amber-200 border-t-amber-500 rounded-full animate-spin mb-4" />
        <p className="text-gray-500 font-medium">
          {state === 'LOADING'
            ? "Préparation de l'examen..."
            : 'Correction en cours...'}
        </p>
      </div>
    );
  }

  // ─── CEP EXAM PLAYER ───────────────────────────────
  if (examType === 'cep') {
    const currentItem = items[currentItemIndex];
    const domainLabel = currentItem ? (DOMAIN_LABELS[currentItem.domain] || currentItem.domain) : '';

    return (
      <div className="min-h-screen bg-white flex flex-col">
        {/* Header */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-100 shadow-sm">
          <div className="flex items-center justify-between p-3 max-w-3xl mx-auto">
            <button
              onClick={handleQuit}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors text-gray-400"
              aria-label="Quitter"
            >
              <X size={22} />
            </button>

            <div className="text-sm font-bold text-gray-700">
              Item {currentItemIndex + 1}/{items.length}
            </div>

            <div
              className={`flex items-center gap-1 text-sm font-bold px-3 py-1.5 rounded-full ${
                isLowTime
                  ? 'bg-red-100 text-red-600 animate-pulse'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              <Clock size={14} />
              {formatTime(timeLeft)}
            </div>
          </div>

          {/* Item tabs */}
          <div className="flex gap-1 px-3 pb-2 max-w-3xl mx-auto">
            {items.map((item, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentItemIndex(idx)}
                className={`flex-1 text-xs font-bold py-1.5 rounded-lg transition-all ${
                  idx === currentItemIndex
                    ? 'bg-amber-500 text-white shadow-md'
                    : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                }`}
              >
                Item {item.item_number}
              </button>
            ))}
          </div>

          {/* Progress bar */}
          <div className="w-full bg-gray-100 h-1.5">
            <div
              className="h-full bg-amber-500 transition-all duration-300"
              style={{
                width: `${(answeredCount / totalQuestions) * 100}%`,
              }}
            />
          </div>
        </header>

        {/* Time warning toast */}
        {showTimeWarning && (
          <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 bg-red-600 text-white px-4 py-2 rounded-xl shadow-lg flex items-center gap-2 animate-slide-up">
            <AlertTriangle size={18} />
            <span className="font-bold text-sm">Plus que 5 minutes !</span>
          </div>
        )}

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-10 max-w-3xl mx-auto w-full">
          {currentItem && (
            <div>
              {/* Domain badge */}
              <div className="mb-4">
                <span className="inline-block text-xs font-bold uppercase px-3 py-1 rounded-full bg-blue-100 text-blue-700">
                  {domainLabel}
                </span>
              </div>

              {/* Context text */}
              {currentItem.context_text && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
                  <p className="text-sm text-amber-900 leading-relaxed font-medium">
                    {currentItem.context_text}
                  </p>
                </div>
              )}

              {/* Sub-questions */}
              <div className="space-y-8">
                {currentItem.sub_questions.map((sq) => {
                  const answerKey = `${currentItem.item_number}-${sq.sub_label}`;
                  const currentAnswer = answers[answerKey] || '';

                  return (
                    <div key={sq.id} className="space-y-3">
                      <div className="flex items-start gap-2">
                        <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-gray-900 text-white text-sm font-bold flex-shrink-0 mt-0.5">
                          {sq.sub_label})
                        </span>
                        <p className="text-gray-900 font-medium leading-relaxed">
                          {sq.text}
                        </p>
                      </div>

                      {sq.depends_on_previous && (
                        <div className="flex items-center gap-1.5 text-xs text-amber-600 font-medium ml-9">
                          <Link2 size={12} />
                          {sq.hint || 'Utilise le résultat de la question précédente.'}
                        </div>
                      )}

                      <div className="ml-9">
                        {/* Numeric input */}
                        {sq.question_type === 'numeric_input' && (
                          <NumericInput
                            answerKey={answerKey}
                            currentAnswer={currentAnswer}
                            onSubmit={(val) => handleCepNumericSubmit(currentItem.item_number, sq.sub_label, val)}
                          />
                        )}

                        {/* Fill blank */}
                        {sq.question_type === 'fill_blank' && (
                          <FillBlankInput
                            questionId={answerKey}
                            currentAnswer={currentAnswer}
                            onSubmit={(_, val) => handleCepFillBlankSubmit(currentItem.item_number, sq.sub_label, val)}
                          />
                        )}

                        {/* True/False */}
                        {sq.question_type === 'true_false' && (
                          <div className="flex gap-3">
                            {['Vrai', 'Faux'].map((opt) => {
                              const isSelected = currentAnswer === opt;
                              return (
                                <button
                                  key={opt}
                                  onClick={() => handleCepSelectAnswer(currentItem.item_number, sq.sub_label, opt)}
                                  className={`flex-1 p-3 rounded-xl border-2 text-center font-bold transition-all duration-200 ${
                                    isSelected
                                      ? 'border-amber-500 bg-amber-50 text-amber-900 shadow-md'
                                      : 'border-gray-200 bg-white hover:border-gray-300 text-gray-700'
                                  }`}
                                >
                                  {opt}
                                </button>
                              );
                            })}
                          </div>
                        )}

                        {/* MCQ */}
                        {sq.question_type === 'mcq' && sq.choices && (
                          <div className="space-y-2">
                            {sq.choices.map((choice, idx) => {
                              const isSelected = currentAnswer === choice;
                              return (
                                <button
                                  key={idx}
                                  onClick={() => handleCepSelectAnswer(currentItem.item_number, sq.sub_label, choice)}
                                  className={`w-full text-left p-3 rounded-xl border-2 transition-all duration-200 font-medium text-sm ${
                                    isSelected
                                      ? 'border-amber-500 bg-amber-50 text-amber-900 shadow-md'
                                      : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50 text-gray-700'
                                  }`}
                                >
                                  <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-xs font-bold mr-2 text-gray-500">
                                    {String.fromCharCode(65 + idx)}
                                  </span>
                                  {choice}
                                </button>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </main>

        {/* Footer navigation */}
        <footer className="sticky bottom-0 bg-white border-t border-gray-100 p-4">
          <div className="flex items-center justify-between max-w-3xl mx-auto gap-3">
            <Button
              variant={ButtonVariant.GHOST}
              onClick={() => setCurrentItemIndex((i) => Math.max(0, i - 1))}
              disabled={currentItemIndex === 0}
              className="px-3"
            >
              <ChevronLeft size={18} className="mr-1" />
              Préc.
            </Button>

            <div className="text-xs text-gray-400 font-medium">
              {answeredCount}/{totalQuestions} répondue{answeredCount !== 1 ? 's' : ''}
            </div>

            {currentItemIndex < items.length - 1 ? (
              <Button
                variant={ButtonVariant.GHOST}
                onClick={() => setCurrentItemIndex((i) => i + 1)}
                className="px-3"
              >
                Suiv.
                <ChevronRight size={18} className="ml-1" />
              </Button>
            ) : (
              <Button
                variant={ButtonVariant.PRIMARY}
                onClick={() => setShowConfirmModal(true)}
                className="px-4"
              >
                Terminer
              </Button>
            )}
          </div>

          {currentItemIndex < items.length - 1 && answeredCount > 0 && (
            <div className="max-w-3xl mx-auto mt-3">
              <Button
                fullWidth
                variant={ButtonVariant.DANGER}
                onClick={() => setShowConfirmModal(true)}
                disabled={isSubmitting}
              >
                Terminer l'examen
              </Button>
            </div>
          )}
        </footer>

        {/* Confirmation modal */}
        <Modal
          isOpen={showConfirmModal}
          onClose={() => setShowConfirmModal(false)}
          title="Terminer l'examen ?"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Tu as répondu à <span className="font-bold">{answeredCount}</span> question
              {answeredCount !== 1 ? 's' : ''} sur{' '}
              <span className="font-bold">{totalQuestions}</span>.
            </p>
            {answeredCount < totalQuestions && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm text-amber-700 flex items-start gap-2">
                <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
                <span>
                  Les questions non répondues seront comptées comme fausses.
                </span>
              </div>
            )}
            <div className="flex gap-3 pt-2">
              <Button
                fullWidth
                variant={ButtonVariant.GHOST}
                onClick={() => setShowConfirmModal(false)}
              >
                Continuer
              </Button>
              <Button
                fullWidth
                variant={ButtonVariant.DANGER}
                onClick={handleComplete}
                isLoading={isSubmitting}
              >
                Terminer
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    );
  }

  // ─── QCM EXAM PLAYER (legacy) ──────────────────────
  const currentQuestion = questions[currentIndex];

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-white border-b border-gray-100 shadow-sm">
        <div className="flex items-center justify-between p-3 max-w-3xl mx-auto">
          <button
            onClick={handleQuit}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors text-gray-400"
            aria-label="Quitter"
          >
            <X size={22} />
          </button>

          <div className="text-sm font-bold text-gray-700">
            Question {currentIndex + 1}/{questions.length}
          </div>

          <div
            className={`flex items-center gap-1 text-sm font-bold px-3 py-1.5 rounded-full ${
              isLowTime
                ? 'bg-red-100 text-red-600 animate-pulse'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            <Clock size={14} />
            {formatTime(timeLeft)}
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-gray-100 h-1.5">
          <div
            className="h-full bg-amber-500 transition-all duration-300"
            style={{
              width: `${((currentIndex + 1) / questions.length) * 100}%`,
            }}
          />
        </div>
      </header>

      {/* Time warning toast */}
      {showTimeWarning && (
        <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 bg-red-600 text-white px-4 py-2 rounded-xl shadow-lg flex items-center gap-2 animate-slide-up">
          <AlertTriangle size={18} />
          <span className="font-bold text-sm">Plus que 5 minutes !</span>
        </div>
      )}

      {/* Question content */}
      <main className="flex-1 overflow-y-auto p-6 md:p-10 max-w-3xl mx-auto w-full">
        {currentQuestion && (
          <div key={currentQuestion.id}>
            <p className="text-lg md:text-xl font-bold text-gray-900 mb-6 leading-relaxed">
              {currentQuestion.text}
            </p>

            {currentQuestion.media_url && (
              <img
                src={currentQuestion.media_url}
                alt="Illustration"
                className="w-full max-w-md mx-auto rounded-xl mb-6"
                loading="lazy"
                decoding="async"
                width={448}
                height={300}
              />
            )}

            {/* MCQ */}
            {currentQuestion.question_type === 'mcq' &&
              currentQuestion.choices && (
                <div className="space-y-3">
                  {currentQuestion.choices.map((choice, idx) => {
                    const isSelected =
                      answers[currentQuestion.id] === choice;
                    return (
                      <button
                        key={idx}
                        onClick={() =>
                          handleSelectAnswer(currentQuestion.id, choice)
                        }
                        className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-200 font-medium ${
                          isSelected
                            ? 'border-amber-500 bg-amber-50 text-amber-900 shadow-md'
                            : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50 text-gray-700'
                        }`}
                      >
                        <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-gray-100 text-sm font-bold mr-3 text-gray-500">
                          {String.fromCharCode(65 + idx)}
                        </span>
                        {choice}
                      </button>
                    );
                  })}
                </div>
              )}

            {/* TRUE_FALSE */}
            {currentQuestion.question_type === 'true_false' && (
              <div className="flex gap-4">
                {['Vrai', 'Faux'].map((opt) => {
                  const isSelected =
                    answers[currentQuestion.id] === opt;
                  return (
                    <button
                      key={opt}
                      onClick={() =>
                        handleSelectAnswer(currentQuestion.id, opt)
                      }
                      className={`flex-1 p-4 rounded-xl border-2 text-center font-bold text-lg transition-all duration-200 ${
                        isSelected
                          ? 'border-amber-500 bg-amber-50 text-amber-900 shadow-md'
                          : 'border-gray-200 bg-white hover:border-gray-300 text-gray-700'
                      }`}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            )}

            {/* FILL_BLANK */}
            {currentQuestion.question_type === 'fill_blank' && (
              <FillBlankInput
                questionId={currentQuestion.id}
                currentAnswer={answers[currentQuestion.id] || ''}
                onSubmit={handleFillBlankSubmit}
              />
            )}
          </div>
        )}
      </main>

      {/* Footer navigation */}
      <footer className="sticky bottom-0 bg-white border-t border-gray-100 p-4">
        <div className="flex items-center justify-between max-w-3xl mx-auto gap-3">
          <Button
            variant={ButtonVariant.GHOST}
            onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
            disabled={currentIndex === 0}
            className="px-3"
          >
            <ChevronLeft size={18} className="mr-1" />
            Préc.
          </Button>

          <div className="text-xs text-gray-400 font-medium">
            {answeredCount}/{questions.length} répondue{answeredCount !== 1 ? 's' : ''}
          </div>

          {currentIndex < questions.length - 1 ? (
            <Button
              variant={ButtonVariant.GHOST}
              onClick={() => setCurrentIndex((i) => i + 1)}
              className="px-3"
            >
              Suiv.
              <ChevronRight size={18} className="ml-1" />
            </Button>
          ) : (
            <Button
              variant={ButtonVariant.PRIMARY}
              onClick={() => setShowConfirmModal(true)}
              className="px-4"
            >
              Terminer
            </Button>
          )}
        </div>

        {currentIndex < questions.length - 1 && answeredCount > 0 && (
          <div className="max-w-3xl mx-auto mt-3">
            <Button
              fullWidth
              variant={ButtonVariant.DANGER}
              onClick={() => setShowConfirmModal(true)}
              disabled={isSubmitting}
            >
              Terminer l'examen
            </Button>
          </div>
        )}
      </footer>

      {/* Confirmation modal */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="Terminer l'examen ?"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Tu as répondu à <span className="font-bold">{answeredCount}</span> question
            {answeredCount !== 1 ? 's' : ''} sur{' '}
            <span className="font-bold">{questions.length}</span>.
          </p>
          {answeredCount < questions.length && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm text-amber-700 flex items-start gap-2">
              <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
              <span>
                Les questions non répondues seront comptées comme fausses.
              </span>
            </div>
          )}
          <div className="flex gap-3 pt-2">
            <Button
              fullWidth
              variant={ButtonVariant.GHOST}
              onClick={() => setShowConfirmModal(false)}
            >
              Continuer
            </Button>
            <Button
              fullWidth
              variant={ButtonVariant.DANGER}
              onClick={handleComplete}
              isLoading={isSubmitting}
            >
              Terminer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

/** Numeric input for CEP sub-questions */
const NumericInput: React.FC<{
  answerKey: string;
  currentAnswer: string;
  onSubmit: (value: string) => void;
}> = ({ answerKey, currentAnswer, onSubmit }) => {
  const [value, setValue] = useState(currentAnswer);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setValue(currentAnswer);
  }, [currentAnswer, answerKey]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [answerKey]);

  return (
    <div className="space-y-2">
      <input
        ref={inputRef}
        type="text"
        inputMode="decimal"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') onSubmit(value);
        }}
        placeholder="Tape ta réponse (nombre)..."
        className="w-full p-3 border-2 border-gray-200 rounded-xl text-base focus:border-amber-500 focus:outline-none transition-colors"
      />
      <Button
        fullWidth
        onClick={() => onSubmit(value)}
        disabled={!value.trim()}
        size="sm"
      >
        Valider
      </Button>
    </div>
  );
};

/** Inline fill-blank input with Enter to submit */
const FillBlankInput: React.FC<{
  questionId: string;
  currentAnswer: string;
  onSubmit: (questionId: string, answer: string) => void;
}> = ({ questionId, currentAnswer, onSubmit }) => {
  const [value, setValue] = useState(currentAnswer);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setValue(currentAnswer);
  }, [currentAnswer, questionId]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [questionId]);

  return (
    <div className="space-y-2">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') onSubmit(questionId, value);
        }}
        placeholder="Tape ta réponse ici..."
        className="w-full p-3 border-2 border-gray-200 rounded-xl text-base focus:border-amber-500 focus:outline-none transition-colors"
      />
      <Button
        fullWidth
        onClick={() => onSubmit(questionId, value)}
        disabled={!value.trim()}
        size="sm"
      >
        Valider la réponse
      </Button>
    </div>
  );
};
