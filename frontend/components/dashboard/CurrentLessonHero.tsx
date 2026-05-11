import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, BookOpen, Sparkles, ChevronRight } from 'lucide-react';
import { Card } from '../ui/Cards';
import { Button } from '../ui/Button';
import { SubjectDTO, SkillDTO } from '../../services/contentService';
import { SkillProgressDTO } from '../../services/progressService';
import { ButtonVariant } from '../../types';

const MASTERY_THRESHOLD = 80;

export interface CurrentLessonHint {
  subject: SubjectDTO;
  skill: SkillDTO;
  /** Total skills in this subject (denominator of the progress bar). */
  subjectTotalSkills: number;
  /** Skills in this subject already touched (totalAttempts > 0). */
  subjectTouchedSkills: number;
  /** Skills in this subject already mastered (score >= MASTERY_THRESHOLD). */
  subjectMasteredSkills: number;
  /** True if every skill across every subject is mastered. */
  allMastered: boolean;
}

/**
 * Pick the "current lesson" the student should focus on.
 *
 * Proxy for curriculum sequencing while trimester data is not yet in the model:
 *  1. Walk subjects in `order`,
 *  2. inside each subject walk skills in `order`,
 *  3. return the first skill that is NOT mastered (smart_score < 80 or never attempted).
 *
 * Returns `null` when there is no content at all. When everything is mastered,
 * returns a hint flagged with `allMastered=true` carrying the last subject/skill
 * so the UI can show a celebration state.
 */
export function pickCurrentLesson(
  subjects: SubjectDTO[],
  skillsBySubject: Map<string, SkillDTO[]>,
  progress: SkillProgressDTO[],
): CurrentLessonHint | null {
  if (subjects.length === 0) return null;
  const progressById = new Map(progress.map(p => [p.skillId, p]));
  const sortedSubjects = [...subjects].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));

  let allMastered = true;
  let fallback: CurrentLessonHint | null = null;

  for (const subject of sortedSubjects) {
    const skills = [...(skillsBySubject.get(subject.id) || [])].sort(
      (a, b) => (a.order ?? 0) - (b.order ?? 0),
    );
    if (skills.length === 0) continue;

    let touched = 0;
    let mastered = 0;
    let firstNotMastered: SkillDTO | null = null;

    for (const skill of skills) {
      const p = progressById.get(skill.id);
      const attempts = p?.totalAttempts ?? 0;
      const score = p?.score ?? 0;
      if (attempts > 0) touched += 1;
      if (score >= MASTERY_THRESHOLD) mastered += 1;
      if (!firstNotMastered && score < MASTERY_THRESHOLD) {
        firstNotMastered = skill;
      }
    }

    if (firstNotMastered) {
      return {
        subject,
        skill: firstNotMastered,
        subjectTotalSkills: skills.length,
        subjectTouchedSkills: touched,
        subjectMasteredSkills: mastered,
        allMastered: false,
      };
    }

    // Everything in this subject is mastered — remember as a fallback in case
    // every other subject is also mastered.
    fallback = {
      subject,
      skill: skills[skills.length - 1],
      subjectTotalSkills: skills.length,
      subjectTouchedSkills: touched,
      subjectMasteredSkills: mastered,
      allMastered: true,
    };
  }

  if (fallback && allMastered) return fallback;
  return fallback;
}

export interface CurrentLessonHeroProps {
  subjects: SubjectDTO[];
  skillsBySubject: Map<string, SkillDTO[]>;
  progress: SkillProgressDTO[];
}

export const CurrentLessonHero: React.FC<CurrentLessonHeroProps> = ({
  subjects,
  skillsBySubject,
  progress,
}) => {
  const navigate = useNavigate();
  const hint = useMemo(
    () => pickCurrentLesson(subjects, skillsBySubject, progress),
    [subjects, skillsBySubject, progress],
  );

  if (!hint) return null;

  const { subject, skill, subjectTotalSkills, subjectTouchedSkills, subjectMasteredSkills, allMastered } = hint;
  const masteredPct = subjectTotalSkills > 0
    ? Math.round((subjectMasteredSkills / subjectTotalSkills) * 100)
    : 0;

  const goToLesson = () => {
    navigate(`/app/student/subjects/${subject.id}/domains/${skill.domainId}/skills/${skill.id}`);
  };

  if (allMastered) {
    return (
      <Card className="bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 border-emerald-200 shadow-clay">
        <div className="flex items-start gap-4 p-2">
          <div className="w-14 h-14 rounded-2xl bg-emerald-100 flex items-center justify-center flex-shrink-0">
            <Sparkles size={28} className="text-emerald-600" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-bold text-emerald-700 uppercase tracking-wide mb-1">
              Programme abord&eacute;
            </p>
            <h2 className="text-xl md:text-2xl font-extrabold text-gray-900 font-display mb-1">
              Bravo — tu ma&icirc;trises tout le programme CM2 !
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Continue de pratiquer pour consolider, ou explore les autres mati&egrave;res.
            </p>
            <Button
              onClick={() => navigate('/app/student/subjects')}
              variant={ButtonVariant.PRIMARY}
              leftIcon={<BookOpen size={18} />}
            >
              Explorer mes mati&egrave;res
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="relative overflow-hidden gradient-hero animate-gradient text-white border-none shadow-clay">
      <div className="relative z-10 p-2">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-bold uppercase tracking-wide bg-white/20 px-3 py-1 rounded-full backdrop-blur-sm">
            &#128218; Cette semaine en CM2
          </span>
        </div>

        <p className="text-sm font-medium text-amber-100 mb-1">
          {subject.emoji ? `${subject.emoji} ` : ''}{subject.name}
          {skill.domainName ? <> &middot; <span className="opacity-90">{skill.domainName}</span></> : null}
        </p>

        <h2 className="text-2xl md:text-3xl font-extrabold mb-4 leading-tight font-display">
          {skill.name}
        </h2>

        <div className="mb-5 max-w-md">
          <div className="flex items-center justify-between text-xs mb-1.5 text-amber-100">
            <span className="font-medium">
              Ta progression en {subject.name.toLowerCase()}
            </span>
            <span className="font-bold text-white">
              {subjectMasteredSkills}/{subjectTotalSkills} le&ccedil;ons ma&icirc;tris&eacute;es
            </span>
          </div>
          <div
            className="w-full bg-white/20 h-2.5 rounded-full overflow-hidden backdrop-blur-sm"
            role="progressbar"
            aria-valuenow={masteredPct}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Progression en ${subject.name}`}
          >
            <div
              className="h-full rounded-full bg-white transition-all duration-500"
              style={{ width: `${masteredPct}%` }}
            />
          </div>
          {subjectTouchedSkills > subjectMasteredSkills && (
            <p className="text-xs text-amber-100 mt-1.5">
              {subjectTouchedSkills - subjectMasteredSkills} le&ccedil;on
              {subjectTouchedSkills - subjectMasteredSkills > 1 ? 's' : ''} en cours
            </p>
          )}
        </div>

        <Button
          onClick={goToLesson}
          className="bg-white text-sitou-primary hover:bg-amber-50 border-none shadow-xl font-bold"
          leftIcon={<Play size={20} className="fill-current" />}
        >
          Continuer la le&ccedil;on
        </Button>
      </div>

      <div className="absolute right-0 bottom-0 opacity-10 transform translate-x-1/4 translate-y-1/4 pointer-events-none">
        <BookOpen size={260} />
      </div>
    </Card>
  );
};
