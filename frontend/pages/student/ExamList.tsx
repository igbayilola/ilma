import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import { ClipboardList, Clock, Lock, Trophy, ChevronRight, History } from 'lucide-react';
import { examService, MockExamDTO, ExamHistoryItemDTO } from '../../services/examService';
import { useAuthStore } from '../../store/authStore';

export const ExamListPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, activeProfile } = useAuthStore();
  const effectiveTier = activeProfile?.subscriptionTier || user?.subscriptionTier;
  const isPremium = effectiveTier !== 'free';

  const [exams, setExams] = useState<MockExamDTO[]>([]);
  const [history, setHistory] = useState<ExamHistoryItemDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [startingId, setStartingId] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      examService.listExams().catch(() => [] as MockExamDTO[]),
      examService.getHistory().catch(() => [] as ExamHistoryItemDTO[]),
    ])
      .then(([examsData, historyData]) => {
        setExams(examsData);
        setHistory(historyData);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const handleStartExam = async (exam: MockExamDTO) => {
    if (!exam.is_free && !isPremium) return;
    setStartingId(exam.id);
    try {
      const session = await examService.startExam(exam.id);
      navigate(`/app/student/exams/${exam.id}/play`, {
        state: { session },
      });
    } catch (err) {
      console.error('Failed to start exam:', err);
      setStartingId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} variant="rect" className="h-40" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <header>
        <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-2 font-display">
          Examens Blancs CEP
        </h1>
        <p className="text-gray-500">
          Entra&icirc;ne-toi dans les conditions r&eacute;elles du CEP.
        </p>
      </header>

      {/* Available exams */}
      {exams.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <ClipboardList size={48} className="mx-auto mb-4 opacity-50" />
          <p className="font-medium">Aucun examen disponible pour le moment.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {exams.map((exam) => {
            const locked = !exam.is_free && !isPremium;
            return (
              <Card key={exam.id} className="p-6 relative overflow-hidden">
                {/* Badge */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center text-amber-600">
                      <ClipboardList size={20} />
                    </div>
                    <span
                      className={`text-xs font-bold uppercase px-2 py-0.5 rounded-full ${
                        exam.is_free
                          ? 'bg-green-100 text-green-700'
                          : 'bg-purple-100 text-purple-700'
                      }`}
                    >
                      {exam.is_free ? 'Gratuit' : 'Premium'}
                    </span>
                  </div>
                  {locked && <Lock size={18} className="text-gray-300" />}
                </div>

                <h3 className="text-lg font-bold text-gray-900 mb-2 font-display">
                  {exam.title}
                </h3>

                {exam.description && (
                  <p className="text-sm text-gray-500 mb-3">{exam.description}</p>
                )}

                <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                  <span className="flex items-center gap-1">
                    <Clock size={14} />
                    {exam.duration_minutes} min
                  </span>
                  <span className="flex items-center gap-1">
                    <ClipboardList size={14} />
                    {exam.total_questions} questions
                  </span>
                </div>

                {locked ? (
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm text-amber-700">
                    <Lock size={14} className="inline mr-1" />
                    Passe en Premium pour acc&eacute;der &agrave; cet examen.
                    <Button
                      variant={ButtonVariant.GHOST}
                      size="sm"
                      className="mt-2 text-amber-700 underline"
                      onClick={() => navigate('/app/subscription/plans')}
                    >
                      Voir les offres
                    </Button>
                  </div>
                ) : (
                  <Button
                    fullWidth
                    onClick={() => handleStartExam(exam)}
                    isLoading={startingId === exam.id}
                    disabled={startingId !== null}
                  >
                    Commencer l'examen
                    <ChevronRight size={18} className="ml-1" />
                  </Button>
                )}
              </Card>
            );
          })}
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-4 font-display flex items-center gap-2">
            <History size={20} />
            Historique
          </h2>
          <div className="space-y-3">
            {history.map((item) => {
              const pct = Math.round(item.percentage ?? (item.total_correct / item.total_questions) * 100);
              const isGood = pct >= 50;
              return (
                <Card
                  key={item.session_id}
                  interactive
                  onClick={() =>
                    navigate(`/app/student/exams/${item.session_id}/correction`)
                  }
                  className="p-4 flex items-center gap-4"
                >
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg ${
                      isGood
                        ? 'bg-green-100 text-green-700'
                        : 'bg-orange-100 text-orange-700'
                    }`}
                  >
                    {pct}%
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-bold text-gray-900 truncate">
                      {item.mock_exam_title}
                    </h4>
                    <p className="text-sm text-gray-500">
                      {item.total_correct}/{item.total_questions} correct
                      {item.predicted_cep_score != null && (
                        <span className="ml-2 text-amber-600 font-semibold">
                          <Trophy size={12} className="inline mr-0.5" />
                          {item.predicted_cep_score}/20 CEP
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {new Date(item.completed_at).toLocaleDateString('fr-FR', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                      })}
                    </p>
                  </div>
                  <ChevronRight size={20} className="text-gray-300" />
                </Card>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
};
