/**
 * Page « Mon programme » — vue annuelle T1/T2/T3 (iter 22).
 *
 * Charge subjects + skills + progress (même flux que le Dashboard) puis
 * délègue à {@link ProgramTimeline}.
 */
import React, { useEffect, useState } from 'react';
import { contentService, SubjectDTO, SkillDTO } from '../../services/contentService';
import { progressService, SkillProgressDTO } from '../../services/progressService';
import { useAuthStore } from '../../store/authStore';
import { ProgramTimeline } from '../../components/dashboard/ProgramTimeline';
import { Skeleton } from '../../components/ui/Skeleton';

export const ProgrammePage: React.FC = () => {
  const { user, activeProfile } = useAuthStore();
  const gradeLevelId = activeProfile?.gradeLevelId || user?.gradeLevelId;
  const [isLoading, setIsLoading] = useState(true);
  const [subjects, setSubjects] = useState<SubjectDTO[]>([]);
  const [skillsBySubject, setSkillsBySubject] = useState<Map<string, SkillDTO[]>>(new Map());
  const [progress, setProgress] = useState<SkillProgressDTO[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const subjectsData = await contentService
          .listSubjects(gradeLevelId)
          .catch(() => [] as SubjectDTO[]);
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
        subjectsData.forEach((s, i) => skillsMap.set(s.id, skillsResults[i]));
        setSkillsBySubject(skillsMap);

        const prog = await progressService.getSkillsProgress().catch(() => [] as SkillProgressDTO[]);
        setProgress(prog);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [gradeLevelId]);

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

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="h-48 w-full" />
          ))}
        </div>
      ) : (
        <ProgramTimeline
          subjects={subjects}
          skillsBySubject={skillsBySubject}
          progress={progress}
        />
      )}
    </div>
  );
};

export default ProgrammePage;
