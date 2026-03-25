import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { ButtonVariant } from '../../types';
import { X, ChevronLeft, ChevronRight, Clock, AlertTriangle } from 'lucide-react';
import {
  examService,
  ExamQuestionDTO,
  ExamSessionDTO,
} from '../../services/examService';

type PlayerState = 'LOADING' | 'ACTIVE' | 'COMPLETING';

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

export const ExamPlayerPage: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  // Session can be passed via location.state from ExamList
  const passedSession = (location.state as { session?: ExamSessionDTO })?.session;

  const [state, setState] = useState<PlayerState>(passedSession ? 'ACTIVE' : 'LOADING');
  const [sessionId, setSessionId] = useState<string>(passedSession?.session_id || '');
  const [questions, setQuestions] = useState<ExamQuestionDTO[]>(
    passedSession?.questions || []
  );
  const [currentIndex, setCurrentIndex] = useState(0);
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
      // Estimate duration from exam metadata - default 60 min
      setTimeLeft(60 * 60);
      return;
    }
    if (!examId) return;

    examService
      .startExam(examId)
      .then((session) => {
        setSessionId(session.session_id);
        setQuestions(session.questions || []);
        setTimeLeft(60 * 60); // default 60 min
        setState('ACTIVE');
      })
      .catch((err) => {
        console.error('Failed to start exam:', err);
        navigate('/app/student/exams');
      });
  }, [examId, passedSession, navigate]);

  // Update timer from exam metadata via exams list
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
      // Navigate anyway so user isn't stuck
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
        // Show warning at 5 minutes
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

  // Submit answer to backend
  const submitAnswer = useCallback(
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

  const handleSelectAnswer = (questionId: string, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
    submitAnswer(questionId, answer);

    // Auto-advance after short delay for MCQ and TRUE_FALSE
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
    submitAnswer(questionId, answer.trim());
    // Auto-advance
    if (currentIndex < questions.length - 1) {
      setTimeout(() => setCurrentIndex((i) => i + 1), 400);
    }
  };

  const handleQuit = () => {
    if (
      window.confirm(
        'Tu veux vraiment quitter ? Tes r\u00e9ponses seront perdues.'
      )
    ) {
      navigate('/app/student/exams');
    }
  };

  const currentQuestion = questions[currentIndex];
  const answeredCount = Object.keys(answers).length;
  const isLowTime = timeLeft <= 5 * 60;

  if (state === 'LOADING' || state === 'COMPLETING') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        <div className="w-12 h-12 border-4 border-amber-200 border-t-amber-500 rounded-full animate-spin mb-4" />
        <p className="text-gray-500 font-medium">
          {state === 'LOADING'
            ? "Pr\u00e9paration de l'examen..."
            : 'Correction en cours...'}
        </p>
      </div>
    );
  }

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
            Pr&eacute;c.
          </Button>

          <div className="text-xs text-gray-400 font-medium">
            {answeredCount}/{questions.length} r&eacute;pondu
            {answeredCount !== 1 ? 'es' : 'e'}
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

        {/* Finish button always visible once some answers exist */}
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
            Tu as r&eacute;pondu &agrave; <span className="font-bold">{answeredCount}</span> question
            {answeredCount !== 1 ? 's' : ''} sur{' '}
            <span className="font-bold">{questions.length}</span>.
          </p>
          {answeredCount < questions.length && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm text-amber-700 flex items-start gap-2">
              <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
              <span>
                Les questions non r&eacute;pondues seront compt&eacute;es comme
                fausses.
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
    <div className="space-y-3">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') onSubmit(questionId, value);
        }}
        placeholder="Tape ta r\u00e9ponse ici..."
        className="w-full p-4 border-2 border-gray-200 rounded-xl text-lg focus:border-amber-500 focus:outline-none transition-colors"
      />
      <Button
        fullWidth
        onClick={() => onSubmit(questionId, value)}
        disabled={!value.trim()}
      >
        Valider la r&eacute;ponse
      </Button>
    </div>
  );
};
