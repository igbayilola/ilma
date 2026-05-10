import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Cards';
import { Skeleton } from '../../components/ui/Skeleton';
import { LessonRenderer } from '../../components/lesson/LessonRenderer';
import { ButtonVariant } from '../../types';
import { ArrowLeft, BookOpen, Play, TrendingUp, Lightbulb } from 'lucide-react';
import { contentService, LessonDTO, SkillDTO } from '../../services/contentService';
import { progressService, SkillProgressDTO } from '../../services/progressService';

export const SkillDetailPage: React.FC = () => {
  const { subjectId, domainId, skillId } = useParams<{
    subjectId: string;
    domainId: string;
    skillId: string;
  }>();
  const navigate = useNavigate();

  const [skill, setSkill] = useState<SkillDTO | null>(null);
  const [lessons, setLessons] = useState<LessonDTO[]>([]);
  const [progress, setProgress] = useState<SkillProgressDTO | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showFullLesson, setShowFullLesson] = useState(false);

  const returnPath = `/app/student/subjects/${subjectId}/domains/${domainId}`;

  useEffect(() => {
    if (!skillId) return;
    setIsLoading(true);

    Promise.all([
      contentService.getSkillWithLessons(skillId),
      progressService.getSkillsProgress().catch(() => [] as SkillProgressDTO[]),
    ])
      .then(([{ skill: sk, lessons: ls }, progressList]) => {
        setSkill(sk);
        setLessons(ls);
        const p = progressList.find(p => p.skillId === skillId) || null;
        setProgress(p);
      })
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, [skillId]);

  const score = progress?.score ?? 0;
  const hasLesson = lessons.length > 0;
  const primaryLesson = hasLesson ? lessons[0] : null;
  const hasStructuredLesson = primaryLesson?.sections != null;

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto p-6 space-y-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <Skeleton variant="rect" className="h-32" />
        <Skeleton variant="rect" className="h-64" />
      </div>
    );
  }

  if (!skill) {
    return (
      <div className="min-h-screen bg-sitou-surface flex flex-col items-center justify-center p-8 text-center">
        <BookOpen size={48} className="text-gray-300 mb-4" />
        <h2 className="text-xl font-bold text-gray-700 mb-2">Comp&eacute;tence introuvable</h2>
        <Button onClick={() => navigate(returnPath)}>Retour</Button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto pb-24">
      {/* Header */}
      <header className="p-4 bg-white border-b border-gray-100 sticky top-0 z-20 flex items-center justify-between">
        <button
          onClick={() => navigate(returnPath)}
          className="flex items-center text-gray-500 font-bold text-sm hover:text-sitou-primary"
        >
          <ArrowLeft size={20} className="mr-1" /> Retour
        </button>
      </header>

      <div className="p-6 space-y-6">
        {/* Skill title + progress */}
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-2">
            {skill.name}
          </h1>
          {skill.description && (
            <p className="text-gray-500">{skill.description}</p>
          )}
        </div>

        {/* Progress card */}
        <Card className="bg-gradient-to-r from-sitou-primary/5 to-amber-50 border border-sitou-primary/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-sitou-primary/10 flex items-center justify-center">
                <TrendingUp size={20} className="text-sitou-primary" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Ma progression</p>
                <p className="text-2xl font-extrabold text-gray-900">{score}%</p>
              </div>
            </div>
            <div className="w-32 h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${score >= 90 ? 'bg-green-500' : score > 0 ? 'bg-sitou-primary' : 'bg-gray-300'}`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        </Card>

        {/* Lesson section */}
        {hasLesson && primaryLesson && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900 flex items-center">
                <BookOpen size={20} className="mr-2 text-sitou-primary" />
                Le&ccedil;on
              </h2>
              {hasStructuredLesson && !showFullLesson && (
                <button
                  onClick={() => setShowFullLesson(true)}
                  className="text-sm text-sitou-primary font-semibold hover:underline"
                >
                  Voir la le&ccedil;on compl&egrave;te
                </button>
              )}
            </div>

            {showFullLesson || !hasStructuredLesson ? (
              <LessonRenderer lesson={primaryLesson} />
            ) : (
              /* Summary preview for structured lessons */
              <Card className="bg-yellow-50 border-yellow-200 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setShowFullLesson(true)}
              >
                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 rounded-lg bg-yellow-100 flex items-center justify-center flex-shrink-0">
                    <Lightbulb size={20} className="text-yellow-600" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 mb-1">{primaryLesson.title}</h3>
                    {primaryLesson.summary && (
                      <p className="text-gray-600 text-sm line-clamp-2">{primaryLesson.summary}</p>
                    )}
                    {primaryLesson.formula && (
                      <p className="mt-2 text-yellow-800 font-mono text-sm bg-yellow-100 inline-block px-2 py-1 rounded">
                        {primaryLesson.formula}
                      </p>
                    )}
                    <p className="text-sitou-primary text-sm font-semibold mt-2">
                      Cliquer pour voir la le&ccedil;on en 4 &eacute;tapes &rarr;
                    </p>
                  </div>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Exercise CTA */}
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-100 z-30 max-w-3xl mx-auto">
          <Button
            fullWidth
            size="lg"
            variant={ButtonVariant.PRIMARY}
            className="h-14 text-lg shadow-lg"
            onClick={() =>
              navigate(`/app/student/exercise/${skillId}`, {
                state: {
                  returnPath: `/app/student/subjects/${subjectId}/domains/${domainId}/skills/${skillId}`,
                  subjectId,
                },
              })
            }
          >
            <Play size={20} className="mr-2" />
            {score > 0 ? 'Continuer les exercices' : 'Commencer les exercices'}
          </Button>
        </div>
      </div>
    </div>
  );
};
