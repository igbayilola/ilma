/**
 * Page « Mon programme » — vue annuelle T1/T2/T3 (iter 22).
 *
 * Charge subjects + skills + progress (même flux que le Dashboard) puis
 * délègue à {@link ProgramTimeline}. Iter 28 : garde `gradeLevelId`
 * manquant et état vide post-chargement.
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, GraduationCap } from 'lucide-react';
import { contentService, SubjectDTO, SkillDTO } from '../../services/contentService';
import { progressService, SkillProgressDTO } from '../../services/progressService';
import { useAuthStore } from '../../store/authStore';
import { ProgramTimeline } from '../../components/dashboard/ProgramTimeline';
import { CEPPredictionCard } from '../../components/dashboard/CEPPredictionCard';
import { Skeleton } from '../../components/ui/Skeleton';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { ButtonVariant } from '../../types';

export const ProgrammePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, activeProfile } = useAuthStore();
  const gradeLevelId = activeProfile?.gradeLevelId || user?.gradeLevelId;
  const [isLoading, setIsLoading] = useState(true);
  const [subjects, setSubjects] = useState<SubjectDTO[]>([]);
  const [skillsBySubject, setSkillsBySubject] = useState<Map<string, SkillDTO[]>>(new Map());
  const [progress, setProgress] = useState<SkillProgressDTO[]>([]);
  const [retryToken, setRetryToken] = useState(0);

  useEffect(() => {
    if (!gradeLevelId) {
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    const load = async () => {
      setIsLoading(true);
      try {
        const subjectsData = await contentService
          .listSubjects(gradeLevelId)
          .catch(() => [] as SubjectDTO[]);
        if (cancelled) return;
        setSubjects(subjectsData);

        const skillsMap = new Map<string, SkillDTO[]>();
        const skillsResults = await Promise.all(
          subjectsData.map(s =>
            contentService
              .listSkills(s.id)
              .then(r => r.items)
              .catch(() => [] as SkillDTO[]),
          ),
        );
        if (cancelled) return;
        subjectsData.forEach((s, i) => skillsMap.set(s.id, skillsResults[i]));
        setSkillsBySubject(skillsMap);

        const prog = await progressService
          .getSkillsProgress()
          .catch(() => [] as SkillProgressDTO[]);
        if (cancelled) return;
        setProgress(prog);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [gradeLevelId, retryToken]);

  const renderBody = () => {
    if (!gradeLevelId) {
      return (
        <Card>
          <div className="text-center py-8 flex flex-col items-center">
            <div className="w-16 h-16 gradient-hero rounded-full flex items-center justify-center mb-4 text-white">
              <GraduationCap size={32} />
            </div>
            <h3 className="text-lg font-bold text-gray-800 mb-1 font-display">
              Choisis ta classe
            </h3>
            <p className="text-gray-500 mb-6">
              Pour voir ton programme annuel, sélectionne d'abord ta classe.
            </p>
            <Button variant={ButtonVariant.PRIMARY} onClick={() => navigate('/select-profile')}>
              Choisir ma classe
            </Button>
          </div>
        </Card>
      );
    }
    if (isLoading) {
      return (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="h-48 w-full" />
          ))}
        </div>
      );
    }
    if (subjects.length === 0) {
      return (
        <Card>
          <div className="text-center py-8 flex flex-col items-center">
            <div className="w-16 h-16 gradient-hero rounded-full flex items-center justify-center mb-4 text-white">
              <AlertCircle size={32} />
            </div>
            <h3 className="text-lg font-bold text-gray-800 mb-1 font-display">
              Programme indisponible
            </h3>
            <p className="text-gray-500 mb-6">
              Aucune matière n'a pu être chargée. Vérifie ta connexion et réessaie.
            </p>
            <Button variant={ButtonVariant.SECONDARY} onClick={() => setRetryToken(t => t + 1)}>
              Réessayer
            </Button>
          </div>
        </Card>
      );
    }
    return (
      <ProgramTimeline
        subjects={subjects}
        skillsBySubject={skillsBySubject}
        progress={progress}
      />
    );
  };

  return (
    <div className="space-y-6 pb-20 md:pb-0">
      <header>
        <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 font-display">
          Mon programme CM2
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          Toutes tes leçons de l'année, regroupées par trimestre et semaine.
        </p>
      </header>

      {gradeLevelId && <CEPPredictionCard />}

      {renderBody()}
    </div>
  );
};

export default ProgrammePage;
