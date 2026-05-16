import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { SanitizedHTML } from '../../components/ui/SanitizedHTML';
import { ButtonVariant } from '../../types';
import {
  CheckCircle2,
  XCircle,
  Trophy,
  ArrowLeft,
  Share2,
  BookOpen,
  Link2,
} from 'lucide-react';
import {
  examService,
  ExamSessionDetailDTO,
} from '../../services/examService';

const DOMAIN_LABELS: Record<string, string> = {
  data_proportionality: 'Données & Proportionnalité',
  measures_operations: 'Mesures & Opérations',
  geometry: 'Géométrie',
};

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
    const isCep = session.exam_type === 'cep';
    const scoreText = isCep
      ? `${session.predicted_cep_score}/20`
      : `${Math.round(session.percentage ?? (session.total_correct / session.total_questions) * 100)}%`;
    const text = `J'ai obtenu ${scoreText} à un examen blanc CEP sur Sitou !`;
    const url = 'https://sitou.app';

    if (navigator.share) {
      navigator.share({ title: 'Mon résultat CEP - Sitou', text, url }).catch(() => {});
    } else {
      navigator.clipboard
        .writeText(`${text} ${url}`)
        .then(() => alert('Résultat copié dans le presse-papier !'))
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

  const isCep = session.exam_type === 'cep';

  // ─── CEP CORRECTION ──────────────────────────────
  if (isCep && session.items) {
    const cepScore = session.predicted_cep_score ?? 0;
    const isGood = cepScore >= 10;

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
              {isGood ? 'Bien joué !' : 'Continue tes efforts !'}
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
                {cepScore}
              </span>
              <span className="text-sm text-gray-400 font-bold">/ 20</span>
            </div>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-white/60 h-3 rounded-full overflow-hidden mb-4">
            <div
              className={`h-full rounded-full transition-all duration-1000 ease-out ${
                isGood ? 'bg-green-500' : 'bg-orange-500'
              }`}
              style={{ width: `${(cepScore / 20) * 100}%` }}
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
                {session.total_questions - (session.total_correct ?? 0)}
              </span>
              <span className="text-xs text-gray-400 font-medium">Erreurs</span>
            </div>
            <div className="bg-white/80 rounded-xl p-3">
              <div className="flex items-center justify-center gap-1">
                <Trophy size={16} className="text-amber-500" />
                <span className="text-xl font-bold text-amber-600">
                  {cepScore}
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

        {/* Items review */}
        <div className="px-6 space-y-8">
          <h2 className="text-lg font-bold text-gray-900 font-display">
            Détail par item
          </h2>

          {session.items.map((item) => {
            const domainLabel = DOMAIN_LABELS[item.domain] || item.domain;
            const itemPoints = item.sub_questions.reduce((s, sq) => s + (sq.points_earned ?? 0), 0);
            const itemTotal = item.sub_questions.reduce((s, sq) => s + (sq.points_possible ?? 0), 0);

            return (
              <div key={item.item_number} className="space-y-4">
                {/* Item header */}
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm">
                    {item.item_number}
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase text-blue-600">{domainLabel}</span>
                    <span className="ml-3 text-xs font-bold text-gray-400">
                      {itemPoints.toFixed(1)} / {itemTotal.toFixed(1)} pts
                    </span>
                  </div>
                </div>

                {/* Context */}
                {item.context_text && (
                  <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {item.context_text}
                    </p>
                  </div>
                )}

                {/* Sub-questions */}
                <div className="space-y-3">
                  {item.sub_questions.map((sq) => (
                    <div
                      key={sq.sub_question_id}
                      className={`rounded-xl border-2 p-4 ${
                        sq.is_correct
                          ? 'border-green-200 bg-green-50/50'
                          : 'border-red-200 bg-red-50/50'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5 flex-shrink-0">
                          {sq.is_correct ? (
                            <CheckCircle2 size={20} className="text-green-500" />
                          ) : (
                            <XCircle size={20} className="text-red-500" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-900 text-white text-xs font-bold">
                              {sq.sub_label})
                            </span>
                            <span className="text-xs font-bold text-gray-400">
                              {sq.points_earned?.toFixed(1)} / {sq.points_possible?.toFixed(1)} pts
                            </span>
                          </div>
                          <p className="text-gray-900 font-medium mb-3 leading-relaxed text-sm">
                            {sq.text}
                          </p>

                          {sq.depends_on_previous && (
                            <div className="flex items-center gap-1.5 text-xs text-amber-600 font-medium mb-2">
                              <Link2 size={12} />
                              {sq.hint || 'Cette question dépend de la précédente.'}
                            </div>
                          )}

                          <div className="space-y-1.5 text-sm">
                            <div className="flex items-start gap-2">
                              <span className="text-gray-400 font-medium min-w-[90px]">
                                Ta réponse :
                              </span>
                              <span
                                className={`font-semibold ${
                                  sq.is_correct ? 'text-green-700' : 'text-red-700'
                                }`}
                              >
                                {sq.student_answer || '(non répondu)'}
                              </span>
                            </div>
                            {!sq.is_correct && (
                              <div className="flex items-start gap-2">
                                <span className="text-gray-400 font-medium min-w-[90px]">
                                  Bonne réponse :
                                </span>
                                <span className="font-semibold text-green-700">
                                  {sq.correct_answer}
                                </span>
                              </div>
                            )}
                          </div>

                          {sq.explanation && (
                            <SanitizedHTML
                              html={sq.explanation}
                              className="mt-3 bg-white/80 rounded-lg p-3 text-sm text-gray-600 leading-relaxed prose prose-sm max-w-none"
                            />
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
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
  }

  // ─── QCM CORRECTION (legacy) ──────────────────────
  const percentage = Math.round(
    session.percentage ?? (session.total_correct / session.total_questions) * 100
  );
  const isGood = percentage >= 50;
  const corrections = session.corrections || session.answers || [];

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
            {isGood ? 'Bien joué !' : 'Continue tes efforts !'}
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
          Détail des réponses
        </h2>

        {corrections.map((ans, idx) => (
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
                      Ta réponse :
                    </span>
                    <span
                      className={`font-semibold ${
                        ans.is_correct ? 'text-green-700' : 'text-red-700'
                      }`}
                    >
                      {ans.student_answer || '(non répondu)'}
                    </span>
                  </div>
                  {!ans.is_correct && (
                    <div className="flex items-start gap-2">
                      <span className="text-gray-400 font-medium min-w-[90px]">
                        Bonne réponse :
                      </span>
                      <span className="font-semibold text-green-700">
                        {ans.correct_answer}
                      </span>
                    </div>
                  )}
                </div>

                {ans.explanation && (
                  <SanitizedHTML
                    html={ans.explanation}
                    className="mt-3 bg-white/80 rounded-lg p-3 text-sm text-gray-600 leading-relaxed prose prose-sm max-w-none"
                  />
                )}

                {ans.related_lesson_id && (
                  <button
                    onClick={() =>
                      navigate(`/app/student/lesson/${ans.related_lesson_id}`)
                    }
                    className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-amber-600 hover:text-amber-700 transition-colors"
                  >
                    <BookOpen size={14} />
                    Voir la micro-leçon
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
