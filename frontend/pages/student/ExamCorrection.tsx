import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import {
  CheckCircle2,
  XCircle,
  Trophy,
  ArrowLeft,
  Share2,
  BookOpen,
} from 'lucide-react';
import {
  examService,
  ExamSessionDetailDTO,
} from '../../services/examService';

export const ExamCorrectionPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<ExamSessionDetailDTO | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    examService
      .getSession(sessionId)
      .then(setSession)
      .catch((err) => {
        console.error('Failed to load session:', err);
        setError("Impossible de charger la correction.");
      })
      .finally(() => setIsLoading(false));
  }, [sessionId]);

  const handleShare = () => {
    if (!session) return;
    const pct = Math.round(session.percentage ?? (session.total_correct / session.total_questions) * 100);
    const text = `J'ai obtenu ${pct}% (${session.predicted_cep_score}/20 CEP) \u00e0 un examen blanc sur ILMA !`;
    const url = 'https://ilma.app';

    if (navigator.share) {
      navigator.share({ title: 'Mon r\u00e9sultat CEP - ILMA', text, url }).catch(() => {});
    } else {
      navigator.clipboard
        .writeText(`${text} ${url}`)
        .then(() => alert('R\u00e9sultat copi\u00e9 dans le presse-papier !'))
        .catch(() => {});
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-3xl mx-auto p-6">
        <Skeleton variant="rect" className="h-48" />
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} variant="rect" className="h-24" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center">
        <XCircle size={48} className="text-gray-300 mb-4" />
        <p className="text-gray-500 mb-4">{error || 'Session introuvable.'}</p>
        <Button onClick={() => navigate('/app/student/exams')}>
          Retour aux examens
        </Button>
      </div>
    );
  }

  const percentage = Math.round(
    session.percentage ?? (session.total_correct / session.total_questions) * 100
  );
  const isGood = percentage >= 50;

  return (
    <div className="max-w-3xl mx-auto pb-8">
      {/* Score header */}
      <div
        className={`p-6 md:p-8 rounded-b-3xl mb-6 ${
          isGood
            ? 'bg-gradient-to-br from-green-50 to-emerald-50'
            : 'bg-gradient-to-br from-orange-50 to-amber-50'
        }`}
      >
        <div className="text-center mb-6">
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-2 font-display">
            {isGood ? 'Bien jou\u00e9 !' : 'Continue tes efforts !'}
          </h1>
          {session.mock_exam_title && (
            <p className="text-gray-500 text-sm">{session.mock_exam_title}</p>
          )}
        </div>

        {/* Score circle */}
        <div className="flex justify-center mb-6">
          <div
            className={`w-28 h-28 rounded-full flex flex-col items-center justify-center border-4 ${
              isGood ? 'border-green-400 bg-white' : 'border-orange-400 bg-white'
            }`}
          >
            <span className="text-3xl font-extrabold text-gray-900">
              {percentage}%
            </span>
            <span className="text-xs text-gray-400 font-medium">
              {session.total_correct}/{session.total_questions}
            </span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-white/60 h-3 rounded-full overflow-hidden mb-4">
          <div
            className={`h-full rounded-full transition-all duration-1000 ease-out ${
              isGood ? 'bg-green-500' : 'bg-orange-500'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-white/80 rounded-xl p-3">
            <span className="block text-xl font-bold text-gray-900">
              {session.total_correct}
            </span>
            <span className="text-xs text-gray-400 font-medium">Correctes</span>
          </div>
          <div className="bg-white/80 rounded-xl p-3">
            <span className="block text-xl font-bold text-gray-900">
              {session.total_questions - session.total_correct}
            </span>
            <span className="text-xs text-gray-400 font-medium">Erreurs</span>
          </div>
          <div className="bg-white/80 rounded-xl p-3">
            <div className="flex items-center justify-center gap-1">
              <Trophy size={16} className="text-amber-500" />
              <span className="text-xl font-bold text-amber-600">
                {session.predicted_cep_score}
              </span>
            </div>
            <span className="text-xs text-gray-400 font-medium">/ 20 CEP</span>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="px-6 flex gap-3 mb-8">
        <Button
          fullWidth
          variant={ButtonVariant.GHOST}
          leftIcon={<Share2 size={16} />}
          onClick={handleShare}
        >
          Partager
        </Button>
        <Button
          fullWidth
          leftIcon={<ArrowLeft size={16} />}
          onClick={() => navigate('/app/student/exams')}
        >
          Retour
        </Button>
      </div>

      {/* Questions review */}
      <div className="px-6 space-y-4">
        <h2 className="text-lg font-bold text-gray-900 font-display">
          D\u00e9tail des r\u00e9ponses
        </h2>

        {session.answers.map((ans, idx) => (
          <div
            key={ans.question_id}
            className={`rounded-xl border-2 p-4 ${
              ans.is_correct
                ? 'border-green-200 bg-green-50/50'
                : 'border-red-200 bg-red-50/50'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5 flex-shrink-0">
                {ans.is_correct ? (
                  <CheckCircle2 size={20} className="text-green-500" />
                ) : (
                  <XCircle size={20} className="text-red-500" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-gray-400 mb-1">
                  Question {idx + 1}
                </p>
                <p className="text-gray-900 font-medium mb-3 leading-relaxed">
                  {ans.question_text}
                </p>

                <div className="space-y-1.5 text-sm">
                  <div className="flex items-start gap-2">
                    <span className="text-gray-400 font-medium min-w-[90px]">
                      Ta r&eacute;ponse :
                    </span>
                    <span
                      className={`font-semibold ${
                        ans.is_correct ? 'text-green-700' : 'text-red-700'
                      }`}
                    >
                      {ans.student_answer || '(non r\u00e9pondu)'}
                    </span>
                  </div>
                  {!ans.is_correct && (
                    <div className="flex items-start gap-2">
                      <span className="text-gray-400 font-medium min-w-[90px]">
                        Bonne r&eacute;ponse :
                      </span>
                      <span className="font-semibold text-green-700">
                        {ans.correct_answer}
                      </span>
                    </div>
                  )}
                </div>

                {ans.explanation && (
                  <div className="mt-3 bg-white/80 rounded-lg p-3 text-sm text-gray-600 leading-relaxed">
                    {ans.explanation}
                  </div>
                )}

                {ans.related_lesson_id && (
                  <button
                    onClick={() =>
                      navigate(`/app/student/lesson/${ans.related_lesson_id}`)
                    }
                    className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-amber-600 hover:text-amber-700 transition-colors"
                  >
                    <BookOpen size={14} />
                    Voir la micro-le\u00e7on
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Bottom return button */}
      <div className="px-6 mt-8">
        <Button
          fullWidth
          variant={ButtonVariant.GHOST}
          onClick={() => navigate('/app/student/exams')}
        >
          Retour aux examens
        </Button>
      </div>
    </div>
  );
};
